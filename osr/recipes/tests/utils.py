# recipes/tests/utils.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from allauth.account.models import EmailAddress

from recipes.models import Category, Recipe, Ingredient, RecipeIngredient, Tag

User = get_user_model()


def create_user(
    email="user@example.com",
    password="Passw0rd!123",
    username=None,
    is_staff=False,
    is_superuser=False,
):
    if username is None:
        username = email.split("@")[0]
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )


def verify_email(user, email=None, primary=True):
    email = email or user.email
    ea, _ = EmailAddress.objects.get_or_create(user=user, email=email)
    ea.verified = True
    ea.primary = primary
    ea.save()
    return ea


def login_via_allauth(client, email, password):
    return client.post(
        reverse("account_login"),
        data={"login": email, "password": password},
        follow=True,
    )


def make_category(name="Dinner"):
    return Category.objects.create(name=name)


def make_recipe(owner, category, title="Test Recipe"):
    return Recipe.objects.create(
        owner=owner,
        title=title,
        category=category,
        prep_time_minutes=5,
        difficulty=1,
        instructions="Step 1",
    )


def add_ingredient_line(recipe, name: str, line_order: int):
    norm = name.strip().lower()
    ing, _ = Ingredient.objects.get_or_create(
        name_normalized=norm,
        defaults={"name": name.strip()},
    )
    return RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ing,
        line_order=line_order,
    )


def add_tags(recipe, names):
    for n in names:
        t, _ = Tag.objects.get_or_create(name=n)
        recipe.tags.add(t)
    recipe.save()
