import os
import time
import requests
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Dish, DishNutrient

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Documented modeling assumption: restaurant dishes are not lab-measured,
# so each dish is decomposed into approximate ingredient weights (grams)
# based on typical home-cook recipe proportions for a single serving.
# This is a known limitation and should be stated as such in any writeup.
DISH_INGREDIENTS = {
    "Chicken Tikka Masala": [
        ("chicken breast, raw", 150),
        ("yogurt, plain, whole milk", 30),
        ("tomato puree", 100),
        ("heavy cream", 50),
        ("onion, raw", 30),
        ("butter, unsalted", 15),
    ],
    "Dal Tadka": [
        ("lentils, cooked", 200),
        ("onion, raw", 20),
        ("tomato, raw", 20),
        ("ghee", 10),
    ],
    "Beef Bhuna": [
        ("beef, chuck, raw", 180),
        ("onion, raw", 40),
        ("tomato, raw", 60),
        ("vegetable oil", 15),
    ],
    "Bhuna Khichuri": [
        ("rice, white, cooked", 150),
        ("lentils, cooked", 100),
        ("onion, raw", 20),
        ("ghee", 10),
    ],
    "Vegetable Fried Rice": [
        ("rice, white, cooked", 200),
        ("mixed vegetables, frozen", 80),
        ("soy sauce", 10),
        ("vegetable oil", 10),
        ("egg, whole, raw", 30),
    ],
    "Kung Pao Chicken": [
        ("chicken breast, raw", 150),
        ("peanuts, raw", 20),
        ("bell pepper, raw", 40),
        ("soy sauce", 10),
        ("vegetable oil", 10),
    ],
    "Margherita Pizza": [
        ("wheat flour, white", 120),
        ("mozzarella cheese", 100),
        ("tomato sauce", 60),
        ("olive oil", 10),
    ],
    "Grilled Salmon Salad": [
        ("salmon, raw", 150),
        ("mixed salad greens", 60),
        ("olive oil", 15),
        ("cherry tomatoes, raw", 30),
    ],
}

# nutrientId -> (field name, unit, daily value used for percent calc)
TRACKED_NUTRIENTS = {
    1003: ("protein_g", "G", None),
    1004: ("fat_g", "G", None),
    1005: ("carbs_g", "G", None),
    1008: ("calories", "KCAL", None),
    1079: ("fiber", "G", 28),
    1087: ("calcium", "MG", 1300),
    1089: ("iron", "MG", 18),
    1092: ("potassium", "MG", 4700),
    1093: ("sodium", "MG", 2300),
    1162: ("vitamin_c", "MG", 90),
    1106: ("vitamin_a", "UG", 900),
    1114: ("vitamin_d", "UG", 20),
    1178: ("vitamin_b12", "UG", 2.4),
}

# Fallback energy sources, used only when nutrientId 1008 is missing.
# 2047 = Energy (Atwater General Factors), 2048 = Energy (Atwater Specific Factors).
# Both are legitimate calorie calculation methods derived from macronutrient
# composition rather than direct calorimetry; using them as a fallback keeps
# the pipeline from silently reporting zero calories for affected ingredients.
ENERGY_FALLBACK_IDS = [2047, 2048]

MACRO_FIELDS = {"protein_g", "fat_g", "carbs_g", "calories"}

_ingredient_cache = {}


def lookup_ingredient(query):
    if query in _ingredient_cache:
        return _ingredient_cache[query]

    params = {
        "query": query,
        "dataType": "Foundation,SR Legacy",
        "pageSize": 1,
        "api_key": USDA_API_KEY,
    }
    response = requests.get(USDA_SEARCH_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    foods = data.get("foods", [])
    if not foods:
        print(f"  warning: no USDA match for '{query}', skipping")
        _ingredient_cache[query] = {}
        return {}

    raw_by_id = {}
    for nutrient in foods[0].get("foodNutrients", []):
        nid = nutrient.get("nutrientId")
        if "value" not in nutrient or nid in raw_by_id:
            continue
        if nid in TRACKED_NUTRIENTS or nid in ENERGY_FALLBACK_IDS:
            raw_by_id[nid] = nutrient["value"]

    result = {}
    for nid, (field, unit, dv) in TRACKED_NUTRIENTS.items():
        if nid in raw_by_id:
            result[field] = raw_by_id[nid]

    if "calories" not in result:
        for fallback_id in ENERGY_FALLBACK_IDS:
            if fallback_id in raw_by_id:
                result["calories"] = raw_by_id[fallback_id]
                break

    time.sleep(0.3)
    _ingredient_cache[query] = result
    return result


def compute_dish_totals(ingredients):
    totals = {field: 0.0 for field, _, _ in TRACKED_NUTRIENTS.values()}

    for ingredient_query, grams in ingredients:
        per_hundred_g = lookup_ingredient(ingredient_query)
        scale = grams / 100.0
        for field, value in per_hundred_g.items():
            totals[field] += value * scale

    return totals


def run():
    db = SessionLocal()
    dishes = db.query(Dish).all()

    for dish in dishes:
        ingredients = DISH_INGREDIENTS.get(dish.name)
        if not ingredients:
            print(f"Skipping '{dish.name}', no ingredient breakdown defined")
            continue

        print(f"Processing '{dish.name}'...")
        totals = compute_dish_totals(ingredients)

        dish.calories = round(totals["calories"])
        dish.protein_g = round(totals["protein_g"], 2)
        dish.carbs_g = round(totals["carbs_g"], 2)
        dish.fat_g = round(totals["fat_g"], 2)

        db.query(DishNutrient).filter(DishNutrient.dish_id == dish.id).delete()

        for nutrient_id, (field, unit, daily_value) in TRACKED_NUTRIENTS.items():
            if field in MACRO_FIELDS:
                continue
            amount = round(totals[field], 3)
            percent_dv = round((amount / daily_value) * 100, 2) if daily_value else None
            db.add(
                DishNutrient(
                    dish_id=dish.id,
                    nutrient_name=field,
                    amount=amount,
                    unit=unit,
                    percent_daily_value=percent_dv,
                )
            )

        db.commit()
        print(f"  calories={dish.calories} protein={dish.protein_g}g carbs={dish.carbs_g}g fat={dish.fat_g}g")

    db.close()
    print("Done.")


if __name__ == "__main__":
    run()
