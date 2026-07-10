import { useEffect, useState } from 'react'
import { getUser, updateUser } from '../api/client'
import { CURRENT_USER_ID } from '../api/constants'

const DIETARY_OPTIONS = ['vegetarian', 'vegan', 'gluten-free', 'halal', 'kosher', 'dairy-free']
const COMMON_ALLERGENS = ['peanuts', 'tree nuts', 'shellfish', 'eggs', 'dairy', 'soy']

function Profile() {
  const [user, setUser] = useState(null)
  const [dietaryRestrictions, setDietaryRestrictions] = useState([])
  const [allergies, setAllergies] = useState([])
  const [calorieTarget, setCalorieTarget] = useState('')
  const [customAllergen, setCustomAllergen] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getUser(CURRENT_USER_ID)
      .then((data) => {
        setUser(data)
        setDietaryRestrictions(data.dietary_restrictions)
        setAllergies(data.allergy_list)
        setCalorieTarget(data.calorie_target ?? '')
      })
      .catch(() => setError('Could not load profile'))
      .finally(() => setLoading(false))
  }, [])

  function toggleDietary(option) {
    setSaved(false)
    setDietaryRestrictions((prev) =>
      prev.includes(option) ? prev.filter((d) => d !== option) : [...prev, option]
    )
  }

  function toggleAllergen(option) {
    setSaved(false)
    setAllergies((prev) => (prev.includes(option) ? prev.filter((a) => a !== option) : [...prev, option]))
  }

  function addCustomAllergen() {
    const trimmed = customAllergen.trim().toLowerCase()
    if (!trimmed || allergies.includes(trimmed)) return
    setAllergies((prev) => [...prev, trimmed])
    setCustomAllergen('')
    setSaved(false)
  }

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      const updated = await updateUser(CURRENT_USER_ID, {
        dietary_restrictions: dietaryRestrictions,
        allergy_list: allergies,
        calorie_target: calorieTarget === '' ? null : Number(calorieTarget),
      })
      setUser(updated)
      setSaved(true)
    } catch {
      setError('Could not save profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="panel">
        <p className="muted">Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="panel">
      <h2 className="panel-heading">{user?.name}'s profile</h2>
      <p className="panel-subtext">
        These preferences aren't wired into search filters yet, this screen stores them for that to build on later.
      </p>

      <label className="field-label">Dietary restrictions</label>
      <div className="chip-row">
        {DIETARY_OPTIONS.map((option) => (
          <button
            key={option}
            onClick={() => toggleDietary(option)}
            className={`chip${dietaryRestrictions.includes(option) ? ' selected' : ''}`}
          >
            {option}
          </button>
        ))}
      </div>

      <label className="field-label">Allergies</label>
      <div className="chip-row">
        {COMMON_ALLERGENS.map((option) => (
          <button
            key={option}
            onClick={() => toggleAllergen(option)}
            className={`chip${allergies.includes(option) ? ' excluded' : ''}`}
          >
            {option}
          </button>
        ))}
        {allergies
          .filter((a) => !COMMON_ALLERGENS.includes(a))
          .map((option) => (
            <button key={option} onClick={() => toggleAllergen(option)} className="chip excluded">
              {option}
            </button>
          ))}
      </div>

      <div className="field-row" style={{ marginBottom: '0.75rem' }}>
        <input
          type="text"
          value={customAllergen}
          onChange={(e) => setCustomAllergen(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addCustomAllergen()}
          placeholder="add another allergy"
          className="input"
          style={{ width: 180 }}
        />
        <button onClick={addCustomAllergen} className="btn btn-ghost btn-small">Add</button>
      </div>

      <label className="field-label">Daily calorie target</label>
      <div className="field-row">
        <input
          type="number"
          value={calorieTarget}
          onChange={(e) => setCalorieTarget(e.target.value)}
          className="input"
          style={{ width: 110 }}
        />
        <button onClick={handleSave} disabled={saving} className="btn">
          {saving ? 'Saving...' : 'Save profile'}
        </button>
      </div>

      {saved && <p className="success-text">Saved.</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  )
}

export default Profile
