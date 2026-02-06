"""
URL configuration for accounts app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse, reverse_lazy
from django.contrib.auth import views as auth_views

# Import views from my apps
from accounts import views

app_name = 'accounts'

urlpatterns = [
    
    # My Auth URLS
    # path('signup/', views.signup, name='signup'), # Display the sign-up page
    # path('login/', views.login_redirect, name='login'), # Currently using 'login_redirect' view to redirect all currently logged-in users to their account page if they go to the url: login/
    # path('login_form/', views.my_login, name='login'), # Display my log-in page
    # path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('accounts:home_page')), name="logout"), # Django's Default Logout View
    
    # Out of date URLS
    # path('login_form/', auth_views.LoginView.as_view(template_name='accounts/login.html', next_page=reverse_lazy('accounts:home_page')), name='login'), # Django's Default Login View
    # path('login/', views.my_login, name='login'), # Display my log-in page
    # path('logout/', views.my_logout, name='logout'), # POST my logout
    
    path('', views.root, name='root_page'), # Display the log-in page unless a user is logged in, in which case it shows the homepage
    path('home/', views.home, name='home_page'), # Display the homepage
    path('homepage/', views.home, name='home'), # Display the homepage
    path('tos/', views.tos, name='tos'), # Display the ToS
    path('privacy/', views.privacy, name='privacy'), # Display the Privacy Policy
    path('account/', views.account, name='account'), #type: ignore
    path('account/edit_details', views.edit_account, name='edit_account'), #type: ignore
    path('account/change_password', views.change_password, name='change_password'), #type: ignore
    path('account/reset_password', views.reset_password, name='reset_password'), #type: ignore
]
