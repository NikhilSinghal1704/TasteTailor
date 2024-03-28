import requests, random
from TasteTailor.settings import CACHE_TIMEOUT
from django.core.cache import cache
from django.http import JsonResponse
from .api_key_manager import get_next_api_key
import logging


def get_recipe_by_tags(tag, include_popularity=True):
    tags = [tag]
    tag = tag.replace(" ", "+")
    # Attempt to retrieve cached data
    cached_data = cache.get(tag)

    if cached_data:
        return JsonResponse(
            cached_data, safe=False
        )  # If data is in cache, return it as a JSON response

    base_url = "https://api.spoonacular.com/recipes/random"

    key = get_next_api_key()

    if include_popularity:
        tags.append("popularity")

    params = {
        "apiKey": key,
        "tags": ", ".join(tags),  # Join tags with a comma and space
        "number": 6,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        recipes = data["recipes"]
        result = []

        for recipe in recipes:
            details = {
                "name": recipe["title"],
                "time_to_prepare": recipe["readyInMinutes"],
                "id": recipe["id"],
            }

            try:
                details["image_url"] = recipe["image"]
            except:
                details[
                    "image_url"
                ] = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.flaticon.com%2Ffree-icon%2Fdish_1083814&psig=AOvVaw1DYMjRB8WsU4UVItLa9Qyz&ust=1697181707693000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCOCKpdz874EDFQAAAAAdAAAAABAE"

            result.append(details)

        # Cache the result for subsequent requests
        cache.set(tag, result, CACHE_TIMEOUT)

        return JsonResponse(result, safe=False)  # Return the result as a list
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for tag {tag}: {e}")
        return JsonResponse({"error": "API request failed"}, status=500)
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing API response for tag {tag}: {e}")
        return JsonResponse({"error": "Error parsing API response"}, status=500)


def get_top_recipe():
    # Use a more suitable cache key
    choices = ["soup", "dessert", "appetizer"]
    query = random.choice(choices)

    cache_key = query + "top_recipes_cache_key"

    # Attempt to retrieve cached data
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return JsonResponse(
            cached_data, safe=False
        )  # If data is in cache, return it as a JSON response

    base_url = "https://api.spoonacular.com/recipes/complexSearch"
    key = get_next_api_key()

    params = {
        "apiKey": key,
        "query": query,
        "sort": "popularity",
        "number": 8,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        recipes = data["results"]
        result = []

        for recipe in recipes:
            details = {
                "name": recipe["title"],
                "id": recipe["id"],
            }

            # Use a reliable default image URL
            details["image_url"] = recipe.get(
                "image",
                "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.flaticon.com%2Ffree-icon%2Fdish_1083814&psig=AOvVaw1DYMjRB8WsU4UVItLa9Qyz&ust=1697181707693000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCOCKpdz874EDFQAAAAAdAAAAABAE",
            )

            result.append(details)

        # Cache the result for subsequent requests with a specific expiration time
        cache.set(cache_key, result, CACHE_TIMEOUT)

        return JsonResponse(result, safe=False)  # Return the result as a list
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for top recipes: {e}")
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing API response for top recipes: {e}")
        return JsonResponse({"error": "Error parsing API response"}, status=500)


def analyze_query(query):
    # Define the URL for the Spoonacular API endpoint
    endpoint = "https://api.spoonacular.com/recipes/queries/analyze"

    # Get a Spoonacular API key
    api_key = get_next_api_key()

    # Define the parameters for the API request
    params = {
        "q": query,
        "apiKey": api_key,
    }

    try:
        # Send a GET request to the Spoonacular API
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        # Parse the JSON response
        data = response.json()
        print(data)
        
        in_ingredients = []
        ex_ingredients = []
        ingredients = data["ingredients"]
        for ing in ingredients:
            if ing["include"]:
                in_ingredients.append(ing["name"])
            else:
                ex_ingredients.append(ing["name"])
                
        cuisines = [cuis["name"] for cuis in data["modifiers"]]
        
        dishes = [dish["name"] for dish in data["dishes"]]
        
        response = {}
        
        # Check if there are dishes in the data
        if dishes:
            response["query"] = ", ".join(dishes)
            if cuisines:
                response["cuisine"] = ", ".join(cuisines)
            if in_ingredients:
                response["includeIngredients"] = ", ".join(in_ingredients)
                
        elif cuisines:
            response["query"] = cuisines[0]
            if in_ingredients:
                response["includeIngredients"] = ", ".join(in_ingredients)           
            
        else:
            response["query"] = query
        
            
        if ex_ingredients:
            response["excludeIngredients"] = ", ".join(ex_ingredients)
            
        return response

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    
def create_nutrition_html(data):
    # Start building the HTML
    html = '<div class="nutrition-info">'
    
    # Add a section for dietary information
    html += '<h2>Dietary Information</h2>'
    html += '<ul>'
    
    if data['vegetarian']:
        html += '<li>Vegetarian</li>'
    if data['vegan']:
        html += '<li>Vegan</li>'
    if data['glutenFree']:
        html += '<li>Gluten-Free</li>'
    if data['dairyFree']:
        html += '<li>Dairy-Free</li>'
    if data['veryHealthy']:
        html += '<li>Very Healthy</li>'
    if data['cheap']:
        html += '<li>Cheap</li>'
    if data['veryPopular']:
        html += '<li>Very Popular</li>'
    if data['sustainable']:
        html += '<li>Sustainable</li>'
    if data['lowFodmap']:
        html += '<li>Low FODMAP</li>'
    
    html += '</ul>'
    
    # Add a section for nutrition facts
    html += '<h2>Nutrition Facts</h2>'
    html += '<table class="nutrition-table">'
    html += '<tr><th class="nutrient-header">Nutrient</th><th class="amount-header">Amount</th><th class="percent-header">% Daily Needs</th></tr>'
    
    for nutrient in data['nutrition']['nutrients']:
        html += f'<tr><td class="nutrient-name">{nutrient["name"]}</td><td class="nutrient-amount">{nutrient["amount"]} {nutrient["unit"]}</td><td class="percent-of-needs">{nutrient["percentOfDailyNeeds"]}%</td></tr>'
    
    html += '</table>'
    
    # Close the main div
    html += '</div>'
    
    return html

def get_recipe_details(recipe_id):
    
    # Define the cache key
    cache_key = f"recipe_{recipe_id}"

    # Attempt to retrieve cached data
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data
    
    # Define the base URL for fetching recipe details by ID
    base_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

    # Define query parameters, including your API key
    params = {
        "apiKey": get_next_api_key(),
        "includeNutrition": "true",  # Include nutrition information
    }

    # Send a GET request to the API
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        #print(data)
        # Extract relevant information from the response
        recipe_info = {
            "nutrients" : create_nutrition_html(data),
            "image_url": data["image"],
            "servings": data["servings"],
            "title": data["title"],
            "summary": data["summary"],
            "health_rating": data["healthScore"],
            "type": data["dishTypes"],  # This might be a list of types
            "time_to_prepare": data["readyInMinutes"],
        }
        

        # Extract ingredients and equipment data
        ingredients_list = []
        for ingredient in data["extendedIngredients"]:
            img = ingredient["image"]
            ingredient_info = {
                "img_url": f"https://spoonacular.com/cdn/ingredients_100x100/{img}",
                "name": ingredient["name"],
                "qty": ingredient["measures"]["metric"]["amount"],
                "metric": ingredient["measures"]["metric"]["unitLong"],
                "price": ingredient.get("estimatedCost", {}).get("value"),
            }

            ingredients_list.append(ingredient_info)
            
        # Initialize an empty set to keep track of unique names
        unique_names = set()
        
        # Initialize a new list for storing unique dictionaries
        unique_list = []
        
        for item in ingredients_list:
            name = item["name"]
            if name not in unique_names:
                # Add the name to the set of unique names
                unique_names.add(name)
                unique_list.append(item)
                    
                result = {"recipe_info": recipe_info, "ingredients": unique_list}
                    
        # Cache the result for subsequent requests with a specific expiration time
        cache.set(cache_key, result, CACHE_TIMEOUT)

        # Return the organized data
        return result
        
    else:
        print(f"Error: {response.status_code}")
        return None

def get_recipe_by_query(query, ex_params = {}):
    # Use a more suitable cache key
    cache_key = query.replace(" ", "+") + "_cache_key"

    # Attempt to retrieve cached data
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return JsonResponse(
            cached_data, safe=False
        )  # If data is in cache, return it as a JSON response

    base_url = "https://api.spoonacular.com/recipes/complexSearch"
    key = get_next_api_key()

    params = {
        "apiKey": key,
        "number": 900,
    }
    
    params.update(analyze_query(query))
    #print(params)
    params.update(ex_params)
    
    if params["intolerances"] == '':
        params.pop("intolerances")
        
    print(params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        recipes = data["results"]
        result = []

        for recipe in recipes:
            details = {
                "name": recipe["title"],
                "id": recipe["id"],
            }

            # Use a reliable default image URL
            details["image_url"] = recipe.get(
                "image",
                "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.flaticon.com%2Ffree-icon%2Fdish_1083814&psig=AOvVaw1DYMjRB8WsU4UVItLa9Qyz&ust=1697181707693000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCOCKpdz874EDFQAAAAAdAAAAABAE",
            )

            result.append(details)

        # Cache the result for subsequent requests with a specific expiration time
        cache.set(cache_key, result, CACHE_TIMEOUT)

        return JsonResponse(result, safe=False)  # Return the result as a list
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for resulting recipes: {e}")
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing API response for resulting recipes: {e}")
        return JsonResponse({"error": "Error parsing API response"}, status=500)
    
    
def get_instructions(recipe_id):
    
    # Define the cache key
    cache_key = f"instructions_{recipe_id}"

    # Attempt to retrieve cached data
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data
    
    base_url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions"

    params = {"apiKey": get_next_api_key(), "stepBreakdown": "true"}

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        result =  json_to_structured_paragraph(data)
        
        cache.set(cache_key, result, CACHE_TIMEOUT)
        
        return result

    else:
        return None
    
    
def json_to_structured_paragraph(data):
    # Initialize an empty HTML string
    html = ""

    # Loop through each section (name) in the data
    for section in data:
        section_name = section["name"]
        html += f"<h3>{section_name}</h3>"  # Create a heading for the section

        # Loop through each step in the section
        for step in section["steps"]:
            step_number = step["number"]
            step_instruction = step["step"]

            html += f"<p><strong>Step {step_number}:</strong> {step_instruction}</p>"

            # Include ingredients, if available
            if step["ingredients"]:
                html += "<p><strong>Ingredients:</strong></p>"
                html += "<ul>"
                for ingredient in step["ingredients"]:
                    ingredient_name = ingredient["name"]
                    html += f"<li>{ingredient_name}</li>"
                html += "</ul>"

            # Include equipment, if available
            if step["equipment"]:
                html += "<p><strong>Equipment:</strong></p>"
                html += "<ul>"
                for equipment in step["equipment"]:
                    equipment_name = equipment["name"]
                    html += f"<li>{equipment_name}</li>"
                html += "</ul>"

    return html


def get_similar_recipes(recipe_id):
    
    api_key = get_next_api_key()
    
    # Define the base URL of the Spoonacular API
    base_url = "https://api.spoonacular.com/recipes"

    # Define the endpoint for finding similar recipes
    endpoint = f"{base_url}/{recipe_id}/similar"

    # Define query parameters including your API key
    params = {
        "apiKey": api_key,
        "number": 8
    }

    try:
        # Make a GET request to the API
        response = requests.get(endpoint, params=params)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract the list of similar recipes and create a list of dictionaries
            similar_recipes = []
            for recipe in data:
                recipe_dict = {
                    "id": recipe["id"]
                }
                
                recipe_dict["image_url"] = f"https://spoonacular.com/recipeImages/{recipe_dict['id']}-312x231.jpg"
                
                similar_recipes.append(recipe_dict)
                
            return similar_recipes
        else:
            # If the request was not successful, raise an exception or handle the error accordingly
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that may occur during the request
        print("Error:", e)
    
    return None  # Return None in case of failure

    
    

