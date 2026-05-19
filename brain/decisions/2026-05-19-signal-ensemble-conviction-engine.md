# Signal Ensemble / Conviction Engine

**Date:** 2026-05-19
**Status:** accepted as future statistical layer
**Scope:** Phase 2.5 / Phase 4 research, not Phase 1 SMC core

## Decision

Add a future Signal Ensemble / Conviction Engine roadmap to the project.

This layer will use statistical, probabilistic, and mathematical checks to score the strength
of a valid SMC setup. It does not replace the WinWorld rules.

## Reason

Being right about direction is not enough. A trader can be directionally right and still lose
money because of timing, sizing, correlation, poor execution, or overconfidence.

The useful principle is:

```text
IR = IC * sqrt(Breadth) * TC
```

For this project, the most important warning is that the number of visible confirmations is not
the same as the number of independent confirmations.

## Application

Future signal families:

- SMC structure: BOS, ChoCh, IDM, sweep quality
- POI quality: OB, FVG, H4 confluence
- session context: Asia, London, New York
- volatility/displacement: ATR, candle body strength, impulse quality
- regime intelligence: Markov, HMM, macro
- forecast confirmation: Kronos or equivalent
- execution quality: RR, SL distance, target distance, spread/slippage proxy

The engine should estimate which families add independent information and which are redundant.

## Consequences

- Add future docs under `docs/roadmap-signal-conviction-engine.md`.
- Future code can live under `smc_ai/scoring/`.
- Backtests should compare SMC pure against SMC + conviction scoring.
- Any sizing logic must remain conservative and capped by risk rules.

## Safety Boundary

The conviction engine may recommend trade tier and maximum allowed risk.

It must not execute trades directly, bypass SMC validity, or justify raw Kelly sizing in live
trading.
