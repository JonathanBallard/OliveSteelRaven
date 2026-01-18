
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect

from accounts.forms import UserModelForm, UserLoginForm

from common.utils import safe_method_validator

# Create your views here.

# *DONE* GET home
# GET login
# POST login
# GET signup
# POST signup
# GET logout

logger = logging.getLogger(__name__)


@safe_method_validator("", ["GET", "HEAD", "OPTIONS"])
def get_root(request, *args, **kwargs):
    """
    Docstring for get_root
    
    :param request: HTTP Request
    
    If user logged in, redirects to homepage
    Else redirects to login
    """
    if(not request.user.is_authenticated):
        # return redirect('accounts:get_login_page')
        return redirect('accounts:login')
    else:
        return redirect('accounts:get_home_page')


# *DONE* Check if user is logged in. If not, redirect to /login/
# *DONE* Otherwise open home.html page
@safe_method_validator(".\\accounts\\home.html", ["GET", "HEAD", "OPTIONS"])
def get_home(request, *args, **kwargs):
    """
    Docstring for get_home
    
    :param request: HTTP Request
    
    Returns the homepage.
    """
    context = {}
    return render(request=request, template_name=".\\accounts\\home.html", context=context)

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGIN` VIEWS
#&-----------------------------------------------------------------------------------------------------

# *DONE* Open login.html page
# Not currently in use, using Django's default login view
@safe_method_validator(".\\accounts\\login.html", ["GET", "HEAD", "OPTIONS"])
def get_login(request, *args, **kwargs):
    """
    Docstring for get_login
    
    :param request: HTTP Request
    
    Returns the Login Page and Form
    """
    context = {}
    form = UserLoginForm
    context['form'] = UserLoginForm(request.GET)
    context['form_action'] = "login/submit"
    
    return render(request=request, template_name=".\\accounts\\login.html", context=context)

# POST Info
# Validate User Information
# *DONE* use django.contrib.auth.authenticate(username="Tax", password="secret") for authentication
# *DONE* Then Open Homepage
# Or if fails, use Django's `messages` framework to display
@csrf_protect
@safe_method_validator(".\\accounts\\login.html", ["POST", "HEAD", "OPTIONS"])
def post_login(request, *args, **kwargs):
    """
    Docstring for post_login
    
    :param request: HTTP Request

    Authenticates User and redirects to homepage upon success or displays failure message upon failure
    """
    context = {}
    posted_data_dict = request.POST.copy()
    
    form = UserLoginForm(request.POST)
    context['form'] = form
    user = authenticate(request, username=posted_data_dict['username'], password=posted_data_dict['password'])
    if user is not None:
        logger.debug("User Authenticated")
        messages.success(request, "User Logged In Succesfully")
        login(request, user)
        return redirect('accounts:get_home_page')
    else:
        logger.debug("User NOT Authenticated")
        messages.error(request, "User Login Failed")
        # handle invalid login
        # then redirect with message
        # return redirect('accounts:get_login_page')
        return redirect('accounts:login')


#&-----------------------------------------------------------------------------------------------------
#^ START `SIGNUP` VIEWS
#&-----------------------------------------------------------------------------------------------------

# *DONE* Open signup.html
@safe_method_validator(".\\accounts\\signup.html", ["GET", "HEAD", "OPTIONS"])
def get_signup(request, *args, **kwargs):
    """
    Docstring for get_signup
    
    :param request: HTTP Request
    
    Renders Signup Page and Form
    """
    context = {}
    form = UserModelForm(request.GET)
    # form = UserCreationForm(request.GET) # uses default Auth.User model
    context['form'] = form
    return render(request=request, template_name=".\\accounts\\signup.html", context=context)

# POST Info
# Validate User Information
# Use the User.objects.create_user() function to create new users``
# Authenticate the user
# Bring user to home.html
@csrf_protect
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def post_signup(request, *args, **kwargs):
    """
    Docstring for post_signup
    
    :param request: HTTP Request
    
    Creates new User and Redirects to Login on Success or Message on Failure
    """
    context = {}
    posted_data_dict = request.POST.copy()
    
    form = UserModelForm(request.POST)
    logger.debug("post signup")
    if form.is_valid():
        form.save()
        logger.debug("saved form")
        messages.success(request, "User Was Succesfully Created")
        # return redirect('accounts:get_login_page') # Assuming successful signup, redirect user to login
        return redirect('accounts:login') # Assuming successful signup, redirect user to login
    elif not form.is_valid:
        messages.error(request, "User Was Not Created")
        logger.debug("Attempted to save invalid form!!")
        form = UserModelForm()
    else:
        form = UserModelForm()
    context['form'] = form
    return redirect('accounts:get_signup_page')

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGOUT` VIEWS
#&-----------------------------------------------------------------------------------------------------

# logout
# Currently not in use, instead using Django's built-in logout view
@csrf_protect
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def post_logout(request, *args, **kwargs):
    """
    Docstring for post_logout
    
    :param request: HTTP Request
    
    Logs the user out. Currently not in use.
    """
    context = {}
    logout(request)
    messages.success(request, "User Was Logged Out")
    return redirect('accounts:login')
    # return redirect('accounts:get_login_page')

