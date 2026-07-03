import { useEffect, useState } from 'react'
import { Link, createFileRoute } from '@tanstack/react-router'
import { api, fmtNum, fmtPct } from '../lib/api'
import type { RunDetail, RunSummary } from '../lib/api'
import { QuarterBars } from '../components/QuarterBars'
import { EquityChart } from '../components/EquityChart'

export const Route = createFileRoute('/')({
  component: Dashboard,
  ssr: false,
})

function Dashboard() {
  const [latest, setLatest] = useState<RunDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listRuns()
      .then((runs: RunSummary[]) => {
        const done = runs.find((r) => r.status === 'done')
        if (!done) {
          setLoading(false)
          return
        }
        return api.getRun(done.id).then((d) => {
          setLatest(d)
          setLoading(false)
        })
      })
      .catch((e) => {
        setError(String(e.message ?? e))
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="page">Chargement…</div>
  if (error)
    return (
      <div className="page">
        <div className="error-banner">
          API injoignable : {error}. Démarre le backend : <span className="mono">uvicorn smc_ai.api.app:app --port 8000</span>
        </div>
      </div>
    )
  if (!latest)
    return (
      <div className="page">
        <h1>Dashboard</h1>
        <p className="subtitle">Aucun backtest terminé pour l'instant.</p>
        <Link to="/backtests" className="btn">
          Lancer un premier backtest
        </Link>
      </div>
    )

  const quarters = latest.quarters.filter((q) => q.label !== 'FULL')
  const valid = quarters.filter((q) => !q.error)
  const totalTrades = valid.reduce((s, q) => s + Number(q.kpis.total_trades ?? 0), 0)
  const totalPnl = valid.reduce(
    (s, q) => s + (Number(q.kpis.ending_balance ?? 10000) - Number(q.kpis.starting_balance ?? 10000)),
    0,
  )
  const lastQ = valid[valid.length - 1]

  // Courbe d'equity cumulée sur tous les trimestres
  let cumulative = 10000
  const cumulativeCurve = valid.flatMap((q) => {
    const base = 10000
    return q.equity_curve.map((p) => ({
      timestamp: p.timestamp,
      equity: Math.round((cumulative + (p.equity - base)) * 100) / 100,
    }))
  })
  valid.forEach((q) => {
    const last = q.equity_curve[q.equity_curve.length - 1]
    if (last) cumulative += last.equity - 10000
  })

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="subtitle">
        Dernier run : #{latest.id} — {latest.symbol} ({latest.kind}) —{' '}
        <Link to="/backtests/$runId" params={{ runId: String(latest.id) }}>
          voir le détail
        </Link>
      </p>

      <div className="grid kpis">
        <Kpi label="Trades (total)" value={String(totalTrades)} />
        <Kpi
          label="P&L cumulé"
          value={`${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(0)} $`}
          tone={totalPnl >= 0 ? 'pos' : 'neg'}
        />
        <Kpi label="Dernier trimestre" value={lastQ ? lastQ.label : '—'} />
        <Kpi label="Win rate (dernier T)" value={lastQ ? fmtPct(lastQ.kpis.win_rate) : '—'} />
        <Kpi
          label="EV (dernier T)"
          value={lastQ ? `${fmtNum(lastQ.kpis.expectancy_r, 3)}R` : '—'}
          tone={lastQ && Number(lastQ.kpis.expectancy_r) >= 0 ? 'pos' : 'neg'}
        />
        <Kpi label="Profit factor (dernier T)" value={lastQ ? fmtNum(lastQ.kpis.profit_factor) : '—'} />
      </div>

      <h2>Évolution trimestrielle (expectancy)</h2>
      <div className="card">
        <QuarterBars quarters={quarters} />
      </div>

      <h2>Courbe d'equity (cumulée)</h2>
      <div className="card">
        <EquityChart points={cumulativeCurve} />
      </div>

      <h2>Trimestres</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Trimestre</th>
              <th>Trades</th>
              <th>Win rate</th>
              <th>Profit factor</th>
              <th>EV</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            {quarters.map((q) => {
              const pnl = Number(q.kpis.ending_balance ?? 10000) - 10000
              return (
                <tr key={q.label}>
                  <td>{q.label}</td>
                  {q.error ? (
                    <td colSpan={5} className="muted">
                      Erreur : {q.error}
                    </td>
                  ) : (
                    <>
                      <td>{String(q.kpis.total_trades ?? '—')}</td>
                      <td>{fmtPct(q.kpis.win_rate)}</td>
                      <td>{fmtNum(q.kpis.profit_factor)}</td>
                      <td>{fmtNum(q.kpis.expectancy_r, 3)}R</td>
                      <td style={{ color: pnl >= 0 ? 'var(--green)' : 'var(--red)' }}>
                        {pnl >= 0 ? '+' : ''}
                        {pnl.toFixed(0)} $
                      </td>
                    </>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Kpi({ label, value, tone }: { label: string; value: string; tone?: 'pos' | 'neg' }) {
  return (
    <div className="card kpi">
      <div className="label">{label}</div>
      <div className={`value ${tone ?? ''}`}>{value}</div>
    </div>
  )
}
