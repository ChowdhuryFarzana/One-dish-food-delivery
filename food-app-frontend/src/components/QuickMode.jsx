import { useState } from 'react'
import { quickMode } from '../api/client'

const DEFAULT_LAT = 41.307
const DEFAULT_LNG = -72.927

function QuickMode() {
  const [enabled, setEnabled] = useState(false)
  const [latitude, setLatitude] = useState(DEFAULT_LAT)
  const [longitude, setLongitude] = useState(DEFAULT_LNG)
  const [radiusKm, setRadiusKm] = useState(2)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [locationSource, setLocationSource] = useState('default')

  function useMyLocation() {
    if (!navigator.geolocation) {
      setError('Geolocation not available in this browser, using default location')
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(position.coords.latitude)
        setLongitude(position.coords.longitude)
        setLocationSource('device')
        setError('')
      },
      () => {
        setError('Location permission denied, using default location instead')
        setLocationSource('default')
      }
    )
  }

  async function handleSearch() {
    setError('')
    setLoading(true)
    try {
      const data = await quickMode({ latitude, longitude, radiusKm })
      setResults(data)
    } catch {
      setError('Something went wrong fetching results')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <div className="card-row" style={{ marginBottom: '0.5rem', alignItems: 'center' }}>
        <h2 className="panel-heading" style={{ marginBottom: 0 }}>Quick and affordable</h2>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--color-clay)' }}>
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />
          on
        </label>
      </div>

      {!enabled && (
        <p className="panel-subtext">
          Toggle this on to see nearby restaurants ranked by price and distance, with active offers surfaced first.
        </p>
      )}

      {enabled && (
        <>
          <div className="field-row">
            <button onClick={useMyLocation} className="btn btn-ghost btn-small">Use my location</button>
            <span className="muted data" style={{ fontSize: '0.78rem' }}>
              {locationSource === 'device' ? 'using device location' : 'using default location'}
            </span>
          </div>

          <div className="field-row">
            <div>
              <label className="field-label">Radius (km)</label>
              <input
                type="number"
                step="0.5"
                value={radiusKm}
                onChange={(e) => setRadiusKm(e.target.value)}
                className="input"
                style={{ width: 90 }}
              />
            </div>
            <button onClick={handleSearch} disabled={loading} className="btn">
              {loading ? 'Searching...' : 'Find nearby'}
            </button>
          </div>

          {error && <p className="error-text">{error}</p>}

          {results.map((r) => (
            <div key={r.restaurant_id} className="card">
              <div className="card-row">
                <p className="card-title">{r.name}</p>
                <span className="data card-meta">{r.distance_km} km</span>
              </div>
              <p className="card-meta data">
                {r.cuisine_type} · {'$'.repeat(r.price_tier || 1)} · ~{r.avg_prep_minutes} min
              </p>
              {r.active_offers.length > 0 && (
                <p style={{ marginTop: '0.5rem' }}>
                  {r.active_offers.map((o) => (
                    <span key={o.id} className="badge-offer">{o.discount_value}% off</span>
                  ))}
                </p>
              )}
              <p className="muted data" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>score: {r.score}</p>
            </div>
          ))}
        </>
      )}
    </div>
  )
}

export default QuickMode
