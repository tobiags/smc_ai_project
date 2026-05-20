from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from smc_ai.backtest.exporter import list_results, read_result
from smc_ai.config import get_settings


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
KPI_LABELS = {
    "starting_balance": "Capital initial",
    "ending_balance": "Capital final",
    "total_trades": "Nombre de trades",
    "win_rate": "Taux de réussite",
    "profit_factor": "Facteur de profit",
    "max_drawdown": "Drawdown max",
}


def _equity_chart_html(equity_curve: list[dict[str, float | str]]) -> str:
    try:
        import plotly.graph_objects as go
    except ModuleNotFoundError:
        return (
            "<div id=\"equity-chart\"></div>"
            "<script>"
            "window.Plotly = window.Plotly || {newPlot: function(){}};"
            "Plotly.newPlot('equity-chart', []);"
            "</script>"
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[point["timestamp"] for point in equity_curve],
            y=[point["equity"] for point in equity_curve],
            mode="lines+markers",
            name="Equity",
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    results = list_results(get_settings().results_dir)
    latest = results[0] if results else None
    return templates.TemplateResponse(
        request,
        "home.html",
        {"latest": latest, "results": results[:10]},
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: str):
    path = get_settings().results_dir / f"{run_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run not found")

    result = read_result(path)
    return templates.TemplateResponse(
        request,
        "run_detail.html",
        {
            "result": result,
            "chart_html": _equity_chart_html(result.equity_curve),
            "kpi_labels": KPI_LABELS,
        },
    )


@router.get("/health", response_class=HTMLResponse)
def health(request: Request):
    results = list_results(get_settings().results_dir)
    latest = results[0] if results else None
    return templates.TemplateResponse(
        request,
        "health.html",
        {"latest": latest, "kpi_labels": KPI_LABELS},
    )
