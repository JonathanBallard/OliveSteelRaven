# recipes/forms.py

from __future__ import annotations

from typing import Iterable, List

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Ingredient, Recipe, RecipeIngredient, Tag, Category
from .utils import normalize_name



class RecipeForm(forms.ModelForm):
    """
    Supports:
    - Selecting existing tags (via the tags M2M field)
    - Creating up to 3 tags via free-text inputs (tag_1..tag_3)
    - Deduping by normalized value (collapsed whitespace + case-insensitive match)
    - Enforcing max 3 total tags per recipe (selected + newly created)
    """
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by("name"),
        empty_label="-Select a Category-",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    tag_1 = forms.CharField(
        max_length=24,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "New tag (optional)"}
        ),
        label="New tag 1",
    )
    tag_2 = forms.CharField(
        max_length=24,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "New tag (optional)"}
        ),
        label="New tag 2",
    )
    tag_3 = forms.CharField(
        max_length=24,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "New tag (optional)"}
        ),
        label="New tag 3",
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "recipe_image",
            "short_description",
            "long_description",
            "instructions",
            "category",
            "prep_time_minutes",
            "difficulty",
            "user_rating",
            "tags",   # existing tags (multi-select)
            "tag_1",  # new tag inputs
            "tag_2",
            "tag_3",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Paint a picture of your recipe"}),
            "long_description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "A more detailed description of your recipe. Consider including substitutions, variations, and pairings."}),
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
        try:
            val = int(val)
        except:
            raise ValidationError("Prep time must be a number of minutes. No text please!")
        return val
    
    def _get_new_tag_inputs(self) -> List[str]:
        raw_vals = [
            self.cleaned_data.get("tag_1", ""),
            self.cleaned_data.get("tag_2", ""),
            self.cleaned_data.get("tag_3", ""),
        ]
        
        normalized: List[str] = []
        seen = set()
        
        for raw in raw_vals:
            name = normalize_name(raw)
            if not name:
                continue
            
            key = name.lower()
            if key in seen:
                continue  # ignore duplicates across tag_1..tag_3
            seen.add(key)
            normalized.append(name)
            
        return normalized
    
    def clean(self):
        cleaned = super().clean()
        
        # Selected existing tags (QuerySet-like; may be empty/None)
        selected_tags = list(cleaned.get("tags") or [])
        selected_count = len(selected_tags)
        
        # New tags entered (0..3, normalized + de-duped across tag_1..tag_3)
        new_tags = self._get_new_tag_inputs()
        
        # Remove any "new" tags that are already selected (case/space-insensitive)
        # normalize_name() already lowercases, so compare normalized strings directly.
        if selected_tags and new_tags:
            selected_keys = {normalize_name(t.name) for t in selected_tags}
            new_tags = [t for t in new_tags if t not in selected_keys]
            
        # Enforce max constraint AFTER de-dupe between selected + new
        total = selected_count + len(new_tags)
        if total > 3:
            raise ValidationError("Please use at most 3 tags total per recipe.")
        
        # Store back so save() uses the filtered list
        cleaned["_new_tags_normalized"] = new_tags
        return cleaned
    
    def _resolve_tags(self, names: Iterable[str]) -> List[Tag]:
        """
        Given normalized tag names, return Tag objects:
        - If an existing Tag matches case-insensitively, reuse it
        - Otherwise create it (handling race conditions)
        """
        tags: List[Tag] = []
        for name in names:
            # Fast path: case-insensitive exact match
            existing = Tag.objects.filter(name__iexact=name).first()
            if existing is not None:
                tags.append(existing)
                continue
            
            try:
                tags.append(Tag.objects.create(name=name))
            except IntegrityError:
                # Another request created it concurrently (or unique constraint triggered)
                tags.append(Tag.objects.get(name__iexact=name))
        return tags
    
    def clean_image(self):
        image = self.cleaned_data.get("image")
        
        if not image:
            return image  # image is optional
        
        valid_mime_types = ["image/jpeg", "image/png", "image/webp"]
        
        if image.content_type not in valid_mime_types:
            raise forms.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
        
        max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        
        if image.size > max_size:
            raise forms.ValidationError(
                f"Image file too large (max {settings.MAX_IMAGE_SIZE_MB} MB)."
            )
            
        return image
    
    def save(self, commit: bool = True):
        # Save the Recipe itself first (M2M needs a PK)
        instance = super().save(commit=False)
        
        # Collect tag intents
        selected = list(self.cleaned_data.get("tags") or [])
        new_names = list(self.cleaned_data.get("_new_tags_normalized") or [])
        
        def _save_m2m():
            # Resolve any new tags, then set the M2M with the combined list
            extra = self._resolve_tags(new_names) if new_names else []
            instance.tags.set([*selected, *extra])
            
        if commit:
            with transaction.atomic():
                instance.save()
                _save_m2m()
        else:
            # Defer M2M until caller invokes form.save_m2m()
            self.save_m2m = _save_m2m  # type: ignore[attr-defined]
    
        return instance


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
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., sugar"}),
    )

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit_text", "prep_note", "line_order"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "unit_text": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., cup"}),
            "prep_note": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., finely chopped"}
            ),
            "line_order": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if "DELETE" in self.fields:
            self.fields["DELETE"].widget = forms.HiddenInput()

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
    
    def add_fields(self, form, index):
        super().add_fields(form, index)
        
        # can_delete=True adds this field at the formset level,
        # so we hide it here (not in the form __init__).
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = forms.HiddenInput()
            
    def clean(self):
        super().clean()
        
        if any(self.errors):
            return
        
        kept = [
            f
            for f in self.forms
            if hasattr(f, "cleaned_data")
            and f.cleaned_data
            and not f.cleaned_data.get("DELETE", False)
        ]
        if not kept:
            raise ValidationError("Please add at least one ingredient.")
        
    def save(self, commit: bool = True):
        instances = super().save(commit=False)
        
        kept_forms = [
            f
            for f in self.forms
            if hasattr(f, "cleaned_data")
            and f.cleaned_data
            and not f.cleaned_data.get("DELETE", False)
        ]
        
        # Auto line_order: 1..N in UI order
        for i, form in enumerate(kept_forms, start=1):
            form.instance.line_order = i
            
        norms: list[str] = []
        for form in kept_forms:
            raw = (form.cleaned_data.get("ingredient_name") or "").strip()
            norm = normalize_name(raw)

            if not norm:
                raise ValidationError("Ingredient name can't be blank.")

            form.cleaned_data["_ingredient_norm"] = norm  # stash for reuse below
            norms.append(norm)

        # De-dupe norms to keep queries small
        unique_norms = list(dict.fromkeys(norms))  # preserves order

        # 1) Fetch all existing Ingredients in one query
        existing = Ingredient.objects.filter(name_normalized__in=unique_norms)
        by_norm = {ing.name_normalized: ing for ing in existing}

        # 2) Bulk create missing (ignore_conflicts handles races)
        missing_norms = [n for n in unique_norms if n not in by_norm]
        if missing_norms:
            Ingredient.objects.bulk_create(
                [Ingredient(name=n.title(), name_normalized=n) for n in missing_norms],
                ignore_conflicts=True,
            )

            # 3) Re-fetch missing to obtain PKs (one query)
            created = Ingredient.objects.filter(name_normalized__in=missing_norms)
            by_norm.update({ing.name_normalized: ing for ing in created})

        # 4) Assign resolved Ingredient FK to each form instance
        for form in kept_forms:
            norm = form.cleaned_data["_ingredient_norm"]
            ingredient = by_norm.get(norm)
            if ingredient is None:
                raise ValidationError(f"Could not resolve ingredient: {norm}")
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
    extra=1,  # initial blank rows
    can_delete=True,  # allow removing ingredient lines
)
