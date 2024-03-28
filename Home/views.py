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
