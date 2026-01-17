
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from common.utils import safe_method_validator

# Create your views here.

# *DONE* GET home
# GET login
# POST login
# GET signup
# POST signup
# GET logout


@safe_method_validator("", ["GET", "HEAD", "OPTIONS"])
def get_root(request, *args, **kwargs):
    if(not request.user.is_authenticated):
        return redirect('accounts:get_login_page')
    else:
        return redirect('accounts:get_home_page')


# *DONE* Check if user is logged in. If not, redirect to /login/
# *DONE* Otherwise open home.html page
@safe_method_validator(".\\accounts\\home.html", ["GET", "HEAD", "OPTIONS"])
def get_home(request, *args, **kwargs):
    context = {}
    if(not request.user.is_authenticated):
        return redirect('accounts:get_login_page')
    else:
        return render(request=request, template_name=".\\accounts\\home.html", context=context)

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGIN` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open login.html page
@safe_method_validator(".\\accounts\\login.html", ["GET", "HEAD", "OPTIONS"])
def get_login(request, *args, **kwargs):
    context = {}
    return render(request=request, template_name=".\\accounts\\login.html", context=context)

# POST Info
# Validate User Information
# use django.contrib.auth.authenticate(username="Tax", password="secret") for authentication
# Tell Django user is authenticated
# Then Open Homepage
@safe_method_validator(".\\accounts\\login.html", ["POST", "HEAD", "OPTIONS"])
def post_login(request, *args, **kwargs):
    context = {}
    posted_data_dict = request.POST.copy()
    
    user = authenticate(request, username=posted_data_dict['username'], password=posted_data_dict['password'])
    if user is not None:
        login(request, user)
        return redirect('accounts:get_home_page')
    else:
        # handle invalid login
        # then redirect
        return redirect('accounts:get_login_page')

#&-----------------------------------------------------------------------------------------------------
#^ START `SIGNUP` VIEWS
#&-----------------------------------------------------------------------------------------------------

# Open signup.html
@safe_method_validator(".\\accounts\\signup.html", ["GET", "HEAD", "OPTIONS"])
def get_signup(request, *args, **kwargs):
    context = {}
    return render(request=request, template_name=".\\accounts\\signup.html", context=context)

# POST Info
# Validate User Information
# Use the User.objects.create_user() function to create new users``
# Authenticate the user
# Bring user to home.html
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def post_signup(request, *args, **kwargs):
    context = {}
    posted_data_dict = request.POST.copy()
    
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('accounts:get_login_page') # Assuming successful signup, redirect user to login
    else:
        form = UserCreationForm()
    return redirect('accounts:get_signup_page', {'form': form})

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGOUT` VIEWS
#&-----------------------------------------------------------------------------------------------------

# logout
# Currently not in use, instead using Django's built-in logout view
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def post_logout(request, *args, **kwargs):
    context = {}
    logout(request)
    return redirect('accounts:get_login_page')

