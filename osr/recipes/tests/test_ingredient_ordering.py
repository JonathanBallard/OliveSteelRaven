# recipes/tests/test_ingredient_ordering.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, Category, Ingredient, RecipeIngredient


class RecipeIngredientOrderingUpdateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="owner", password="pw12345", email="tester@testing.com")
        self.client.login(username="owner", password="pw12345")

        self.category = Category.objects.create(name="Dinner")

        self.recipe = Recipe.objects.create(
            owner=self.user,
            title="Ordering Test",
            category=self.category,
            prep_time_minutes=5,
            difficulty=1,
        )

        # Seed two ingredient lines on the recipe
        salt = Ingredient.objects.create(name="Salt", name_normalized="salt")
        pepper = Ingredient.objects.create(name="Pepper", name_normalized="pepper")

        self.ri_salt = RecipeIngredient.objects.create(recipe=self.recipe, ingredient=salt, line_order=1)
        self.ri_pepper = RecipeIngredient.objects.create(recipe=self.recipe, ingredient=pepper, line_order=2)

    def test_update_reorders_and_allows_duplicate_ingredient_lines(self):
        url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})

        data = {
            # RecipeForm required fields
            "title": self.recipe.title,
            "short_description": self.recipe.short_description,
            "long_description": self.recipe.long_description,
            "instructions": self.recipe.instructions,
            "category": str(self.category.pk),
            "prep_time_minutes": str(self.recipe.prep_time_minutes),
            "difficulty": str(self.recipe.difficulty),
            "user_rating": "",

            # Tags
            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # Ingredient inline formset (prefix="ingredients")
            "ingredients-TOTAL_FORMS": "3",
            "ingredients-INITIAL_FORMS": "2",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # Form 0: existing pepper line
            "ingredients-0-id": str(self.ri_pepper.pk),
            "ingredients-0-ingredient_name": "pepper",
            "ingredients-0-DELETE": "",

            # Form 1: existing salt line
            "ingredients-1-id": str(self.ri_salt.pk),
            "ingredients-1-ingredient_name": "salt",
            "ingredients-1-DELETE": "",

            # Form 2: NEW duplicate salt line
            "ingredients-2-id": "",
            "ingredients-2-ingredient_name": "salt",
            "ingredients-2-DELETE": "",
        }

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)

        lines = list(
            RecipeIngredient.objects.filter(recipe=self.recipe)
            .select_related("ingredient")
            .order_by("line_order")
        )
        self.assertEqual(len(lines), 3)
        self.assertEqual([li.line_order for li in lines], [1, 2, 3])
        self.assertEqual([li.ingredient.name_normalized for li in lines], ["pepper", "salt", "salt"])

        self.assertEqual(Ingredient.objects.filter(name_normalized="salt").count(), 1)
