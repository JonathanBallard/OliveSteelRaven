# accounts/tests/test_change_password.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .utils import create_user, set_email_verified, login_via_allauth

User = get_user_model()

class ChangePasswordTests(TestCase):
    def test_change_password_flow(self):
        user = create_user(email="cp@example.com", password="OldPassw0rd!123")
        set_email_verified(user)

        login_via_allauth(self.client, "cp@example.com", "OldPassw0rd!123")
        self.assertIn("_auth_user_id", self.client.session)

        # Try Django PasswordChangeForm field names first, then allauth names
        payloads = [
            {
                "old_password": "OldPassw0rd!123",
                "new_password1": "NewPassw0rd!123",
                "new_password2": "NewPassw0rd!123",
            },
            {
                "oldpassword": "OldPassw0rd!123",
                "password1": "NewPassw0rd!123",
                "password2": "NewPassw0rd!123",
            },
        ]

        changed = False
        last_resp = None

        for data in payloads:
            last_resp = self.client.post(
                reverse("account_change_password"),
                data=data,
                follow=True,
            )
            user.refresh_from_db()
            if user.check_password("NewPassw0rd!123"):
                changed = True
                break

        if not changed:
            # Surface helpful form errors if available
            if last_resp is not None and getattr(last_resp, "context", None):
                form = last_resp.context.get("form") or last_resp.context.get("password_change_form")
                if form is not None:
                    raise AssertionError(f"Password did not change. Form errors: {form.errors.as_json()}")
            raise AssertionError("Password did not change. Field names likely mismatch your change_password view.")

        # Logout and verify old password fails, new works
        self.client.logout()
        self.assertNotIn("_auth_user_id", self.client.session)

        login_via_allauth(self.client, "cp@example.com", "OldPassw0rd!123")
        self.assertNotIn("_auth_user_id", self.client.session)

        login_via_allauth(self.client, "cp@example.com", "NewPassw0rd!123")
        self.assertIn("_auth_user_id", self.client.session)
