import { useState } from 'react'
import { nutritionSearch } from '../api/client'
import { CURRENT_USER_ID } from '../api/constants'
import { CURRENT_USER_ID } from '../api/constants'

const NUTRIENTS = ['fiber', 'calcium', 'iron', 'potassium', 'sodium', 'vitamin_c', 'vitamin_a', 'vitamin_d', 'vitamin_b12']

function formatNutrientLabel(nutrient) {
  return nutrient.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function NutritionSearch() {
  const [nutrient, setNutrient] = useState('vitamin_d')
  const [minPercentDv, setMinPercentDv] = useState('')
  const [maxCalories, setMaxCalories] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  async function handleSearch() {
    setError('')
    setLoading(true)
    setSearched(true)
    try {
      const data = await nutritionSearch({ nutrient, minPercentDv, maxCalories, userId: CURRENT_USER_ID })
      setResults(data)
    } catch {
      setError('Something went wrong fetching results')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <h2 className="panel-heading">Find dishes by nutrient</h2>
      <p className="panel-subtext">Low on something? Search dishes ranked by how much of your daily value they cover.</p>

      <div className="field-row">
        <div>
          <label className="field-label">Nutrient</label>
          <select value={nutrient} onChange={(e) => setNutrient(e.target.value)} style={{ minWidth: 170 }}>
            {NUTRIENTS.map((n) => (
              <option key={n} value={n}>{formatNutrientLabel(n)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="field-label">Min % daily value</label>
          <input
            type="number"
            value={minPercentDv}
            onChange={(e) => setMinPercentDv(e.target.value)}
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
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}
      {searched && !loading && results.length === 0 && !error && (
        <p className="empty-text">No dishes matched those filters.</p>
      )}

      {results.map((dish) => (
        <div key={dish.dish_id} className="card">
          <div className="card-row">
            <p className="card-title">{dish.dish_name}</p>
            <span className="data card-meta">{dish.calories} kcal</span>
          </div>
          <p className="card-meta data">
            {formatNutrientLabel(dish.matched_nutrient)}: {dish.amount}{dish.unit.toLowerCase()}
            {dish.percent_daily_value != null && ` (${dish.percent_daily_value}% DV)`}
          </p>
        </div>
      ))}
    </div>
  )
}

export default NutritionSearch
