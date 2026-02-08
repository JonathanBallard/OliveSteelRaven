# recipes/tests/test_line_order_normalization.py
from django.test import TestCase
from django.urls import reverse

from recipes.models import RecipeIngredient
from .utils import (
    create_user, verify_email, login_via_allauth,
    make_category, make_recipe, add_ingredient_line
)

class LineOrderNormalizationTests(TestCase):
    def test_update_normalizes_line_order_to_1_through_n(self):
        user = create_user(email="owner@example.com", password="Passw0rd!123")
        verify_email(user)
        login_via_allauth(self.client, "owner@example.com", "Passw0rd!123")

        cat = make_category()
        recipe = make_recipe(owner=user, category=cat)

        ri1 = add_ingredient_line(recipe, "Salt", 1)
        ri2 = add_ingredient_line(recipe, "Pepper", 2)

        url = reverse("recipes:update_recipe", kwargs={"recipe_id": recipe.pk})

        data = {
            # ---- RecipeForm fields (must satisfy RecipeForm.is_valid()) ----
            "title": recipe.title,
            "short_description": recipe.short_description,
            "long_description": recipe.long_description,
            "instructions": recipe.instructions,
            "category": str(cat.pk),
            "prep_time_minutes": str(recipe.prep_time_minutes),
            "difficulty": str(recipe.difficulty),
            "user_rating": "",

            # Tags
            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # ---- Formset management ----
            "ingredients-TOTAL_FORMS": "2",
            "ingredients-INITIAL_FORMS": "2",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # ---- Existing rows (swap their order + weird line_order values) ----
            "ingredients-0-id": str(ri2.pk),
            "ingredients-0-ingredient_name": "Pepper",
            "ingredients-0-line_order": "99",
            "ingredients-0-DELETE": "",

            "ingredients-1-id": str(ri1.pk),
            "ingredients-1-ingredient_name": "Salt",
            "ingredients-1-line_order": "4",
            "ingredients-1-DELETE": "",
        }

        resp = self.client.post(url, data=data)

        # If this fails, show errors so we can align fields
        if resp.status_code != 302:
            form = getattr(resp, "context", {}).get("form") if getattr(resp, "context", None) else None
            formset = getattr(resp, "context", {}).get("formset") if getattr(resp, "context", None) else None
            msg = "Expected redirect but got %s." % resp.status_code
            if form is not None:
                msg += f" Form errors: {form.errors.as_json()}"
            if formset is not None:
                msg += f" Formset errors: {formset.errors} Non-form: {formset.non_form_errors()}"
            raise AssertionError(msg)

        lines = list(RecipeIngredient.objects.filter(recipe=recipe).order_by("line_order"))
        self.assertEqual([li.line_order for li in lines], [1, 2])
