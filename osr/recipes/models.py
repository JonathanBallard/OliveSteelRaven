
# recipes\models.py

from __future__ import annotations

import re
from PIL import Image
from io import BytesIO

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.base import ContentFile

def normalize_ingredient_name(raw: str) -> str:
    """
    Normalization used for de-duping + searching.
    V1: strip, collapse whitespace, lowercase.
    """
    if raw is None:
        return ""
    s = raw.strip()
    s = re.sub(r"\s+", " ", s)
    return s.lower()


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """
    Docstring for Tag
    
    Tags will be checkboxes for users to check per recipe. Max of 3 each.
    
    Tags:
        Vegan
        Meat-Free
        Gluten-Free
        Low/No Sugar
        
    """
    name = models.CharField(max_length=24, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """
    Global ingredient catalog shared across all users.
    Prevent duplicates with a normalized unique field.
    """
    name = models.CharField(max_length=120)
    name_normalized = models.CharField(max_length=120, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ingredients"
        indexes = [
            # Useful for “contains”/prefix-ish queries on normalized names
            models.Index(fields=["name_normalized"], name="idx_ing_norm"),
        ]

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValueError("Ingredient.name cannot be empty.")
        self.name_normalized = normalize_ingredient_name(self.name)
        super().save(*args, **kwargs)

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

    title = models.CharField(max_length=100)
    
    recipe_image = models.ImageField(upload_to="recipe_images/", blank=True, null=True)
    
    short_description = models.CharField(
        max_length=300,
        blank=True,
        default="This is my new recipe.",
        help_text="Type a short description of 300 characters or less. This will show up when people search for your recipe."
    )
    long_description = models.TextField(
        blank=True,
        default="Let me tell you a little about my recipe.",
        help_text="Type a description of your recipe. Talk about its history, origins, or your creative process here."
    )

    # ✅ Single text box (textarea) for all steps/instructions
    # Store as plain text; users can separate steps with new lines, numbers, bullets, etc.
    instructions = models.TextField(
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

    prep_time_minutes = models.IntegerField(default=0)
    
    difficulty = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )

    # SQL: integer CHECK (user_rating >= 1 AND user_rating <= 5), nullable
    user_rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column="created_at")
    updated_at = models.DateTimeField(auto_now=True, db_column="updated_at")

    # M:N via junction table recipe_tags
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        related_name="recipes",
        blank=True,
    )

    # M:N via rich junction recipe_ingredients
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.recipe_image:
            return

        img = Image.open(self.recipe_image)

        # Convert to RGB if needed (PNG/WebP safety)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Resize to 200x200 (center-cropped, no distortion)
        img.thumbnail((settings.RECIPE_IMAGE_SIZE, settings.RECIPE_IMAGE_SIZE), Image.LANCZOS) #type: ignore

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        # Replace the file
        self.recipe_image.save(
            self.recipe_image.name,
            ContentFile(buffer.read()),
            save=False,
        )

        super().save(update_fields=["recipe_image"])

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

    line_order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, validators=[MinValueValidator(0)])
    unit_text = models.CharField(max_length=40, null=True, blank=True)
    prep_note = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "recipe_ingredients"
        constraints = [
            # Composite PK in SQL → UniqueConstraint in Django
            models.UniqueConstraint(
                fields=["recipe", "line_order"],
                name="uq_recipe_line_order_pk",
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
        
    def __str__(self) -> str:
        qty = f"{self.quantity:g} " if self.quantity is not None else ""
        unit = f"{self.unit_text} " if self.unit_text else ""
        return f"{self.recipe}: {qty}{unit}{self.ingredient.name}"
        # return f"{self.recipe_id}: {qty}{unit}{self.ingredient.name}"


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
        return f"{self.user.pk} & {self.recipe.pk}"

