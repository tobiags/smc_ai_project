# Decision: Add Trading Math for Expectancy, Variance, and Fixed Risk

**Date:** 2026-06-04
**Status:** accepted

## Source

User-provided trading psychology / math transcription.

## Useful Facts Extracted

- A strategy must be judged by expectancy, not by the latest trade.
- Expectancy combines win rate, average win, and average loss.
- High win rate alone is not enough; high R multiple alone is not enough.
- Break-even win rate depends on reward-to-risk.
- Short-term results are noisy because of variance.
- One trade means nothing; a small sample means very little.
- Position size must keep account risk constant even when stop distance changes.
- Large drawdowns are mathematically hard to recover from.
- Strategy review should use large enough samples and weekly/monthly reviews, not emotion after
  a losing streak.

## Implementation Decision

Add a pure math module:

```text
smc_ai.core.trading_math
```

Initial functions:

- `expectancy_r`
- `breakeven_win_rate`
- `recovery_gain_required`
- `fixed_risk_position_size`

## How It Should Be Used

- Backtest reports should show expectancy, not only win rate.
- Journal reviews should compare realized expectancy against expected expectancy.
- Risk sizing should be calculated from account risk and stop distance.
- Weekly ARIS reviews should avoid changing a strategy from a tiny sample.

## Boundary

These formulas are support metrics. They do not replace WinWorld SMC entry rules, POI rules, or
invalidation rules.
