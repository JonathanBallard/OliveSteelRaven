# accounts/tests/test_edit_details.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .utils import create_user, verify_email, login_via_allauth

User = get_user_model()


class EditDetailsTests(TestCase):
    def test_edit_details_page_loads(self):
        user = create_user(email="edit@example.com", password="Passw0rd!123")
        verify_email(user)
        login_via_allauth(self.client, "edit@example.com", "Passw0rd!123")

        resp = self.client.get(reverse("accounts:edit_account"))
        self.assertEqual(resp.status_code, 200)

    def test_edit_details_post_does_not_change_email_by_default(self):
        """
        Email changes should go through allauth's change-email flow,
        not the 'edit details' form.
        """
        user = create_user(email="edit2@example.com", password="Passw0rd!123")
        verify_email(user)
        login_via_allauth(self.client, "edit2@example.com", "Passw0rd!123")

        resp = self.client.post(
            reverse("accounts:edit_account"),
            data={
                # include any fields your form expects here.
                # We intentionally try to change email and ensure it doesn't.
                "email": "hacker@example.com",
            },
            follow=True,
        )

        user.refresh_from_db()
        self.assertEqual(user.email, "edit2@example.com")
