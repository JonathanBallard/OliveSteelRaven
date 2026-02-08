# accounts/tests/test_allauth_login.py
from django.test import TestCase
from django.urls import reverse

from .utils import create_user, verify_email


class AllauthLoginFlowTests(TestCase):
    def test_login_page_loads(self):
        resp = self.client.get(reverse("account_login"))
        self.assertEqual(resp.status_code, 200)

    def test_login_blocked_when_email_not_verified(self):
        user = create_user(email="unverified@example.com", password="Passw0rd!123")
        # Do NOT verify email

        resp = self.client.post(
            reverse("account_login"),
            data={"login": "unverified@example.com", "password": "Passw0rd!123"},
            follow=True,
        )

        # Not authenticated
        self.assertNotIn("_auth_user_id", self.client.session)
        # Allauth typically re-renders login page with form errors
        self.assertEqual(resp.status_code, 200)

    def test_login_succeeds_when_email_verified(self):
        user = create_user(email="verified@example.com", password="Passw0rd!123")
        verify_email(user)

        resp = self.client.post(
            reverse("account_login"),
            data={"login": "verified@example.com", "password": "Passw0rd!123"},
            follow=True,
        )

        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(resp.status_code, 200)
