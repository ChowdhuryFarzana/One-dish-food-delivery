import { useState } from 'react'
import { moodMatch } from '../api/client'
import { CURRENT_USER_ID } from '../api/constants'

const AVAILABLE_MOODS = ['comforting', 'indulgent', 'spicy', 'light', 'energizing', 'vegetarian']

function MoodMatch() {
  const [selectedMoods, setSelectedMoods] = useState([])
  const [excludedMoods, setExcludedMoods] = useState([])
  const [minCalories, setMinCalories] = useState('')
  const [maxCalories, setMaxCalories] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function toggleMood(mood) {
    setSelectedMoods((prev) => (prev.includes(mood) ? prev.filter((m) => m !== mood) : [...prev, mood]))
  }

  function toggleExclude(mood) {
    setExcludedMoods((prev) => (prev.includes(mood) ? prev.filter((m) => m !== mood) : [...prev, mood]))
  }

  async function handleSearch() {
    if (selectedMoods.length === 0) {
      setError('Pick at least one mood')
      return
    }
    setError('')
    setLoading(true)
    try {
      const data = await moodMatch({ moods: selectedMoods, minCalories, maxCalories, excludeTags: excludedMoods, userId: CURRENT_USER_ID })
      setResults(data)
    } catch {
      setError('Something went wrong fetching results')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <h2 className="panel-heading">What are you in the mood for?</h2>
      <p className="panel-subtext">Pick one or more moods. We'll rank dishes by how well they fit.</p>

      <div className="chip-row">
        {AVAILABLE_MOODS.map((mood) => (
          <button
            key={mood}
            onClick={() => toggleMood(mood)}
            className={`chip${selectedMoods.includes(mood) ? ' selected' : ''}`}
          >
            {mood}
          </button>
        ))}
      </div>

      <label className="field-label">Exclude</label>
      <div className="chip-row">
        {AVAILABLE_MOODS.map((mood) => (
          <button
            key={`exclude-${mood}`}
            onClick={() => toggleExclude(mood)}
            className={`chip${excludedMoods.includes(mood) ? ' excluded' : ''}`}
          >
            {mood}
          </button>
        ))}
      </div>

      <div className="field-row">
        <div>
          <label className="field-label">Min calories</label>
          <input
            type="number"
            value={minCalories}
            onChange={(e) => setMinCalories(e.target.value)}
            className="input"
            style={{ width: 90 }}
          />
        </div>
        <div>
          <label className="field-label">Max calories</label>
          <input
            type="number"
            value={maxCalories}
            onChange={(e) => setMaxCalories(e.target.value)}
            className="input"
            style={{ width: 90 }}
          />
        </div>
        <button onClick={handleSearch} disabled={loading} className="btn">
          {loading ? 'Searching...' : 'Find dishes'}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {results.map((dish) => (
        <div key={dish.dish_id} className="card">
          <div className="card-row">
            <p className="card-title">{dish.dish_name}</p>
            <span className="data card-title">${dish.price.toFixed(2)}</span>
          </div>
          <p className="card-meta data">
            {dish.restaurant_name} · {dish.calories} kcal
          </p>
          <p className="card-desc" style={{ marginTop: '0.4rem' }}>{dish.reason}</p>
          <p className="muted data" style={{ fontSize: '0.75rem' }}>score: {dish.score}</p>
        </div>
      ))}
    </div>
  )
}

export default MoodMatch
