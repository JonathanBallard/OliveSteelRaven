
# accounts\models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class User(AbstractUser):
    """
    Maps to SQL table: "users"

    Key mapping differences vs default Django:
    - username max_length=50
    - email unique + CHECK constraint (regex) + validator
    - password stored in DB column password_hash (TEXT)
    - last_login stored in DB column last_login_at (timestamptz)
    - profile_image_url stored as TEXT (we'll use TextField)
    """

    # Override username length to match varchar(50)
    # username = models.CharField(max_length=50, unique=True)

    # Email: unique + validator + DB CHECK constraint equivalent
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[
            RegexValidator(
                regex=EMAIL_REGEX,
                message="Email must match required pattern.",
                code="invalid_email_format",
            )
        ],
    )

    # Store Django's hashed password in column "password_hash" (TEXT)
    # password = models.TextField(db_column="password_hash")

    # Text column in SQL
    profile_image_url = models.TextField(null=True, blank=True, default="./assets/icons/users/default_user.png")

    # Map AbstractUser's last_login to last_login_at
    last_login = models.DateTimeField(null=True, blank=True, db_column="last_login_at")

    # Timestamps in SQL
    created_at = models.DateTimeField(auto_now_add=True, db_column="created_at")
    updated_at = models.DateTimeField(auto_now=True, db_column="updated_at")

    class Meta:
        db_table = "users"
        constraints = [
            # Mirrors: CHECK (email ~* 'regex')
            models.CheckConstraint(
                condition=Q(email__iregex=EMAIL_REGEX),
                name="valid_email",
            ),
        ]

    def __str__(self) -> str:
        return f"User: username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name}"
