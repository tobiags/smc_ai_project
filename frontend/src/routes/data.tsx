import { useCallback, useEffect, useRef, useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { api } from '../lib/api'
import type { Dataset } from '../lib/api'

export const Route = createFileRoute('/data')({
  component: DataPage,
  ssr: false,
})

function DataPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [symbol, setSymbol] = useState('EURUSD')
  const [bars, setBars] = useState('25000')
  const [fetchState, setFetchState] = useState<{ status: string; message: string }>({
    status: 'idle',
    message: '',
  })
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const refresh = useCallback(() => {
    api.listDatasets().then(setDatasets).catch((e) => setError(String(e.message ?? e)))
  }, [])

  const pollFetch = useCallback(() => {
    api
      .fetchStatus()
      .then((s) => {
        setFetchState(s)
        if (s.status !== 'running' && s.status !== 'starting' && pollRef.current) {
          clearInterval(pollRef.current)
          pollRef.current = null
          refresh()
        }
      })
      .catch(() => undefined)
  }, [refresh])

  useEffect(() => {
    refresh()
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [refresh])

  const startFetch = () => {
    setError(null)
    api
      .startFetch(symbol, parseInt(bars, 10))
      .then(() => {
        setFetchState({ status: 'starting', message: '' })
        if (!pollRef.current) pollRef.current = setInterval(pollFetch, 3000)
      })
      .catch((e) => setError(String(e.message ?? e)))
  }

  const busy = fetchState.status === 'running' || fetchState.status === 'starting'

  return (
    <div className="page">
      <h1>Données</h1>
      <p className="subtitle">
        Fichiers OHLCV disponibles pour le backtest, et téléchargement Twelve Data (D1 + H4 + M15).
      </p>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-row">
          <div>
            <label>Symbole</label>
            <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
          </div>
          <div>
            <label>Bougies M15</label>
            <input value={bars} onChange={(e) => setBars(e.target.value)} />
          </div>
          <div>
            <button onClick={startFetch} disabled={busy}>
              {busy ? 'Téléchargement…' : '⬇ Télécharger'}
            </button>
          </div>
        </div>
        {fetchState.status !== 'idle' && (
          <p className={fetchState.status === 'failed' ? 'error-banner' : 'muted'} style={{ marginTop: 12 }}>
            {fetchState.status === 'running' && '⏳ '}
            {fetchState.status === 'done' && '✅ '}
            {fetchState.status === 'failed' && '❌ '}
            {fetchState.message || fetchState.status}
          </p>
        )}
        <p className="muted" style={{ marginTop: 8 }}>
          Limite plan gratuit : 8 requêtes/minute — 25 000 bougies M15 ≈ 5 pages ≈ 1 minute.
        </p>
      </div>

      <h2>Fichiers CSV</h2>
      <div className="card">
        {datasets.length === 0 ? (
          <p className="muted">Aucun fichier dans data/.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Fichier</th>
                <th>Symbole</th>
                <th>Timeframe</th>
                <th>Lignes</th>
                <th>Du</th>
                <th>Au</th>
                <th>Taille</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.file}>
                  <td className="mono">{d.file}</td>
                  <td>{d.symbol}</td>
                  <td>{d.timeframe}</td>
                  <td>{d.rows.toLocaleString('fr-FR')}</td>
                  <td className="mono">{d.first ? String(d.first).slice(0, 10) : '—'}</td>
                  <td className="mono">{d.last ? String(d.last).slice(0, 10) : '—'}</td>
                  <td>{d.size_kb} Ko</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
