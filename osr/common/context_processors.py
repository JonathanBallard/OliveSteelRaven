# common/context_processors.py
from django.conf import settings

def global_settings(request):
    """
    Expose a small, safe subset of settings to all templates.
    Keep this non-sensitive and mostly UI-related.
    """
    return {
        # Basics
        "APP_NAME": getattr(settings, "APP_NAME", "RecipeBook"),
        "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", "Jonathan Ballard"),
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "2ravenstech@gmail.com"),
        "GITHUB_LINK": getattr(settings, "GITHUB_LINK", "https://github.com/JonathanBallard/OliveSteelRaven"),
        "DEVELOPER_LINKEDIN": getattr(settings, "DEVELOPER_LINKEDIN", "https://www.linkedin.com/in/jonathanbal"),
        "TOS_DATE": getattr(settings, "TOS_DATE", "2/4/26"),
        
        # Defaults
        "HERO_RECIPE_PK": getattr(settings, "HERO_RECIPE_PK", 0),
        "DEFAULT_USER_IMAGE": getattr(settings, "DEFAULT_USER_IMAGE", "default_user.png"),
        "DEFAULT_RECIPE_IMAGE": getattr(settings, "DEFAULT_RECIPE_IMAGE", "default_recipe.png"),
        "RECIPE_IMAGE_SIZE": getattr(settings, "RECIPE_IMAGE_SIZE", 400),
        "HERO_MAX_IMAGE_SIZE": getattr(settings, "HERO_MAX_IMAGE_SIZE", 500),
        "ENABLE_RECIPE_IMAGES": getattr(settings, "ENABLE_RECIPE_IMAGES", True),
        
        "MAX_TAGS_PER_RECIPE": getattr(settings, "MAX_TAGS_PER_RECIPE", 3),
        "MAX_INGREDIENTS_PER_RECIPE": getattr(settings, "MAX_INGREDIENTS_PER_RECIPE", 30),

        # Often useful in templates:
        "STATIC_URL": getattr(settings, "STATIC_URL", "/static/"),
        "MEDIA_URL": getattr(settings, "MEDIA_URL", "/media/"),
        "DEBUG": getattr(settings, "DEBUG", False),
    }
