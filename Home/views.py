from django.shortcuts import render
from API.recipe_tag import *
from API.jsontest import json_to_txt
import json
import threading


def home(request):
    # Create a dictionary to store the results
    var = {"top": None}

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
            target=fetch_and_store_recipes, args=("breakfast", "breakfasts")
        ),
        threading.Thread(
            target=fetch_and_store_recipes, args=("main course", "lunches")
        ),
        threading.Thread(target=fetch_and_store_recipes, args=("dessert", "dinners")),
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
    var = {}

    def search(s):
        var["results"] = json.loads(get_recipe_by_query(s).content.decode())

    query = None  # Initialize query outside of the POST block

    if request.method == "POST":
        query = request.POST["q"]
        var["query"] = query

    if query:
        thread = threading.Thread(
            target=search, args=(query,)  # Pass query as a single-element tuple
        )
        thread.start()
        return render(request, "result.html", var)

    return render(request, "result.html", var)
