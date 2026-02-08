# accounts/tests/test_account_access.py
from django.test import TestCase
from django.urls import reverse

from .utils import create_user, verify_email, login_via_allauth


class AccountAccessTests(TestCase):
    def test_account_page_requires_login(self):
        resp = self.client.get(reverse("accounts:account"))
        self.assertEqual(resp.status_code, 302)

    def test_account_page_loads_for_logged_in_user(self):
        user = create_user(email="u@example.com", password="Passw0rd!123")
        verify_email(user)

        login_via_allauth(self.client, "u@example.com", "Passw0rd!123")

        resp = self.client.get(reverse("accounts:account"))
        self.assertEqual(resp.status_code, 200)

    def test_edit_account_requires_login(self):
        resp = self.client.get(reverse("accounts:edit_account"))
        self.assertEqual(resp.status_code, 302)

    def test_change_password_requires_login(self):
        resp = self.client.get(reverse("accounts:change_password"))
        self.assertEqual(resp.status_code, 302)
