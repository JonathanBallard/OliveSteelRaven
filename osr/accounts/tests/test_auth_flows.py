from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .utils import create_user, verify_email, login_via_allauth


User = get_user_model()


class AuthFlowTests(TestCase):
    def setUp(self) -> None:
        # Create a user who CAN log in (verified email)
        self.user = create_user(
            username="Tester",
            email="tester@testing.com",
            password="Pw123456!!",
        )
        verify_email(self.user)

        self.signup_url = reverse("account_signup")
        self.login_url = reverse("account_login")
        self.logout_url = reverse("account_logout")

        self.home_url = reverse("accounts:home_page")
        self.account_url = reverse("accounts:account")

    # ------------------------------------------------------------------
    # Login tests (allauth email-only)
    # ------------------------------------------------------------------

    def test_user_login_success_verified_email(self):
        resp = self.client.post(
            self.login_url,
            data={"login": "tester@testing.com", "password": "Pw123456!!"},
            follow=True,
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_user_login_bad_password(self):
        resp = self.client.post(
            self.login_url,
            data={"login": "tester@testing.com", "password": "someotherstring"},
            follow=True,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_login_bad_email(self):
        resp = self.client.post(
            self.login_url,
            data={"login": "nope@testing.com", "password": "Pw123456!!"},
            follow=True,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_login_password_case_mismatch(self):
        resp = self.client.post(
            self.login_url,
            data={"login": "tester@testing.com", "password": "pW123456!!"},
            follow=True,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_login_blocked_if_email_not_verified(self):
        user2 = create_user(username="NoVerify", email="noverify@testing.com", password="Pw123456!!")
        # Do NOT verify email for user2

        resp = self.client.post(
            self.login_url,
            data={"login": "noverify@testing.com", "password": "Pw123456!!"},
            follow=True,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    # ------------------------------------------------------------------
    # Signup tests (allauth signup form)
    # ------------------------------------------------------------------

    def test_signup_user_empty_password(self):
        resp = self.client.post(
            self.signup_url,
            data={"email": "new@testing.com", "password1": "", "password2": ""},
        )
        # Allauth re-renders form with errors (status 200)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(email="new@testing.com").count(), 0)

    def test_signup_user_empty_email(self):
        resp = self.client.post(
            self.signup_url,
            data={"email": "", "password1": "Pw123456!!", "password2": "Pw123456!!"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_signup_user_invalid_email(self):
        resp = self.client.post(
            self.signup_url,
            data={"email": "pickles@", "password1": "Pw123456!!", "password2": "Pw123456!!"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_signup_user_password_mismatch(self):
        resp = self.client.post(
            self.signup_url,
            data={"email": "new2@testing.com", "password1": "Pw123456!!", "password2": "DifferentPw!!"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.filter(email="new2@testing.com").count(), 0)

    def test_signup_success_creates_user(self):
        resp = self.client.post(
            reverse("account_signup"),
            data={
                "email": "brandnew@testing.com",
                "password1": "Pw123456!!",
                "password2": "Pw123456!!",
                "agreed_to_tos": "on",  # ✅ checkbox field
            },
            follow=True,
        )

        self.assertEqual(User.objects.filter(email="brandnew@testing.com").count(), 1)
        
    def test_signup_requires_tos(self):
        resp = self.client.post(
            reverse("account_signup"),
            data={
                "email": "no-tos@testing.com",
                "password1": "Pw123456!!",
                "password2": "Pw123456!!",
                # no agreed_to_tos
            },
            follow=True,
        )
        self.assertEqual(User.objects.filter(email="no-tos@testing.com").count(), 0)

    # ------------------------------------------------------------------
    # Logout tests (allauth)
    # ------------------------------------------------------------------

    def test_logout(self):
        # Login first
        login_via_allauth(self.client, "tester@testing.com", "Pw123456!!")
        self.assertIn("_auth_user_id", self.client.session)

        # Logout via POST (required when ACCOUNT_LOGOUT_ON_GET = False)
        resp = self.client.post(reverse("account_logout"), follow=True)

        # Session should be cleared
        self.assertNotIn("_auth_user_id", self.client.session)

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------

    def test_anonymous_account_redirects(self):
        resp = self.client.get(self.account_url)
        self.assertEqual(resp.status_code, 302)
