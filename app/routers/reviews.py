import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[schemas.ReviewOut])
def list_reviews(
    restaurant_id: uuid.UUID | None = None,
    dish_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Review)
    if restaurant_id:
        query = query.filter(models.Review.restaurant_id == restaurant_id)
    if dish_id:
        query = query.filter(models.Review.dish_id == dish_id)
    return query.all()


@router.get("/{review_id}", response_model=schemas.ReviewOut)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    review = db.get(models.Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/", response_model=schemas.ReviewOut, status_code=201)
def create_review(payload: schemas.ReviewCreate, db: Session = Depends(get_db)):
    review = models.Review(**payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
