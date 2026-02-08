from __future__ import annotations

import os
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

#! BEFORE RUNNING, Either make sure accounts/management/commands/seed_admin.py has been run, or explicitly choose owner
#$ python manage.py seed_admin

#* Run using:                        
#$ python manage.py seed_recipes 
#* Explicitly choose owner:       
#$ python manage.py seed_recipes --owner-id 1


class Command(BaseCommand):
    help = "Seed common recipes by running the SQL seed file via psql."

    def add_arguments(self, parser):
        parser.add_argument(
            "--owner-id",
            type=int,
            default=1,
            help="Owner user id for seeded recipes (default: 1).",
        )
        parser.add_argument(
            "--sql-path",
            type=str,
            default="recipes/sql/seed_recipes.sql",
            help="Path (relative to BASE_DIR) to the seed SQL file.",
        )

    def handle(self, *args, **options):
        owner_id: int = options["owner_id"]
        sql_rel_path: str = options["sql_path"]

        db = settings.DATABASES["default"]
        engine = db.get("ENGINE", "")
        if "postgresql" not in engine:
            raise CommandError(
                f"This command is intended for PostgreSQL. ENGINE={engine!r}"
            )

        base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
        sql_path = (base_dir / sql_rel_path).resolve()

        if not sql_path.exists():
            raise CommandError(f"SQL file not found: {sql_path}")

        # Build psql command from Django DB settings
        dbname = db.get("NAME")
        user = db.get("USER") or ""
        password = db.get("PASSWORD") or ""
        host = db.get("HOST") or ""
        port = str(db.get("PORT") or "")

        if not dbname:
            raise CommandError("DATABASES['default']['NAME'] is missing.")

        cmd = ["psql", "-v", f"owner_id={owner_id}", "-f", str(sql_path), dbname]

        # Add optional connection args
        if user:
            cmd.extend(["-U", user])
        if host:
            cmd.extend(["-h", host])
        if port:
            cmd.extend(["-p", port])

        env = os.environ.copy()
        if password:
            # Allows non-interactive auth without prompting
            env["PGPASSWORD"] = password

        self.stdout.write(f"Running seed SQL: {sql_path}")
        self.stdout.write(f"Using owner_id={owner_id}")

        try:
            subprocess.run(cmd, check=True, env=env)
        except FileNotFoundError as e:
            raise CommandError(
                "psql not found. Install PostgreSQL client tools and ensure 'psql' is on PATH."
            ) from e
        except subprocess.CalledProcessError as e:
            raise CommandError(
                f"psql exited with code {e.returncode}. See output above for details."
            ) from e

        self.stdout.write(self.style.SUCCESS("Recipe seed completed successfully."))
