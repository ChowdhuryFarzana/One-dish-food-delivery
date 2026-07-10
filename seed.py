from app.database import SessionLocal
from app.models import Restaurant, Dish


def seed():
    db = SessionLocal()

    restaurants_data = [
        {
            "name": "Spice Route",
            "cuisine_type": "Indian",
            "price_tier": 2,
            "latitude": 41.3083,
            "longitude": -72.9279,
            "avg_prep_minutes": 25,
        },
        {
            "name": "Dhaka Kitchen",
            "cuisine_type": "Bangladeshi",
            "price_tier": 2,
            "latitude": 41.3100,
            "longitude": -72.9250,
            "avg_prep_minutes": 30,
        },
        {
            "name": "Golden Wok",
            "cuisine_type": "Chinese",
            "price_tier": 1,
            "latitude": 41.3050,
            "longitude": -72.9300,
            "avg_prep_minutes": 20,
        },
        {
            "name": "Verde Trattoria",
            "cuisine_type": "Italian",
            "price_tier": 3,
            "latitude": 41.3070,
            "longitude": -72.9260,
            "avg_prep_minutes": 35,
        },
    ]

    restaurants = {}
    for data in restaurants_data:
        restaurant = Restaurant(**data)
        db.add(restaurant)
        db.flush()
        restaurants[data["name"]] = restaurant

    dishes_data = [
        {
            "restaurant_name": "Spice Route",
            "name": "Chicken Tikka Masala",
            "description": "Grilled chicken in a creamy tomato curry",
            "price": 14.99,
            "calories": 650,
            "protein_g": 38,
            "carbs_g": 30,
            "fat_g": 40,
            "mood_tags": ["comforting", "indulgent", "spicy"],
        },
        {
            "restaurant_name": "Spice Route",
            "name": "Dal Tadka",
            "description": "Yellow lentils tempered with cumin and garlic",
            "price": 9.99,
            "calories": 320,
            "protein_g": 16,
            "carbs_g": 45,
            "fat_g": 8,
            "mood_tags": ["light", "comforting", "vegetarian"],
        },
        {
            "restaurant_name": "Dhaka Kitchen",
            "name": "Beef Bhuna",
            "description": "Slow cooked beef in a thick spiced gravy",
            "price": 15.99,
            "calories": 580,
            "protein_g": 42,
            "carbs_g": 20,
            "fat_g": 35,
            "mood_tags": ["indulgent", "spicy", "comforting"],
        },
        {
            "restaurant_name": "Dhaka Kitchen",
            "name": "Bhuna Khichuri",
            "description": "Rice and lentils cooked with warming spices",
            "price": 11.99,
            "calories": 480,
            "protein_g": 18,
            "carbs_g": 70,
            "fat_g": 12,
            "mood_tags": ["comforting", "light"],
        },
        {
            "restaurant_name": "Golden Wok",
            "name": "Vegetable Fried Rice",
            "description": "Wok tossed rice with mixed vegetables",
            "price": 8.99,
            "calories": 420,
            "protein_g": 10,
            "carbs_g": 65,
            "fat_g": 12,
            "mood_tags": ["quick", "light"],
        },
        {
            "restaurant_name": "Golden Wok",
            "name": "Kung Pao Chicken",
            "description": "Diced chicken with peanuts and chili peppers",
            "price": 12.99,
            "calories": 550,
            "protein_g": 32,
            "carbs_g": 35,
            "fat_g": 28,
            "mood_tags": ["spicy", "energizing"],
        },
        {
            "restaurant_name": "Verde Trattoria",
            "name": "Margherita Pizza",
            "description": "San Marzano tomatoes, fresh mozzarella, basil",
            "price": 16.99,
            "calories": 700,
            "protein_g": 28,
            "carbs_g": 80,
            "fat_g": 30,
            "mood_tags": ["comforting", "indulgent"],
        },
        {
            "restaurant_name": "Verde Trattoria",
            "name": "Grilled Salmon Salad",
            "description": "Salmon over greens with a lemon vinaigrette",
            "price": 18.99,
            "calories": 410,
            "protein_g": 35,
            "carbs_g": 15,
            "fat_g": 22,
            "mood_tags": ["light", "energizing"],
        },
    ]

    for data in dishes_data:
        restaurant_name = data.pop("restaurant_name")
        dish = Dish(restaurant_id=restaurants[restaurant_name].id, **data)
        db.add(dish)

    db.commit()
    db.close()
    print(f"Seeded {len(restaurants_data)} restaurants and {len(dishes_data)} dishes.")


if __name__ == "__main__":
    seed()
