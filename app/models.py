import uuid
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, ForeignKey, TIMESTAMP, ARRAY, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    dietary_restrictions = Column(ARRAY(String), default=list)
    allergy_list = Column(ARRAY(String), default=list)
    calorie_target = Column(Integer)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    cuisine_type = Column(String(100))
    price_tier = Column(SmallInteger)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    avg_prep_minutes = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    dishes = relationship("Dish", back_populates="restaurant", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="restaurant", cascade="all, delete-orphan")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(8, 2), nullable=False)
    calories = Column(Integer)
    protein_g = Column(Numeric(6, 2))
    carbs_g = Column(Numeric(6, 2))
    fat_g = Column(Numeric(6, 2))
    mood_tags = Column(ARRAY(String), default=list)
    allergens = Column(ARRAY(String), default=list)
    photo_url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="dishes")
    nutrients = relationship("DishNutrient", back_populates="dish", cascade="all, delete-orphan")


class DishNutrient(Base):
    __tablename__ = "dish_nutrients"

    dish_id = Column(UUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True)
    nutrient_name = Column(String(50), primary_key=True)
    amount = Column(Numeric(8, 3), nullable=False)
    unit = Column(String(20), nullable=False)
    percent_daily_value = Column(Numeric(5, 2))

    dish = relationship("Dish", back_populates="nutrients")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    discount_type = Column(String(50), nullable=False)
    discount_value = Column(Numeric(6, 2), nullable=False)
    valid_until = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="offers")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    status = Column(String(30), nullable=False, default="placed")
    eta_estimate_minutes = Column(Integer)
    actual_delivery_minutes = Column(Integer)
    total_price = Column(Numeric(8, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    special_instructions = Column(Text)

    order = relationship("Order", back_populates="items")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("food_rating BETWEEN 1 AND 5", name="food_rating_range"),
        CheckConstraint("delivery_rating BETWEEN 1 AND 5", name="delivery_rating_range"),
        CheckConstraint("platform_rating BETWEEN 1 AND 5", name="platform_rating_range"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    dish_id = Column(UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=True)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    food_rating = Column(SmallInteger)
    delivery_rating = Column(SmallInteger)
    platform_rating = Column(SmallInteger)
    text = Column(Text)
    photo_url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String(50), nullable=False)
    dish_id = Column(UUID(as_uuid=True), ForeignKey("dishes.id"), nullable=True)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=True)
    event_metadata = Column("metadata", JSONB, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
