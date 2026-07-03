import { useEffect, useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { api } from '../lib/api'

export const Route = createFileRoute('/settings')({
  component: SettingsPage,
  ssr: false,
})

const LABELS: Record<string, string> = {
  default_symbol: 'Symbole par défaut',
  min_rr: 'RR minimum',
  scan_step: 'Scan step (bougies M15)',
  sim_horizon: 'Horizon de simulation',
  risk_per_trade_pct: 'Risque par trade (%)',
  starting_balance: 'Capital initial ($)',
}

function SettingsPage() {
  const [values, setValues] = useState<Record<string, string>>({})
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getSettings().then(setValues).catch((e) => setError(String(e.message ?? e)))
  }, [])

  const save = () => {
    setSaved(false)
    api
      .updateSettings(values)
      .then((v) => {
        setValues(v)
        setSaved(true)
      })
      .catch((e) => setError(String(e.message ?? e)))
  }

  return (
    <div className="page">
      <h1>Paramètres</h1>
      <p className="subtitle">Persistés en base de données (table settings).</p>

      {error && <div className="error-banner">{error}</div>}

      <div className="card" style={{ maxWidth: 520 }}>
        {Object.keys(LABELS).map((key) => (
          <div key={key} style={{ marginBottom: 14 }}>
            <label>{LABELS[key]}</label>
            <input
              value={values[key] ?? ''}
              onChange={(e) => setValues({ ...values, [key]: e.target.value })}
            />
          </div>
        ))}
        <button onClick={save}>Enregistrer</button>
        {saved && <span style={{ marginLeft: 12, color: 'var(--green)' }}>✅ Enregistré</span>}
      </div>
    </div>
  )
}
