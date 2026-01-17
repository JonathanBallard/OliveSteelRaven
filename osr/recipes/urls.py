"""
URL configuration for recipes app.

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
from django.urls import path, include

# Import views from my apps
from recipes import views

app_name = 'recipes'

urlpatterns = [
    path('browse/', views.get_browse, name='get_browse_page'), # Display the browse page
    path('account/', views.get_account, name='get_account_page'), # Display the account page
    path('recipe/<str:recipe_id>/', views.get_recipe, name='get_recipe_page'), # Display the recipe details page
    path('create/', views.get_create, name='get_create_page'), # Display the create page
    path('create/submit', views.post_create, name='post_create'), # POST create
    path('update/', views.get_update, name='get_update_page'), # Display the update page
    path('update/submit', views.post_update, name='post_update'), # POST update
    path('delete/', views.get_delete, name='get_delete_page'), # Display the delete page
    path('delete/submit', views.post_delete, name='post_delete'), # POST delete
    path('search/', views.get_search, name='get_search_page'), # Display the search page
    path('search/submit', views.post_search, name='post_search'), # POST search
    path('search_results/', views.get_search_results, name='get_search_results_page'), # Display the search results page
    path('search/my_recipes/', views.get_my_recipes, name='get_my_recipes_page')
]
