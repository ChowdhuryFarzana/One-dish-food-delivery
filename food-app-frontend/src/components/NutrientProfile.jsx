function formatNutrientLabel(nutrient) {
  return nutrient.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function NutrientProfile({ profile, onClose }) {
  if (!profile) return null

  const sortedNutrients = [...profile.nutrients].sort(
    (a, b) => (b.percent_daily_value || 0) - (a.percent_daily_value || 0)
  )

  return (
    <div className="card">
      <div className="card-row" style={{ marginBottom: '0.75rem' }}>
        <p className="card-title" style={{ marginBottom: 0 }}>{profile.dish_name}</p>
        <button onClick={onClose} className="link-danger">close ×</button>
      </div>

      <div className="macro-row data">
        <span><strong>{profile.calories}</strong> kcal</span>
        <span><strong>{profile.protein_g}</strong>g protein</span>
        <span><strong>{profile.carbs_g}</strong>g carbs</span>
        <span><strong>{profile.fat_g}</strong>g fat</span>
      </div>

      <table className="dv-table">
        <thead>
          <tr>
            <th>Nutrient</th>
            <th>Amount</th>
            <th>% Daily Value</th>
          </tr>
        </thead>
        <tbody>
          {sortedNutrients.map((n) => (
            <tr key={n.nutrient_name}>
              <td>{formatNutrientLabel(n.nutrient_name)}</td>
              <td className="data">
                {n.amount}{n.unit.toLowerCase()}
              </td>
              <td>
                {n.percent_daily_value != null ? (
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="dv-track">
                      <span
                        className="dv-fill"
                        style={{
                          width: `${Math.min(n.percent_daily_value, 100)}%`,
                          background: n.percent_daily_value >= 15 ? 'var(--color-cardamom)' : 'var(--color-clay)',
                        }}
                      />
                    </span>
                    <span className="data">{n.percent_daily_value}%</span>
                  </span>
                ) : (
                  <span className="muted">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted" style={{ fontSize: '0.75rem', marginTop: '0.75rem', marginBottom: 0 }}>
        Computed from an approximate ingredient breakdown against USDA FoodData Central, not lab-measured for this specific dish.
      </p>
    </div>
  )
}

export default NutrientProfile
