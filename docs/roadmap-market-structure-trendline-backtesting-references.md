# Market Structure, Trendline, and Backtesting References

**Date:** 2026-06-04
**Status:** Accepted as implementation references
**Current priority remains:** WinWorld SMC core first

These references strengthen the reusable strategy infrastructure. They do not replace the
WinWorld SMC rules.

---

## References

- `neurotrader888/market-structure`
- `neurotrader888/TrendLineAutomation`
- `ChadThackray/price-trends-2023`
- `ChadThackray/multi-timeframe-backtesting-py-2022`
- `ChadThackray/backtesting-py-stop-losses`
- `ChadThackray/backtesting.py-speed-2025`

---

## What To Use

### Market Structure

`neurotrader888/market-structure` and `ChadThackray/price-trends-2023` are useful for
turning raw candles into readable structure:

- swing highs and swing lows
- HH / HL / LH / LL labels
- directional change concepts
- possible multi-scale structure detection
- trend state extraction for future non-SMC strategies

For the current project, the immediate use is a small local module:

```text
OHLCV candles
-> swings
-> HH/HL/LH/LL labels
-> future BOS/ChoCh/IDM logic
```

This keeps WinWorld-specific logic inside our own strategy layer.

### Dynamic Trendlines

`neurotrader888/TrendLineAutomation` is accepted as a future trendline reference.

Useful ideas:

- calculate trendlines over a range of periods, for example 7 to 30 candles
- score each trendline by how closely it fits highs or lows
- keep the best-scored line as the "true trendline"
- use the trendline as context, not as an automatic entry trigger

In our system, trendlines may later help with:

- visual dashboard overlays
- confluence filters
- chart review in the trading journal
- future ICT or swing-trading strategy profiles

They must not override WinWorld SMC invalidation rules.

### Backtesting Patterns

The Chad Thackray repositories are accepted as backtesting references:

- `multi-timeframe-backtesting-py-2022`: D1/H4/M15 coordination patterns
- `backtesting-py-stop-losses`: stop-loss and trade management experiments
- `backtesting.py-speed-2025`: performance ideas for heavier backtest runs

Use these as references only. The current engine remains independent and strategy-agnostic.

---

## Boundaries

- No direct external code copy without license review.
- No trendline or ML filter can replace SMC structure validation.
- No optimization result is accepted without walk-forward or out-of-sample verification.
- The engine must stay strategy-agnostic: WinWorld today, ICT and Simple Markets later.

---

## Placement

```text
Phase 1
  Local market_structure module for HH/HL/LH/LL labels

Phase 2
  Multi-timeframe backtesting refinements
  Structural stop-loss experiments

Phase 2+
  Dynamic trendline dashboard overlays and confluence filters

Phase 3+
  Reusable structure tools for ICT, Simple Markets Swing Trading Plan, and future profiles
```
