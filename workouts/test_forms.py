from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from .models import Exercise, UserProfile
from .forms import (
    WorkoutSessionForm,
    ExerciseRecordForm,
    ExerciseForm,
    UserProfileForm,
    CustomLoginForm,
    CustomSignupForm,
)

User = get_user_model()


class WorkoutSessionFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"date": date.today(), "notes": "Test workout"}
        form = WorkoutSessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"date": "invalid-date", "notes": "Test workout"}
        form = WorkoutSessionForm(data=form_data)
        self.assertFalse(form.is_valid())


class ExerciseRecordFormTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name="Bench Press")

    def test_valid_form(self):
        form_data = {
            "exercise": self.exercise.id,
            "weight_kg": 80.0,
            "reps": 10,
            "sets": 3,
            "difficulty_rating": 7,
            "notes": "Felt good",
        }
        form = ExerciseRecordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_required_fields(self):
        form_data = {
            "exercise": self.exercise.id,
            "weight_kg": 80.0,
            # Missing reps, sets, difficulty_rating
        }
        form = ExerciseRecordForm(data=form_data)
        self.assertFalse(form.is_valid())


class ExerciseFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            "name": "Squat",
            "description": "Leg exercise",
            "muscle_groups": "Quadriceps, Glutes",
        }
        form = ExerciseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_name(self):
        form_data = {
            "description": "Leg exercise",
            "muscle_groups": "Quadriceps, Glutes",
        }
        form = ExerciseForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.partner = User.objects.create_user(
            email="partner@example.com", username="partner", password="testpass123"
        )

    def test_valid_form(self):
        profile = UserProfile.objects.create(user=self.user)
        form_data = {
            "preferred_units": "kg",
            "default_workout_partner": self.partner.id,
        }
        form = UserProfileForm(data=form_data, instance=profile)
        self.assertTrue(form.is_valid())

    def test_form_excludes_current_user_from_partners(self):
        profile = UserProfile.objects.create(user=self.user)
        form = UserProfileForm(instance=profile)
        self.assertNotIn(self.user, form.fields["default_workout_partner"].queryset)


class CustomLoginFormTest(TestCase):
    def test_remember_field_removed(self):
        """Test that the remember field is removed from the login form"""
        form = CustomLoginForm()
        self.assertNotIn("remember", form.fields)

    def test_bootstrap_classes_applied(self):
        """Test that Bootstrap classes are applied to form fields"""
        form = CustomLoginForm()
        self.assertIn(
            "form-control", form.fields["login"].widget.attrs.get("class", "")
        )
        self.assertIn(
            "form-control", form.fields["password"].widget.attrs.get("class", "")
        )

    def test_placeholders_set(self):
        """Test that placeholders are set for form fields"""
        form = CustomLoginForm()
        self.assertEqual(
            "Enter your email", form.fields["login"].widget.attrs.get("placeholder")
        )
        self.assertEqual(
            "Enter your password",
            form.fields["password"].widget.attrs.get("placeholder"),
        )


class CustomSignupFormTest(TestCase):
    def test_bootstrap_classes_applied(self):
        """Test that Bootstrap classes are applied to signup form fields"""
        form = CustomSignupForm()
        self.assertIn(
            "form-control", form.fields["email"].widget.attrs.get("class", "")
        )
        self.assertIn(
            "form-control", form.fields["password1"].widget.attrs.get("class", "")
        )
        self.assertIn(
            "form-control", form.fields["password2"].widget.attrs.get("class", "")
        )

    def test_placeholders_set(self):
        """Test that placeholders are set for signup form fields"""
        form = CustomSignupForm()
        self.assertEqual(
            "Enter your email", form.fields["email"].widget.attrs.get("placeholder")
        )
        self.assertEqual(
            "Create a password",
            form.fields["password1"].widget.attrs.get("placeholder"),
        )
        self.assertEqual(
            "Confirm your password",
            form.fields["password2"].widget.attrs.get("placeholder"),
        )
