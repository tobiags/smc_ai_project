"""Generate a quarterly HTML report from quarterly backtest JSON output.

Usage:
    python -m smc_ai.cli quarterly --symbol EURUSD --data-dir data > data/quarterly_result.json
    python scripts/generate_quarterly_report.py
"""
from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smc_ai.utils import load_dotenv, read_text_auto


def _color_pf(pf: float) -> str:
    if pf >= 1.5:
        return "#3fb950"
    if pf >= 1.0:
        return "#e3b341"
    return "#f85149"


def _color_wr(wr: float) -> str:
    if wr >= 0.35:
        return "#3fb950"
    if wr >= 0.25:
        return "#e3b341"
    return "#f85149"


def _color_ev(ev: float) -> str:
    return "#3fb950" if ev > 0 else "#f85149"


def build_html(data: dict) -> str:
    symbol = data.get("symbol", "?")
    all_quarters = data.get("quarters", [])
    quarters = [q for q in all_quarters if "error" not in q and q.get("kpis")]
    failed = [q for q in all_quarters if "error" in q]

    if not quarters:
        return "<html><body><h1>No quarterly data available.</h1></body></html>"

    failed_banner = ""
    if failed:
        items = "".join(
            f"<li><strong>{q['quarter']}</strong>: {q['error']}</li>" for q in failed
        )
        failed_banner = (
            '<div style="background:#4a1e1e;border:1px solid #da3633;border-radius:8px;'
            'padding:12px 16px;margin-bottom:20px;color:#f85149">'
            f"<strong>{len(failed)} trimestre(s) en echec :</strong><ul>{items}</ul></div>"
        )

    # Chart data
    labels      = [q["quarter"] for q in quarters]
    wr_values   = [round(q["kpis"].get("win_rate", 0) * 100, 1) for q in quarters]
    pf_values   = [q["kpis"].get("profit_factor", 0) for q in quarters]
    ev_values   = [q["kpis"].get("expectancy_r", 0) for q in quarters]
    trade_vals  = [q["kpis"].get("total_trades", 0) for q in quarters]
    pnl_vals    = [round(q["kpis"].get("ending_balance", 10000) - 10000, 2) for q in quarters]
    dd_values   = [round(q["kpis"].get("max_drawdown", 0) * 100, 1) for q in quarters]

    labels_js      = json.dumps(labels)
    wr_js          = json.dumps(wr_values)
    pf_js          = json.dumps(pf_values)
    ev_js          = json.dumps(ev_values)
    trades_js      = json.dumps(trade_vals)
    pnl_js         = json.dumps(pnl_vals)
    dd_js          = json.dumps(dd_values)

    # Quarter rows
    rows = ""
    for q in quarters:
        k = q["kpis"]
        wr  = k.get("win_rate", 0)
        pf  = k.get("profit_factor", 0)
        ev  = k.get("expectancy_r", 0)
        pnl = round(k.get("ending_balance", 10000) - 10000, 2)
        dd  = round(k.get("max_drawdown", 0) * 100, 1)
        trades = k.get("total_trades", 0)
        stn = k.get("signal_to_noise", 0)
        hk  = round(k.get("half_kelly_pct", 0) * 100, 1)
        vp  = k.get("validation_progress_pct", 0)
        outcomes = {}
        for t in q.get("trades", []):
            o = t.get("outcome", "?")
            outcomes[o] = outcomes.get(o, 0) + 1
        tp_n  = outcomes.get("tp", 0)
        sl_n  = outcomes.get("sl", 0)
        open_n = outcomes.get("open", 0)

        pnl_color = "#3fb950" if pnl >= 0 else "#f85149"
        # PF 0.0 with wins but zero losses = degenerate sample, not bad performance
        degenerate_pf = pf == 0.0 and k.get("avg_loss_r", 0) == 0.0 and k.get("avg_win_r", 0) > 0
        pf_cell = (
            '<td style="color:#8b949e;font-weight:600">N/A (0 perte)</td>'
            if degenerate_pf
            else f'<td style="color:{_color_pf(pf)};font-weight:600">{pf:.2f}</td>'
        )
        rows += f"""
        <tr>
          <td style="font-weight:700;color:#58a6ff">{q['quarter']}</td>
          <td>{trades}</td>
          <td style="color:{_color_wr(wr)};font-weight:600">{round(wr*100,1)}%</td>
          {pf_cell}
          <td style="color:{_color_ev(ev)};font-weight:600">{ev:+.3f}R</td>
          <td style="color:{pnl_color};font-weight:600">${pnl:+.0f}</td>
          <td>{dd}%</td>
          <td style="font-size:12px;color:#8b949e">TP:{tp_n} SL:{sl_n} Open:{open_n}</td>
          <td style="color:#8b949e;font-size:12px">{stn:.3f}</td>
          <td style="color:#8b949e;font-size:12px">{hk}%</td>
          <td>
            <div style="background:#21262d;border-radius:4px;height:8px;width:100%;min-width:80px">
              <div style="background:#58a6ff;height:8px;border-radius:4px;width:{min(vp,100):.0f}%"></div>
            </div>
            <span style="font-size:11px;color:#8b949e">{vp:.0f}%</span>
          </td>
        </tr>"""

    # Summary stats
    total_trades = sum(q["kpis"].get("total_trades", 0) for q in quarters)
    avg_wr  = sum(q["kpis"].get("win_rate", 0) for q in quarters) / len(quarters) * 100
    avg_pf  = sum(q["kpis"].get("profit_factor", 0) for q in quarters) / len(quarters)
    avg_ev  = sum(q["kpis"].get("expectancy_r", 0) for q in quarters) / len(quarters)
    total_pnl = sum(round(q["kpis"].get("ending_balance", 10000) - 10000, 2) for q in quarters)
    # Exclude degenerate samples (no losses → PF forced to 0.0) from best/worst ranking
    rankable = [q for q in quarters if q["kpis"].get("avg_loss_r", 0) > 0] or quarters
    best_q  = max(rankable, key=lambda q: q["kpis"].get("profit_factor", 0))["quarter"]
    worst_q = min(rankable, key=lambda q: q["kpis"].get("profit_factor", 0))["quarter"]

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SMC AI — Rapport Trimestriel {symbol}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:24px}}
  h1{{color:#f0f6fc;font-size:22px;margin-bottom:4px}}
  .subtitle{{color:#8b949e;font-size:14px;margin-bottom:28px}}
  .summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:28px}}
  .kpi-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}}
  .kpi-label{{font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}}
  .kpi-value{{font-size:24px;font-weight:700;color:#f0f6fc}}
  .kpi-sub{{font-size:11px;color:#8b949e;margin-top:3px}}
  .charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:28px}}
  .chart-box{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}}
  .chart-title{{font-size:13px;color:#8b949e;margin-bottom:12px;font-weight:600}}
  .chart-box canvas{{max-height:200px}}
  .table-wrap{{background:#161b22;border:1px solid #30363d;border-radius:8px;overflow:auto;margin-bottom:28px}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{padding:10px 14px;text-align:left;color:#8b949e;font-weight:600;font-size:11px;text-transform:uppercase;border-bottom:1px solid #30363d;background:#0d1117}}
  td{{padding:10px 14px;border-bottom:1px solid #21262d}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#1c2128}}
  .badge{{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600}}
  .best{{background:#1f4a2c;color:#3fb950;border:1px solid #2ea043}}
  .worst{{background:#4a1e1e;color:#f85149;border:1px solid #da3633}}
  @media(max-width:700px){{.charts-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<h1>SMC AI — Rapport Trimestriel</h1>
{failed_banner}
<div class="subtitle">{symbol} &nbsp;·&nbsp; {len(quarters)} trimestres analysés &nbsp;·&nbsp; RR minimum {quarters[0]["kpis"].get("rr_ratio", 2.5):.1f} &nbsp;·&nbsp; Meilleur: <span class="badge best">{best_q}</span> &nbsp; Pire: <span class="badge worst">{worst_q}</span></div>

<!-- Summary KPIs -->
<div class="summary-grid">
  <div class="kpi-card">
    <div class="kpi-label">Trades totaux</div>
    <div class="kpi-value">{total_trades}</div>
    <div class="kpi-sub">sur {len(quarters)} trimestres</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Win Rate moyen</div>
    <div class="kpi-value" style="color:{_color_wr(avg_wr/100)}">{avg_wr:.1f}%</div>
    <div class="kpi-sub">besoin min ~29%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Profit Factor moyen</div>
    <div class="kpi-value" style="color:{_color_pf(avg_pf)}">{avg_pf:.2f}</div>
    <div class="kpi-sub">>1.0 = profitable</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">EV moyen</div>
    <div class="kpi-value" style="color:{_color_ev(avg_ev)}">{avg_ev:+.3f}R</div>
    <div class="kpi-sub">par trade</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">PnL cumulé simulé</div>
    <div class="kpi-value" style="color:{'#3fb950' if total_pnl>=0 else '#f85149'}">${total_pnl:+.0f}</div>
    <div class="kpi-sub">base 10 000$/trimestre</div>
  </div>
</div>

<!-- Charts -->
<div class="charts-grid">
  <div class="chart-box">
    <div class="chart-title">Win Rate par trimestre (%)</div>
    <canvas id="wrChart"></canvas>
  </div>
  <div class="chart-box">
    <div class="chart-title">Profit Factor par trimestre</div>
    <canvas id="pfChart"></canvas>
  </div>
  <div class="chart-box">
    <div class="chart-title">Esperance (EV) en R par trimestre</div>
    <canvas id="evChart"></canvas>
  </div>
  <div class="chart-box">
    <div class="chart-title">Nombre de trades par trimestre</div>
    <canvas id="tradesChart"></canvas>
  </div>
</div>

<!-- Quarterly table -->
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Trimestre</th><th>Trades</th><th>Win Rate</th><th>Profit Factor</th>
        <th>EV (R)</th><th>PnL sim.</th><th>Max DD</th><th>Resultats</th>
        <th>Signal/Bruit</th><th>Half Kelly</th><th>Validation</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>

<script>
const LABELS = {labels_js};
const CFG = (id, type, data, color, extra={{}}) => {{
  new Chart(document.getElementById(id), {{
    type: type,
    data: {{
      labels: LABELS,
      datasets: [{{
        data: data,
        backgroundColor: Array.isArray(color) ? color : color + '33',
        borderColor: color,
        borderWidth: 2,
        fill: type === 'line',
        tension: 0.3,
        pointRadius: 4,
        ...extra
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#8b949e', font: {{ size: 11 }} }}, grid: {{ color: '#21262d' }} }},
        y: {{ ticks: {{ color: '#8b949e', font: {{ size: 11 }} }}, grid: {{ color: '#21262d' }} }}
      }}
    }}
  }});
}};

CFG('wrChart', 'bar', {wr_js},
  {wr_js}.map(v => v >= 35 ? '#3fb950' : v >= 25 ? '#e3b341' : '#f85149'));
CFG('pfChart', 'bar', {pf_js},
  {pf_js}.map(v => v >= 1.5 ? '#3fb950' : v >= 1.0 ? '#e3b341' : '#f85149'));
CFG('evChart', 'line', {ev_js}, '#58a6ff');
CFG('tradesChart', 'bar', {trades_js}, '#58a6ff');
</script>
</body>
</html>"""


def main() -> None:
    load_dotenv()

    result_path = Path("data/quarterly_result.json")
    if not result_path.exists():
        print("ERROR: data/quarterly_result.json not found.")
        print("Run first: python -m smc_ai.cli quarterly --symbol EURUSD --data-dir data > data/quarterly_result.json")
        sys.exit(1)

    text = read_text_auto(result_path)

    # Strip potential leading text before JSON
    start = text.find("{")
    if start > 0:
        text = text[start:]

    data = json.loads(text)
    html = build_html(data)

    out = Path("reports/quarterly_EURUSD.html")
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Report -> {out.resolve()}")
    webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
