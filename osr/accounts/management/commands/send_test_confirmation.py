from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.conf import settings
from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = "Send a test email confirmation to a user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help="Optional email address. If omitted, uses TEST_CONFIRMATION_EMAIL from settings.",
        )

    def handle(self, *args, **options):
        email = options.get("email") or getattr(settings, "TEST_CONFIRMATION_EMAIL", None)

        if not email:
            self.stdout.write(self.style.ERROR(
                "No email provided and TEST_CONFIRMATION_EMAIL not set in settings."
            ))
            return

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with email '{email}' not found."))
            return

        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={
                "verified": False,
                "primary": True,
            },
        )

        request = RequestFactory().get("/", HTTP_HOST="localhost")

        email_address.send_confirmation(request)

        self.stdout.write(self.style.SUCCESS(f"Confirmation email sent to {email}."))
