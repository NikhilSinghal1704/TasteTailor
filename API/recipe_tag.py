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


def get_recipe_by_query(query):
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
        "query": query,
        "sort": "popularity",
        "number": 60,
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
        logging.error(f"API request failed for resulting recipes: {e}")
        return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing API response for resulting recipes: {e}")
        return JsonResponse({"error": "Error parsing API response"}, status=500)
