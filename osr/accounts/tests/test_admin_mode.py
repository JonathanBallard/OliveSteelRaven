from django.test import TestCase
from django.urls import reverse
from .utils import create_user, set_email_verified, login_via_allauth

class AdminModeTests(TestCase):
    def test_toggle_admin_mode_works_for_superuser(self):
        user = create_user(email="admin@example.com", password="Passw0rd!123", is_superuser=True)
        set_email_verified(user)
        login_via_allauth(self.client, "admin@example.com", "Passw0rd!123")
        self.assertIn("_auth_user_id", self.client.session)

        # Use GET or POST depending on your view. Try GET first.
        self.client.get(reverse("accounts:toggle_admin_mode"))

        # Reload session state
        self.assertTrue(self.client.session.get("admin_mode", False))

    def test_toggle_admin_mode_works_for_staff(self):
        user = create_user(email="staff@example.com", password="Passw0rd!123", is_superuser=False, is_staff=True)
        set_email_verified(user)
        login_via_allauth(self.client, "staff@example.com", "Passw0rd!123")
        self.assertIn("_auth_user_id", self.client.session)

        # Use GET or POST depending on your view. Try GET first.
        self.client.get(reverse("accounts:toggle_admin_mode"))

        # Reload session state
        self.assertTrue(self.client.session.get("admin_mode", False))

    def test_non_staff_non_superuser_cannot_toggle_admin_mode(self):
        user = create_user(email="normie@example.com", password="Passw0rd!123")
        set_email_verified(user)
        login_via_allauth(self.client, "normie@example.com", "Passw0rd!123")

        # Attempt toggle
        resp = self.client.get(reverse("accounts:toggle_admin_mode"))

        # Should redirect to account page
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("accounts:account"))

        # Should NOT set admin_mode
        self.assertFalse(self.client.session.get("admin_mode", False))
