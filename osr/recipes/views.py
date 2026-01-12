from django.shortcuts import render
from django.http import HttpResponseRedirect

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
def get_browse(request, _context):
    return render(request=request, template_name=".\\recipes\\browse.html", context=_context)

# Open account.html
@safe_method_validator(".\\recipes\\account.html", ["GET", "HEAD", "OPTIONS"])
def get_account(request, _context):
    return render(request=request, template_name=".\\recipes\\account.html", context=_context)

# Open recipe.html
@safe_method_validator(".\\recipes\\recipe.html", ["GET", "HEAD", "OPTIONS"])
def get_recipe(request, _context):
    return render(request=request, template_name=".\\recipes\\recipe.html", context=_context)

#&-----------------------------------------------------------------------------------------------------
#^ START `CREATE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open create.html
@safe_method_validator(".\\recipes\\create.html", ["GET", "HEAD", "OPTIONS"])
def get_create(request, _context):
    return render(request=request, template_name=".\\recipes\\create.html", context=_context)

# POST create recipe page
# If POST fails, redirect to create recipe page
# Otherwise get newly created recipe ID, and redirect to that details page
@safe_method_validator(".\\recipes\\create.html", ["POST", "HEAD", "OPTIONS"])
def post_create(request, _context):
    posted_data_dict = request.POST.copy()
    recipe_id = 0 # get from posted_data_dict, then pass for the redirect
    
    if recipe_id == 0:
        return HttpResponseRedirect('/create/')
    return HttpResponseRedirect('/recipe/' + str(recipe_id) + '/') # Redirect to created recipe

#&-----------------------------------------------------------------------------------------------------
#^ START `UPDATE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Show update.html
@safe_method_validator(".\\recipes\\update.html", ["GET", "HEAD", "OPTIONS"])
def get_update(request, _context):
    return render(request=request, template_name=".\\recipes\\update.html", context=_context)

# POST updated recipe
# if POST fails, redirect to update recipe page
# Otherwise redirect to updated recipe details pages
@safe_method_validator(".\\recipes\\update.html", ["POST", "HEAD", "OPTIONS"])
def post_update(request, _context):
    posted_data_dict = request.POST.copy()
    recipe_id = 0 # get from posted_data_dict, then pass for the redirect
    
    if recipe_id == 0:
        return HttpResponseRedirect('/update/')
    return HttpResponseRedirect('/recipe/' + str(recipe_id) + '/') # Redirect to updated recipe

#&-----------------------------------------------------------------------------------------------------
#^ START `DELETE` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open delete.html
@safe_method_validator(".\\recipes\\delete.html", ["GET", "HEAD", "OPTIONS"])
def get_delete(request, _context):
    return render(request=request, template_name=".\\recipes\\delete.html", context=_context)

# POST delete
# Ensure recipe deleted
# Then redirect to my recipes
@safe_method_validator(".\\recipes\\delete.html", ["POST", "HEAD", "OPTIONS"])
def post_delete(request, _context):
    posted_data_dict = request.POST.copy()
    return HttpResponseRedirect('/account/my_recipes') # Return to my recipes

#&-----------------------------------------------------------------------------------------------------
#^ START `SEARCH` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open search.html
@safe_method_validator(".\\recipes\\search.html", ["GET", "HEAD", "OPTIONS"])
def get_search(request, _context):
    return render(request=request, template_name=".\\recipes\\search.html", context=_context)

# POST search
# Return search_results
@safe_method_validator(".\\recipes\\search.html", ["POST", "HEAD", "OPTIONS"])
def post_search(request, _context):
    posted_data_dict = request.POST.copy()
    return get_search_results(request, _context) #Get search results with passed context

# Open search_results.html
@safe_method_validator(".\\recipes\\search_results.html", ["GET", "HEAD", "OPTIONS"])
def get_search_results(request, _context):
    return render(request=request, template_name=".\\recipes\\search_results.html", context=_context)

