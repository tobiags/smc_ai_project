"""Generate a standalone HTML backtest report and open it in the browser.

Usage:
    python scripts/generate_report.py --symbol EURUSD.s --data-dir data --min-rr 5.0

Or pipe from the CLI:
    python -m smc_ai.cli backtest --symbol EURUSD.s --data-dir data | python scripts/generate_report.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path


# ── HTML template ─────────────────────────────────────────────────────────────

def _build_html(result: dict) -> str:
    kpis   = result.get("kpis", {})
    trades = result.get("trades", [])
    equity = result.get("equity_curve", [])
    analyses = result.get("analyses", [])
    symbol   = result.get("symbol", "?")
    run_id   = result.get("run_id", "")

    # ── equity curve data ────────────────────────────────────────────────────
    eq_labels = [e["timestamp"][:16].replace("T", " ") for e in equity]
    eq_values = [e["equity"] for e in equity]

    # ── trade outcomes ────────────────────────────────────────────────────────
    n_tp   = sum(1 for t in trades if t.get("outcome") == "tp")
    n_sl   = sum(1 for t in trades if t.get("outcome") == "sl")
    n_open = sum(1 for t in trades if t.get("outcome") == "open")

    # ── rejection reasons ─────────────────────────────────────────────────────
    rejections: dict[str, int] = {}
    for a in analyses:
        reason = a.get("rejection_reason")
        if reason:
            rejections[reason] = rejections.get(reason, 0) + 1
    rej_labels = list(rejections.keys())
    rej_values = list(rejections.values())

    # ── trade rows ────────────────────────────────────────────────────────────
    trade_rows = ""
    for t in trades:
        ts  = t.get("timestamp", "")[:16].replace("T", " ")
        dir_ = t.get("direction", "")
        outcome = t.get("outcome", "")
        pnl_r = t.get("pnl_r", 0)
        pnl   = t.get("pnl", 0)
        entry = t.get("entry", 0)
        sl    = t.get("stop_loss", 0)
        tp    = t.get("take_profit", 0)

        dir_badge = (
            '<span class="badge buy">▲ BUY</span>' if dir_ == "buy"
            else '<span class="badge sell">▼ SELL</span>'
        )
        if outcome == "tp":
            outcome_badge = '<span class="badge win">✓ TP</span>'
            pnl_class = "pos"
        elif outcome == "sl":
            outcome_badge = '<span class="badge loss">✗ SL</span>'
            pnl_class = "neg"
        else:
            outcome_badge = '<span class="badge open">● OPEN</span>'
            pnl_class = ""

        trade_rows += f"""
        <tr>
            <td>{ts}</td>
            <td>{dir_badge}</td>
            <td>{entry:.5f}</td>
            <td>{sl:.5f}</td>
            <td>{tp:.5f}</td>
            <td>{outcome_badge}</td>
            <td class="{pnl_class}">{pnl_r:+.1f} R</td>
            <td class="{pnl_class}">{pnl:+.0f} $</td>
        </tr>"""

    # ── analysis rows ─────────────────────────────────────────────────────────
    analysis_rows = ""
    for a in analyses:
        d = a.get("decision", {})
        ts  = d.get("timestamp", "")[:16].replace("T", " ")
        accepted = d.get("accepted", False)
        direction = d.get("direction") or "—"
        schema    = d.get("schema") or "—"
        reason    = d.get("reason") or a.get("rejection_reason") or "—"
        poi = d.get("poi")
        poi_str = f"{poi['kind']} {poi['direction']} @ {poi['top']:.5f}" if poi else "—"

        status_badge = (
            '<span class="badge win">✓ Accepté</span>' if accepted
            else '<span class="badge loss">✗ Rejeté</span>'
        )
        dir_badge = (
            '<span class="badge buy">▲ BUY</span>' if direction == "buy"
            else ('<span class="badge sell">▼ SELL</span>' if direction == "sell" else "—")
        )
        analysis_rows += f"""
        <tr>
            <td>{ts}</td>
            <td>{status_badge}</td>
            <td>{dir_badge}</td>
            <td>{schema}</td>
            <td>{poi_str}</td>
            <td class="reason">{reason}</td>
        </tr>"""

    # ── KPI values ────────────────────────────────────────────────────────────
    wr_pct    = kpis.get("win_rate", 0) * 100
    pf        = kpis.get("profit_factor", 0)
    exp_r     = kpis.get("expectancy_r", 0)
    dd_pct    = kpis.get("max_drawdown", 0) * 100
    start_bal = kpis.get("starting_balance", 10000)
    end_bal   = kpis.get("ending_balance", 10000)
    n_trades  = kpis.get("total_trades", 0)
    net_pnl   = end_bal - start_bal
    net_sign  = "+" if net_pnl >= 0 else ""
    gen_time  = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SMC AI — Backtest {symbol}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;min-height:100vh}}
  header{{background:linear-gradient(135deg,#1a2332,#0d1117);border-bottom:1px solid #30363d;padding:20px 32px;display:flex;align-items:center;justify-content:space-between}}
  header h1{{font-size:22px;font-weight:700;color:#58a6ff}}
  header .meta{{font-size:12px;color:#8b949e}}
  .container{{max-width:1400px;margin:0 auto;padding:24px 32px}}

  /* KPI cards */
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:28px}}
  .kpi{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px 16px;text-align:center}}
  .kpi .label{{font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px}}
  .kpi .value{{font-size:28px;font-weight:700;line-height:1}}
  .kpi .sub{{font-size:11px;color:#8b949e;margin-top:4px}}
  .kpi.pos .value{{color:#3fb950}}
  .kpi.neg .value{{color:#f85149}}
  .kpi.neu .value{{color:#58a6ff}}

  /* Charts */
  .charts-grid{{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:28px}}
  .chart-card{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px}}
  .chart-card h2{{font-size:14px;font-weight:600;color:#8b949e;margin-bottom:16px;text-transform:uppercase;letter-spacing:.6px}}
  .chart-wrap{{position:relative;height:260px}}

  /* Tables */
  .section{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px;margin-bottom:20px}}
  .section h2{{font-size:14px;font-weight:600;color:#8b949e;margin-bottom:16px;text-transform:uppercase;letter-spacing:.6px}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{color:#8b949e;font-weight:500;text-align:left;padding:8px 12px;border-bottom:1px solid #30363d;font-size:11px;text-transform:uppercase;letter-spacing:.5px}}
  td{{padding:10px 12px;border-bottom:1px solid #21262d;vertical-align:middle}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#1c2128}}
  .pos{{color:#3fb950;font-weight:600}}
  .neg{{color:#f85149;font-weight:600}}
  .reason{{color:#8b949e;font-size:12px}}

  /* Badges */
  .badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}}
  .badge.buy{{background:#0d2137;color:#58a6ff;border:1px solid #1f4e79}}
  .badge.sell{{background:#2d1b1b;color:#f0883e;border:1px solid #5a2d0c}}
  .badge.win{{background:#0d2a14;color:#3fb950;border:1px solid #1a5c26}}
  .badge.loss{{background:#2d1b1b;color:#f85149;border:1px solid #5c1e1e}}
  .badge.open{{background:#1c2128;color:#8b949e;border:1px solid #30363d}}

  /* Tabs */
  .tabs{{display:flex;gap:4px;margin-bottom:16px}}
  .tab{{padding:6px 16px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid #30363d;background:transparent;color:#8b949e}}
  .tab.active{{background:#1f4e79;color:#58a6ff;border-color:#1f4e79}}
  .tab-content{{display:none}}.tab-content.active{{display:block}}

  footer{{text-align:center;padding:24px;color:#484f58;font-size:12px;border-top:1px solid #21262d;margin-top:8px}}
</style>
</head>
<body>
<header>
  <div>
    <h1>SMC AI WinWorld — Rapport Backtest</h1>
    <div class="meta">Symbole: <strong style="color:#e6edf3">{symbol}</strong> &nbsp;|&nbsp; ID: {run_id} &nbsp;|&nbsp; Généré le {gen_time}</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:32px;font-weight:700;color:{'#3fb950' if net_pnl>=0 else '#f85149'}">{net_sign}{net_pnl:.0f} $</div>
    <div class="meta">sur {start_bal:,.0f} $ simulés</div>
  </div>
</header>

<div class="container">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi {'pos' if net_pnl>=0 else 'neg'}">
      <div class="label">Résultat net</div>
      <div class="value">{net_sign}{net_pnl:.0f}$</div>
      <div class="sub">{net_sign}{(net_pnl/start_bal*100):.1f}%</div>
    </div>
    <div class="kpi neu">
      <div class="label">Trades</div>
      <div class="value">{n_trades}</div>
      <div class="sub">{n_tp} TP · {n_sl} SL · {n_open} open</div>
    </div>
    <div class="kpi {'pos' if wr_pct>=40 else 'neg'}">
      <div class="label">Win Rate</div>
      <div class="value">{wr_pct:.0f}%</div>
      <div class="sub">trades fermés</div>
    </div>
    <div class="kpi {'pos' if pf>=1.5 else 'neg'}">
      <div class="label">Profit Factor</div>
      <div class="value">{pf:.2f}</div>
      <div class="sub">&gt;1.5 = bon</div>
    </div>
    <div class="kpi {'pos' if exp_r>0 else 'neg'}">
      <div class="label">Espérance</div>
      <div class="value">{exp_r:+.2f}R</div>
      <div class="sub">par trade</div>
    </div>
    <div class="kpi {'pos' if dd_pct<10 else 'neg'}">
      <div class="label">Max Drawdown</div>
      <div class="value">{dd_pct:.1f}%</div>
      <div class="sub">&lt;10% = sain</div>
    </div>
    <div class="kpi neu">
      <div class="label">RR minimum</div>
      <div class="value">1:5</div>
      <div class="sub">filtre stratégie</div>
    </div>
  </div>

  <!-- Charts -->
  <div class="charts-grid">
    <div class="chart-card">
      <h2>Courbe d'équité</h2>
      <div class="chart-wrap"><canvas id="equityChart"></canvas></div>
    </div>
    <div class="chart-card">
      <h2>Résultats des trades</h2>
      <div class="chart-wrap"><canvas id="outcomeChart"></canvas></div>
    </div>
  </div>

  <!-- Trades Table -->
  <div class="section">
    <h2>Trades ({n_trades})</h2>
    <div style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>Date/Heure</th><th>Direction</th>
        <th>Entrée</th><th>Stop Loss</th><th>Take Profit</th>
        <th>Résultat</th><th>PnL (R)</th><th>PnL ($)</th>
      </tr></thead>
      <tbody>{trade_rows}</tbody>
    </table>
    </div>
  </div>

  <!-- Analysis Log -->
  <div class="section">
    <h2>Journal des analyses ({len(analyses)} scans)</h2>
    <div class="tabs">
      <button class="tab active" onclick="showTab('all')">Tout</button>
      <button class="tab" onclick="showTab('accepted')">Acceptés</button>
      <button class="tab" onclick="showTab('rejected')">Rejetés</button>
    </div>
    <div style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>Date/Heure</th><th>Statut</th><th>Direction</th>
        <th>Schéma</th><th>POI</th><th>Raison</th>
      </tr></thead>
      <tbody id="analysisBody">{analysis_rows}</tbody>
    </table>
    </div>
  </div>

  <!-- Rejection breakdown -->
  {'<div class="charts-grid" style="grid-template-columns:1fr"><div class="chart-card"><h2>Raisons de rejet</h2><div class="chart-wrap"><canvas id="rejChart"></canvas></div></div></div>' if rej_labels else ''}

</div>

<footer>SMC AI WinWorld &nbsp;·&nbsp; Backtest Walk-Forward &nbsp;·&nbsp; {gen_time}</footer>

<script>
// ── Equity Curve ──────────────────────────────────────────────────────────────
const eqCtx = document.getElementById('equityChart').getContext('2d');
new Chart(eqCtx, {{
  type: 'line',
  data: {{
    labels: {json.dumps(eq_labels)},
    datasets: [{{
      label: 'Équité ($)',
      data: {json.dumps(eq_values)},
      borderColor: '#3fb950',
      backgroundColor: 'rgba(63,185,80,0.08)',
      borderWidth: 2.5,
      pointRadius: 4,
      pointBackgroundColor: '#3fb950',
      fill: true,
      tension: 0.3
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color:'#8b949e', font:{{size:10}} }}, grid:{{ color:'#21262d' }} }},
      y: {{ ticks: {{ color:'#8b949e', callback: v=>'$'+v.toLocaleString() }}, grid:{{ color:'#21262d' }} }}
    }}
  }}
}});

// ── Outcome Donut ─────────────────────────────────────────────────────────────
const ocCtx = document.getElementById('outcomeChart').getContext('2d');
new Chart(ocCtx, {{
  type: 'doughnut',
  data: {{
    labels: ['TP ✓', 'SL ✗', 'Open ●'],
    datasets: [{{
      data: [{n_tp}, {n_sl}, {n_open}],
      backgroundColor: ['#3fb950','#f85149','#484f58'],
      borderColor: '#161b22', borderWidth: 3
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position:'bottom', labels:{{ color:'#8b949e', padding:16, font:{{size:12}} }} }}
    }}
  }}
}});

// ── Rejection Bar ─────────────────────────────────────────────────────────────
{f"""
const rjCtx = document.getElementById('rejChart').getContext('2d');
new Chart(rjCtx, {{
  type: 'bar',
  data: {{
    labels: {json.dumps(rej_labels)},
    datasets: [{{
      label: 'Nombre',
      data: {json.dumps(rej_values)},
      backgroundColor: 'rgba(88,166,255,0.5)',
      borderColor: '#58a6ff', borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend:{{ display:false }} }},
    scales: {{
      x: {{ ticks:{{ color:'#8b949e' }}, grid:{{ color:'#21262d' }} }},
      y: {{ ticks:{{ color:'#8b949e', font:{{size:11}} }}, grid:{{ color:'#21262d' }} }}
    }}
  }}
}});
""" if rej_labels else ''}

// ── Tab filter ────────────────────────────────────────────────────────────────
function showTab(which) {{
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  event.target.classList.add('active');
  const rows = document.querySelectorAll('#analysisBody tr');
  rows.forEach(row => {{
    const hasWin  = row.querySelector('.badge.win');
    const hasLoss = row.querySelector('.badge.loss');
    if (which==='all')      row.style.display='';
    else if(which==='accepted') row.style.display = hasWin  ? '' : 'none';
    else                        row.style.display = hasLoss ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""
    return html


# ── main ──────────────────────────────────────────────────────────────────────

def run(symbol: str, data_dir: str, min_rr: float, scan_step: int, out: str) -> None:
    """Run backtest via CLI and generate HTML report."""
    print(f"Running backtest for {symbol}…")
    cmd = [
        sys.executable, "-m", "smc_ai.cli", "backtest",
        "--symbol", symbol,
        "--data-dir", data_dir,
        "--min-rr", str(min_rr),
        "--scan-step", str(scan_step),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("Backtest error:")
        print(proc.stderr)
        sys.exit(1)

    result = json.loads(proc.stdout)
    html   = _build_html(result)

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"✓ Report saved → {out_path.resolve()}")
    webbrowser.open(out_path.resolve().as_uri())
    print("  Opening in browser…")


def main() -> None:
    # If stdin has data, read JSON directly (pipe mode)
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
        result = json.loads(raw)
        symbol = result.get("symbol", "UNKNOWN")
        out_path = Path(f"reports/backtest_{symbol}.html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(_build_html(result), encoding="utf-8")
        print(f"✓ Report → {out_path.resolve()}")
        webbrowser.open(out_path.resolve().as_uri())
        return

    parser = argparse.ArgumentParser(description="Generate HTML backtest report")
    parser.add_argument("--symbol",     default="EURUSD.s")
    parser.add_argument("--data-dir",   default="data",     dest="data_dir")
    parser.add_argument("--min-rr",     type=float, default=5.0, dest="min_rr")
    parser.add_argument("--scan-step",  type=int,   default=40,  dest="scan_step")
    parser.add_argument("--out",        default="reports/backtest_{symbol}.html")
    args = parser.parse_args()

    out = args.out.replace("{symbol}", args.symbol)
    run(args.symbol, args.data_dir, args.min_rr, args.scan_step, out)


if __name__ == "__main__":
    main()
