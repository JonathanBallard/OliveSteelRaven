# recipes/tests/test_tag_limits.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, Category, Tag


class RecipeTagLimitTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw12345", email="tester@testing.com")
        self.client.login(username="tester", password="pw12345")

        self.category = Category.objects.create(name="Dinner")

        # 3 existing tags
        self.t1 = Tag.objects.create(name="easy")
        self.t2 = Tag.objects.create(name="quick")
        self.t3 = Tag.objects.create(name="dinner")

        self.create_url = reverse("recipes:create_recipe")

    def _base_post_data(self) -> dict:
        """
        Minimal valid payload for RecipeForm + RecipeIngredientFormSet(prefix="ingredients")
        """
        return {
            "title": "Test Recipe",
            "recipe_image": "",
            "short_description": "short",
            "long_description": "long",
            "instructions": "step 1\nstep 2",
            "category": str(self.category.pk),
            "prep_time_minutes": "5",
            "difficulty": "1",
            "user_rating": "",

            # New tag inputs
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # Ingredient formset management form (prefix="ingredients")
            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            "ingredients-0-ingredient_name": "Onion Powder",
        }

    def test_create_rejects_more_than_3_total_tags(self):
        data = self._base_post_data()

        data["tags"] = [str(self.t1.pk), str(self.t2.pk), str(self.t3.pk)]
        data["tag_1"] = "spicy"

        before = Recipe.objects.count()
        resp = self.client.post(self.create_url, data=data)

        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, "at most 3 tags", status_code=400)
        self.assertEqual(Recipe.objects.count(), before)

    def test_create_allows_up_to_3_total_tags(self):
        data = self._base_post_data()

        data["tags"] = [str(self.t1.pk), str(self.t2.pk)]
        data["tag_1"] = "spicy"

        before = Recipe.objects.count()
        resp = self.client.post(self.create_url, data=data)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Recipe.objects.count(), before + 1)

        recipe = Recipe.objects.latest("id")
        self.assertEqual(recipe.tags.count(), 3)
