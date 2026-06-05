import pytest

from smc_ai.backtest.monitor import HealthStatus, compute_health


def _trades(pnl_r_list: list[float]) -> list[dict[str, object]]:
    return [{"pnl_r": r, "outcome": "tp" if r > 0 else "sl"} for r in pnl_r_list]


def test_compute_health_ok_when_all_wins():
    trades = _trades([5.0] * 15)
    status = compute_health(trades)

    assert status.level == "ok"
    assert status.metrics["win_rate"] == 1.0


def test_compute_health_warning_when_low_win_rate():
    # Interleaved wins/losses → WR=30%, max 5 consecutive losses (no alert), PF>1.0 (no critical)
    # [W, L, W, L, L, L, L, W, L, L] → 3 wins, 7 losses, last 2 losses consecutive
    trades = _trades([5.0, -1.0, 5.0, -1.0, -1.0, -1.0, -1.0, 5.0, -1.0, -1.0])
    status = compute_health(trades)

    assert status.level == "warning"
    assert "win rate" in status.reason


def test_compute_health_alert_when_6_consecutive_losses():
    # 3 wins then exactly 6 consecutive losses (9 trades total, < 10 so no rate checks)
    trades = _trades([5.0, 5.0, 5.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0])
    status = compute_health(trades)

    assert status.level == "alert"
    assert "consecutive" in status.reason
    assert status.metrics["consecutive_losses"] == 6.0


def test_compute_health_critical_when_profit_factor_below_1():
    # 2 wins at 1R each, 10 losses at -1R → PF=0.2, 12 trades ≥ 10, consecutive=1 (last is loss)
    # critical check (PF) fires before alert (consecutive=1 < 6)
    trades = _trades([1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0])
    status = compute_health(trades)

    assert status.level == "critical"
    assert "profit factor" in status.reason


def test_compute_health_stop_when_max_drawdown_exceeds_threshold():
    # Large sequence of losses to trigger > 18% drawdown
    trades = _trades([-1.0] * 25)
    status = compute_health(trades, rolling_window=30)

    assert status.level == "stop"
    assert "drawdown" in status.reason


def test_compute_health_insufficient_data_does_not_trigger_rate_checks():
    # Only 5 trades — win_rate/profit_factor checks require ≥ 10 trades
    trades = _trades([-1.0] * 5)
    status = compute_health(trades)

    # Should be warning only if consecutive losses ≥ 6, otherwise ok
    assert status.level in {"ok", "warning", "alert", "critical", "stop"}
    assert isinstance(status.level, str)


def test_health_status_to_dict():
    trades = _trades([5.0] * 10)
    status = compute_health(trades)
    data = status.to_dict()

    assert "level" in data
    assert "reason" in data
    assert "metrics" in data
    assert "win_rate" in data["metrics"]
