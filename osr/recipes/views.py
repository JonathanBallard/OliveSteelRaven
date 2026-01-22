import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import csrf_protect

from .models import Recipe
from .forms import RecipeForm, RecipeIngredientFormSet

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

# Open browse.html
@safe_method_validator(".\\recipes\\browse.html", ["GET", "HEAD", "OPTIONS"])
def browse(request, *args, **kwargs):
    """
    Docstring for browse
    
    :param request: HTTP Request
    
    GET: Renders the Browse Categories Template
    """
    context = {}
    return render(request=request, template_name=".\\recipes\\browse.html", context=context)

# Render recipe.html
@safe_method_validator(".\\recipes\\recipe.html", ["GET", "HEAD", "OPTIONS"])
def recipe(request, recipe_id, *args, **kwargs):
    """
    Docstring for recipe
    
    :param request: HTTP Request
    
    GET: Renders the Recipe Details Page
    """
    context = {}
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request=request, template_name=".\\recipes\\recipe.html", context=context)

#&-----------------------------------------------------------------------------------------------------
#^ START `CREATE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Render create.html
@csrf_protect
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
        formset = RecipeIngredientFormSet(prefix="ingredients")

        context = {
            "form": form,
            "formset": formset,
        }
        return render(request=request, template_name=".\\recipes\\recipe_form.html", context=context)
    # POST create recipe page
    # If POST fails, redirect to create recipe page
    # Otherwise get newly created recipe ID, and redirect to that details page
    elif(request.method == "POST"):
        form = RecipeForm(request.POST)
        formset = RecipeIngredientFormSet(request.POST, prefix="ingredients")
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                recipe = form.save(commit=False)
                recipe.owner = request.user
                recipe.save()
                
                # Save M2M (tags) after recipe exists
                form.save_m2m()
                
                # Attach recipe to formset and save ingredient lines
                formset.instance = recipe
                formset.save()
        return redirect('recipes:recipe', pk=recipe.pk) # Redirect to created recipe
    return render(request=request, template_name=".\\recipes\\recipe_form.html", context=context)




#&-----------------------------------------------------------------------------------------------------
#^ START `UPDATE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Render update.html
@csrf_protect
@safe_method_validator(".\\recipes\\update.html", ["POST", "GET", "HEAD", "OPTIONS"])
def update(request, recipe_id=0, *args, **kwargs):
    """
    Docstring for update
    
    :param request: HTTP Request
    
    GET: Renders the Update Recipe Form Template
    POST: Updates the Recipe Form
    """
    context = {}
    if(request.method == "GET"):
        return render(request=request, template_name=".\\recipes\\update.html", context=context)
    
    # POST updated recipe
    # if POST fails, redirect to update recipe page
    # Otherwise redirect to updated recipe details pages
    elif(request.method == "POST"):
        recipe = get_object_or_404(Recipe, pk=recipe_id, owner=request.user)
        
        posted_data_dict = request.POST.copy()
        recipe_id = 0 # get from posted_data_dict, then pass for the redirect
        
        if recipe_id == 0:
            return redirect('recipes:update')
        return redirect('recipes:recipe', recipe_id=recipe_id) # Redirect to updated recipe
    return render(request=request, template_name=".\\recipes\\update.html", context=context)


#&-----------------------------------------------------------------------------------------------------
#^ START `DELETE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Render delete.html
@csrf_protect
@safe_method_validator(".\\recipes\\delete.html", ["POST", "GET", "HEAD", "OPTIONS"])
def delete(request, *args, **kwargs):
    """
    Docstring for delete
    
    :param request: HTTP Request
    
    GET: Renders the Deletion Confirmation Template
    POST: Deletes Recipe
    """
    context = {}
    if(request.method == "GET"):
        return render(request=request, template_name=".\\recipes\\delete.html", context=context)
    
    # POST delete
    # Ensure recipe deleted
    # Then redirect to my recipes
    elif(request.method == "POST"):
        posted_data_dict = request.POST.copy()
        return redirect('recipes:my_recipes') # Return to my recipes
    return render(request=request, template_name=".\\recipes\\delete.html", context=context)



#&-----------------------------------------------------------------------------------------------------
#^ START `SEARCH` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open search.html
@csrf_protect
@safe_method_validator(".\\recipes\\search.html", ["POST", "GET", "HEAD", "OPTIONS"])
def search(request, *args, **kwargs):
    """
    Docstring for search
    
    :param request: HTTP Request
    
    GET: Renders the Search Form Template
    POST: Searches for matching recipes
    """
    context = {}
    if(request.method == "GET"):
        return render(request=request, template_name=".\\recipes\\search.html", context=context)
    
    # POST search
    # Return search_results
    elif(request.method == "POST"):
        posted_data_dict = request.POST.copy()
        return search_results(request, context) #Get search results with passed context
    
    return render(request=request, template_name=".\\recipes\\search.html", context=context)


# Render search_results.html
@safe_method_validator(".\\recipes\\search_results.html", ["GET", "HEAD", "OPTIONS"])
def search_results(request, *args, **kwargs):
    """
    Docstring for search_results
    
    :param request: HTTP Request
    
    GET: Renders the search results
    """
    context = {}
    return render(request=request, template_name=".\\recipes\\search_results.html", context=context)

# Open my recipes
# Return search results for authenticated user
@csrf_protect
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
    return render(request=request, template_name=".\\recipes\\search_results.html", context=context)

