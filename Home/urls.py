from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('search', views.search, name = "search"),
    path('recipeinfo/<id>', views.recipeinfo, name = "Recipe Info"),
    path('contact', views.contact, name = "contact"),
    path('meal-plan', views.meal_plan, name="meal_plan"),
    # Pantry and ingredient search
    path('pantry', views.pantry, name='pantry'),
    path('pantry/add', views.pantry_add, name='pantry_add'),
    path('pantry/remove/<int:item_id>', views.pantry_remove, name='pantry_remove'),
    path('api/ingredients/autocomplete', views.api_ingredient_autocomplete, name='ingredient_autocomplete'),
    path('search-by-ingredients', views.search_by_ingredients, name='search_by_ingredients'),
    # AI Recipe generation
    path('ai/generate', views.generate_recipe, name="generate_recipe"),
    path('ai/my-recipes', views.my_generated_recipes, name="my_generated_recipes"),
    path('ai/recipe/<int:id>', views.generated_recipe_detail, name="generated_recipe_detail"),
]
