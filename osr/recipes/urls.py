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
    path('browse/', views.browse, name='browse'), # Display the browse page
    path('recipe/<str:recipe_id>/', views.recipe, name='view_recipe'), # Display the recipe details page
    path('create/', views.create, name='create_recipe'), # Display the create page
    path('update/', views.update, name='update_recipe'), # Display the update page
    path('delete/', views.delete, name='delete_recipe'), # Display the delete page
    path('search/', views.search, name='search'), # Display the search page
    path('search_results/', views.search_results, name='search_results'), # Display the search results page
    path('search/my_recipes/', views.my_recipes, name='my_recipes')
]
