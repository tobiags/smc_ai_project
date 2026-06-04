# Decision: Add Market Structure, Trendline, and Backtesting References

**Date:** 2026-06-04
**Status:** accepted

## Decision

Add the latest market structure, dynamic trendline, and backtesting repositories as references
for the reusable trading infrastructure.

## Accepted References

- `neurotrader888/market-structure`
- `neurotrader888/TrendLineAutomation`
- `ChadThackray/price-trends-2023`
- `ChadThackray/multi-timeframe-backtesting-py-2022`
- `ChadThackray/backtesting-py-stop-losses`
- `ChadThackray/backtesting.py-speed-2025`

## Why It Helps

The project must support replaceable strategies. WinWorld SMC is the first strategy, but the
same engine should later support ICT, Simple Markets Swing Trading Plan, and other documented
methods.

These references help separate durable infrastructure from strategy-specific rules:

- swing and structure labeling
- trend state extraction
- dynamic trendline scoring
- multi-timeframe backtesting
- stop-loss and trade management testing
- performance patterns for larger historical runs

## Boundaries

- They are references, not Phase 1 dependencies.
- Direct code reuse requires license review.
- Dynamic trendlines are context/confluence, not entry authority.
- WinWorld SMC invalidation rules remain the source of truth for the current profile.
- The first implementation target is a local `market_structure` module with HH/HL/LH/LL labels.

## Follow-Up

Implement the first reusable structure module:

```text
candles -> swings -> HH/HL/LH/LL -> structure bias
```

Then use that module as a base for future BOS/ChoCh logic.
