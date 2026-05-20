from fastapi.testclient import TestClient

from smc_ai.backtest.exporter import write_result
from smc_ai.backtest.runner import run_sample_backtest
from smc_ai.config import get_settings
from smc_ai.dashboard.app import create_app


def _clear_settings_cache():
    get_settings.cache_clear()


def test_dashboard_home_lists_latest_run(tmp_path, monkeypatch):
    result = run_sample_backtest("EURUSD", bars=160)
    write_result(result, tmp_path)
    monkeypatch.setenv("SMC_RESULTS_DIR", str(tmp_path))
    _clear_settings_cache()

    client = TestClient(create_app())
    response = client.get("/")

    _clear_settings_cache()

    assert response.status_code == 200
    assert result.run_id in response.text
    assert "EURUSD" in response.text
    assert "Dernier backtest" in response.text
    assert "Taux de réussite" in response.text


def test_run_detail_includes_plotly_chart(tmp_path, monkeypatch):
    result = run_sample_backtest("EURUSD", bars=160)
    write_result(result, tmp_path)
    monkeypatch.setenv("SMC_RESULTS_DIR", str(tmp_path))
    _clear_settings_cache()

    client = TestClient(create_app())
    response = client.get(f"/runs/{result.run_id}")

    _clear_settings_cache()

    assert response.status_code == 200
    assert "Plotly.newPlot" in response.text
    assert "EURUSD" in response.text
    assert "Capital initial" in response.text
    assert "Schéma" in response.text


def test_run_detail_returns_404_for_missing_run(tmp_path, monkeypatch):
    monkeypatch.setenv("SMC_RESULTS_DIR", str(tmp_path))
    _clear_settings_cache()

    client = TestClient(create_app())
    response = client.get("/runs/missing")

    _clear_settings_cache()

    assert response.status_code == 404
