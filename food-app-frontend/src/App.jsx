import { useEffect, useState } from 'react'
import Home from './components/Home'
import MoodMatch from './components/MoodMatch'
import NutritionSearch from './components/NutritionSearch'
import QuickMode from './components/QuickMode'
import Cart from './components/Cart'
import Profile from './components/Profile'

function App() {
  const [status, setStatus] = useState('checking...')
  const [activeTab, setActiveTab] = useState('home')
  const [cartItems, setCartItems] = useState([])
  const [cartRestaurantId, setCartRestaurantId] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus('backend unreachable'))
  }, [])

  function addToCart(dish, restaurant) {
    if (cartRestaurantId && cartRestaurantId !== restaurant.id) {
      const confirmed = window.confirm(
        'Your cart has items from a different restaurant. Clear it and start a new cart?'
      )
      if (!confirmed) return
      setCartItems([])
    }
    setCartRestaurantId(restaurant.id)
    setCartItems((prev) => {
      const existing = prev.find((item) => item.dish.id === dish.id)
      if (existing) {
        return prev.map((item) =>
          item.dish.id === dish.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      }
      return [...prev, { dish, quantity: 1 }]
    })
  }

  function updateQuantity(dishId, newQuantity) {
    if (newQuantity <= 0) {
      removeFromCart(dishId)
      return
    }
    setCartItems((prev) =>
      prev.map((item) => (item.dish.id === dishId ? { ...item, quantity: newQuantity } : item))
    )
  }

  function removeFromCart(dishId) {
    setCartItems((prev) => prev.filter((item) => item.dish.id !== dishId))
  }

  function handleOrderPlaced() {
    setCartItems([])
    setCartRestaurantId(null)
  }

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0)

  const TABS = [
    { id: 'home', label: 'Browse', render: () => <Home onAddToCart={addToCart} /> },
    { id: 'mood', label: 'Mood Match', render: () => <MoodMatch /> },
    { id: 'nutrition', label: 'Nutrition', render: () => <NutritionSearch /> },
    { id: 'quick', label: 'Quick Mode', render: () => <QuickMode /> },
    {
      id: 'cart',
      label: `Cart${cartCount > 0 ? ` (${cartCount})` : ''}`,
      render: () => (
        <Cart
          cartItems={cartItems}
          restaurantId={cartRestaurantId}
          onUpdateQuantity={updateQuantity}
          onRemove={removeFromCart}
          onOrderPlaced={handleOrderPlaced}
        />
      ),
    },
    { id: 'profile', label: 'Profile', render: () => <Profile /> },
  ]

  const activeTabConfig = TABS.find((t) => t.id === activeTab)

  return (
    <div className="app-shell">
      <div className="app-header">
        <h1 className="app-title">Mishti</h1>
        <p className="app-status">backend: {status}</p>
        <div className="tab-bar">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button${activeTab === tab.id ? ' active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      {activeTabConfig.render()}
    </div>
  )
}

export default App
