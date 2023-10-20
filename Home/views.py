from django.shortcuts import render
from API.recipe_tag import *
from API.jsontest import json_to_txt
import json
import threading


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
        var["query"] = query

    if query:
        
        var["results"] = json.loads(get_recipe_by_query(query).content.decode())
        
        return render(request, "result.html", var)

    return render(request, "result.html", var)

def recipeinfo(request, id):
    
    recipe_data = get_recipe_details(id)
    Instructions = get_instructions(id)
    similar = get_similar_recipes(id)
    
    json_to_txt(similar, 'lul.txt')
    
    if recipe_data:
        # Pass the recipe_data to the HTML template
        var = {
            'what': "/static/img/bhaisab.png",
            'recipe_info': recipe_data['recipe_info'],
            'ingredients': recipe_data['ingredients'],
            "Instructions" : Instructions,
            "similar" : similar
        }

        return render(request, 'recipeinfo.html', var)

    # Handle the case where data retrieval failed, e.g., by displaying an error message
    error_message = "Recipe data could not be retrieved."
    var = {'error_message': error_message}
        
    return render(request, 'recipeinfo.html', var)
