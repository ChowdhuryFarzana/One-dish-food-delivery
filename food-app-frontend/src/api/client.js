const BASE_URL = 'http://localhost:8000'

export async function getRestaurants() {
  const response = await fetch(`${BASE_URL}/restaurants/`)
  if (!response.ok) {
    throw new Error('Failed to fetch restaurants')
  }
  return response.json()
}

export async function getDishes(restaurantId) {
  const params = new URLSearchParams()
  if (restaurantId) params.append('restaurant_id', restaurantId)

  const response = await fetch(`${BASE_URL}/dishes/?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch dishes')
  }
  return response.json()
}

export async function getDishNutrients(dishId) {
  const response = await fetch(`${BASE_URL}/dishes/${dishId}/nutrients`)
  if (!response.ok) {
    throw new Error('Failed to fetch dish nutrients')
  }
  return response.json()
}

export async function moodMatch({ moods, minCalories, maxCalories, excludeTags, userId }) {
  const params = new URLSearchParams()
  moods.forEach((m) => params.append('moods', m))
  excludeTags.forEach((t) => params.append('exclude_tag', t))
  if (minCalories) params.append('min_calories', minCalories)
  if (maxCalories) params.append('max_calories', maxCalories)
  if (userId) params.append('user_id', userId)

  const response = await fetch(`${BASE_URL}/dishes/mood-match?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Mood match request failed')
  }
  return response.json()
}

export async function nutritionSearch({ nutrient, minPercentDv, maxCalories, userId }) {
  const params = new URLSearchParams()
  params.append('nutrient', nutrient)
  if (minPercentDv) params.append('min_percent_dv', minPercentDv)
  if (maxCalories) params.append('max_calories', maxCalories)
  if (userId) params.append('user_id', userId)

  const response = await fetch(`${BASE_URL}/dishes/nutrition-search?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Nutrition search request failed')
  }
  return response.json()
}

export async function quickMode({ latitude, longitude, radiusKm }) {
  const params = new URLSearchParams()
  params.append('latitude', latitude)
  params.append('longitude', longitude)
  params.append('radius_km', radiusKm)

  const response = await fetch(`${BASE_URL}/restaurants/quick-mode?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Quick mode request failed')
  }
  return response.json()
}

export async function createOrder({ userId, restaurantId, items }) {
  const response = await fetch(`${BASE_URL}/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      restaurant_id: restaurantId,
      items: items.map((i) => ({
        dish_id: i.dish.id,
        quantity: i.quantity,
        special_instructions: i.specialInstructions || null,
      })),
    }),
  })
  if (!response.ok) {
    throw new Error('Failed to create order')
  }
  return response.json()
}

export async function updateOrderStatus(orderId, status) {
  const response = await fetch(`${BASE_URL}/orders/${orderId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  if (!response.ok) {
    throw new Error('Failed to update order status')
  }
  return response.json()
}

export async function createReview({ userId, orderId, dishId, restaurantId, foodRating, deliveryRating, platformRating, text }) {
  const response = await fetch(`${BASE_URL}/reviews/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      order_id: orderId,
      dish_id: dishId,
      restaurant_id: restaurantId,
      food_rating: foodRating,
      delivery_rating: deliveryRating,
      platform_rating: platformRating,
      text: text || null,
    }),
  })
  if (!response.ok) {
    throw new Error('Failed to submit review')
  }
  return response.json()
}

export async function getUser(userId) {
  const response = await fetch(`${BASE_URL}/users/${userId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch user')
  }
  return response.json()
}

export async function updateUser(userId, updates) {
  const response = await fetch(`${BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  })
  if (!response.ok) {
    throw new Error('Failed to update user')
  }
  return response.json()
}
