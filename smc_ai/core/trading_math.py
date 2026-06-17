import math


def expectancy_r(win_rate: float, average_win_r: float, average_loss_r: float) -> float:
    if not 0 <= win_rate <= 1:
        raise ValueError("win_rate must be between 0 and 1")
    if average_win_r <= 0:
        raise ValueError("average_win_r must be positive")
    if average_loss_r <= 0:
        raise ValueError("average_loss_r must be positive")

    loss_rate = 1 - win_rate
    return round(win_rate * average_win_r - loss_rate * average_loss_r, 4)


def breakeven_win_rate(reward_to_risk: float) -> float:
    if reward_to_risk <= 0:
        raise ValueError("reward_to_risk must be positive")
    return round(1 / (reward_to_risk + 1), 4)


def recovery_gain_required(drawdown: float) -> float:
    if not 0 < drawdown < 1:
        raise ValueError("drawdown must be greater than 0 and less than 1")
    return round(drawdown / (1 - drawdown), 4)


def kelly_criterion(win_rate: float, rr_ratio: float) -> float:
    """Full Kelly fraction — risk this % of account per trade.

    Kelly % = W - (1-W) / R
    where R = average_win / average_loss (reward-to-risk ratio).

    Returns a value clamped to [0, 1]. Negative Kelly means no edge.
    """
    if rr_ratio <= 0:
        return 0.0
    k = win_rate - (1 - win_rate) / rr_ratio
    return round(max(0.0, min(1.0, k)), 4)


def half_kelly(win_rate: float, rr_ratio: float) -> float:
    """Half Kelly — safer sizing that gives ~75% of full-Kelly growth."""
    return round(kelly_criterion(win_rate, rr_ratio) / 2, 4)


def risk_of_ruin(
    win_rate: float,
    rr_ratio: float,
    n_units: int = 100,
) -> float:
    """Probability of losing the entire account before the edge emerges.

    Formula (simplified):
        RoR = ((1-W)/W × 1/R) ^ n_units

    Args:
        win_rate:  Fraction of trades that are winners (0-1).
        rr_ratio:  Average win / average loss ratio.
        n_units:   Account size expressed in units of risk-per-trade.
                   E.g. $10,000 account with $100 risk/trade → 100 units.

    Returns probability as a fraction (0-1). Values below 0.01 are negligible.
    """
    if win_rate <= 0 or win_rate >= 1 or rr_ratio <= 0 or n_units <= 0:
        return 1.0
    base = ((1 - win_rate) / win_rate) * (1 / rr_ratio)
    if base >= 1.0:
        return 1.0
    return round(base ** n_units, 10)


def std_dev_r(pnl_r: list[float]) -> float:
    """Sample standard deviation of trade results in R."""
    n = len(pnl_r)
    if n < 2:
        return 0.0
    mean = sum(pnl_r) / n
    variance = sum((r - mean) ** 2 for r in pnl_r) / (n - 1)
    return round(math.sqrt(variance), 4)


def signal_to_noise(pnl_r: list[float]) -> float:
    """Mean / std_dev — Sharpe ratio per trade (not annualised).

    Interpretation:
        > 0.50 : clean edge, statistically meaningful
        0.20–0.50 : probable edge, needs more sample size
        < 0.20 : buried in noise, unproven
    """
    if len(pnl_r) < 2:
        return 0.0
    mean = sum(pnl_r) / len(pnl_r)
    sd = std_dev_r(pnl_r)
    if sd <= 0:
        return 0.0
    return round(mean / sd, 4)


def validation_progress(n_trades: int, win_rate: float) -> dict[str, float]:
    """How far along we are toward statistical significance (95% confidence).

    Uses the sample-size formula:
        n = (Z² × p × (1-p)) / E²
    with Z=1.96 (95%), E=0.05 (5% margin of error).

    Returns:
        required  : number of trades needed
        progress  : percentage completed (0-100)
        confident : True if n_trades >= required
    """
    if not 0 < win_rate < 1:
        win_rate = max(0.01, min(0.99, win_rate if win_rate > 0 else 0.5))
    z = 1.96
    e = 0.05
    required = math.ceil((z ** 2 * win_rate * (1 - win_rate)) / (e ** 2))
    required = max(required, 300)
    progress = min(100.0, round(n_trades / required * 100, 1))
    return {
        "required_trades": float(required),
        "progress_pct": progress,
        "confident": n_trades >= required,
    }


def fixed_risk_position_size(
    account_balance: float,
    risk_percent: float,
    stop_distance: float,
    value_per_unit_move: float,
) -> float:
    if account_balance <= 0:
        raise ValueError("account_balance must be positive")
    if not 0 < risk_percent <= 1:
        raise ValueError("risk_percent must be greater than 0 and less than or equal to 1")
    if stop_distance <= 0:
        raise ValueError("stop_distance must be positive")
    if value_per_unit_move <= 0:
        raise ValueError("value_per_unit_move must be positive")

    currency_risk = account_balance * risk_percent
    return round(currency_risk / (stop_distance * value_per_unit_move), 4)
