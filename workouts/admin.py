from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Exercise, WorkoutSession, ExerciseRecord, UserProfile


class ExerciseRecordInline(admin.TabularInline):
    model = ExerciseRecord
    extra = 0
    fields = ["exercise", "weight_kg", "reps", "sets", "difficulty_rating", "notes"]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "muscle_groups", "created_at"]
    list_filter = ["muscle_groups", "created_at"]
    search_fields = ["name", "description", "muscle_groups"]
    ordering = ["name"]


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "date",
        "start_time",
        "end_time",
        "is_completed",
        "exercise_count",
    ]
    list_filter = ["date", "is_completed", "user"]
    search_fields = ["user__username", "user__email", "notes"]
    date_hierarchy = "date"
    inlines = [ExerciseRecordInline]

    def exercise_count(self, obj):
        return obj.exercise_records.count()

    exercise_count.short_description = "Exercises"


@admin.register(ExerciseRecord)
class ExerciseRecordAdmin(admin.ModelAdmin):
    list_display = [
        "exercise",
        "workout_session",
        "weight_kg",
        "reps",
        "sets",
        "difficulty_rating",
        "total_volume",
    ]
    list_filter = ["exercise", "difficulty_rating", "workout_session__date"]
    search_fields = ["exercise__name", "workout_session__user__username", "notes"]
    date_hierarchy = "workout_session__date"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
