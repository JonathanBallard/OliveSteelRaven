from django.core.management.base import BaseCommand
from django.db import connection, transaction
from recipes.models import Category

CATEGORIES = [
    (1, "Breakfast"),
    (2, "Brunch"),
    (3, "Lunch"),
    (4, "Dinner"),
    (5, "Snacks"),
    (6, "Desserts"),
    (7, "Appetizers"),
    (8, "Soups & Stews"),
    (9, "Salads"),
    (10, "Side Dishes"),
    (11, "Main Courses"),
    (12, "Sandwiches"),
    (13, "Casseroles"),
    (14, "Beef"),
    (15, "Chicken"),
    (16, "Pork"),
    (17, "Seafood"),
    (18, "Vegetarian"),
    (19, "Vegan"),
    (20, "American"),
    (21, "Italian"),
    (22, "Mexican"),
    (23, "Asian"),
    (24, "Mediterranean"),
    (25, "Indian"),
    (26, "Breads"),
    (27, "Baking"),
    (28, "Drinks"),
    (29, "Sauces"),
    (30, "Slow Cooker"),
]

class Command(BaseCommand):
    help = "Seed categories with fixed IDs to match development."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing categories...")
        Category.objects.all().delete()

        self.stdout.write("Creating categories...")
        Category.objects.bulk_create(
            [Category(id=cat_id, name=name) for cat_id, name in CATEGORIES]
        )

        # Reset PostgreSQL sequence for categories.id (db_table = "categories")
        max_id = max(cat_id for cat_id, _ in CATEGORIES)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence(%s, %s), %s, true);",
                ["categories", "id", max_id],
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(CATEGORIES)} categories."))
