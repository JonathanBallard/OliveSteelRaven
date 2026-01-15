
from django.shortcuts import render
from django.http import HttpResponseRedirect

from common.utils import safe_method_validator

# Create your views here.

# *DONE* GET home
# GET login
# POST login
# GET signup
# POST signup
# GET logout

# *DONE* Check if user is logged in. If not, redirect to /login/
# *DONE* Otherwise open home.html page
@safe_method_validator("", ["GET", "HEAD", "OPTIONS"])
def get_home(request, *args, **kwargs):
    context = {}
    if(not request.user.is_authenticated):
        return HttpResponseRedirect('/login/')
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
# Tell Django user is authenticated
# Then Open Homepage
@safe_method_validator(".\\accounts\\login.html", ["POST", "HEAD", "OPTIONS"])
def post_login(request, *args, **kwargs):
    context = {}
    posted_data_dict = request.POST.copy()
    return HttpResponseRedirect('') # Assuming successful login, redirect user to homepage

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
# Bring user to login.html
@safe_method_validator(".\\accounts\\signup.html", ["POST", "HEAD", "OPTIONS"])
def post_signup(request, *args, **kwargs):
    context = {}
    posted_data_dict = request.POST.copy()
    return HttpResponseRedirect('') # Assuming successful signup, redirect user to home

#&-----------------------------------------------------------------------------------------------------
#^ START `LOGOUT` VIEWS
#&-----------------------------------------------------------------------------------------------------

# logout
@safe_method_validator(".\\accounts\\signup.html", ["GET", "HEAD", "OPTIONS"])
def get_logout(request, *args, **kwargs):
    context = {}
    return render(request=request, template_name=".\\accounts\\login.html", context=context)

