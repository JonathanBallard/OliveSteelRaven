import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

from dotenv import load_dotenv

# Run with:  python manage.py seed_admin

class Command(BaseCommand):
    help = "Create or update the admin user (id=1) using an env var for the password."

    def handle(self, *args, **options):
        # Load .env already called in settings, but just in case
        load_dotenv()

        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            raise CommandError(
                "ADMIN_PASSWORD not found.\n"
                "Add it to your .env file:\n\n"
                "  ADMIN_PASSWORD=StrongPassword123!"
            )

        User = get_user_model()

        email = os.getenv("ADMIN_LOGIN")
        
        if not email:
            email = "admin@recipebook.com"

        # Get or create user with explicit ID = 1
        user, created = User.objects.get_or_create(
            id=1,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        # Ensure fields are correct even if user already existed
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        # Properly hash password
        user.set_password(password)

        user.save()
        
        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"verified": True, "primary": True},
        )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} admin user: id={user.id}, email={user.email}"
            )
        )
