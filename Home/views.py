from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from API.recipe_tag import *
from API.jsontest import json_to_txt
import json
import threading
from .models import Contact


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
