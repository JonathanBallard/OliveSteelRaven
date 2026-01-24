# recipes/tests/test_views.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe, Category, Tag, Ingredient, RecipeIngredient


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
        
        # IMPORTANT: update this URL name if yours differs.
        # Common patterns: "recipes:update" or "recipes:update_recipe"
        url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})
        
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 404)


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

        # IMPORTANT: update if your create URL name differs.
        self.create_url = reverse("recipes:create_recipe")

    def _base_post_data(self) -> dict:
        """
        Minimal valid payload for RecipeForm + RecipeIngredientFormSet(prefix="ingredients")
        """
        return {
            # RecipeForm fields (adjust if your model/form requires others)
            "title": "Test Recipe",
            "recipe_image": "",  # optional
            "short_description": "short",
            "long_description": "long",
            "instructions": "step 1\nstep 2",
            "category": str(self.category.pk),
            "prep_time_minutes": "5",
            "difficulty": "1",
            "user_rating": "",  # nullable/blank

            # New tag inputs
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # Ingredient formset management form (prefix="ingredients")
            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # One ingredient line (must match what your formset expects)
            "ingredients-0-ingredient_name": "Onion Powder",
            # Include these if your RecipeIngredient form exposes them; safe to omit if not present:
            # "ingredients-0-quantity": "1",
            # "ingredients-0-unit_text": "tsp",
            # "ingredients-0-prep_note": "",
        }

    def test_create_rejects_more_than_3_total_tags(self):
        """
        Selecting 3 existing tags + adding 1 new tag should fail (max 3 total).
        """
        data = self._base_post_data()

        # Select 3 existing tags
        data["tags"] = [str(self.t1.pk), str(self.t2.pk), str(self.t3.pk)]
        # Add 1 new tag (total would be 4)
        data["tag_1"] = "spicy"

        before = Recipe.objects.count()
        resp = self.client.post(self.create_url, data=data)

        # Your create view returns status=400 when invalid
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, "at most 3 tags", status_code=400)
        self.assertEqual(Recipe.objects.count(), before)

    def test_create_allows_up_to_3_total_tags(self):
        """
        Selecting 2 existing tags + adding 1 new tag should succeed (total 3).
        """
        data = self._base_post_data()

        # 2 existing + 1 new = 3 total
        data["tags"] = [str(self.t1.pk), str(self.t2.pk)]
        data["tag_1"] = "spicy"

        before = Recipe.objects.count()
        resp = self.client.post(self.create_url, data=data)

        # Success should redirect to recipe detail
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Recipe.objects.count(), before + 1)

        recipe = Recipe.objects.latest("id")
        self.assertEqual(recipe.tags.count(), 3)


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

        self.ri_salt = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=salt,
            line_order=1,
        )
        self.ri_pepper = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=pepper,
            line_order=2,
        )

    def test_update_reorders_and_allows_duplicate_ingredient_lines(self):
        """
        Update should:
        - reorder ingredient lines based on submitted form order (line_order reassigned 1..N)
        - allow duplicate ingredient lines in the same recipe
        - dedupe the global Ingredient catalog by normalized name (one Ingredient row per name_normalized)
        """
        url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})

        data = {
            # --- RecipeForm required fields (include everything your form expects) ---
            "title": self.recipe.title,
            "short_description": self.recipe.short_description,
            "long_description": self.recipe.long_description,
            "instructions": self.recipe.instructions,
            "category": str(self.category.pk),
            "prep_time_minutes": str(self.recipe.prep_time_minutes),
            "difficulty": str(self.recipe.difficulty),
            "user_rating": "",

            # Tags fields (safe defaults)
            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # --- Ingredient inline formset (prefix="ingredients") ---
            "ingredients-TOTAL_FORMS": "3",
            "ingredients-INITIAL_FORMS": "2",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # Reorder existing rows by swapping which IDs appear first.
            # Form 0: existing pepper line
            "ingredients-0-id": str(self.ri_pepper.pk),
            "ingredients-0-ingredient_name": "pepper",
            "ingredients-0-DELETE": "",

            # Form 1: existing salt line
            "ingredients-1-id": str(self.ri_salt.pk),
            "ingredients-1-ingredient_name": "salt",
            "ingredients-1-DELETE": "",

            # Form 2: NEW duplicate salt line (allowed)
            "ingredients-2-id": "",
            "ingredients-2-ingredient_name": "salt",
            "ingredients-2-DELETE": "",
        }

        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 302)

        # Check through-table ordering and duplicates
        lines = list(
            RecipeIngredient.objects.filter(recipe=self.recipe)
            .select_related("ingredient")
            .order_by("line_order")
        )
        self.assertEqual(len(lines), 3)
        self.assertEqual([li.line_order for li in lines], [1, 2, 3])
        self.assertEqual([li.ingredient.name_normalized for li in lines], ["pepper", "salt", "salt"])

        # Global Ingredient catalog should still have only one "salt"
        self.assertEqual(Ingredient.objects.filter(name_normalized="salt").count(), 1)
        



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

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pw12345",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pw12345",
        )

        self.category = Category.objects.create(name="Dinner")

        self.create_url = reverse("recipes:create_recipe")
        self.login_url = reverse("accounts:login")

        # Seed a recipe owned by owner with 1 ingredient line so update can validate
        self.recipe = Recipe.objects.create(
            owner=self.owner,
            title="Original Title",
            category=self.category,
            prep_time_minutes=5,
            difficulty=1,
            instructions="Original instructions",
        )

        salt = Ingredient.objects.create(name="Salt", name_normalized="salt")
        self.ri_salt = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=salt,
            line_order=1,
        )

        self.update_url = reverse("recipes:update_recipe", kwargs={"recipe_id": self.recipe.pk})
        self.delete_url = reverse("recipes:delete_recipe", kwargs={"recipe_id": self.recipe.pk})
        self.search_url = reverse("recipes:search")

    # --------------------------
    # Helpers
    # --------------------------
    def _valid_create_post_data(self, title: str = "Created Recipe") -> dict:
        """
        Minimal valid payload for:
        - RecipeForm
        - RecipeIngredientFormSet(prefix="ingredients") with at least one ingredient_name
        """
        return {
            # RecipeForm fields
            "title": title,
            "recipe_image": "",
            "short_description": "short",
            "long_description": "long",
            "instructions": "step 1\nstep 2",
            "category": str(self.category.pk),
            "prep_time_minutes": "5",
            "difficulty": "1",
            "user_rating": "",

            # Tags fields (safe defaults)
            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # Ingredient formset management (prefix="ingredients")
            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # One ingredient line
            "ingredients-0-ingredient_name": "Salt",
            "ingredients-0-DELETE": "",
        }

    def _valid_update_post_data(self, title: str, ingredient_name: str = "Salt") -> dict:
        """
        Minimal valid payload for update:
        - Includes one existing ingredient form row (id present)
        """
        return {
            # RecipeForm fields (keep required ones)
            "title": title,
            "short_description": self.recipe.short_description,
            "long_description": self.recipe.long_description,
            "instructions": self.recipe.instructions,
            "category": str(self.category.pk),
            "prep_time_minutes": str(self.recipe.prep_time_minutes),
            "difficulty": str(self.recipe.difficulty),
            "user_rating": "",

            # Tags fields (safe defaults)
            "tags": [],
            "tag_1": "",
            "tag_2": "",
            "tag_3": "",

            # Ingredient formset management (prefix="ingredients")
            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "1",
            "ingredients-MIN_NUM_FORMS": "0",
            "ingredients-MAX_NUM_FORMS": "1000",

            # Existing ingredient row
            "ingredients-0-id": str(self.ri_salt.pk),
            "ingredients-0-ingredient_name": ingredient_name,
            "ingredients-0-DELETE": "",
        }

    # --------------------------
    # 1) Anonymous blocked
    # --------------------------
    def test_anonymous_blocked_from_create_update_delete(self):
        # Create: GET
        resp = self.client.get(self.create_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        # Create: POST
        resp = self.client.post(self.create_url, data=self._valid_create_post_data())
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        # Update: GET
        resp = self.client.get(self.update_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        # Update: POST
        resp = self.client.post(self.update_url, data=self._valid_update_post_data(title="Nope"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

        # Delete: POST (most delete views are POST-only; if yours is GET, this still shows auth wall)
        resp = self.client.post(self.delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.login_url, resp["Location"])

    # --------------------------
    # 2) Owner update success
    # --------------------------
    def test_owner_can_get_and_post_update_successfully(self):
        self.client.login(username="owner", password="pw12345")

        # GET update should load
        resp = self.client.get(self.update_url)
        self.assertEqual(resp.status_code, 200)

        # POST update should redirect and persist changes
        new_title = "Updated Title"
        resp = self.client.post(self.update_url, data=self._valid_update_post_data(title=new_title))
        self.assertEqual(resp.status_code, 302)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, new_title)

    # --------------------------
    # 3) Atomic update: invalid formset means no partial recipe update
    # --------------------------
    def test_update_is_atomic_invalid_ingredients_does_not_change_recipe(self):
        self.client.login(username="owner", password="pw12345")

        original_title = self.recipe.title

        # Try to change the title, but make the ingredient formset invalid (blank ingredient)
        data = self._valid_update_post_data(title="Should Not Persist", ingredient_name="   ")
        resp = self.client.post(self.update_url, data=data)

        # Your update view re-renders with status=400 when invalid
        self.assertEqual(resp.status_code, 400)

        # Recipe should NOT have been updated (atomic behavior / no partial save)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, original_title)

    # --------------------------
    # 4) Search sanity
    # --------------------------
    def test_search_returns_recipe_by_title(self):
        self.client.login(username="owner", password="pw12345")

        # Search by title substring
        resp = self.client.get(self.search_url, data={"q": "Original", "category_id": ""})
        self.assertEqual(resp.status_code, 200)

        # Should contain the recipe title in rendered HTML
        self.assertContains(resp, "Original Title", status_code=200)