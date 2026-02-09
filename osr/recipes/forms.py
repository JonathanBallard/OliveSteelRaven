# recipes/forms.py

from __future__ import annotations

from typing import Iterable, List

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction, models
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
    ingredient_name = forms.CharField(
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., sugar"}),
    )

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit_text", "prep_note"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "unit_text": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., cup"}),
            "prep_note": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., finely chopped"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # When editing existing lines, prefill ingredient_name from FK
        if self.instance and self.instance.pk and getattr(self.instance, "ingredient_id", None):
            self.fields["ingredient_name"].initial = self.instance.ingredient.name

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
    def _is_deleted(self, form) -> bool:
        return bool(getattr(form, "cleaned_data", {}).get("DELETE", False))

    def _is_empty(self, form) -> bool:
        """
        A form is 'empty' if it has no ingredient_name.
        quantity/unit/prep_note are optional and don't make a row 'real'.
        """
        cd = getattr(form, "cleaned_data", {}) or {}
        name = (cd.get("ingredient_name") or "").strip()
        return name == ""
    
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # can_delete=True adds this field at the formset level,
        # so we hide it here (not in the form __init__).
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = forms.HiddenInput()

        # ✅ CRITICAL: avoid pre-save validate_unique collisions while we reorder+delete
        # We enforce uniqueness via:
        # - our own deterministic 1..N renumbering
        # - the DB constraint
        # - the two-phase save (offset range -> final range)
        form._validate_unique = False
    
    def get_queryset(self):
        qs = super().get_queryset()
        # ✅ CRITICAL: ensure DOM order == DB line_order
        return qs.order_by("line_order", "pk")
    
    
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        kept = [
            f for f in self.forms
            if hasattr(f, "cleaned_data") and f.cleaned_data
            and not self._is_deleted(f)
            and not self._is_empty(f)
        ]

        if not kept:
            raise ValidationError("Please add at least one ingredient.")
    
    # IMPORTANT:
    # We enforce a UNIQUE constraint on (recipe_id, line_order).
    # When reordering ingredients, we must avoid transient duplicates
    # (e.g. two rows briefly having line_order=1).
    #
    # To do this safely, we renumber in TWO PHASES:
    #   1) Move all kept rows into a temporary, high offset range
    #      so no (recipe_id, line_order) collisions can occur.
    #   2) Assign the final sequential order (1..N).
    #
    # This guarantees deterministic ordering while respecting the DB constraint.
    def save(self, commit: bool = True):
        instances = super().save(commit=False)

        kept_forms = [
            f for f in self.forms
            if hasattr(f, "cleaned_data") and f.cleaned_data
            and not self._is_deleted(f)
            and not self._is_empty(f)
        ]

        kept_instances_all = [f.instance for f in kept_forms]  # new (pk None) + existing

        # Auto line_order: 1..N in UI order (in-memory for now)
        for i, form in enumerate(kept_forms, start=1):
            form.instance.line_order = i

        # --- ingredient normalization + FK resolution ---
        norms: list[str] = []
        for form in kept_forms:
            raw = (form.cleaned_data.get("ingredient_name") or "").strip()
            norm = normalize_name(raw)

            if not norm:
                raise ValidationError("Ingredient name can't be blank.")

            form.cleaned_data["_ingredient_norm"] = norm
            norms.append(norm)

        unique_norms = list(dict.fromkeys(norms))
        existing = Ingredient.objects.filter(name_normalized__in=unique_norms)
        by_norm = {ing.name_normalized: ing for ing in existing}

        missing_norms = [n for n in unique_norms if n not in by_norm]
        if missing_norms:
            Ingredient.objects.bulk_create(
                [Ingredient(name=n.title(), name_normalized=n) for n in missing_norms],
                ignore_conflicts=True,
            )
            created = Ingredient.objects.filter(name_normalized__in=missing_norms)
            by_norm.update({ing.name_normalized: ing for ing in created})

        for form in kept_forms:
            norm = form.cleaned_data["_ingredient_norm"]
            ingredient = by_norm.get(norm)
            if ingredient is None:
                raise ValidationError(f"Could not resolve ingredient: {norm}")
            form.instance.ingredient = ingredient
        # --- end logic ---

        if not commit:
            return instances

        with transaction.atomic():
            # 1) Save kept instances (new + existing)
            for inst in kept_instances_all:
                inst.save()

            # 2) Apply deletions explicitly
            for obj in getattr(self, "deleted_objects", []):
                obj.delete()

            # 3) Two-phase line_order write to avoid unique collisions:
            current_max = (
                RecipeIngredient.objects
                .filter(recipe=self.instance)
                .aggregate(m=models.Max("line_order"))["m"]
                or 0
            )
            offset = current_max + 1000

            # ✅ IMPORTANT: recompute after save so new rows (now with PKs) are included
            kept_instances = [f.instance for f in kept_forms if f.instance.pk]

            # Phase A: temporary range
            for idx, inst in enumerate(kept_instances, start=1):
                inst.line_order = offset + idx
                inst.save(update_fields=["line_order"])

            # Phase B: final 1..N
            for idx, inst in enumerate(kept_instances, start=1):
                inst.line_order = idx
                inst.save(update_fields=["line_order"])

            self.save_m2m()

        return kept_instances_all



RecipeIngredientFormSetCreate = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    form=RecipeIngredientLineForm,
    formset=BaseRecipeIngredientFormSet,
    extra=1,          # show 1 blank on CREATE
    can_delete=True,
)

RecipeIngredientFormSetUpdate = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    form=RecipeIngredientLineForm,
    formset=BaseRecipeIngredientFormSet,
    extra=0,          # show ONLY existing rows on UPDATE
    can_delete=True,
)