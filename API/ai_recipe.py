import os
from typing import Dict, Any

import google.generativeai as genai

# Default to 2.5-flash as requested, but allow override via .env
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _configure_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment. Please add it to your .env")
    genai.configure(api_key=api_key)


def build_constraints(preferences) -> Dict[str, Any]:
    diet = (preferences.diet_type or "").strip().lower() if preferences else ""
    vegetarian = diet in {"vegetarian", "lacto-vegetarian", "ovo-vegetarian"}
    vegan = diet == "vegan"

    excluded = []
    for attr in ("allergies", "intolerances", "disliked_ingredients"):
        val = getattr(preferences, attr, None)
        if val:
            for part in val.split(','):
                p = part.strip()
                if p:
                    excluded.append(p)

    return {
        "diet_type": diet or None,
        "vegetarian": vegetarian,
        "vegan": vegan,
        "excluded": excluded,
    }


def get_gemini_recipe(user_prompt: str, preferences) -> Dict[str, Any]:
    """
    Returns a structured JSON dict for the recipe.
    {
      title, servings, ready_in_minutes, cuisine?, diet_labels[],
      ingredients: [{name, quantity, unit}],
      steps: [..],
      tips: [..],
      estimated_nutrition: { calories_kcal, protein_g, carbs_g, fat_g }
    }
    """
    _configure_api()

    constraints = build_constraints(preferences)

    sys_instructions = (
        "You are an expert recipe creator. Generate delicious, clear, and achievable recipes. "
        "Always honor dietary restrictions and exclude any allergens or intolerances. "
        "Prefer widely available ingredients. Keep steps precise and numbered."
    )

    exclusions = ", ".join(constraints["excluded"]) if constraints["excluded"] else "none"
    diet_line = (
        "vegan" if constraints["vegan"] else ("vegetarian" if constraints["vegetarian"] else (constraints["diet_type"] or "none"))
    )

    json_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "servings": {"type": "integer"},
            "ready_in_minutes": {"type": "integer"},
            "cuisine": {"type": "string"},
            "diet_labels": {"type": "array", "items": {"type": "string"}},
            "ingredients": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "steps": {"type": "array", "items": {"type": "string"}},
            "tips": {"type": "array", "items": {"type": "string"}},
            "estimated_nutrition": {
                "type": "object",
                "properties": {
                    "calories_kcal": {"type": "number"},
                    "protein_g": {"type": "number"},
                    "carbs_g": {"type": "number"},
                    "fat_g": {"type": "number"}
                }
            }
        },
        "required": ["title", "ingredients", "steps"]
    }

    prompt_text = f"""
SYSTEM:
{sys_instructions}

TASK:
Create a single complete recipe as JSON only.

USER REQUEST: {user_prompt}
DIET: {diet_line}
EXCLUDE: {exclusions}

CONSTRAINTS:
- Do NOT include excluded items.
- If vegan or vegetarian, strictly avoid animal products accordingly.
- Favor healthy but tasty choices.
- Keep steps concise and numbered.

SCHEMA (keys and types):
{json_schema}

OUTPUT:
Return ONLY a compact JSON object that matches the schema. No prose, no code fences, no extra commentary.
"""

    # Try configured model first; then pragmatic fallbacks for broader availability
    tried_models = []
    last_err = None
    for name in (MODEL_NAME, "gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-1.5-flash"):
        if name in tried_models:
            continue
        tried_models.append(name)
        try:
            model = genai.GenerativeModel(name, generation_config={
                "response_mime_type": "application/json"
            })
            # Ask for JSON-only response via mime type + compact prompt
            response = model.generate_content(prompt_text)
            if not getattr(response, "text", None):
                raise RuntimeError("Empty response from model")
            break
        except Exception as e:
            last_err = e
            response = None
    if response is None:
        raise RuntimeError(f"Gemini generation failed for models {tried_models}: {last_err}")

    text = response.text.strip()

    # Attempt to locate JSON if wrapped with code fences
    import json, re
    m = re.search(r"\{[\s\S]*\}\s*$", text)
    if m:
        text = m.group(0)

    data = json.loads(text)

    # Basic fill-ins
    data.setdefault("servings", 2)
    data.setdefault("ready_in_minutes", 25)
    data.setdefault("diet_labels", [])

    return {
        "data": data,
        "constraints": constraints,
    }
