import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/dishes", tags=["dishes"])

VALID_NUTRIENTS = {
    "fiber", "calcium", "iron", "potassium", "sodium",
    "vitamin_c", "vitamin_a", "vitamin_d", "vitamin_b12",
}

MOOD_WEIGHT = 2.0
CALORIE_WEIGHT = 1.0

# Only "vegetarian" has real per-dish tag support today (via mood_tags).
# Other dietary restrictions a user might set (vegan, halal, kosher,
# gluten-free) are stored on their profile but not yet enforceable here,
# since no dish carries that structured data.
ENFORCEABLE_DIETARY_TAGS = {"vegetarian"}


def get_user_constraints(db: Session, user_id: uuid.UUID | None):
    if not user_id:
        return set(), set()
    user = db.get(models.User, user_id)
    if not user:
        return set(), set()
    allergies = set(user.allergy_list or [])
    dietary = set(user.dietary_restrictions or []) & ENFORCEABLE_DIETARY_TAGS
    return allergies, dietary


def violates_constraints(dish, allergies, dietary):
    dish_allergens = set(dish.allergens or [])
    if allergies & dish_allergens:
        return True
    if dietary:
        dish_tags = set(dish.mood_tags or [])
        if not dietary.issubset(dish_tags):
            return True
    return False


@router.get("/", response_model=list[schemas.DishOut])
def list_dishes(
    restaurant_id: uuid.UUID | None = None,
    mood_tag: str | None = None,
    max_calories: int | None = None,
    user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Dish)
    if restaurant_id:
        query = query.filter(models.Dish.restaurant_id == restaurant_id)
    if mood_tag:
        query = query.filter(models.Dish.mood_tags.any(mood_tag))
    if max_calories:
        query = query.filter(models.Dish.calories <= max_calories)

    results = query.all()

    event = models.InteractionEvent(
        user_id=user_id,
        event_type="search",
        event_metadata={
            "restaurant_id": str(restaurant_id) if restaurant_id else None,
            "mood_tag": mood_tag,
            "max_calories": max_calories,
            "result_count": len(results),
        },
    )
    db.add(event)
    db.commit()

    return results


@router.get("/nutrition-search", response_model=list[schemas.NutritionSearchResult])
def nutrition_search(
    nutrient: str = Query(..., description=f"One of: {', '.join(sorted(VALID_NUTRIENTS))}"),
    min_percent_dv: float | None = Query(default=None, ge=0),
    max_calories: int | None = None,
    user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    if nutrient not in VALID_NUTRIENTS:
        raise HTTPException(status_code=400, detail=f"nutrient must be one of {sorted(VALID_NUTRIENTS)}")

    allergies, dietary = get_user_constraints(db, user_id)

    query = (
        db.query(models.DishNutrient, models.Dish)
        .join(models.Dish, models.DishNutrient.dish_id == models.Dish.id)
        .filter(models.DishNutrient.nutrient_name == nutrient)
    )
    if min_percent_dv is not None:
        query = query.filter(models.DishNutrient.percent_daily_value >= min_percent_dv)
    if max_calories is not None:
        query = query.filter(models.Dish.calories <= max_calories)

    query = query.order_by(models.DishNutrient.percent_daily_value.desc().nullslast())
    rows = query.all()

    results = []
    for dn, dish in rows:
        if violates_constraints(dish, allergies, dietary):
            continue
        results.append(
            schemas.NutritionSearchResult(
                dish_id=dish.id,
                dish_name=dish.name,
                restaurant_id=dish.restaurant_id,
                calories=dish.calories,
                matched_nutrient=dn.nutrient_name,
                amount=float(dn.amount),
                unit=dn.unit,
                percent_daily_value=float(dn.percent_daily_value) if dn.percent_daily_value is not None else None,
            )
        )

    event = models.InteractionEvent(
        user_id=user_id,
        event_type="nutrition_search",
        event_metadata={
            "nutrient": nutrient,
            "min_percent_dv": min_percent_dv,
            "max_calories": max_calories,
            "result_count": len(results),
        },
    )
    db.add(event)
    db.commit()

    return results


@router.get("/mood-match", response_model=list[schemas.MoodMatchResult])
def mood_match(
    moods: list[str] = Query(default=[], description="One or more mood tags, e.g. comforting, spicy, light"),
    min_calories: int | None = None,
    max_calories: int | None = None,
    exclude_tag: list[str] = Query(default=[], description="Mood tags to exclude, e.g. indulgent"),
    limit: int = Query(default=5, ge=1, le=20),
    user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    if not moods:
        raise HTTPException(status_code=400, detail="At least one mood must be provided")

    requested = set(moods)
    excluded = set(exclude_tag)
    allergies, dietary = get_user_constraints(db, user_id)

    dishes = (
        db.query(models.Dish)
        .join(models.Restaurant, models.Dish.restaurant_id == models.Restaurant.id)
        .all()
    )

    scored = []
    for dish in dishes:
        if violates_constraints(dish, allergies, dietary):
            continue

        dish_tags = set(dish.mood_tags or [])

        if excluded and dish_tags & excluded:
            continue
        if min_calories is not None and (dish.calories is None or dish.calories < min_calories):
            continue
        if max_calories is not None and (dish.calories is None or dish.calories > max_calories):
            continue

        matched = requested & dish_tags
        if not matched:
            continue

        mood_score = (len(matched) / len(requested)) * MOOD_WEIGHT

        calorie_score = 0.0
        if min_calories is not None and max_calories is not None and dish.calories is not None:
            bracket_width = max(max_calories - min_calories, 1)
            if min_calories <= dish.calories <= max_calories:
                calorie_score = CALORIE_WEIGHT
            else:
                deviation = min(abs(dish.calories - min_calories), abs(dish.calories - max_calories))
                calorie_score = max(0.0, CALORIE_WEIGHT * (1 - deviation / bracket_width))

        total_score = round(mood_score + calorie_score, 3)

        reason_parts = [f"matches {len(matched)}/{len(requested)} requested moods ({', '.join(sorted(matched))})"]
        if min_calories is not None or max_calories is not None:
            reason_parts.append(f"{dish.calories} kcal")
        reason = "; ".join(reason_parts)

        scored.append((total_score, dish, matched, reason))

    scored.sort(key=lambda row: row[0], reverse=True)
    top = scored[:limit]

    results = [
        schemas.MoodMatchResult(
            dish_id=dish.id,
            dish_name=dish.name,
            restaurant_id=dish.restaurant_id,
            restaurant_name=dish.restaurant.name,
            price=float(dish.price),
            calories=dish.calories,
            mood_tags=dish.mood_tags or [],
            matched_moods=sorted(matched),
            score=score,
            reason=reason,
        )
        for score, dish, matched, reason in top
    ]

    event = models.InteractionEvent(
        user_id=user_id,
        event_type="mood_match_search",
        event_metadata={
            "moods": moods,
            "exclude_tag": exclude_tag,
            "min_calories": min_calories,
            "max_calories": max_calories,
            "result_count": len(results),
        },
    )
    db.add(event)
    db.commit()

    return results


@router.get("/{dish_id}", response_model=schemas.DishOut)
def get_dish(dish_id: uuid.UUID, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.get("/{dish_id}/nutrients", response_model=schemas.DishNutrientProfile)
def get_dish_nutrients(dish_id: uuid.UUID, db: Session = Depends(get_db)):
    dish = db.get(models.Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    nutrients = db.query(models.DishNutrient).filter(models.DishNutrient.dish_id == dish_id).all()

    return schemas.DishNutrientProfile(
        dish_id=dish.id,
        dish_name=dish.name,
        calories=dish.calories,
        protein_g=float(dish.protein_g) if dish.protein_g is not None else None,
        carbs_g=float(dish.carbs_g) if dish.carbs_g is not None else None,
        fat_g=float(dish.fat_g) if dish.fat_g is not None else None,
        nutrients=nutrients,
    )


@router.post("/", response_model=schemas.DishOut, status_code=201)
def create_dish(payload: schemas.DishCreate, db: Session = Depends(get_db)):
    dish = models.Dish(**payload.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish
