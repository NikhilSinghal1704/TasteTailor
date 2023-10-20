from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('search', views.search, name = "search"),
    path('recipeinfo/<id>', views.recipeinfo, name = "Recipe Info"),
]
