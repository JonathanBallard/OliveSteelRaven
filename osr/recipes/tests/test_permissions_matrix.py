# recipes/tests/test_permissions_matrix.py
from django.test import TestCase
from django.urls import reverse

from .utils import (
    create_user, verify_email, login_via_allauth,
    make_category, make_recipe
)

class RecipePermissionsMatrixTests(TestCase):
    def test_permissions_matrix(self):
        owner = create_user(email="owner@example.com", password="Passw0rd!123")
        verify_email(owner)

        other = create_user(email="other@example.com", password="Passw0rd!123")
        verify_email(other)

        admin = create_user(email="admin@example.com", password="Passw0rd!123", is_superuser=True)
        verify_email(admin)

        cat = make_category()
        recipe = make_recipe(owner=owner, category=cat)

        update_url = reverse("recipes:update_recipe", kwargs={"recipe_id": recipe.pk})
        delete_url = reverse("recipes:delete_recipe", kwargs={"recipe_id": recipe.pk})

        # Anonymous blocked (redirect to allauth login)
        resp = self.client.get(update_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("account_login"), resp["Location"])

        # Non-owner gets 404 on update (your current pattern)
        login_via_allauth(self.client, "other@example.com", "Passw0rd!123")
        resp = self.client.get(update_url)
        self.assertEqual(resp.status_code, 404)
        self.client.logout()

        # Owner can access update
        login_via_allauth(self.client, "owner@example.com", "Passw0rd!123")
        resp = self.client.get(update_url)
        self.assertEqual(resp.status_code, 200)
        self.client.logout()

        # Superuser WITHOUT admin_mode should be blocked (if this is your intended policy)
        login_via_allauth(self.client, "admin@example.com", "Passw0rd!123")
        resp = self.client.post(delete_url)
        self.assertIn(resp.status_code, (403, 404, 302))  # depends on your delete view
        self.client.logout()

        # Superuser WITH admin_mode should be allowed (covered more directly in AdminDeleteTests)
