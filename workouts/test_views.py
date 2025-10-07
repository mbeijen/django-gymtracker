from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.formats import date_format
from datetime import date, time
from decimal import Decimal

from .models import Exercise, WorkoutSession, ExerciseRecord
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
