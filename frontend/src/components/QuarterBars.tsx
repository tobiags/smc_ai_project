// Barres d'expectancy (R) par trimestre — SVG pur, pas de dépendance
import type { Quarter } from '../lib/api'

export function QuarterBars({ quarters, height = 200 }: { quarters: Quarter[]; height?: number }) {
  const valid = quarters.filter((q) => !q.error)
  if (!valid.length) return <p className="muted">Aucun trimestre.</p>

  const width = 800
  const pad = 40
  const evs = valid.map((q) => Number(q.kpis.expectancy_r ?? 0))
  const maxAbs = Math.max(...evs.map(Math.abs), 0.5)
  const zeroY = height / 2
  const barW = Math.min(80, (width - 2 * pad) / valid.length - 20)

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
      <line x1={pad} x2={width - pad} y1={zeroY} y2={zeroY} stroke="var(--border)" />
      {valid.map((q, i) => {
        const ev = evs[i]
        const h = (Math.abs(ev) / maxAbs) * (height / 2 - pad)
        const cx = pad + ((i + 0.5) / valid.length) * (width - 2 * pad)
        return (
          <g key={q.label}>
            <rect
              x={cx - barW / 2}
              y={ev >= 0 ? zeroY - h : zeroY}
              width={barW}
              height={Math.max(h, 1)}
              rx="4"
              fill={ev >= 0 ? 'var(--green)' : 'var(--red)'}
              opacity="0.85"
            >
              <title>{`${q.label} — EV ${ev >= 0 ? '+' : ''}${ev.toFixed(3)}R`}</title>
            </rect>
            <text x={cx} y={height - 10} textAnchor="middle" fill="var(--text-dim)" fontSize="12">
              {q.label}
            </text>
            <text
              x={cx}
              y={ev >= 0 ? zeroY - h - 6 : zeroY + h + 14}
              textAnchor="middle"
              fill="var(--text)"
              fontSize="12"
              fontWeight="600"
            >
              {ev >= 0 ? '+' : ''}
              {ev.toFixed(2)}R
            </text>
          </g>
        )
      })}
    </svg>
  )
}
