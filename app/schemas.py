import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    name: str
    dietary_restrictions: list[str] = []
    allergy_list: list[str] = []
    calorie_target: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    dietary_restrictions: Optional[list[str]] = None
    allergy_list: Optional[list[str]] = None
    calorie_target: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: Optional[str] = None
    price_tier: Optional[int] = None
    latitude: float
    longitude: float
    avg_prep_minutes: Optional[int] = None


class RestaurantOut(RestaurantCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class DishCreate(BaseModel):
    restaurant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: float
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    mood_tags: list[str] = []
    allergens: list[str] = []
    photo_url: Optional[str] = None


class DishOut(DishCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class DishNutrientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nutrient_name: str
    amount: float
    unit: str
    percent_daily_value: Optional[float] = None


class DishNutrientProfile(BaseModel):
    dish_id: uuid.UUID
    dish_name: str
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    nutrients: list[DishNutrientOut]


class NutritionSearchResult(BaseModel):
    dish_id: uuid.UUID
    dish_name: str
    restaurant_id: uuid.UUID
    calories: Optional[int] = None
    matched_nutrient: str
    amount: float
    unit: str
    percent_daily_value: Optional[float] = None


class MoodMatchResult(BaseModel):
    dish_id: uuid.UUID
    dish_name: str
    restaurant_id: uuid.UUID
    restaurant_name: str
    price: float
    calories: Optional[int] = None
    mood_tags: list[str]
    matched_moods: list[str]
    score: float
    reason: str


class OfferCreate(BaseModel):
    restaurant_id: uuid.UUID
    discount_type: str
    discount_value: float
    valid_until: datetime


class OfferOut(OfferCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class QuickModeResult(BaseModel):
    restaurant_id: uuid.UUID
    name: str
    cuisine_type: Optional[str] = None
    price_tier: Optional[int] = None
    avg_prep_minutes: Optional[int] = None
    distance_km: float
    active_offers: list[OfferOut]
    score: float


class ReviewCreate(BaseModel):
    user_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    dish_id: Optional[uuid.UUID] = None
    restaurant_id: uuid.UUID
    food_rating: Optional[int] = Field(default=None, ge=1, le=5)
    delivery_rating: Optional[int] = Field(default=None, ge=1, le=5)
    platform_rating: Optional[int] = Field(default=None, ge=1, le=5)
    text: Optional[str] = None
    photo_url: Optional[str] = None


class ReviewOut(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class OrderItemCreate(BaseModel):
    dish_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)
    special_instructions: Optional[str] = None


class OrderItemOut(OrderItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class OrderCreate(BaseModel):
    user_id: uuid.UUID
    restaurant_id: uuid.UUID
    items: list[OrderItemCreate]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    restaurant_id: uuid.UUID
    status: str
    eta_estimate_minutes: Optional[int] = None
    actual_delivery_minutes: Optional[int] = None
    total_price: float
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: str
