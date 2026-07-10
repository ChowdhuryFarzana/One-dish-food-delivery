import uuid
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

EARTH_RADIUS_KM = 6371.0
DISTANCE_WEIGHT = 1.0
PRICE_WEIGHT = 1.0


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * atan2(sqrt(a), sqrt(1 - a))


@router.get("/", response_model=list[schemas.RestaurantOut])
def list_restaurants(cuisine_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Restaurant)
    if cuisine_type:
        query = query.filter(models.Restaurant.cuisine_type == cuisine_type)
    return query.all()


@router.get("/quick-mode", response_model=list[schemas.QuickModeResult])
def quick_mode(
    latitude: float,
    longitude: float,
    radius_km: float = Query(default=2.0, gt=0),
    limit: int = Query(default=10, ge=1, le=50),
    user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    restaurants = db.query(models.Restaurant).all()
    now = datetime.now(timezone.utc)

    candidates = []
    for restaurant in restaurants:
        distance = haversine_km(latitude, longitude, float(restaurant.latitude), float(restaurant.longitude))
        if distance > radius_km:
            continue

        active_offers = [o for o in restaurant.offers if o.valid_until >= now]

        distance_score = max(0.0, 1 - (distance / radius_km)) * DISTANCE_WEIGHT

        price_tier = restaurant.price_tier or 4
        price_score = max(0.0, 1 - ((price_tier - 1) / 3)) * PRICE_WEIGHT

        offer_bonus = 0.2 if active_offers else 0.0

        total_score = round(distance_score + price_score + offer_bonus, 3)

        candidates.append((total_score, restaurant, distance, active_offers))

    candidates.sort(key=lambda row: row[0], reverse=True)
    top = candidates[:limit]

    results = [
        schemas.QuickModeResult(
            restaurant_id=restaurant.id,
            name=restaurant.name,
            cuisine_type=restaurant.cuisine_type,
            price_tier=restaurant.price_tier,
            avg_prep_minutes=restaurant.avg_prep_minutes,
            distance_km=round(distance, 2),
            active_offers=active_offers,
            score=score,
        )
        for score, restaurant, distance, active_offers in top
    ]

    event = models.InteractionEvent(
        user_id=user_id,
        event_type="quick_mode_search",
        event_metadata={
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "result_count": len(results),
        },
    )
    db.add(event)
    db.commit()

    return results


@router.get("/{restaurant_id}", response_model=schemas.RestaurantOut)
def get_restaurant(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.post("/", response_model=schemas.RestaurantOut, status_code=201)
def create_restaurant(payload: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    restaurant = models.Restaurant(**payload.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant
