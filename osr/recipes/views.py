import logging

from django.db.models import Q, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_protect

from .models import Recipe, Category, Tag, RecipeIngredient, Ingredient
from .forms import RecipeForm, RecipeIngredientFormSetCreate, RecipeIngredientFormSetUpdate
from .utils import normalize_name

from common.utils import safe_method_validator

# Create your views here.

# Browse
# Account
# Recipe
# Create
# Update
# Delete
# Search
# Search Results


#&-----------------------------------------------------------------------------------------------------
#^ START `CATEGORIES` VIEWS
#&-----------------------------------------------------------------------------------------------------

@safe_method_validator(".\\recipes\\categories.html", ["GET", "HEAD", "OPTIONS"])
def categories(request, *args, **kwargs):
    """
    Docstring for categories
    
    :param request: HTTP Request
    
    GET: Renders the Browse Categories Template
    """
    context = {"categories": Category.objects.all().order_by("name")}
    return render(request=request, template_name=".\\recipes\\categories.html", context=context)


@safe_method_validator(".\\recipes\\categories.html", ["GET", "HEAD", "OPTIONS"])
def recipe_by_category(request, category_id, *args, **kwargs):
    """
    Docstring for recipe_by_category
    
    :param request: HTTP Request
    :param category_id: PK of the category that we're displaying the search results for
    
    GET: Renders the Browse Categories Template
    """
    qs = Recipe.objects.select_related("category")
    
    categories = Category.objects.all()  # ordered via Meta
    
    category_recipes = Recipe.objects.filter(category_id = category_id)
    category_name = Category.objects.get(pk=category_id).name
    filters = Q()
    
    selected_category = get_object_or_404(Category, pk=category_id)
    filters &= Q(category_id=selected_category.id) #type: ignore
    
    if category_id:
        recipes = (
            qs.filter(filters)
            .distinct()
            .order_by("title")
        )
        results_count = recipes.count()
    else:
        recipes = Recipe.objects.none()
        results_count = None
    context = {
        "categories": categories,
        "recipes": recipes,
        "selected_category": selected_category,
        "results_count": results_count,
    }
    return render(request, "recipes/search.html", context)

#&-----------------------------------------------------------------------------------------------------
#^ START `RECIPE` VIEWS
#&-----------------------------------------------------------------------------------------------------

@safe_method_validator(".\\recipes\\recipe.html", ["GET", "HEAD", "OPTIONS"])
def recipe(request, recipe_id, *args, **kwargs):
    """
    GET: Renders the Recipe Details Page
    """
    # Prefetch tags + ingredient lines (through model) in a bounded number of queries
    recipe_obj = get_object_or_404(
        Recipe.objects
        .select_related("category", "owner")
        .prefetch_related("tags")
        .prefetch_related(
            Prefetch(
                "recipeingredient_set",
                queryset=RecipeIngredient.objects
                    .select_related("ingredient")
                    .order_by("line_order"),
                to_attr="ingredient_lines",
            )
        ),
        pk=recipe_id,
    )
    
    context = {"recipe": recipe_obj}
    return render(
        request=request,
        template_name=".\\recipes\\recipe.html",
        context=context,
    )

#&-----------------------------------------------------------------------------------------------------
#^ START `CREATE` VIEWS
#&-----------------------------------------------------------------------------------------------------


@csrf_protect
@login_required
@safe_method_validator(".\\recipes\\create.html", ["POST", "GET", "HEAD", "OPTIONS"])
def create(request, *args, **kwargs):
    """
    Docstring for create
    
    :param request: HTTP Request
    
    GET: Renders the Create Recipe Form. 
    POST: Saves the Form
    """
    context = {}
    
    if(request.method == "GET"):
        form = RecipeForm()
        formset = RecipeIngredientFormSetCreate(prefix="ingredients")
        
        context = {
            "form": form,
            "formset": formset,
            "is_update": False,
        }
        return render(request=request, template_name=".\\recipes\\recipe_form.html", context=context)
    # POST create recipe page
    # If POST fails, redirect to create recipe page
    # Otherwise get newly created recipe ID, and redirect to that details page
    elif request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeIngredientFormSetCreate(request.POST, prefix="ingredients")
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                recipe = form.save(commit=False)
                recipe.owner = request.user
                recipe.save()
                
                # Save M2M (tags)
                form.instance = recipe
                form.save_m2m()
                
                # Attach recipe to ingredient formset and save
                formset.instance = recipe
                formset.save()
                
            return redirect("recipes:view_recipe", recipe_id=recipe.pk)
        
        # INVALID — re-render template with bound forms (NO redirect)
        messages.error(request, "Please fix the errors below.")
        
        context = {
            "form": form,
            "formset": formset,
        }
        return render(
            request=request,
            template_name=".\\recipes\\recipe_form.html",
            context=context,
            status=400,
        )
        
    return render(request=request, template_name=".\\recipes\\recipe_form.html", context=context)




#&-----------------------------------------------------------------------------------------------------
#^ START `UPDATE` VIEWS
#&-----------------------------------------------------------------------------------------------------
@csrf_protect
@login_required
@safe_method_validator(".\\recipes\\update.html", ["POST", "GET", "HEAD", "OPTIONS"])
def update(request, recipe_id=0, *args, **kwargs):
    """
    :param request: HTTP Request
    :param recipe_id: PK of the recipe we're updating

    GET: Renders the Update Recipe Form Template (pre-populated)
    POST: Updates the Recipe Form (including image uploads)
    """
    # Always enforce ownership (both GET + POST)
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    # If not owner and not staff or superuser, 404 on update
    if (not recipe.owner == request.user and not request.user.is_staff and not request.user.is_superuser):
        recipe = get_object_or_404(Recipe, pk=recipe_id, owner=request.user)

    if request.method == "GET":
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSetUpdate(instance=recipe, prefix="ingredients")

        context = {
            "recipe": recipe,
            "form": form,
            "formset": formset,
            "is_update": True,
        }
        return render(
            request=request,
            template_name=".\\recipes\\recipe_form.html",
            context=context,
        )

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = RecipeIngredientFormSetUpdate(
            request.POST,
            instance=recipe,
            prefix="ingredients",
        )

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    updated_recipe = form.save()   # Recipe fields
                    #form.save_m2m()                # tags M2M, handled inside recipes.forms.py
                    formset.save()                 # ingredient lines + deletions + renumbering
            except IntegrityError:
                # Usually means a DB constraint hit (e.g., unique(recipe, line_order))
                messages.error(
                    request,
                    "Couldn’t save ingredient changes due to an ordering conflict. "
                    "Please refresh the page and try again."
                )

                context = {
                    "recipe": recipe,
                    "form": form,
                    "formset": formset,
                    "is_update": True,
                }
                return render(
                    request=request,
                    template_name=".\\recipes\\recipe_form.html",
                    context=context,
                    status=400,
                )

            return redirect("recipes:view_recipe", recipe_id=updated_recipe.pk)

        # INVALID — re-render template with bound forms (NO redirect)
        messages.error(request, "Please fix the errors below.")

        context = {
            "recipe": recipe,
            "form": form,
            "formset": formset,
            "is_update": True,
        }
        return render(
            request=request,
            template_name=".\\recipes\\recipe_form.html",
            context=context,
            status=400,
        )

    # Just in case safe_method_validator fails or is later removed
    return HttpResponseNotAllowed(["GET", "POST"])




#&-----------------------------------------------------------------------------------------------------
#^ START `DELETE` VIEWS
#&-----------------------------------------------------------------------------------------------------


@csrf_protect
@login_required
@safe_method_validator(".\\recipes\\delete.html", ["POST", "GET", "HEAD", "OPTIONS"])
def delete(request, recipe_id, *args, **kwargs):
    """
    Docstring for delete
    
    :param request: HTTP Request
    :param recipe_id: PK of the recipe we're deleting
    
    GET: Renders the Deletion Confirmation Template
    POST: Deletes Recipe
    """
    context = {}
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if(request.method == "GET"):
        return redirect('recipes:my_recipes')
    
    # POST delete
    # Ensure recipe deleted
    # Then redirect to my recipes
    elif(request.method == "POST"):
        if(request.user.is_authenticated and recipe.owner == request.user):
            recipe.delete()
        elif(request.session.get("admin_mode", False) and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            recipe.delete()
        else:
            messages.error(request, "You do not have permission to delete this recipe.")
        posted_data_dict = request.POST.copy()
        return redirect('recipes:my_recipes') # Return to my recipes
    return redirect('recipes:my_recipes')



#&-----------------------------------------------------------------------------------------------------
#^ START `SEARCH` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open search.html
@csrf_protect
@login_required
@safe_method_validator(".\\recipes\\search.html", ["POST", "GET", "HEAD", "OPTIONS"])
def search(request, *args, **kwargs):
    """
    Docstring for search
    
    :param request: HTTP Request
    
    GET: Renders the Search Form Template
    POST: Searches for matching recipes
    """
    
    # --- Search guardrails ---
    MIN_Q_LEN = settings.MIN_Q_LEN
    MAX_Q_LEN = settings.MAX_Q_LEN
    
    if not(MIN_Q_LEN):
        MIN_Q_LEN = 2
    if not(MAX_Q_LEN):
        MAX_Q_LEN = 64
    
    q_raw = (request.GET.get("q") or "").strip()
    q_raw = q_raw[:MAX_Q_LEN]
    
    # Ignore ultra-short queries (e.g. "a") to avoid noisy/expensive searches
    if len(q_raw) < MIN_Q_LEN:
        q_raw = ""
    
    q_norm = normalize_name(q_raw) if q_raw else ""
    category_id = (request.GET.get("category_id") or "").strip()

    categories = Category.objects.all()  # ordered via Meta
    selected_category = None

    # Base queryset: ALL recipes
    qs = (
        Recipe.objects
        .select_related("category")
        .prefetch_related("tags", "ingredients")
    )

    filters = Q()

    # Category filter
    if category_id:
        selected_category = get_object_or_404(Category, pk=category_id)
        filters &= Q(category_id=selected_category.id) #type: ignore

    # Title OR ingredient search
    if q_raw:
        filters &= (
            Q(title__icontains=q_raw)
            | Q(ingredients__name_normalized__icontains=q_norm)
            | Q(ingredients__name__icontains=q_raw)
            | Q(tags__name__icontains=q_raw)
        )

    # Only hit the DB when at least one filter is provided
    if q_raw or category_id:
        recipes = (
            qs.filter(filters)
            .distinct()
            .order_by("title")
        )
        results_count = recipes.count()
    else:
        recipes = Recipe.objects.none()
        results_count = None

    context = {
        "categories": categories,
        "recipes": recipes,
        "query": q_raw or None,
        "selected_category": selected_category,
        "results_count": results_count,
    }
    return render(request, "recipes/search.html", context)



@safe_method_validator(".\\recipes\\search_results.html", ["GET", "HEAD", "OPTIONS"])
def search_results(request, *args, **kwargs):
    """
    Docstring for search_results
    
    :param request: HTTP Request
    
    GET: Renders the search results
    """
    context = {}
    return render(request=request, template_name=".\\recipes\\search_results.html", context=context)


@csrf_protect
@login_required
@safe_method_validator(".\\recipes\\search_results.html", ["GET", "POST", "HEAD", "OPTIONS"])
def my_recipes(request, *args, **kwargs):
    """
    Docstring for my_recipes
    
    :param request: HTTP Request
    
    GET: Renders Logged-in User's Recipes
    POST: Searches for Logged-in User's Recipes
    """
    posted_data_dict = request.POST.copy()
    context = {}
    if(not request.user.is_authenticated):
        return redirect('account_login')
    else:
        my_recipes = Recipe.objects.filter(owner=request.user.pk)
        context['recipes'] = my_recipes
        results_count = my_recipes.count()
        categories = Category.objects.all()  # ordered via Meta
        context = {
            "categories": categories,
            "recipes": my_recipes,
            "query": None,
            "selected_category": None,
            "results_count": results_count,
        }
    return render(request=request, template_name=".\\recipes\\search.html", context=context)


