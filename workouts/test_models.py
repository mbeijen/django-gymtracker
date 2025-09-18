from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from decimal import Decimal

from .models import Exercise, WorkoutSession, ExerciseRecord, UserProfile

User = get_user_model()


class ExerciseModelTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            description="Chest exercise",
            muscle_groups="Chest, Triceps, Shoulders",
        )

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.name, "Bench Press")
        self.assertEqual(self.exercise.description, "Chest exercise")
        self.assertEqual(self.exercise.muscle_groups, "Chest, Triceps, Shoulders")
        self.assertTrue(self.exercise.created_at)

    def test_exercise_str(self):
        self.assertEqual(str(self.exercise), "Bench Press")

    def test_exercise_ordering(self):
        Exercise.objects.create(name="Squat")
        exercises = list(Exercise.objects.all())
        self.assertEqual(exercises[0].name, "Bench Press")
        self.assertEqual(exercises[1].name, "Squat")


class WorkoutSessionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.workout = WorkoutSession.objects.create(
            user=self.user, date=date.today(), notes="Test workout"
        )

    def test_workout_creation(self):
        self.assertEqual(self.workout.user, self.user)
        self.assertEqual(self.workout.date, date.today())
        self.assertEqual(self.workout.notes, "Test workout")
        self.assertFalse(self.workout.is_completed)
        self.assertTrue(self.workout.start_time)

    def test_workout_str(self):
        expected = f"{self.user.username} - {date.today()} ({self.workout.start_time})"
        self.assertEqual(str(self.workout), expected)

    def test_workout_duration(self):
        # Test without end_time
        self.assertIsNone(self.workout.duration)

        # Test with end_time
        self.workout.end_time = time(14, 30)  # 2:30 PM
        self.workout.start_time = time(13, 0)  # 1:00 PM
        duration = self.workout.duration
        self.assertEqual(duration.total_seconds(), 5400)  # 1.5 hours

    def test_workout_ordering(self):
        workout2 = WorkoutSession.objects.create(
            user=self.user, date=date.today() - timedelta(days=1)
        )
        workouts = list(WorkoutSession.objects.filter(user=self.user))
        self.assertEqual(workouts[0], self.workout)  # More recent first
        self.assertEqual(workouts[1], workout2)


class ExerciseRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.exercise = Exercise.objects.create(name="Bench Press")
        self.workout = WorkoutSession.objects.create(user=self.user, date=date.today())
        self.record = ExerciseRecord.objects.create(
            workout_session=self.workout,
            exercise=self.exercise,
            weight_kg=Decimal("80.0"),
            reps=10,
            sets=3,
            difficulty_rating=7,
            notes="Felt good",
        )

    def test_exercise_record_creation(self):
        self.assertEqual(self.record.workout_session, self.workout)
        self.assertEqual(self.record.exercise, self.exercise)
        self.assertEqual(self.record.weight_kg, Decimal("80.0"))
        self.assertEqual(self.record.reps, 10)
        self.assertEqual(self.record.sets, 3)
        self.assertEqual(self.record.difficulty_rating, 7)
        self.assertEqual(self.record.notes, "Felt good")

    def test_exercise_record_str(self):
        expected = "Bench Press - 80.0kg x 10 (3 sets)"
        self.assertEqual(str(self.record), expected)

    def test_total_volume_calculation(self):
        expected_volume = 80.0 * 10 * 3  # 2400
        self.assertEqual(self.record.total_volume, expected_volume)

    def test_difficulty_choices(self):
        self.assertIn((1, "Very Easy"), ExerciseRecord.DIFFICULTY_CHOICES)
        self.assertIn((10, "Failure"), ExerciseRecord.DIFFICULTY_CHOICES)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user, preferred_units="kg")

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.preferred_units, "kg")
        self.assertTrue(self.profile.created_at)
        self.assertTrue(self.profile.updated_at)

    def test_profile_str(self):
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.profile), expected)
