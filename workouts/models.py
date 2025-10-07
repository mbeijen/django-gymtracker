from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Exercise(models.Model):
    """Represents a type of exercise (e.g., 'Leg Press', 'Bench Press')"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    muscle_groups = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkoutSession(models.Model):
    """Represents a single workout session on a specific day"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="workout_sessions"
    )
    date = models.DateField()
    start_time = models.TimeField(auto_now_add=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        unique_together = ["user", "date", "start_time"]

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.start_time})"

    @property
    def duration(self):
        """Calculate workout duration if end_time is set"""
        if self.end_time:
            from datetime import datetime

            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = datetime.combine(self.date, self.end_time)
            return end_datetime - start_datetime
        return None


class ExerciseRecord(models.Model):
    """Represents a single exercise performed during a workout session"""

    DIFFICULTY_CHOICES = [
        (1, "Very Easy"),
        (2, "Easy"),
        (3, "Somewhat Easy"),
        (4, "Moderate"),
        (5, "Somewhat Hard"),
        (6, "Hard"),
        (7, "Very Hard"),
        (8, "Extremely Hard"),
        (9, "Maximum Effort"),
        (10, "Failure"),
    ]

    workout_session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="exercise_records"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )
    reps = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sets = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    difficulty_rating = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate how difficult this exercise felt (1=Very Easy, 10=Failure)",
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.exercise.name} - {self.weight_kg}kg x {self.reps} ({self.sets} sets)"

    @property
    def total_volume(self):
        """Calculate total volume (weight × reps × sets)"""
        return float(self.weight_kg) * self.reps * self.sets


class UserProfile(models.Model):
    """Extended user profile for gym tracker specific settings"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Your display name (leave blank to use email)",
    )
    preferred_units = models.CharField(
        max_length=10, choices=[("kg", "Kilograms"), ("lbs", "Pounds")], default="kg"
    )
    default_workout_partner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_profiles",
        help_text="Default workout partner for shared sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def display_name(self):
        """Get the user's display name, falling back to email if no name is set"""
        return self.name.strip() if self.name and self.name.strip() else self.user.email
