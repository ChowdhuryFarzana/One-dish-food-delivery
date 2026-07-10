import { useEffect, useState } from 'react'
import { getRestaurants, getDishes, getDishNutrients } from '../api/client'
import NutrientProfile from './NutrientProfile'

function Home({ onAddToCart }) {
  const [restaurants, setRestaurants] = useState([])
  const [selectedRestaurant, setSelectedRestaurant] = useState(null)
  const [dishes, setDishes] = useState([])
  const [loadingRestaurants, setLoadingRestaurants] = useState(true)
  const [loadingDishes, setLoadingDishes] = useState(false)
  const [error, setError] = useState('')
  const [expandedDishId, setExpandedDishId] = useState(null)
  const [nutrientProfile, setNutrientProfile] = useState(null)
  const [loadingNutrients, setLoadingNutrients] = useState(false)

  useEffect(() => {
    getRestaurants()
      .then(setRestaurants)
      .catch(() => setError('Could not load restaurants'))
      .finally(() => setLoadingRestaurants(false))
  }, [])

  function selectRestaurant(restaurant) {
    setSelectedRestaurant(restaurant)
    setExpandedDishId(null)
    setNutrientProfile(null)
    setLoadingDishes(true)
    setError('')
    getDishes(restaurant.id)
      .then(setDishes)
      .catch(() => setError('Could not load dishes'))
      .finally(() => setLoadingDishes(false))
  }

  function toggleDish(dish) {
    if (expandedDishId === dish.id) {
      setExpandedDishId(null)
      setNutrientProfile(null)
      return
    }
    setExpandedDishId(dish.id)
    setLoadingNutrients(true)
    getDishNutrients(dish.id)
      .then(setNutrientProfile)
      .catch(() => setError('Could not load nutrition info'))
      .finally(() => setLoadingNutrients(false))
  }

  return (
    <div className="panel">
      <h2 className="panel-heading">Restaurants</h2>
      {loadingRestaurants && <p className="muted">Loading...</p>}
      {error && <p className="error-text">{error}</p>}

      <div className="chip-row" style={{ marginBottom: '1.5rem' }}>
        {restaurants.map((r) => (
          <div
            key={r.id}
            onClick={() => selectRestaurant(r)}
            className={`card selectable${selectedRestaurant?.id === r.id ? ' active' : ''}`}
            style={{ minWidth: 150, marginBottom: 0 }}
          >
            <p className="card-title" style={{ marginBottom: '0.15rem' }}>{r.name}</p>
            <p className="card-meta data">
              {r.cuisine_type} · {'$'.repeat(r.price_tier || 1)}
            </p>
          </div>
        ))}
      </div>

      {selectedRestaurant && (
        <>
          <h3 className="panel-heading" style={{ fontSize: '1.15rem' }}>{selectedRestaurant.name}</h3>
          {loadingDishes && <p className="muted">Loading dishes...</p>}
          {!loadingDishes && dishes.length === 0 && (
            <p className="empty-text">No dishes found for this restaurant.</p>
          )}
          {dishes.map((dish) => (
            <div key={dish.id}>
              <div className="card" style={{ marginBottom: expandedDishId === dish.id ? 0 : '0.85rem' }}>
                <div onClick={() => toggleDish(dish)} style={{ cursor: 'pointer' }}>
                  <div className="card-row">
                    <p className="card-title">{dish.name}</p>
                    <span className="data card-title">${dish.price.toFixed(2)}</span>
                  </div>
                  <p className="card-desc">{dish.description}</p>
                </div>
                <div className="card-row">
                  <p className="card-meta data">
                    {dish.calories} kcal · {dish.mood_tags.join(', ')}
                  </p>
                  <button onClick={() => onAddToCart(dish, selectedRestaurant)} className="btn btn-small">
                    Add to cart
                  </button>
                </div>
              </div>

              {expandedDishId === dish.id && (
                <div style={{ marginBottom: '0.85rem' }}>
                  {loadingNutrients && <p className="muted">Loading nutrition...</p>}
                  {!loadingNutrients && nutrientProfile && (
                    <NutrientProfile
                      profile={nutrientProfile}
                      onClose={() => {
                        setExpandedDishId(null)
                        setNutrientProfile(null)
                      }}
                    />
                  )}
                </div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  )
}

export default Home
