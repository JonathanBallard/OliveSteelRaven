import logging

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.views.decorators.csrf import csrf_protect

from common.utils import safe_method_validator

# Create your views here.

# GET Browse
# GET Account
# GET Recipe
# GET Create
# POST Create
# GET Update
# POST Update
# GET Delete
# POST Delete
# GET Search
# POST Search
# GET Search Results

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
def recipe(request, *args, **kwargs):
    """
    Docstring for recipe
    
    :param request: HTTP Request
    
    GET: Renders the Recipe Details Page
    """
    context = {}
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
        return render(request=request, template_name=".\\recipes\\create.html", context=context)
    # POST create recipe page
    # If POST fails, redirect to create recipe page
    # Otherwise get newly created recipe ID, and redirect to that details page
    elif(request.method == "POST"):
        posted_data_dict = request.POST.copy()
        recipe_id = 0 # get from posted_data_dict, then pass for the redirect
        
        if recipe_id == 0:
            return redirect('recipes:get_create_page')
        return redirect('recipes:recipe', recipe_id=recipe_id) # Redirect to created recipe
    return render(request=request, template_name=".\\recipes\\create.html", context=context)




#&-----------------------------------------------------------------------------------------------------
#^ START `UPDATE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Render update.html
@csrf_protect
@safe_method_validator(".\\recipes\\update.html", ["POST", "GET", "HEAD", "OPTIONS"])
def update(request, *args, **kwargs):
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

