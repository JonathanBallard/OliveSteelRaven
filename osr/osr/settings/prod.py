from .base import *
import os
from django.core.management.utils import get_random_secret_key

DEBUG = False

# Paths
MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/www/recipebook/media"

HERO_RECIPE_PK = 17 # This recipe is our homepage Hero recipe, otherwise random - SET FOR PRODUCTION
FEATURED_RECIPE_PKS = [] # These recipes will be shown on the front page, otherwise picked at random

SECRET_KEY = os.getenv('SECRET_KEY') or get_random_secret_key()

STATIC_URL = 'static/'
STATIC_ROOT = "/var/www/recipebook/static"
STATICFILES_DIRS = [
    BASE_DIR / "static",   # project-wide static folder
]

CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"