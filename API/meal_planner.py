import requests
from datetime import date
from typing import Dict, Any

from .api_key_manager import get_next_api_key


SPOON_BASE = "https://api.spoonacular.com"


def _compose_image_url(recipe_id: int, size: str = "312x231") -> str:
    return f"https://spoonacular.com/recipeImages/{recipe_id}-{size}.jpg"


def estimate_calories(preferences) -> int:
    """
    Very simple calorie estimation. If user has set daily_calorie_target, use it.
    Otherwise default to 2000.
    """
    if getattr(preferences, "daily_calorie_target", None):
        return int(preferences.daily_calorie_target)
    # Fallback
    return 2000


def build_exclusions(preferences) -> str:
    parts = []
    if getattr(preferences, "intolerances", None):
        parts.append(preferences.intolerances)
    if getattr(preferences, "allergies", None):
        parts.append(preferences.allergies)
    if getattr(preferences, "disliked_ingredients", None):
        parts.append(preferences.disliked_ingredients)
    # Comma-separated values expected by Spoonacular
    return ",".join([p.strip() for chunk in parts for p in chunk.split(',') if p.strip()])


def generate_day_plan(preferences, for_date: date | None = None) -> Dict[str, Any]:
    """
    Call Spoonacular mealplanner/generate for a single day using user preferences.
    Returns dict with keys: meals (list) and nutrients (dict)
    """
    if for_date is None:
        for_date = date.today()

    api_key = get_next_api_key()
    if not api_key:
        raise RuntimeError("No Spoonacular API keys are configured. Please add at least one APIKey in the admin.")
    params = {
        "timeFrame": "day",
        "apiKey": api_key,
    }

    # Map preferences to parameters
    calories = estimate_calories(preferences)
    if calories:
        params["targetCalories"] = calories

    if getattr(preferences, "diet_type", None):
        params["diet"] = preferences.diet_type

    exclude = build_exclusions(preferences)
    if exclude:
        params["exclude"] = exclude

    url = f"{SPOON_BASE}/mealplanner/generate"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    payload = resp.json()

    # The API returns meals with id, title, readyInMinutes, servings, sourceUrl
    meals = payload.get("meals", [])
    nutrients = payload.get("nutrients", {})

    # Enrich with image url and a rough meal_type mapping
    meal_type_order = ["breakfast", "lunch", "dinner"]
    enriched = []
    for idx, m in enumerate(meals):
        enriched.append({
            **m,
            "image_url": _compose_image_url(m.get("id")),
            "meal_type": meal_type_order[idx] if idx < len(meal_type_order) else "lunch",
        })

    return {
        "date": for_date.isoformat(),
        "meals": enriched,
        "nutrients": nutrients,
        "raw": payload,
        "params": params,
    }
