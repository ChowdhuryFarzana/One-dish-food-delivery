import { useState } from 'react'
import { createOrder, updateOrderStatus, createReview } from '../api/client'
import { CURRENT_USER_ID } from '../api/constants'

function Cart({ cartItems, restaurantId, onUpdateQuantity, onRemove, onOrderPlaced }) {
  const [placingOrder, setPlacingOrder] = useState(false)
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')
  const [reviewText, setReviewText] = useState('')
  const [foodRating, setFoodRating] = useState(5)
  const [deliveryRating, setDeliveryRating] = useState(5)
  const [reviewSubmitted, setReviewSubmitted] = useState(false)

  const total = cartItems.reduce((sum, item) => sum + item.dish.price * item.quantity, 0)

  async function handleCheckout() {
    setPlacingOrder(true)
    setError('')
    try {
      const newOrder = await createOrder({ userId: CURRENT_USER_ID, restaurantId, items: cartItems })
      setOrder(newOrder)
      onOrderPlaced()
    } catch {
      setError('Could not place order')
    } finally {
      setPlacingOrder(false)
    }
  }

  async function handleMarkDelivered() {
    try {
      const updated = await updateOrderStatus(order.id, 'delivered')
      setOrder(updated)
    } catch {
      setError('Could not update order status')
    }
  }

  async function handleSubmitReview() {
    try {
      await createReview({
        userId: CURRENT_USER_ID,
        orderId: order.id,
        dishId: order.items[0]?.dish_id,
        restaurantId: order.restaurant_id,
        foodRating,
        deliveryRating,
        platformRating: 5,
        text: reviewText,
      })
      setReviewSubmitted(true)
    } catch {
      setError('Could not submit review')
    }
  }

  if (order) {
    return (
      <div className="panel">
        <h2 className="panel-heading">Order placed</h2>
        <div className="card">
          <p style={{ margin: '0 0 0.5rem' }}>
            Status: <strong className="data">{order.status}</strong>
          </p>
          <p className="data" style={{ margin: '0 0 0.5rem' }}>Total: ${order.total_price.toFixed(2)}</p>
          <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
            {order.items.map((item) => (
              <li key={item.id} className="muted">
                {item.quantity}x {item.special_instructions ? `(${item.special_instructions})` : ''}
              </li>
            ))}
          </ul>
        </div>

        {order.status !== 'delivered' && (
          <button onClick={handleMarkDelivered} className="btn btn-ghost" style={{ marginBottom: '1.5rem' }}>
            Mark as delivered
          </button>
        )}

        {order.status === 'delivered' && !reviewSubmitted && (
          <div className="card">
            <p className="card-title">Leave a review</p>
            <div className="field-row">
              <div>
                <label className="field-label">Food rating</label>
                <select value={foodRating} onChange={(e) => setFoodRating(Number(e.target.value))}>
                  {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              <div>
                <label className="field-label">Delivery rating</label>
                <select value={deliveryRating} onChange={(e) => setDeliveryRating(Number(e.target.value))}>
                  {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
            </div>
            <textarea
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="How was it?"
              style={{ marginBottom: '0.75rem' }}
            />
            <button onClick={handleSubmitReview} className="btn">Submit review</button>
          </div>
        )}

        {reviewSubmitted && <p className="success-text">Review submitted, thank you.</p>}
        {error && <p className="error-text">{error}</p>}
      </div>
    )
  }

  return (
    <div className="panel">
      <h2 className="panel-heading">Cart</h2>

      {cartItems.length === 0 && <p className="empty-text">Your cart is empty. Add dishes from Browse.</p>}

      {cartItems.map((item) => (
        <div key={item.dish.id} className="card">
          <div className="card-row" style={{ alignItems: 'center' }}>
            <div>
              <p className="card-title" style={{ marginBottom: '0.15rem' }}>{item.dish.name}</p>
              <p className="card-meta data">${item.dish.price.toFixed(2)} each</p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button onClick={() => onUpdateQuantity(item.dish.id, item.quantity - 1)} className="btn-icon">-</button>
              <span className="data">{item.quantity}</span>
              <button onClick={() => onUpdateQuantity(item.dish.id, item.quantity + 1)} className="btn-icon">+</button>
              <button onClick={() => onRemove(item.dish.id)} className="link-danger" style={{ marginLeft: '0.5rem' }}>
                remove
              </button>
            </div>
          </div>
        </div>
      ))}

      {cartItems.length > 0 && (
        <>
          <p className="data card-title" style={{ marginTop: '1rem' }}>Total: ${total.toFixed(2)}</p>
          <button onClick={handleCheckout} disabled={placingOrder} className="btn">
            {placingOrder ? 'Placing order...' : 'Checkout'}
          </button>
        </>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  )
}

export default Cart
