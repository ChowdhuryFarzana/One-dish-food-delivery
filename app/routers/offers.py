import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/", response_model=list[schemas.OfferOut])
def list_offers(restaurant_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Offer)
    if restaurant_id:
        query = query.filter(models.Offer.restaurant_id == restaurant_id)
    return query.all()


@router.post("/", response_model=schemas.OfferOut, status_code=201)
def create_offer(payload: schemas.OfferCreate, db: Session = Depends(get_db)):
    offer = models.Offer(**payload.model_dump())
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer
