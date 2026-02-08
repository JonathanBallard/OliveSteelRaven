# recipes/signals.py
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Recipe

DEFAULT_IMAGE_NAME = "defaults/default_recipe.png"

def _is_deletable_upload(image_field) -> bool:
    """
    Return True only if this looks like an uploaded MEDIA file we should delete.
    """
    if not image_field:
        return False
    if not getattr(image_field, "name", ""):
        return False

    name = image_field.name

    # Never delete the "default" marker
    if name == DEFAULT_IMAGE_NAME:
        return False

    # Guard: if someone accidentally stored a URL or static path, don't delete it
    if name.startswith("http://") or name.startswith("https://"):
        return False
    if name.startswith("/static/") or name.startswith("static/"):
        return False

    return True


@receiver(post_delete, sender=Recipe)
def delete_recipe_image_on_delete(sender, instance: Recipe, **kwargs):
    """
    Delete uploaded recipe image when the Recipe is deleted.
    """
    img = getattr(instance, "recipe_image", None)
    if _is_deletable_upload(img):
        img.delete(save=False) #type: ignore


@receiver(pre_save, sender=Recipe)
def delete_old_recipe_image_on_change(sender, instance: Recipe, **kwargs):
    """
    If recipe_image is changed (or cleared), delete the old uploaded file.
    Prevents orphaned uploads when updating images.
    """
    if not instance.pk:
        return

    try:
        old = Recipe.objects.get(pk=instance.pk)
    except Recipe.DoesNotExist:
        return

    old_img = getattr(old, "recipe_image", None)
    new_img = getattr(instance, "recipe_image", None)

    if not _is_deletable_upload(old_img):
        return

    old_name = old_img.name #type: ignore
    new_name = getattr(new_img, "name", "") if new_img else ""

    # If changed or cleared, delete the old
    if old_name and old_name != new_name:
        old_img.delete(save=False) #type: ignore
