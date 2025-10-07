from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.formats import date_format
from datetime import date, time, timedelta
from decimal import Decimal

from .models import Exercise, WorkoutSession, ExerciseRecord, UserProfile
from .views import AddExerciseToWorkoutView

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.exercise = Exercise.objects.create(name="Bench Press")
        self.workout = WorkoutSession.objects.create(user=self.user, date=date.today())

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("workouts:dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("workouts:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back")

    def test_create_workout_requires_login(self):
        response = self.client.get(reverse("workouts:create_workout"))
        self.assertEqual(response.status_code, 302)

    def test_create_workout_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("workouts:create_workout"))
        self.assertEqual(response.status_code, 200)

    def test_create_workout_post(self):
        self.client.login(email="test@example.com", password="testpass123")
        form_data = {"date": date.today(), "notes": "Test workout"}
        response = self.client.post(reverse("workouts:create_workout"), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            WorkoutSession.objects.filter(user=self.user, notes="Test workout").exists()
        )

    def test_workout_detail_requires_login(self):
        response = self.client.get(
            reverse("workouts:workout_detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_workout_detail_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:workout_detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)
        # Check for formatted date - workout was created with date.today()
        expected_date = date_format(self.workout.date, "DATE_FORMAT")
        self.assertContains(response, expected_date)

    def test_add_exercise_requires_login(self):
        response = self.client.get(
            reverse("workouts:add_exercise", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_exercise_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:add_exercise", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_add_exercise_post(self):
        self.client.login(email="test@example.com", password="testpass123")
        form_data = {
            "exercise": self.exercise.id,
            "weight_kg": 80.0,
            "reps": 10,
            "sets": 3,
            "difficulty_rating": 7,
            "notes": "Felt good",
        }
        response = self.client.post(
            reverse("workouts:add_exercise", kwargs={"pk": self.workout.pk}), form_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(
            ExerciseRecord.objects.filter(
                workout_session=self.workout, exercise=self.exercise
            ).exists()
        )

    def test_exercise_list_requires_login(self):
        response = self.client.get(reverse("workouts:exercise_list"))
        self.assertEqual(response.status_code, 302)

    def test_exercise_list_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("workouts:exercise_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bench Press")

    def test_workout_history_requires_login(self):
        response = self.client.get(reverse("workouts:workout_history"))
        self.assertEqual(response.status_code, 302)

    def test_workout_history_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("workouts:workout_history"))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_requires_login(self):
        response = self.client.get(reverse("workouts:user_profile"))
        self.assertEqual(response.status_code, 302)

    def test_user_profile_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("workouts:user_profile"))
        self.assertEqual(response.status_code, 200)

    def test_complete_workout_requires_login(self):
        response = self.client.get(
            reverse("workouts:complete_workout", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_complete_workout_authenticated(self):
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:complete_workout", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_complete_workout_post(self):
        self.client.login(email="test@example.com", password="testpass123")
        form_data = {
            "end_time": "14:30",
            "notes": "Great workout!",
            "is_completed": True,
        }
        response = self.client.post(
            reverse("workouts:complete_workout", kwargs={"pk": self.workout.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.workout.refresh_from_db()
        self.assertTrue(self.workout.is_completed)


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.exercise = Exercise.objects.create(name="Bench Press")

    def test_full_workout_flow(self):
        """Test the complete workflow: create workout -> add exercise -> complete workout"""
        self.client.login(email="test@example.com", password="testpass123")

        # 1. Create workout
        form_data = {"date": date.today(), "notes": "Test workout"}
        response = self.client.post(reverse("workouts:create_workout"), form_data)
        self.assertEqual(response.status_code, 302)

        workout = WorkoutSession.objects.get(user=self.user, date=date.today())

        # 2. Add exercise
        form_data = {
            "exercise": self.exercise.id,
            "weight_kg": 80.0,
            "reps": 10,
            "sets": 3,
            "difficulty_rating": 7,
            "notes": "Felt good",
        }
        response = self.client.post(
            reverse("workouts:add_exercise", kwargs={"pk": workout.pk}), form_data
        )
        self.assertEqual(response.status_code, 302)

        # 3. Complete workout
        form_data = {
            "end_time": "14:30",
            "notes": "Great workout!",
            "is_completed": True,
        }
        response = self.client.post(
            reverse("workouts:complete_workout", kwargs={"pk": workout.pk}), form_data
        )
        self.assertEqual(response.status_code, 302)

        # Verify everything was created correctly
        workout.refresh_from_db()
        self.assertTrue(workout.is_completed)
        self.assertEqual(workout.end_time, time(14, 30))

        exercise_record = ExerciseRecord.objects.get(workout_session=workout)
        self.assertEqual(exercise_record.exercise, self.exercise)
        self.assertEqual(exercise_record.weight_kg, Decimal("80.0"))
        self.assertEqual(exercise_record.reps, 10)
        self.assertEqual(exercise_record.sets, 3)
        self.assertEqual(exercise_record.difficulty_rating, 7)


class AddExerciseToWorkoutViewTests(TestCase):
    """Test the AddExerciseToWorkoutView, especially the _get_recommended_weight method"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.exercise = Exercise.objects.create(name="Bench Press")
        self.workout = WorkoutSession.objects.create(user=self.user, date=date.today())
        self.view = AddExerciseToWorkoutView()
        self.view.request = type("MockRequest", (), {"user": self.user})()

    def test_get_recommended_weight_no_previous_record(self):
        """Test recommendation when there's no previous record"""
        result = self.view._get_recommended_weight(None)
        self.assertEqual(result, 0)

    def test_get_recommended_weight_easy_difficulty(self):
        """Test recommendation for easy difficulty (1-5) - should increase weight"""
        last_record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=3,  # Easy
        )
        result = self.view._get_recommended_weight(last_record)
        self.assertEqual(result, Decimal("82.5"))  # 80 + 2.5

    def test_get_recommended_weight_moderate_difficulty(self):
        """Test recommendation for moderate difficulty (6-7) - should keep same weight"""
        last_record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=6,  # Moderate
        )
        result = self.view._get_recommended_weight(last_record)
        self.assertEqual(result, Decimal("80.0"))  # Same weight

    def test_get_recommended_weight_hard_difficulty(self):
        """Test recommendation for hard difficulty (8-10) - should decrease weight"""
        last_record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=9,  # Very hard
        )
        result = self.view._get_recommended_weight(last_record)
        self.assertEqual(result, Decimal("77.5"))  # 80 - 2.5

    def test_get_recommended_weight_hard_difficulty_minimum_zero(self):
        """Test that weight doesn't go below 0 for hard difficulty"""
        last_record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("1.0"),
            reps=10,
            sets=3,
            difficulty_rating=10,  # Maximum difficulty
        )
        result = self.view._get_recommended_weight(last_record)
        self.assertEqual(result, Decimal("0.0"))  # max(0, 1.0 - 2.5) = 0

    def test_get_recommended_weight_with_none_weight(self):
        """Test recommendation when weight_kg is None (edge case)"""
        # Create a record with None weight (this shouldn't happen in normal operation)
        last_record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=5,
        )
        # Manually set weight to None to simulate the edge case
        last_record.weight_kg = None
        result = self.view._get_recommended_weight(last_record)
        self.assertEqual(result, 0)  # Should return 0 for None weight

    def test_add_exercise_view_with_recommendations(self):
        """Test that the add exercise view works with exercise recommendations"""
        # Create a previous record to generate recommendations
        ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=5,
        )

        # Test that the view loads without errors
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:add_exercise", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Check that exercise recommendations are in context
        self.assertIn("exercise_recommendations", response.context)
        recommendations = response.context["exercise_recommendations"]
        self.assertIn(self.exercise.id, recommendations)

        # Check the recommendation values
        recommendation = recommendations[self.exercise.id]
        self.assertEqual(recommendation["last_weight"], Decimal("80.0"))
        self.assertEqual(recommendation["last_difficulty"], 5)
        self.assertEqual(recommendation["recommended_weight"], Decimal("82.5"))


class WorkoutDetailViewTests(TestCase):
    """Test the WorkoutDetailView with smart exercise list functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.workout = WorkoutSession.objects.create(user=self.user, date=date.today())
        self.exercise1 = Exercise.objects.create(
            name="Bench Press", muscle_groups="Chest, Triceps"
        )
        self.exercise2 = Exercise.objects.create(name="Squat", muscle_groups="Legs")
        self.exercise3 = Exercise.objects.create(
            name="Deadlift", muscle_groups="Back, Legs"
        )

        # Create some historical records
        old_workout = WorkoutSession.objects.create(
            user=self.user, date=date.today() - timedelta(days=30)
        )
        ExerciseRecord.objects.create(
            workout_session=old_workout,
            exercise=self.exercise1,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=5,
        )

        recent_workout = WorkoutSession.objects.create(
            user=self.user, date=date.today() - timedelta(days=1)
        )
        ExerciseRecord.objects.create(
            workout_session=recent_workout,
            exercise=self.exercise2,
            weight_kg=Decimal("100.0"),
            reps=8,
            sets=3,
            difficulty_rating=7,
        )

    def test_workout_detail_shows_available_exercises(self):
        """Test that workout detail shows available exercises sorted by recency"""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:workout_detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("available_exercises", response.context)

        available_exercises = response.context["available_exercises"]
        # Should have all 3 exercises since none are done in current workout
        self.assertEqual(len(available_exercises), 3)

        # Should be sorted by last_used (most recent first)
        # exercise2 was done 1 day ago, exercise1 was done 30 days ago, exercise3 never
        self.assertEqual(available_exercises[0], self.exercise2)  # Most recent
        self.assertEqual(available_exercises[1], self.exercise1)  # Older
        self.assertEqual(available_exercises[2], self.exercise3)  # Never done

    def test_workout_detail_excludes_done_exercises(self):
        """Test that exercises already done in current workout are excluded"""
        # Add an exercise to the current workout
        ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise1,
            weight_kg=Decimal("85.0"),
            reps=10,
            sets=3,
            difficulty_rating=6,
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:workout_detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)

        available_exercises = response.context["available_exercises"]
        # Should only have 2 exercises (exercise1 is excluded)
        self.assertEqual(len(available_exercises), 2)
        self.assertNotIn(self.exercise1, available_exercises)
        self.assertIn(self.exercise2, available_exercises)
        self.assertIn(self.exercise3, available_exercises)

    def test_add_exercise_with_preselected_exercise(self):
        """Test that add exercise view pre-selects exercise from URL parameter"""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(
            reverse("workouts:add_exercise", kwargs={"pk": self.workout.pk})
            + f"?exercise={self.exercise1.id}"
        )
        self.assertEqual(response.status_code, 200)

        # Check that the form has the exercise pre-selected
        form = response.context["form"]
        self.assertEqual(form.initial.get("exercise"), self.exercise1)


class UserManagementTests(TestCase):
    """Test user management functionality for superusers"""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass123"
        )
        self.regular_user = User.objects.create_user(
            email="user@example.com", username="user", password="userpass123"
        )
        # Create profiles
        UserProfile.objects.create(user=self.superuser)
        UserProfile.objects.create(user=self.regular_user)

    def test_manage_users_requires_superuser(self):
        """Test that manage users page requires superuser status"""
        # Regular user should be redirected
        self.client.login(email="user@example.com", password="userpass123")
        response = self.client.get(reverse("workouts:manage_users"))
        self.assertEqual(response.status_code, 403)

    def test_manage_users_allows_superuser(self):
        """Test that superuser can access manage users page"""
        self.client.login(email="admin@example.com", password="adminpass123")
        response = self.client.get(reverse("workouts:manage_users"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.context)

    def test_invite_user_creates_inactive_user(self):
        """Test that inviting a user creates an inactive user account"""
        self.client.login(email="admin@example.com", password="adminpass123")
        response = self.client.post(
            reverse("workouts:invite_user"), {"email": "newuser@example.com"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check that user was created
        new_user = User.objects.get(email="newuser@example.com")
        self.assertFalse(new_user.is_active)
        self.assertEqual(new_user.username, "newuser@example.com")

        # Check that profile was created
        self.assertTrue(hasattr(new_user, "profile"))

    def test_toggle_superuser_status(self):
        """Test toggling superuser status"""
        self.client.login(email="admin@example.com", password="adminpass123")

        # Make regular user a superuser
        response = self.client.post(
            reverse(
                "workouts:toggle_superuser", kwargs={"user_id": self.regular_user.id}
            )
        )
        self.assertEqual(response.status_code, 302)

        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_superuser)
        self.assertTrue(self.regular_user.is_staff)

    def test_cannot_toggle_own_superuser_status(self):
        """Test that users cannot change their own superuser status"""
        self.client.login(email="admin@example.com", password="adminpass123")

        response = self.client.post(
            reverse("workouts:toggle_superuser", kwargs={"user_id": self.superuser.id})
        )
        self.assertEqual(response.status_code, 302)

        # Should still be superuser
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_superuser)
