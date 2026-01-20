from django import forms
from django.contrib.auth import get_user_model

from .models import Recipe, RecipeFavorite, RecipeIngredient, RecipeTag, Ingredient

class RecipeModelForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = Recipe
        fields = ["title", "short_description", "long_description", "instructions", "difficulty", "prep_time_minutes"]
