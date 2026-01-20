# recipes/forms.py

from __future__ import annotations

import re

from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Ingredient, Recipe, RecipeIngredient


_whitespace_re = re.compile(r"\s+")


def normalize_ingredient_name(raw: str) -> str:
    """Keep this consistent with Ingredient.name_normalized."""
    s = (raw or "").strip()
    s = _whitespace_re.sub(" ", s)
    return s.lower()


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "short_description",
            "long_description",
            "instructions",
            "category",
            "prep_time_minutes",
            "difficulty",
            "user_rating",
            "tags",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "long_description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "instructions": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "prep_time_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "difficulty": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "user_rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def clean_prep_time_minutes(self):
        val = self.cleaned_data.get("prep_time_minutes")
        if val is None:
            return val
        if val < 0:
            raise ValidationError("Prep time can’t be negative (unless your oven is a black hole).")
        return val


class RecipeIngredientLineForm(forms.ModelForm):
    """
    One ingredient line entry for a recipe.

    We intentionally *do not* expose the Ingredient FK as a dropdown.
    Instead we accept ingredient_name and resolve it to the global Ingredient
    catalog (deduped by name_normalized).
    """
    ingredient_name = forms.CharField(
        max_length=120,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., sugar"}
        ),
    )

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit_text", "prep_note", "line_order"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "unit_text": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., cup"}),
            "prep_note": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., finely chopped"}),
            "line_order": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # When editing existing lines, prefill ingredient_name from FK
        if self.instance and self.instance.pk and getattr(self.instance, "ingredient_id", None):
            self.fields["ingredient_name"].initial = self.instance.ingredient.name

        # Typically better UX: line_order is managed automatically.
        self.fields["line_order"].required = False
        self.fields["line_order"].widget = forms.HiddenInput()

    def clean_ingredient_name(self) -> str:
        name = (self.cleaned_data.get("ingredient_name") or "").strip()
        if not name:
            raise ValidationError("Ingredient name is required.")
        return name


class BaseRecipeIngredientFormSet(BaseInlineFormSet):
    """
    Formset behavior:
    - requires at least one ingredient line
    - assigns line_order based on the order the forms appear on the page
    - resolves ingredient_name -> Ingredient FK (create if missing; dedupe globally)
    """

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        kept = [
            f for f in self.forms
            if hasattr(f, "cleaned_data")
            and f.cleaned_data
            and not f.cleaned_data.get("DELETE", False)
        ]
        if not kept:
            raise ValidationError("Please add at least one ingredient.")

    def save(self, commit: bool = True):
        instances = super().save(commit=False)

        kept_forms = [
            f for f in self.forms
            if hasattr(f, "cleaned_data")
            and f.cleaned_data
            and not f.cleaned_data.get("DELETE", False)
        ]

        # Auto line_order: 1..N in UI order
        for i, form in enumerate(kept_forms, start=1):
            form.instance.line_order = i

        # Resolve Ingredient FK for each form
        for form in kept_forms:
            pretty = form.cleaned_data["ingredient_name"].strip()
            norm = normalize_ingredient_name(pretty)

            ingredient = Ingredient.objects.filter(name_normalized=norm).first()
            if ingredient is None:
                try:
                    ingredient = Ingredient.objects.create(
                        name=pretty,
                        name_normalized=norm,
                    )
                except IntegrityError:
                    # Another request created it concurrently.
                    ingredient = Ingredient.objects.get(name_normalized=norm)

            form.instance.ingredient = ingredient

        if commit:
            for inst in instances:
                inst.save()
            self.save_m2m()

        return instances


RecipeIngredientFormSet = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    form=RecipeIngredientLineForm,
    formset=BaseRecipeIngredientFormSet,
    extra=3,         # initial blank rows
    can_delete=True, # allow removing ingredient lines
)
