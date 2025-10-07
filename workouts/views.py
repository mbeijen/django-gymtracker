from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Exercise, WorkoutSession, ExerciseRecord, UserProfile
from .forms import WorkoutSessionForm, ExerciseRecordForm, ExerciseForm, UserProfileForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard showing recent workouts and quick stats"""

    template_name = "workouts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get recent workout sessions
        recent_workouts = WorkoutSession.objects.filter(user=user).order_by(
            "-date", "-start_time"
        )[:5]

        # Get today's workout if it exists
        today_workout = WorkoutSession.objects.filter(
            user=user, date=date.today()
        ).first()

        # Get workout stats for the last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_workouts_count = WorkoutSession.objects.filter(
            user=user, date__gte=thirty_days_ago
        ).count()

        # Get most recent exercise records for weight recommendations
        recent_exercises = ExerciseRecord.objects.filter(
            workout_session__user=user
        ).order_by("-created_at")[:10]

        context.update(
            {
                "recent_workouts": recent_workouts,
                "today_workout": today_workout,
                "recent_workouts_count": recent_workouts_count,
                "recent_exercises": recent_exercises,
            }
        )
        return context


class CreateWorkoutSessionView(LoginRequiredMixin, CreateView):
    """Create a new workout session"""

    model = WorkoutSession
    form_class = WorkoutSessionForm
    template_name = "workouts/create_workout.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, f"Workout session started for {form.instance.date}"
        )
        return response

    def get_success_url(self):
        return reverse("workouts:workout_detail", kwargs={"pk": self.object.pk})


class WorkoutSessionDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific workout session"""

    model = WorkoutSession
    template_name = "workouts/workout_detail.html"
    context_object_name = "workout"

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout = self.get_object()

        # Get exercise records for this workout
        exercise_records = workout.exercise_records.all().order_by("-created_at")

        # Calculate total volume
        total_volume = sum(record.total_volume for record in exercise_records)

        # Get exercises already done in this workout
        done_exercise_ids = set(exercise_records.values_list("exercise_id", flat=True))

        # Get all exercises, excluding ones already done in this workout
        available_exercises = Exercise.objects.exclude(id__in=done_exercise_ids)

        # Sort by most recent usage (last time this exercise was done by this user)
        # We'll annotate with the last usage date and sort by it
        from django.db.models import Max, Q

        available_exercises = available_exercises.annotate(
            last_used=Max(
                "exerciserecord__created_at",
                filter=Q(exerciserecord__workout_session__user=self.request.user),
            )
        ).order_by("-last_used", "name")

        context.update(
            {
                "exercise_records": exercise_records,
                "total_volume": total_volume,
                "available_exercises": available_exercises,
            }
        )
        return context


class AddExerciseToWorkoutView(LoginRequiredMixin, CreateView):
    """Add an exercise to a workout session"""

    model = ExerciseRecord
    form_class = ExerciseRecordForm
    template_name = "workouts/add_exercise.html"

    def dispatch(self, request, *args, **kwargs):
        # Only get workout if user is authenticated
        if request.user.is_authenticated:
            self.workout = get_object_or_404(
                WorkoutSession, pk=kwargs["pk"], user=request.user
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Pre-select exercise if provided in URL
        exercise_id = self.request.GET.get("exercise")
        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                kwargs["initial"] = {"exercise": exercise}
            except Exercise.DoesNotExist:
                pass

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workout"] = self.workout

        # Get recent performance for each exercise for weight recommendations
        exercises = Exercise.objects.all()
        exercise_recommendations = {}

        for exercise in exercises:
            last_record = (
                ExerciseRecord.objects.filter(
                    exercise=exercise, workout_session__user=self.request.user
                )
                .order_by("-created_at")
                .first()
            )

            if last_record:
                exercise_recommendations[exercise.id] = {
                    "last_weight": last_record.weight_kg,
                    "last_difficulty": last_record.difficulty_rating,
                    "recommended_weight": self._get_recommended_weight(last_record),
                }

        context["exercise_recommendations"] = exercise_recommendations
        return context

    def form_valid(self, form):
        form.instance.workout_session = self.workout
        response = super().form_valid(form)
        messages.success(
            self.request, f"Added {form.instance.exercise.name} to workout"
        )
        return response

    def get_success_url(self):
        return reverse("workouts:workout_detail", kwargs={"pk": self.workout.pk})

    def _get_recommended_weight(self, last_record):
        """Simple weight recommendation based on last difficulty"""
        from decimal import Decimal

        if not last_record or last_record.weight_kg is None:
            return Decimal(
                "0"
            )  # Default weight if no previous record or weight is None

        if last_record.difficulty_rating <= 5:
            # Easy to moderate, increase weight by 2.5kg
            return last_record.weight_kg + Decimal("2.5")
        elif last_record.difficulty_rating <= 7:
            # Hard, keep same weight
            return last_record.weight_kg
        else:
            # Very hard, decrease weight by 2.5kg
            return max(Decimal("0"), last_record.weight_kg - Decimal("2.5"))


class EditExerciseRecordView(LoginRequiredMixin, UpdateView):
    """Edit an exercise record"""

    model = ExerciseRecord
    form_class = ExerciseRecordForm
    template_name = "workouts/edit_exercise.html"

    def get_queryset(self):
        return ExerciseRecord.objects.filter(workout_session__user=self.request.user)

    def get_success_url(self):
        return reverse(
            "workouts:workout_detail", kwargs={"pk": self.object.workout_session.pk}
        )


class DeleteExerciseRecordView(LoginRequiredMixin, DeleteView):
    """Delete an exercise record"""

    model = ExerciseRecord
    template_name = "workouts/delete_exercise.html"

    def get_queryset(self):
        return ExerciseRecord.objects.filter(workout_session__user=self.request.user)

    def get_success_url(self):
        return reverse(
            "workouts:workout_detail", kwargs={"pk": self.object.workout_session.pk}
        )


class CompleteWorkoutView(LoginRequiredMixin, UpdateView):
    """Mark a workout session as completed"""

    model = WorkoutSession
    fields = ["end_time", "notes", "is_completed"]
    template_name = "workouts/complete_workout.html"

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.is_completed = True
        if not form.instance.end_time:
            form.instance.end_time = timezone.now().time()
        response = super().form_valid(form)
        messages.success(self.request, "Workout completed! Great job!")
        return response

    def get_success_url(self):
        return reverse("workouts:dashboard")


class ExerciseListView(LoginRequiredMixin, ListView):
    """List all available exercises"""

    model = Exercise
    template_name = "workouts/exercise_list.html"
    context_object_name = "exercises"
    paginate_by = 20


class AddExerciseView(LoginRequiredMixin, CreateView):
    """Add a new exercise type"""

    model = Exercise
    form_class = ExerciseForm
    template_name = "workouts/add_exercise_type.html"
    success_url = reverse_lazy("workouts:exercise_list")


class WorkoutHistoryView(LoginRequiredMixin, ListView):
    """View workout history with filtering"""

    model = WorkoutSession
    template_name = "workouts/workout_history.html"
    context_object_name = "workouts"
    paginate_by = 10

    def get_queryset(self):
        queryset = WorkoutSession.objects.filter(user=self.request.user)

        # Add date filtering if provided
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by("-date", "-start_time")


class UserProfileView(LoginRequiredMixin, UpdateView):
    """User profile settings"""

    model = UserProfile
    form_class = UserProfileForm
    template_name = "workouts/user_profile.html"
    success_url = reverse_lazy("workouts:user_profile")

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class SuperUserRequiredMixin(UserPassesTestMixin):
    """Mixin to require superuser status"""

    def test_func(self):
        return self.request.user.is_superuser


class ManageUsersView(SuperUserRequiredMixin, ListView):
    """Manage users page for superusers"""

    model = get_user_model()
    template_name = "workouts/manage_users.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return get_user_model().objects.all().order_by("-date_joined")


class InviteUserView(SuperUserRequiredMixin, CreateView):
    """Invite a new user"""

    model = get_user_model()
    fields = ["email"]
    template_name = "workouts/invite_user.html"
    success_url = reverse_lazy("workouts:manage_users")

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        # Check if user already exists
        if get_user_model().objects.filter(email=email).exists():
            messages.error(self.request, f"User with email {email} already exists.")
            return redirect("workouts:manage_users")

        # Create user account (they'll need to set password via email)
        user = form.save(commit=False)
        user.username = email  # Use email as username
        user.is_active = False  # User needs to activate via email
        user.save()

        # Create user profile
        UserProfile.objects.create(user=user)

        # Send invitation email
        try:
            send_mail(
                subject="Invitation to Gym Tracker",
                message=f"""
Hello!

You have been invited to join Gym Tracker. Please click the link below to set up your account:

{settings.SITE_URL}/accounts/signup/?email={email}

If you have any questions, please contact the administrator.

Best regards,
Gym Tracker Team
                """.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(self.request, f"Invitation sent to {email}")
        except Exception as e:
            messages.error(self.request, f"Failed to send invitation: {str(e)}")

        return redirect("workouts:manage_users")


class ResendInviteView(SuperUserRequiredMixin, TemplateView):
    """Resend invitation to a user"""

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(get_user_model(), id=user_id)

        try:
            send_mail(
                subject="Gym Tracker - Account Setup Reminder",
                message=f"""
Hello!

This is a reminder that you have an account on Gym Tracker. Please click the link below to set up your account:

{settings.SITE_URL}/accounts/signup/?email={user.email}

If you have any questions, please contact the administrator.

Best regards,
Gym Tracker Team
                """.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(self.request, f"Invitation resent to {user.email}")
        except Exception as e:
            messages.error(self.request, f"Failed to resend invitation: {str(e)}")

        return redirect("workouts:manage_users")


class ToggleSuperuserView(SuperUserRequiredMixin, TemplateView):
    """Toggle superuser status for a user"""

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = get_object_or_404(get_user_model(), id=user_id)

        # Don't allow removing superuser status from self
        if user == request.user:
            messages.error(self.request, "You cannot change your own superuser status.")
            return redirect("workouts:manage_users")

        user.is_superuser = not user.is_superuser
        user.is_staff = user.is_superuser  # Staff status follows superuser status
        user.save()

        status = "granted" if user.is_superuser else "removed"
        messages.success(self.request, f"Superuser status {status} for {user.email}")

        return redirect("workouts:manage_users")
