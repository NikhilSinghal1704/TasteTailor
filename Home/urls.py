from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('search', views.search, name = "search"),
    path('recipeinfo/<id>', views.recipeinfo, name = "Recipe Info"),
    path('contact', views.contact, name = "contact"),
    path('meal-plan', views.meal_plan, name="meal_plan"),
    # AI Recipe generation
    path('ai/generate', views.generate_recipe, name="generate_recipe"),
    path('ai/my-recipes', views.my_generated_recipes, name="my_generated_recipes"),
    path('ai/recipe/<int:id>', views.generated_recipe_detail, name="generated_recipe_detail"),
]
