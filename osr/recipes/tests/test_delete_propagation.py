from django.test import TestCase
from django.urls import reverse

from recipes.models import RecipeIngredient, Ingredient, Tag, Recipe
from .utils import (
    create_user,
    verify_email,
    login_via_allauth,
    make_category,
    make_recipe,
    add_ingredient_line,
    add_tags,
)


class DeletePropagationTests(TestCase):
    def test_delete_recipe_removes_lines_and_m2m_but_keeps_catalogs(self):
        # Arrange: owner + verified email (allauth-friendly)
        user = create_user(email="owner@example.com", password="Passw0rd!123")
        verify_email(user)
        login_via_allauth(self.client, "owner@example.com", "Passw0rd!123")

        cat = make_category()
        recipe = make_recipe(owner=user, category=cat)

        # Add 2 ingredient lines
        add_ingredient_line(recipe, "Salt", 1)
        add_ingredient_line(recipe, "Pepper", 2)

        # Add 2 tags via M2M
        add_tags(recipe, ["easy", "dinner"])

        # Sanity checks pre-delete
        self.assertTrue(Recipe.objects.filter(pk=recipe.pk).exists())
        self.assertEqual(RecipeIngredient.objects.filter(recipe=recipe).count(), 2)
        self.assertEqual(recipe.tags.count(), 2)

        through = recipe.tags.through
        self.assertEqual(through.objects.filter(recipe_id=recipe.pk).count(), 2)

        # Act: delete the recipe
        delete_url = reverse("recipes:delete_recipe", kwargs={"recipe_id": recipe.pk})
        resp = self.client.post(delete_url)

        # Assert: recipe gone
        self.assertIn(resp.status_code, (302, 200))
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

        # Assert: dependent rows gone
        self.assertEqual(RecipeIngredient.objects.filter(recipe_id=recipe.pk).count(), 0)
        self.assertEqual(through.objects.filter(recipe_id=recipe.pk).count(), 0)

        # Assert: catalogs remain (global Ingredient + Tag tables should not be nuked)
        self.assertTrue(Ingredient.objects.filter(name_normalized="salt").exists())
        self.assertTrue(Ingredient.objects.filter(name_normalized="pepper").exists())
        self.assertTrue(Tag.objects.filter(name="easy").exists())
        self.assertTrue(Tag.objects.filter(name="dinner").exists())
