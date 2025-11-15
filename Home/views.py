from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from API.recipe_tag import *
from API.jsontest import json_to_txt
import json
import threading
from datetime import date
from API.meal_planner import generate_day_plan
from Auth.models import UserPreferences
from .models import MealPlan, Meal, GeneratedRecipe, Contact
from API.ai_recipe import get_gemini_recipe


def home(request):
    # Create a dictionary to store the results
    var = {"top": None, 'what': "/static/img/bhaisab.png",}

    # Define a function to fetch recipes and store them in the var dictionary
    def fetch_and_store_recipes(tag, key):
        recipes = get_recipe_by_tags(tag).content.decode()
        var[key] = json.loads(recipes)

    # function for fetching top recipes
    def top():
        var["top"] = json.loads(get_top_recipe().content.decode())

    # Create threads for each function call
    threads = [
        threading.Thread(
            target=fetch_and_store_recipes, args=("appetizer", "starters")
        ),
        threading.Thread(
            target=fetch_and_store_recipes, args=("main course", "lunches")
        ),
        threading.Thread(
            target=fetch_and_store_recipes, args=("dessert", "dinners")
        ),
        threading.Thread(target=top),
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return render(request, "index.html", var)


def search(request):
    var = {'what': "/static/img/bhaisab.png",}
    

    query = None  # Initialize query outside of the POST block

    if request.method == "POST":
        query = request.POST["q"]
        Diet = request.POST.get('Diet')
        intolerances = request.POST.getlist('intolerances')
        Type = request.POST.get('Type')
        sort = request.POST.get('sort')
        var["query"] = query
        var["Diet"] = Diet
        var["intolerances"] = intolerances
        var["Type"] = Type
        var["sort"] = sort
        
        ex = {}
        
        if Diet != "":
            ex["diet"] = Diet
        if Type != "":
            ex["type"] = Type
        if sort != "":
            ex["sort"] = sort
        if intolerances != "":
            ex["intolerances"] = ",".join(intolerances)

        #print(ex)
        
        var["results"] = json.loads(get_recipe_by_query(query, ex).content.decode())
        
        return render(request, "result.html", var)

    return render(request, "result.html", var)

def recipeinfo(request, id):
    
    var = {
            'what': "/static/img/bhaisab.png",
            'breadcrumb_items': [
                {'url': '/', 'label': 'Home'},
                {'url': '/result/', 'label': 'Recipes'},
                {'label': 'Recipe Details'}
            ]
        }
    
    # Define a function to fetch recipe data
    def get_recipe_data():
        recipe_data = get_recipe_details(id)
        var['recipe_info'] = recipe_data['recipe_info']
        var['ingredients'] = recipe_data['ingredients']

    # Define a function to fetch instructions
    def get_recipe_instructions():
        Instructions = get_instructions(id)
        var["Instructions"] = Instructions

    # Define a function to fetch similar recipes
    def get_similar_recipes_data():
        similar = get_similar_recipes(id)
        var["similar"] = similar
    
    threads = [
        threading.Thread(
            target=get_recipe_data
        ),
        threading.Thread(
            target=get_recipe_instructions
        ),
        threading.Thread(
            target=get_similar_recipes_data
        ),
    ]
    
    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    if var['recipe_info']:

        return render(request, 'recipeinfo.html', var)

    # Handle the case where data retrieval failed, e.g., by displaying an error message
    error_message = "Recipe data could not be retrieved."
    var = {'error_message': error_message}
        
    return render(request, 'recipeinfo.html', var)


@login_required(login_url='/authentication/signin')
def meal_plan(request):
    """Generate a 3-meal day plan from user preferences and render it."""
    # Ensure preferences exist and completed
    try:
        prefs = UserPreferences.objects.get(user=request.user)
    except UserPreferences.DoesNotExist:
        return redirect('preferences')

    if not prefs.preferences_completed:
        return redirect('preferences')

    target_date = date.today()

    # Generate via Spoonacular
    try:
        plan_data = generate_day_plan(prefs, target_date)
    except Exception as e:
        messages.error(request, f"Failed to generate meal plan: {e}")
        return redirect('/')

    # Persist MealPlan and Meals (upsert for the date)
    mealplan, _created = MealPlan.objects.update_or_create(
        user=request.user,
        date=target_date,
        timeframe='day',
        defaults={
            'calories': plan_data.get('nutrients', {}).get('calories'),
            'protein': plan_data.get('nutrients', {}).get('protein'),
            'fat': plan_data.get('nutrients', {}).get('fat'),
            'carbohydrates': plan_data.get('nutrients', {}).get('carbohydrates'),
            'source_payload': plan_data.get('raw'),
        }
    )

    # Replace existing meals for the plan
    mealplan.meals.all().delete()
    for m in plan_data["meals"]:
        Meal.objects.create(
            plan=mealplan,
            spoonacular_id=m.get('id'),
            title=m.get('title'),
            image_url=m.get('image_url'),
            source_url=m.get('sourceUrl'),
            meal_type=m.get('meal_type', 'lunch'),
            ready_in_minutes=m.get('readyInMinutes'),
            servings=m.get('servings'),
        )

    context = {
        'plan': mealplan,
        'meals': mealplan.meals.all(),
        'nutrients': {
            'calories': mealplan.calories,
            'protein': mealplan.protein,
            'fat': mealplan.fat,
            'carbohydrates': mealplan.carbohydrates,
        },
        'what': "/static/img/bhaisab.png",
    }

    return render(request, 'meal_plan.html', context)


@login_required(login_url='/authentication/signin')
def generate_recipe(request):
    """Form to collect a user's idea and generate an AI recipe with Gemini."""
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        if not prompt:
            messages.error(request, 'Please describe what you want to cook.')
            return render(request, 'generate_recipe.html', { 'what': "/static/img/bhaisab.png" })

        # Get preferences for diet/allergies; require completion for best results but allow fallback.
        prefs = None
        try:
            prefs = UserPreferences.objects.get(user=request.user)
        except UserPreferences.DoesNotExist:
            messages.info(request, 'Preferences not set yet — generating with defaults. Consider completing your preferences for better results.')

        try:
            result = get_gemini_recipe(prompt, prefs)
            data = result['data']
            constraints = result['constraints']

            # Save in DB
            rec = GeneratedRecipe.objects.create(
                user=request.user,
                prompt=prompt,
                title=data.get('title') or 'AI Recipe',
                data=data,
                diet_type=constraints.get('diet_type'),
                vegetarian=constraints.get('vegetarian', False),
                vegan=constraints.get('vegan', False),
                excluded_ingredients=", ".join(constraints.get('excluded') or []),
            )

            return redirect('generated_recipe_detail', id=rec.id)
        except Exception as e:
            messages.error(request, f"Failed to generate recipe: {e}")
            return render(request, 'generate_recipe.html', { 'what': "/static/img/bhaisab.png" })

    return render(request, 'generate_recipe.html', { 'what': "/static/img/bhaisab.png" })


@login_required(login_url='/authentication/signin')
def my_generated_recipes(request):
    recipes = GeneratedRecipe.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_generated_recipes.html', { 'recipes': recipes, 'what': "/static/img/bhaisab.png" })


@login_required(login_url='/authentication/signin')
def generated_recipe_detail(request, id):
    try:
        rec = GeneratedRecipe.objects.get(id=id, user=request.user)
    except GeneratedRecipe.DoesNotExist:
        messages.error(request, 'Recipe not found')
        return redirect('my_generated_recipes')

    return render(request, 'generated_recipe_detail.html', { 'rec': rec, 'what': "/static/img/bhaisab.png" })


def contact(request):
    """Handle contact form submissions"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Validate form data
        if not all([name, email, subject, message_text]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'All fields are required.'})
            messages.error(request, 'All fields are required.')
            return redirect('home')

        # Create and save the contact message
        try:
            contact_msg = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            contact_msg.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Thank you! Your message has been sent successfully. We will get back to you soon.'})
            
            messages.success(request, 'Thank you! Your message has been sent successfully. We will get back to you soon.')
            return redirect('home')
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
            
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('home')

    return redirect('home')
