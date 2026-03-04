from .base import *
import os
from django.core.management.utils import get_random_secret_key

DEBUG = True

# safe defaults for local
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# optional: console email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media" #development

HERO_RECIPE_PK = 64 # This recipe is our homepage Hero recipe, otherwise random - SET FOR PRODUCTION
FEATURED_RECIPE_PKS = [] # These recipes will be shown on the front page, otherwise picked at random

SECRET_KEY="dev-insecure-key-9x!p3#kL2@recipebook-local-only-2026"

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles" #development

STATICFILES_DIRS = [
    BASE_DIR / "static",   # project-wide static folder
]

CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SECURE = False

SECURE_SSL_REDIRECT = False

SECURE_HSTS_SECONDS = 0

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
TEST_CONFIRMATION_EMAIL = "2ravenstech@gmail.com"

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'osrdb'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Or the host IP if not local
        'PORT': os.getenv('DB_PORT', ''),           # PostgreSQL default port is 5432. Leaving empty uses the default.
    }
}
