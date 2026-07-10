from app.database import SessionLocal
from app.models import Dish
from nutrition_pipeline import DISH_INGREDIENTS

# Keyword -> allergen tag. Deliberately conservative: matches on ingredient
# name substrings from the same breakdown the nutrition pipeline already uses.
ALLERGEN_KEYWORDS = {
    "peanut": "peanuts",
    "soy sauce": "soy",
    "egg": "eggs",
    "yogurt": "dairy",
    "cream": "dairy",
    "butter": "dairy",
    "cheese": "dairy",
    "ghee": "dairy",
    "milk": "dairy",
}


def derive_allergens(ingredients):
    found = set()
    for ingredient_name, _grams in ingredients:
        lowered = ingredient_name.lower()
        for keyword, allergen in ALLERGEN_KEYWORDS.items():
            if keyword in lowered:
                found.add(allergen)
    return sorted(found)


def run():
    db = SessionLocal()
    dishes = db.query(Dish).all()

    for dish in dishes:
        ingredients = DISH_INGREDIENTS.get(dish.name)
        if not ingredients:
            continue
        allergens = derive_allergens(ingredients)
        dish.allergens = allergens
        print(f"{dish.name}: {allergens if allergens else 'none detected'}")

    db.commit()
    db.close()
    print("Done.")


if __name__ == "__main__":
    run()
