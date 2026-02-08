# recipes/tests/test_permissions.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, Category


class RecipeOwnershipTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(username="owner", password="Pw12345", email="tester@testing.com")
        self.other = User.objects.create_user(username="other", password="Pw12345", email="other@testing.com")

        self.category = Category.objects.create(name="Lasagna")

        self.recipe = Recipe.objects.create(
            owner=self.owner,
            title="Owner's Secret Lasagna",
            category=self.category,
            prep_time_minutes=10,
            difficulty=1,
        )

    def test_non_owner_cannot_access_update_view(self):
        """
        Non-owner should NOT be able to load the update page for someone else's recipe.
        Your update view uses get_object_or_404(Recipe, pk=..., owner=request.user),
        so the expected response is 404.
        """
        self.client.login(username="other", password="Pw12345")

        url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 404)
