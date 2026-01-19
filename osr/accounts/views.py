
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect

from accounts.forms import UserModelForm, UserLoginForm, UserUpdateForm

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
def root(request, *args, **kwargs):
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
        return redirect('accounts:home_page')


# *DONE* Check if user is logged in. If not, redirect to /login/
# *DONE* Otherwise open home.html page
@safe_method_validator(".\\accounts\\home.html", ["GET", "HEAD", "OPTIONS"])
def home(request, *args, **kwargs):
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
# If we revert to this, it doesn't currently work, and requires renaming to 'login' not 'my_login'
@csrf_protect
@safe_method_validator(".\\accounts\\login.html", ["GET", "POST", "HEAD", "OPTIONS"])
def my_login(request, *args, **kwargs):
    """
    Docstring for login
    
    :param request: HTTP Request
    
    Returns the Login Page and Form
    """
    context = {}
    
    if(request.method == 'GET'):
        form = UserLoginForm
        context['form'] = UserLoginForm(request.GET)
        context['form_action'] = "login/submit"
    elif(request.method == "POST"):
        logger.debug("POST login")
        context = {}
        posted_data_dict = request.POST.copy()
        
        form = UserLoginForm(request.POST)
        context['form'] = form
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password1'))
        logger.debug("AUTHENTICATION attempted")
        if user is not None:
            logger.debug("User Authenticated")
            messages.success(request, "User Logged In Succesfully")
            login(request, user)
            return redirect('accounts:home_page')
        else:
            logger.debug("User NOT Authenticated")
            messages.error(request, "User Login Failed")
            # handle invalid login
            # then redirect with message
            # return redirect('accounts:get_login_page')
            return redirect('accounts:login')
    
    return render(request=request, template_name=".\\accounts\\login.html", context=context)

#&-----------------------------------------------------------------------------------------------------
#^ START `SIGNUP` VIEWS
#&-----------------------------------------------------------------------------------------------------

# *DONE* Open signup.html
@csrf_protect
@safe_method_validator(".\\accounts\\signup.html", ["GET", "POST", "HEAD", "OPTIONS"])
def signup(request, *args, **kwargs):
    """
    Docstring for signup
    
    :param request: HTTP Request
    
    Renders Signup Page and Form
    """
    context = {}
    if(request.method == 'GET'):
        form = UserModelForm(request.GET)
        # form = UserCreationForm(request.GET) # uses default Auth.User model
        context['form'] = form
        return render(request=request, template_name=".\\accounts\\signup.html", context=context)
    elif(request.method == "POST"):
        posted_data_dict = request.POST.copy()
        
        form = UserModelForm(request.POST)
        User = get_user_model()
        
        logger.debug("Received Signup POST")
        if form.is_valid():
            logger.debug("Form Valid")
            user = User.objects.create_user(first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'), username=request.POST.get('username'), email=request.POST.get('email'), password=request.POST.get('password1'))
            
            user.save()
            messages.success(request, "User Was Succesfully Created")
            # return redirect('accounts:get_login_page') # Assuming successful signup, redirect user to login
            return redirect('accounts:login') # Assuming successful signup, redirect user to login
        elif not form.is_valid:
            messages.error(request, "User Was Not Created")
            form = UserModelForm()
        else:
            messages.error(request, "User Was Not Created: Other Error")
            form = UserModelForm()
        context['form'] = form
        return redirect('accounts:get_signup')
    else:
        return render(request=request, template_name=".\\accounts\\signup.html", context=context)

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGOUT` VIEWS
#&-----------------------------------------------------------------------------------------------------

# logout
# Currently not in use, instead using Django's built-in logout view
@csrf_protect
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def my_logout(request, *args, **kwargs):
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

#&-----------------------------------------------------------------------------------------------------
#^ START `ACCOUNTS` VIEWS
#&-----------------------------------------------------------------------------------------------------

@csrf_protect
@safe_method_validator(".\\accounts\\signup.html", ["GET", "POST", "HEAD", "OPTIONS"])
def account(request, *args, **kwargs):
    """
    Docstring for account
    
    :param request: HTTP Request
    
    Renders account page and allows user to change some basic information
    """
    context = {}
    user = request.user
    
    
    if(not user.is_authenticated):
        return redirect('accounts:login')
    
    if(request.method == "GET"):
        form = UserUpdateForm(instance=request.user)
        # add all appropriate user info to context (to avoid passing hashed passwords)
        context['user'] = user
        context['form'] = form
        return render(request=request, template_name=".\\accounts\\account.html", context=context)
    elif(request.method == "POST"):
        form = UserUpdateForm(request.POST, instance=request.user)
        context['form'] = form
        if(form.is_valid):
            messages.success(request, "User Account Information Updated!")
            form.save()
        else:
            messages.error(request, "Updating User Account Failed")
        return redirect('accounts:account')