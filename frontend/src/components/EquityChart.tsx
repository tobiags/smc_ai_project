// Mini graphique SVG sans dépendance externe — courbe d'equity
interface Point {
  timestamp: string
  equity: number
}

export function EquityChart({
  points,
  height = 220,
  baseline = 10000,
}: {
  points: Point[]
  height?: number
  baseline?: number
}) {
  if (!points.length) {
    return <p className="muted">Aucune donnée d'equity.</p>
  }

  const width = 800
  const pad = 40
  const values = [baseline, ...points.map((p) => p.equity)]
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const x = (i: number) => pad + (i / Math.max(points.length - 1, 1)) * (width - 2 * pad)
  const yy = (v: number) => pad + ((max - v) / range) * (height - 2 * pad)

  const path = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(i)},${yy(p.equity)}`).join(' ')
  const last = points[points.length - 1].equity
  const up = last >= baseline

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
      {/* ligne de base */}
      <line
        x1={pad}
        x2={width - pad}
        y1={yy(baseline)}
        y2={yy(baseline)}
        stroke="var(--border)"
        strokeDasharray="4 4"
      />
      <text x={width - pad + 4} y={yy(baseline) + 4} fill="var(--text-dim)" fontSize="11">
        {baseline}
      </text>
      <path d={path} fill="none" stroke={up ? 'var(--green)' : 'var(--red)'} strokeWidth="2" />
      {points.map((p, i) => (
        <circle key={i} cx={x(i)} cy={yy(p.equity)} r="3" fill={up ? 'var(--green)' : 'var(--red)'}>
          <title>{`${p.timestamp} — ${p.equity}`}</title>
        </circle>
      ))}
      <text x={pad} y={16} fill="var(--text-dim)" fontSize="11">
        max {max.toFixed(0)}
      </text>
      <text x={pad} y={height - 8} fill="var(--text-dim)" fontSize="11">
        min {min.toFixed(0)}
      </text>
    </svg>
  )
}
