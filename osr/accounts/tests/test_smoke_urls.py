# accounts/tests/test_smoke_urls.py
from django.test import TestCase
from django.urls import reverse


class PublicPagesSmokeTests(TestCase):
    def test_root_page(self):
        resp = self.client.get(reverse("accounts:root_page"))
        self.assertIn(resp.status_code, (200, 302))

    def test_home_page(self):
        resp = self.client.get(reverse("accounts:home_page"))
        self.assertIn(resp.status_code, (200, 302))

    def test_tos(self):
        resp = self.client.get(reverse("accounts:tos"))
        self.assertEqual(resp.status_code, 200)

    def test_privacy(self):
        resp = self.client.get(reverse("accounts:privacy"))
        self.assertEqual(resp.status_code, 200)
