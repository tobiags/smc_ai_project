// Client API — toutes les requêtes passent par le proxy Vite /api → FastAPI :8000

export interface RunSummary {
  id: number
  symbol: string
  kind: 'quarterly' | 'full'
  min_rr: number
  scan_step: number
  sim_horizon: number
  status: 'pending' | 'running' | 'done' | 'failed'
  error: string | null
  created_at: string | null
  started_at: string | null
  finished_at: string | null
}

export interface Quarter {
  id: number
  run_id: number
  label: string
  start: string
  end: string
  kpis: Record<string, number | string | boolean>
  equity_curve: { timestamp: string; equity: number }[]
  error: string | null
}

export interface RunDetail extends RunSummary {
  quarters: Quarter[]
}

export interface TradeRow {
  id: number
  quarter_label: string | null
  symbol: string
  timestamp: string
  direction: string
  entry: number
  stop_loss: number
  take_profit: number
  rr: number
  pnl: number
  pnl_r: number
  outcome: string
  status: string
}

export interface Dataset {
  file: string
  symbol: string
  timeframe: string
  rows: number
  first: string | null
  last: string | null
  size_kb: number
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!resp.ok) {
    let detail = `${resp.status} ${resp.statusText}`
    try {
      const body = await resp.json()
      if (body.detail) detail = body.detail
    } catch {
      /* pas de corps JSON */
    }
    throw new Error(detail)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export const api = {
  health: () => request<{ status: string; busy: boolean }>('/api/health'),
  listRuns: () => request<RunSummary[]>('/api/runs'),
  getRun: (id: number | string) => request<RunDetail>(`/api/runs/${id}`),
  getTrades: (id: number | string, quarter?: string) =>
    request<TradeRow[]>(
      `/api/runs/${id}/trades${quarter ? `?quarter=${encodeURIComponent(quarter)}` : ''}`,
    ),
  createRun: (payload: {
    symbol: string
    kind: string
    min_rr: number
    scan_step: number
    sim_horizon: number
  }) => request<{ id: number }>('/api/runs', { method: 'POST', body: JSON.stringify(payload) }),
  deleteRun: (id: number) => request<void>(`/api/runs/${id}`, { method: 'DELETE' }),
  listDatasets: () => request<Dataset[]>('/api/datasets'),
  startFetch: (symbol: string, bars_m15: number) =>
    request<{ started: boolean }>('/api/datasets/fetch', {
      method: 'POST',
      body: JSON.stringify({ symbol, bars_m15 }),
    }),
  fetchStatus: () =>
    request<{ status: string; symbol: string | null; message: string }>(
      '/api/datasets/fetch/status',
    ),
  getSettings: () => request<Record<string, string>>('/api/settings'),
  updateSettings: (values: Record<string, string>) =>
    request<Record<string, string>>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify({ values }),
    }),
}

export function fmtPct(v: unknown): string {
  return typeof v === 'number' ? `${(v * 100).toFixed(1)}%` : '—'
}

export function fmtNum(v: unknown, digits = 2): string {
  return typeof v === 'number' ? v.toFixed(digits) : '—'
}
