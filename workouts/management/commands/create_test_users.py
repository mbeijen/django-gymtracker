from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workouts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for development"

    def handle(self, *args, **options):
        # Create Alice
        alice, created = User.objects.get_or_create(
            email="alice@example.com",
            defaults={
                "username": "alice",
                "first_name": "Alice",
                "last_name": "Smith",
                "is_active": True,
            },
        )
        if created:
            alice.set_password("some_pass")
            alice.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {alice.email}"))
        else:
            self.stdout.write(self.style.WARNING(f"User already exists: {alice.email}"))

        # Create Bob
        bob, created = User.objects.get_or_create(
            email="bob@example.com",
            defaults={
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Johnson",
                "is_active": True,
            },
        )
        if created:
            bob.set_password("some_pass")
            bob.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {bob.email}"))
        else:
            self.stdout.write(self.style.WARNING(f"User already exists: {bob.email}"))

        # Create profiles for both users
        alice_profile, created = UserProfile.objects.get_or_create(
            user=alice,
            defaults={
                "preferred_units": "kg",
                "default_workout_partner": bob,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created profile for: {alice.email}"))

        bob_profile, created = UserProfile.objects.get_or_create(
            user=bob,
            defaults={
                "preferred_units": "kg",
                "default_workout_partner": alice,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created profile for: {bob.email}"))

        self.stdout.write(
            self.style.SUCCESS(
                "\nTest users created successfully!\n"
                "Alice: alice@example.com / some_pass\n"
                "Bob: bob@example.com / some_pass"
            )
        )
