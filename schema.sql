/* Core schema for the food review and recipe app
   Run against a fresh PostgreSQL database.
   This is the foundation every later feature (mood matching,
   nutrition curation, ranking models) will read from. */

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    dietary_restrictions TEXT[] DEFAULT '{}',
    allergy_list TEXT[] DEFAULT '{}',
    calorie_target INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    cuisine_type VARCHAR(100),
    price_tier SMALLINT CHECK (price_tier BETWEEN 1 AND 4),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    avg_prep_minutes INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE dishes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(8, 2) NOT NULL,
    calories INT,
    protein_g NUMERIC(6, 2),
    carbs_g NUMERIC(6, 2),
    fat_g NUMERIC(6, 2),
    mood_tags TEXT[] DEFAULT '{}',
    photo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

/* Micronutrients live in their own table since not every dish
   will have this data, and the list of tracked nutrients will grow */
CREATE TABLE dish_nutrients (
    dish_id UUID NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    nutrient_name VARCHAR(50) NOT NULL,
    amount NUMERIC(8, 3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    percent_daily_value NUMERIC(5, 2),
    PRIMARY KEY (dish_id, nutrient_name)
);

CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    discount_type VARCHAR(50) NOT NULL,
    discount_value NUMERIC(6, 2) NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    status VARCHAR(30) NOT NULL DEFAULT 'placed',
    eta_estimate_minutes INT,
    actual_delivery_minutes INT,
    total_price NUMERIC(8, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    dish_id UUID NOT NULL REFERENCES dishes(id),
    quantity INT NOT NULL DEFAULT 1,
    special_instructions TEXT
);

/* Reviews are split into three axes on purpose, so a restaurant
   is not unfairly blamed for a delivery problem and vice versa */
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    order_id UUID REFERENCES orders(id),
    dish_id UUID REFERENCES dishes(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    food_rating SMALLINT CHECK (food_rating BETWEEN 1 AND 5),
    delivery_rating SMALLINT CHECK (delivery_rating BETWEEN 1 AND 5),
    platform_rating SMALLINT CHECK (platform_rating BETWEEN 1 AND 5),
    text TEXT,
    photo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

/* Event log for every search, filter, click, and order.
   This is the table Phase 3 model training reads from,
   so start writing to it from day one even before any model exists. */
CREATE TABLE interaction_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    dish_id UUID REFERENCES dishes(id),
    restaurant_id UUID REFERENCES restaurants(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_dishes_restaurant ON dishes(restaurant_id);
CREATE INDEX idx_dishes_mood_tags ON dishes USING GIN(mood_tags);
CREATE INDEX idx_restaurants_location ON restaurants(latitude, longitude);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_reviews_restaurant ON reviews(restaurant_id);
CREATE INDEX idx_interaction_events_user ON interaction_events(user_id);
CREATE INDEX idx_interaction_events_type ON interaction_events(event_type);