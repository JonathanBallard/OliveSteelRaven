# recipes/tests/test_update_formset_extra.py
from django.test import TestCase
from django.urls import reverse

from .utils import (
    create_user, verify_email, login_via_allauth,
    make_category, make_recipe, add_ingredient_line
)

class UpdateFormsetExtraTests(TestCase):
    def test_update_get_shows_only_existing_ingredients(self):
        user = create_user(email="owner@example.com", password="Passw0rd!123")
        verify_email(user)
        login_via_allauth(self.client, "owner@example.com", "Passw0rd!123")

        cat = make_category()
        recipe = make_recipe(owner=user, category=cat)

        add_ingredient_line(recipe, "Salt", 1)
        add_ingredient_line(recipe, "Pepper", 2)

        url = reverse("recipes:update_recipe", kwargs={"recipe_id": recipe.pk})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

        formset = resp.context["formset"]
        self.assertEqual(formset.initial_form_count(), 2)
        # ✅ This is the key requirement: no extra blank row on edit
        self.assertEqual(formset.total_form_count(), 2)
