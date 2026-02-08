# recipes/tests/test_critical_flows.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, Category, Ingredient, RecipeIngredient


class RecipeCriticalFlowTests(TestCase):
    """
    Critical recipe tests:
    1) Anonymous blocked from create/update/delete
    2) Owner update success (GET + POST)
    3) Atomic update: invalid ingredient formset prevents partial recipe updates
    4) Search sanity (title search returns expected recipe)
    """

    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="pw12345")
        self.other = User.objects.create_user(username="other", email="other@example.com", password="pw12345")

        self.category = Category.objects.create(name="Dinner")

        self.create_url = reverse("recipes:create_recipe")
        self.login_url = reverse("account_login")  # allauth

        self.recipe = Recipe.objects.create(
            owner=self.owner,
            title="Original Title",
            category=self.category,
            prep_time_minutes=5,
            difficulty=1,
            instructions="Original instructions",
        )

        salt = Ingredient.objects.create(name="Salt", name_normalized="salt")
        self.ri_salt = RecipeIngredient.objects.create(recipe=self.recipe, ingredient=salt, line_order=1)

        self.update_url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})
        self.delete_url = reverse("recipes:delete_recipe", kwargs={"recipe_id": self.recipe.pk})
        self.search_url = reverse("recipes:search")

    def _valid_create_post_data(self, title: str = "Created Recipe") -> dict:
        return {
            "title": title,
            "recipe_image": "",
            "short_description": "short",
            "long_description": "long",
            "instructions": "step 1\nstep 2",
            "category": str(self.category.pk),
            "prep_time_minutes": "5",
            "difficulty": "1",
            "user_rating": "",

            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            "ingredients-0-ingredient_name": "Salt",
            "ingredients-0-DELETE": "",
        }

    def _valid_update_post_data(self, title: str, ingredient_name: str = "Salt") -> dict:
        return {
            "title": title,
            "short_description": self.recipe.short_description,
            "long_description": self.recipe.long_description,
            "instructions": self.recipe.instructions,
            "category": str(self.category.pk),
            "prep_time_minutes": str(self.recipe.prep_time_minutes),
            "difficulty": str(self.recipe.difficulty),
            "user_rating": "",

            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "1",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            "ingredients-0-id": str(self.ri_salt.pk),
            "ingredients-0-ingredient_name": ingredient_name,
            "ingredients-0-DELETE": "",
        }

    def test_anonymous_blocked_from_create_update_delete(self):
        resp = self.client.get(self.create_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        resp = self.client.post(self.create_url, data=self._valid_create_post_data())
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        resp = self.client.get(self.update_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        resp = self.client.post(self.update_url, data=self._valid_update_post_data(title="Nope"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        resp = self.client.post(self.delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

    def test_owner_can_get_and_post_update_successfully(self):
        self.client.login(username="owner", password="pw12345")

        resp = self.client.get(self.update_url)
        self.assertEqual(resp.status_code, 200)

        new_title = "Updated Title"
        resp = self.client.post(self.update_url, data=self._valid_update_post_data(title=new_title))
        self.assertEqual(resp.status_code, 302)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, new_title)

    def test_update_is_atomic_invalid_ingredients_does_not_change_recipe(self):
        self.client.login(username="owner", password="pw12345")

        original_title = self.recipe.title
        data = self._valid_update_post_data(title="Should Not Persist", ingredient_name="   ")
        resp = self.client.post(self.update_url, data=data)

        self.assertEqual(resp.status_code, 400)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, original_title)

    def test_search_returns_recipe_by_title(self):
        self.client.login(username="owner", password="pw12345")

        resp = self.client.get(self.search_url, data={"q": "Original", "category_id": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Original Title", status_code=200)
