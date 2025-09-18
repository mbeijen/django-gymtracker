from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import LoginForm, SignupForm
from .models import Exercise, WorkoutSession, ExerciseRecord, UserProfile


class WorkoutSessionForm(forms.ModelForm):
    """Form for creating a new workout session"""

    class Meta:
        model = WorkoutSession
        fields = ["date", "notes"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "value": forms.DateInput().value_from_datadict({}, {}, "date")
                    or "",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes about your workout...",
                }
            ),
        }
        labels = {"date": "Workout Date", "notes": "Notes"}


class ExerciseRecordForm(forms.ModelForm):
    """Form for adding/editing exercise records"""

    class Meta:
        model = ExerciseRecord
        fields = ["exercise", "weight_kg", "reps", "sets", "difficulty_rating", "notes"]
        widgets = {
            "exercise": forms.Select(
                attrs={
                    "class": "form-control",
                    "hx-get": "/workouts/get-exercise-recommendation/",
                    "hx-target": "#weight-recommendation",
                    "hx-trigger": "change",
                }
            ),
            "weight_kg": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.5",
                    "min": "0",
                    "placeholder": "Weight in kg",
                }
            ),
            "reps": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Number of repetitions",
                }
            ),
            "sets": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "value": "1"}
            ),
            "difficulty_rating": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Optional notes about this exercise...",
                }
            ),
        }
        labels = {
            "exercise": "Exercise",
            "weight_kg": "Weight (kg)",
            "reps": "Repetitions",
            "sets": "Sets",
            "difficulty_rating": "Difficulty (1-10)",
            "notes": "Notes",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for difficulty rating
        self.fields[
            "difficulty_rating"
        ].help_text = "1 = Very Easy, 5 = Moderate, 10 = Maximum Effort/Failure"


class ExerciseForm(forms.ModelForm):
    """Form for adding new exercise types"""

    class Meta:
        model = Exercise
        fields = ["name", "description", "muscle_groups"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Bench Press, Squat, Deadlift",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional description of the exercise...",
                }
            ),
            "muscle_groups": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Chest, Triceps, Shoulders",
                }
            ),
        }
        labels = {
            "name": "Exercise Name",
            "description": "Description",
            "muscle_groups": "Muscle Groups",
        }


class UserProfileForm(forms.ModelForm):
    """Form for user profile settings"""

    class Meta:
        model = UserProfile
        fields = ["preferred_units", "default_workout_partner"]
        widgets = {
            "preferred_units": forms.Select(attrs={"class": "form-control"}),
            "default_workout_partner": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "preferred_units": "Preferred Units",
            "default_workout_partner": "Default Workout Partner",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show other users as potential workout partners
        self.fields["default_workout_partner"].queryset = User.objects.exclude(
            id=self.instance.user.id if self.instance and self.instance.user else 0
        )
        self.fields["default_workout_partner"].empty_label = "No default partner"


class QuickAddExerciseForm(forms.Form):
    """Quick form for adding exercises during workout"""

    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "hx-get": "/workouts/get-exercise-recommendation/",
                "hx-target": "#weight-recommendation",
                "hx-trigger": "change",
            }
        ),
    )
    weight_kg = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.5",
                "min": "0",
                "placeholder": "Weight in kg",
            }
        ),
    )
    reps = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "placeholder": "Reps"}
        ),
    )
    sets = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )
    difficulty_rating = forms.ChoiceField(
        choices=ExerciseRecord.DIFFICULTY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class CustomLoginForm(LoginForm):
    """Custom login form with Bootstrap styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap classes to form fields
        self.fields["login"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your email"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"}
        )
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs.update({"class": "form-check-input"})


class CustomSignupForm(SignupForm):
    """Custom signup form with Bootstrap styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap classes to form fields
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your email"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Create a password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm your password"}
        )
