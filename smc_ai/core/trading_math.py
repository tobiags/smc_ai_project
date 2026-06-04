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
