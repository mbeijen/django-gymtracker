from django.urls import path
from . import views

app_name = "workouts"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path(
        "workout/new/", views.CreateWorkoutSessionView.as_view(), name="create_workout"
    ),
    path(
        "workout/<int:pk>/",
        views.WorkoutSessionDetailView.as_view(),
        name="workout_detail",
    ),
    path(
        "workout/<int:pk>/add-exercise/",
        views.AddExerciseToWorkoutView.as_view(),
        name="add_exercise",
    ),
    path(
        "workout/<int:workout_pk>/exercise/<int:pk>/edit/",
        views.EditExerciseRecordView.as_view(),
        name="edit_exercise",
    ),
    path(
        "workout/<int:workout_pk>/exercise/<int:pk>/delete/",
        views.DeleteExerciseRecordView.as_view(),
        name="delete_exercise",
    ),
    path(
        "workout/<int:pk>/complete/",
        views.CompleteWorkoutView.as_view(),
        name="complete_workout",
    ),
    path("exercises/", views.ExerciseListView.as_view(), name="exercise_list"),
    path("exercises/add/", views.AddExerciseView.as_view(), name="add_exercise_type"),
    path("history/", views.WorkoutHistoryView.as_view(), name="workout_history"),
    path("profile/", views.UserProfileView.as_view(), name="user_profile"),
    # Admin-only user management
    path("manage-users/", views.ManageUsersView.as_view(), name="manage_users"),
    path("invite-user/", views.InviteUserView.as_view(), name="invite_user"),
    path(
        "resend-invite/<int:user_id>/",
        views.ResendInviteView.as_view(),
        name="resend_invite",
    ),
    path(
        "toggle-superuser/<int:user_id>/",
        views.ToggleSuperuserView.as_view(),
        name="toggle_superuser",
    ),
]
