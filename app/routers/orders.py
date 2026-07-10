import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])

VALID_STATUSES = {"placed", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"}


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(
    user_id: uuid.UUID | None = None,
    restaurant_id: uuid.UUID | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Order).options(joinedload(models.Order.items))
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    if restaurant_id:
        query = query.filter(models.Order.restaurant_id == restaurant_id)
    if status:
        query = query.filter(models.Order.status == status)
    return query.all()


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=schemas.OrderOut, status_code=201)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must include at least one item")

    dish_ids = [item.dish_id for item in payload.items]
    dishes = db.query(models.Dish).filter(models.Dish.id.in_(dish_ids)).all()
    dish_price_by_id = {dish.id: dish.price for dish in dishes}

    missing = set(dish_ids) - set(dish_price_by_id.keys())
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown dish ids: {missing}")

    total_price = sum(
        dish_price_by_id[item.dish_id] * item.quantity for item in payload.items
    )

    order = models.Order(
        user_id=payload.user_id,
        restaurant_id=payload.restaurant_id,
        total_price=total_price,
    )
    db.add(order)
    db.flush()

    for item in payload.items:
        db.add(
            models.OrderItem(
                order_id=order.id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                special_instructions=item.special_instructions,
            )
        )

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(order_id: uuid.UUID, payload: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Status must be one of {VALID_STATUSES}")

    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
