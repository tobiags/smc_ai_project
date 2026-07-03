import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, createFileRoute } from '@tanstack/react-router'
import { api, fmtNum, fmtPct } from '../../lib/api'
import type { RunDetail, TradeRow } from '../../lib/api'
import { EquityChart } from '../../components/EquityChart'
import { QuarterBars } from '../../components/QuarterBars'

export const Route = createFileRoute('/backtests/$runId')({
  component: RunDetailPage,
  ssr: false,
})

function RunDetailPage() {
  const { runId } = Route.useParams()
  const [run, setRun] = useState<RunDetail | null>(null)
  const [trades, setTrades] = useState<TradeRow[]>([])
  const [quarterFilter, setQuarterFilter] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const refresh = useCallback(() => {
    api
      .getRun(runId)
      .then((d) => {
        setRun(d)
        const active = d.status === 'pending' || d.status === 'running'
        if (!active && pollRef.current) {
          clearInterval(pollRef.current)
          pollRef.current = null
        }
        if (active && !pollRef.current) {
          pollRef.current = setInterval(refresh, 2000)
        }
      })
      .catch((e) => setError(String(e.message ?? e)))
  }, [runId])

  useEffect(() => {
    refresh()
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [refresh])

  useEffect(() => {
    if (run?.status === 'done') {
      api
        .getTrades(runId, quarterFilter || undefined)
        .then(setTrades)
        .catch((e) => setError(String(e.message ?? e)))
    }
  }, [runId, run?.status, quarterFilter])

  if (error) return <div className="page"><div className="error-banner">{error}</div></div>
  if (!run) return <div className="page">Chargement…</div>

  const quarters = run.quarters
  const labels = quarters.map((q) => q.label)

  return (
    <div className="page">
      <h1>
        Run #{run.id} — {run.symbol}
      </h1>
      <p className="subtitle">
        {run.kind === 'quarterly' ? 'Backtest trimestriel' : 'Backtest global'} · RR ≥ {run.min_rr} ·
        scan {run.scan_step} · <span className={`badge ${run.status}`}>{run.status}</span> ·{' '}
        <Link to="/backtests">← retour</Link>
      </p>

      {run.status === 'failed' && <div className="error-banner">{run.error}</div>}
      {(run.status === 'running' || run.status === 'pending') && (
        <div className="card">⏳ Backtest en cours… la page se met à jour automatiquement.</div>
      )}

      {quarters.length > 1 && (
        <>
          <h2>Évolution trimestrielle</h2>
          <div className="card">
            <QuarterBars quarters={quarters} />
          </div>
        </>
      )}

      {quarters.map((q) => (
        <div key={q.label}>
          <h2>{q.label}</h2>
          {q.error ? (
            <div className="error-banner">Échec : {q.error}</div>
          ) : (
            <>
              <div className="grid kpis">
                <Kpi label="Trades" value={String(q.kpis.total_trades ?? '—')} />
                <Kpi label="Win rate" value={fmtPct(q.kpis.win_rate)} />
                <Kpi label="Profit factor" value={fmtNum(q.kpis.profit_factor)} />
                <Kpi
                  label="Expectancy"
                  value={`${fmtNum(q.kpis.expectancy_r, 3)}R`}
                  tone={Number(q.kpis.expectancy_r) >= 0 ? 'pos' : 'neg'}
                />
                <Kpi label="Max drawdown" value={fmtPct(q.kpis.max_drawdown)} />
                <Kpi
                  label="Capital final"
                  value={`${fmtNum(q.kpis.ending_balance, 0)} $`}
                  tone={Number(q.kpis.ending_balance) >= 10000 ? 'pos' : 'neg'}
                />
              </div>
              {q.equity_curve.length > 0 && (
                <div className="card" style={{ marginTop: 12 }}>
                  <EquityChart points={q.equity_curve} />
                </div>
              )}
            </>
          )}
        </div>
      ))}

      {run.status === 'done' && (
        <>
          <h2>Trades</h2>
          {labels.length > 1 && (
            <div style={{ maxWidth: 240, marginBottom: 12 }}>
              <label>Filtrer par trimestre</label>
              <select value={quarterFilter} onChange={(e) => setQuarterFilter(e.target.value)}>
                <option value="">Tous</option>
                {labels.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="card">
            {trades.length === 0 ? (
              <p className="muted">Aucun trade.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Trimestre</th>
                    <th>Direction</th>
                    <th>Entrée</th>
                    <th>SL</th>
                    <th>TP</th>
                    <th>RR</th>
                    <th>Résultat</th>
                    <th>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((t) => (
                    <tr key={t.id}>
                      <td className="mono">{t.timestamp.slice(0, 16).replace('T', ' ')}</td>
                      <td>{t.quarter_label ?? '—'}</td>
                      <td>{t.direction === 'bullish' ? '📈 Achat' : '📉 Vente'}</td>
                      <td className="mono">{t.entry.toFixed(5)}</td>
                      <td className="mono">{t.stop_loss.toFixed(5)}</td>
                      <td className="mono">{t.take_profit.toFixed(5)}</td>
                      <td>{t.rr.toFixed(2)}</td>
                      <td>
                        <span className={`badge ${t.outcome}`}>{t.outcome.toUpperCase()}</span>
                      </td>
                      <td style={{ color: t.pnl >= 0 ? 'var(--green)' : 'var(--red)' }}>
                        {t.pnl >= 0 ? '+' : ''}
                        {t.pnl.toFixed(0)} $
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
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
