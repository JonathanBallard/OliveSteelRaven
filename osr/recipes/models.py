
# recipes\models.py

from django.conf import settings
from django.db import models
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "categories"

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=24, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        db_table = "ingredients"

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    # SQL: owner_user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="owner_user_id",
        related_name="recipes_authored",
    )

    title = models.CharField(max_length=200)

    short_description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        default="This is my new recipe.",
    )
    long_description = models.TextField(
        null=True,
        blank=True,
        default="Let me tell you a little about my recipe.",
    )

    # ✅ Single text box (textarea) for all steps/instructions
    # Store as plain text; users can separate steps with new lines, numbers, bullets, etc.
    instructions = models.TextField(
        null=True,
        blank=True,
        default="",
        help_text="Type the full recipe instructions here. Use new lines for steps if you like.",
    )

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="category_id",
        related_name="recipes",
    )

    prep_time_minutes = models.IntegerField()

    # SQL: integer CHECK (user_rating >= 1 AND user_rating <= 5), nullable
    user_rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column="created_at")
    updated_at = models.DateTimeField(auto_now=True, db_column="updated_at")

    # M:N via junction table recipe_tags
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        related_name="recipes",
    )

    # M:N via rich junction recipe_ingredients
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )

    class Meta:
        db_table = "recipes"
        constraints = [
            models.CheckConstraint(
                condition=Q(prep_time_minutes__gte=0),
                name="recipes_prep_time_minutes_gte_0",
            ),
            # Allow NULL, otherwise 1..5
            models.CheckConstraint(
                condition=Q(user_rating__isnull=True)
                | (Q(user_rating__gte=1) & Q(user_rating__lte=5)),
                name="rating_range",
            ),
        ]
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return self.title


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, db_column="recipe_id")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column="tag_id")

    class Meta:
        db_table = "recipe_tags"
        constraints = [
            models.UniqueConstraint(fields=["recipe", "tag"], name="recipe_tags_pk"),
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, db_column="recipe_id")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.RESTRICT, db_column="ingredient_id")

    line_order = models.IntegerField(default=1)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    unit_text = models.CharField(max_length=40, null=True, blank=True)
    prep_note = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "recipe_ingredients"
        constraints = [
            # Composite PK in SQL → UniqueConstraint in Django
            models.UniqueConstraint(
                fields=["recipe", "ingredient", "line_order"],
                name="recipe_ingredients_pk",
            ),
            models.CheckConstraint(
                condition=Q(line_order__gt=0),
                name="recipe_ingredients_line_order_gt_0",
            ),
        ]
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["ingredient"]),
        ]


class RecipeFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="recipe_favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        db_column="recipe_id",
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="created_at")

    class Meta:
        db_table = "recipe_favorites"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="recipe_favorites_pk"),
        ]
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} ♥ {self.recipe_id}"
