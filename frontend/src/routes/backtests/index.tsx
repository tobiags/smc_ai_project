import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, createFileRoute } from '@tanstack/react-router'
import { api } from '../../lib/api'
import type { RunSummary } from '../../lib/api'

export const Route = createFileRoute('/backtests/')({
  component: BacktestsPage,
  ssr: false,
})

function BacktestsPage() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    symbol: 'EURUSD',
    kind: 'quarterly',
    min_rr: '2.5',
    scan_step: '120',
    sim_horizon: '500',
  })
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const refresh = useCallback(() => {
    api
      .listRuns()
      .then((r) => {
        setRuns(r)
        setError(null)
        // continue le polling tant qu'un run est actif
        const active = r.some((x) => x.status === 'pending' || x.status === 'running')
        if (!active && pollRef.current) {
          clearInterval(pollRef.current)
          pollRef.current = null
        }
        if (active && !pollRef.current) {
          pollRef.current = setInterval(refresh, 2000)
        }
      })
      .catch((e) => setError(String(e.message ?? e)))
  }, [])

  useEffect(() => {
    refresh()
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [refresh])

  const launch = () => {
    setSubmitting(true)
    api
      .createRun({
        symbol: form.symbol,
        kind: form.kind,
        min_rr: parseFloat(form.min_rr),
        scan_step: parseInt(form.scan_step, 10),
        sim_horizon: parseInt(form.sim_horizon, 10),
      })
      .then(() => refresh())
      .catch((e) => setError(String(e.message ?? e)))
      .finally(() => setSubmitting(false))
  }

  const remove = (id: number) => {
    api
      .deleteRun(id)
      .then(() => refresh())
      .catch((e) => setError(String(e.message ?? e)))
  }

  return (
    <div className="page">
      <h1>Backtests</h1>
      <p className="subtitle">Lance un backtest et suis son avancement — les résultats sont persistés en base.</p>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-row">
          <div>
            <label>Symbole</label>
            <input
              value={form.symbol}
              onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
            />
          </div>
          <div>
            <label>Type</label>
            <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
              <option value="quarterly">Par trimestre</option>
              <option value="full">Global</option>
            </select>
          </div>
          <div>
            <label>RR min</label>
            <input value={form.min_rr} onChange={(e) => setForm({ ...form, min_rr: e.target.value })} />
          </div>
          <div>
            <label>Scan step (M15)</label>
            <input
              value={form.scan_step}
              onChange={(e) => setForm({ ...form, scan_step: e.target.value })}
            />
          </div>
          <div>
            <label>Horizon simu</label>
            <input
              value={form.sim_horizon}
              onChange={(e) => setForm({ ...form, sim_horizon: e.target.value })}
            />
          </div>
          <div>
            <button onClick={launch} disabled={submitting}>
              {submitting ? 'Lancement…' : '▶ Lancer'}
            </button>
          </div>
        </div>
      </div>

      <h2>Historique</h2>
      <div className="card">
        {runs.length === 0 ? (
          <p className="muted">Aucun run pour l'instant.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Symbole</th>
                <th>Type</th>
                <th>RR</th>
                <th>Scan</th>
                <th>Statut</th>
                <th>Créé le</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>
                    <Link to="/backtests/$runId" params={{ runId: String(r.id) }}>
                      #{r.id}
                    </Link>
                  </td>
                  <td>{r.symbol}</td>
                  <td>{r.kind === 'quarterly' ? 'Trimestriel' : 'Global'}</td>
                  <td>{r.min_rr}</td>
                  <td>{r.scan_step}</td>
                  <td>
                    <span className={`badge ${r.status}`}>{statusLabel(r.status)}</span>
                    {r.error && <div className="muted mono">{r.error}</div>}
                  </td>
                  <td className="muted">{r.created_at ? new Date(r.created_at).toLocaleString('fr-FR') : '—'}</td>
                  <td>
                    <button className="danger" onClick={() => remove(r.id)}>
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function statusLabel(s: string): string {
  switch (s) {
    case 'done':
      return 'Terminé'
    case 'failed':
      return 'Échec'
    case 'running':
      return 'En cours'
    case 'pending':
      return 'En attente'
    default:
      return s
  }
}
