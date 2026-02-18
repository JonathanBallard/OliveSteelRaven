# osr/accounts/management/commands/seed_admin.py
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import Max
from allauth.account.models import EmailAddress
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Create/update the singleton admin user (by email) and fix the Postgres PK sequence."

    def handle(self, *args, **options):
        load_dotenv()

        password = os.getenv("ADMIN_PASSWORD")
        if not password:
            raise CommandError(
                "ADMIN_PASSWORD not found.\n"
                "Add it to your .env file:\n\n"
                "  ADMIN_PASSWORD=StrongPassword123!"
            )

        email = (os.getenv("ADMIN_LOGIN") or "admin@recipebook.com").strip().lower()

        User = get_user_model()

        # These will be: table="users", pk_col="id" for your model
        table = User._meta.db_table
        pk_field = User._meta.pk
        pk_col = pk_field.column

        if connection.vendor != "postgresql":
            raise CommandError("This command is currently written for PostgreSQL only.")

        with transaction.atomic():
            # Singleton by email (email is unique in your model)
            user = User.objects.filter(email=email).first()
            created = False

            if user is None:
                # Choose an unused PK above current max so ordering remains sensible.
                current_max = User.objects.aggregate(m=Max(pk_field.name))["m"] or 0
                new_id = current_max + 1

                # Defensive loop in case something bizarre already used that id.
                while User.objects.filter(**{pk_field.name: new_id}).exists():
                    new_id += 1

                user = User(**{pk_field.name: new_id, "email": email})
                created = True

            # Ensure flags + password
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()

            # allauth: mark verified+primary
            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True},
            )

            # Critical: bump the sequence to MAX(id) so next insert uses MAX+1
            self._reset_postgres_sequence(table=table, pk_col=pk_col)

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin user: id={user.pk}, email={user.email}"))

    def _reset_postgres_sequence(self, table: str, pk_col: str) -> None:
        with connection.cursor() as cursor:
            # Works for serial/identity-backed columns in normal Django migrations
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence(%s, %s),
                    COALESCE((SELECT MAX("{pk_col}") FROM "{table}"), 1),
                    true
                );
                """,
                [table, pk_col],
            )
