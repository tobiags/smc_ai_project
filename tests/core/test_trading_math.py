import pytest

from smc_ai.core.trading_math import (
    breakeven_win_rate,
    expectancy_r,
    fixed_risk_position_size,
    recovery_gain_required,
)


def test_expectancy_r_combines_win_rate_average_win_and_average_loss():
    expectancy = expectancy_r(win_rate=0.40, average_win_r=4.0, average_loss_r=1.0)

    assert expectancy == 1.0


def test_breakeven_win_rate_uses_reward_to_risk():
    assert breakeven_win_rate(reward_to_risk=1.0) == 0.50
    assert breakeven_win_rate(reward_to_risk=4.0) == 0.20
    assert breakeven_win_rate(reward_to_risk=5.0) == pytest.approx(0.1667, abs=0.0001)


def test_recovery_gain_required_after_drawdown():
    assert recovery_gain_required(drawdown=0.10) == pytest.approx(0.1111, abs=0.0001)
    assert recovery_gain_required(drawdown=0.30) == pytest.approx(0.4286, abs=0.0001)
    assert recovery_gain_required(drawdown=0.50) == 1.0


def test_fixed_risk_position_size_keeps_currency_risk_constant():
    units = fixed_risk_position_size(
        account_balance=1000.0,
        risk_percent=0.005,
        stop_distance=0.0025,
        value_per_unit_move=1.0,
    )

    assert units == 2000.0


@pytest.mark.parametrize(
    ("win_rate", "average_win_r", "average_loss_r"),
    [
        (-0.1, 4.0, 1.0),
        (1.1, 4.0, 1.0),
        (0.5, 0.0, 1.0),
        (0.5, 4.0, 0.0),
    ],
)
def test_expectancy_r_rejects_invalid_inputs(win_rate, average_win_r, average_loss_r):
    with pytest.raises(ValueError):
        expectancy_r(win_rate, average_win_r, average_loss_r)


@pytest.mark.parametrize("drawdown", [-0.1, 0.0, 1.0])
def test_recovery_gain_required_rejects_invalid_drawdown(drawdown):
    with pytest.raises(ValueError):
        recovery_gain_required(drawdown)
