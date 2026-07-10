from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import restaurants, dishes, reviews, orders, offers, users

app = FastAPI(title="Food Review and Recipe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants.router)
app.include_router(dishes.router)
app.include_router(reviews.router)
app.include_router(orders.router)
app.include_router(offers.router)
app.include_router(users.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
