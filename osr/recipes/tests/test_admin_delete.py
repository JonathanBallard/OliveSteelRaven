# recipes/tests/test_admin_delete.py
from django.test import TestCase
from django.urls import reverse

from .utils import (
    create_user, verify_email, login_via_allauth,
    make_category, make_recipe
)

class AdminDeleteTests(TestCase):
    def test_superuser_in_admin_mode_can_delete_non_owned_recipe(self):
        owner = create_user(email="owner@example.com", password="Passw0rd!123")
        verify_email(owner)

        admin = create_user(email="admin@example.com", password="Passw0rd!123", is_superuser=True)
        verify_email(admin)

        cat = make_category()
        recipe = make_recipe(owner=owner, category=cat, title="Owner Recipe")

        login_via_allauth(self.client, "admin@example.com", "Passw0rd!123")

        # Enable admin mode in session (either via toggle view or direct session)
        session = self.client.session
        session["admin_mode"] = True
        session.save()

        url = reverse("recipes:delete_recipe", kwargs={"recipe_id": recipe.pk})
        resp = self.client.post(url, follow=True)

        self.assertEqual(resp.status_code, 200)  # after follow=True, you land somewhere
        self.assertFalse(type(recipe).objects.filter(pk=recipe.pk).exists())
