# Signal Ensemble / Conviction Engine Roadmap

**Date:** 2026-05-19
**Status:** Validated by user as future statistical/probabilistic layer
**Current priority remains:** SMC core first, then serious backtests

This document records how the "Fundamental Law of Active Management" idea can help the SMC
project mathematically and statistically.

The key lesson is simple:

```text
Being right about direction is not the same as having a profitable model.
```

The future system should not only ask whether an SMC setup is valid. It should also ask:

- how much independent evidence supports the trade
- whether the confirmations are genuinely different or just correlated versions of the same view
- whether the trade deserves full size, reduced size, or rejection
- whether the system's edge is stable enough to trust

---

## Core Principle

The useful framework is:

```text
IR = IC * sqrt(Breadth) * TC
```

Where:

- `IR` = information ratio, the system's risk-adjusted edge
- `IC` = information coefficient, the forecast skill of individual signals
- `Breadth` = effective number of independent bets/signals
- `TC` = transfer coefficient, implementation efficiency after execution frictions

For this project, the most important part is not the formula alone. It is the warning:

```text
10 confirmations do not equal 10 independent signals.
```

If the confirmations are correlated, their effective breadth is much lower.

---

## How This Applies to SMC

The WinWorld SMC rules remain the source of trade validity.

This layer comes after validity:

```text
SMC validity
-> signal family scoring
-> correlation / independence check
-> conviction score
-> trade tier
-> sizing recommendation
```

Example trade tiers:

- `A+`: valid SMC setup, strong independent confirmations, clean RR, acceptable regime
- `A`: valid SMC setup, good confirmation, manageable risk
- `B`: valid but lower breadth or weaker execution quality
- `C`: watchlist only
- `Reject`: valid-looking setup but poor statistical context, low RR, or high correlation risk

This should help prevent a common trading failure:

```text
The trader is right about direction, but enters too early, sizes too large, or overcounts
correlated confirmations.
```

---

## Candidate Signal Families

The future engine should treat signals by family, not as isolated checklist items.

```text
1. SMC structure
   BOS, ChoCh, IDM, sweep quality

2. POI quality
   OB, FVG, H4 confluence, mitigation state

3. Session context
   Asia range, London, New York, kill zone behavior

4. Volatility / displacement
   ATR, candle body strength, impulse quality, spread proxy

5. Regime intelligence
   Markov observable states, HMM hidden regimes, macro context

6. Forecast confirmation
   Kronos or other future sequence model confirmation

7. Execution quality
   RR, distance to SL, distance to liquidity target, spread/slippage proxy
```

The engine should estimate whether these families add independent information or simply repeat
the same market structure signal.

---

## Statistical Requirements

No signal should receive weight because it "feels right".

Each signal family must be evaluated with walk-forward tests:

- no future data leakage
- per-pair performance
- per-session performance
- per-regime performance
- rolling win rate
- profit factor
- drawdown contribution
- average RR captured
- correlation with other signal families
- stability over time

Useful measurements:

```text
IC(signal) = correlation between signal score and future trade outcome
effective_breadth = number of independent signals after correlation penalty
conviction_score = weighted signal score adjusted for noise and correlation
```

The goal is not to maximize win rate alone. The goal is to improve expected value:

```text
EV = win_rate * avg_win - loss_rate * avg_loss
```

---

## Position Sizing Direction

Kelly-style sizing is useful as a research reference, but it must be conservative.

Future sizing should use:

- fixed fractional risk first
- max daily/weekly drawdown gates
- reduced size when edge estimate is unstable
- Monte Carlo stress testing before any live use
- hard cap per trade even when conviction is high

Empirical Kelly can be tested later, but never as raw full Kelly.

Recommended rule:

```text
SMC validity decides if a trade may exist.
Conviction engine decides trade tier and maximum allowed risk.
Risk rules still cap the final size.
```

---

## Future Code Placement

```text
smc_ai/
+-- scoring/
    +-- __init__.py
    +-- signal_quality.py
    +-- correlation.py
    +-- breadth.py
    +-- conviction.py
    +-- position_sizing.py
```

Planned responsibilities:

- `signal_quality.py`: IC, forward outcome labeling, signal family statistics
- `correlation.py`: correlation matrix and shared-variance checks
- `breadth.py`: effective number of independent signals
- `conviction.py`: A+/A/B/C/reject scoring
- `position_sizing.py`: conservative risk recommendation, not direct execution

---

## Backtest Variants

After SMC pure is stable, compare:

```text
A = SMC pure
B = SMC + regime filter
C = SMC + Kronos confirmation
D = SMC + conviction engine
E = SMC + regime + Kronos + conviction engine
```

Evaluation should include:

- win rate
- profit factor
- max drawdown
- average RR
- Sharpe / Sortino
- stability by pair
- stability by session
- effective breadth of confirmations

---

## Explicit Non-Goals

This layer must not:

- replace WinWorld SMC rules
- turn every weak confirmation into a reason to trade
- use correlated signals as fake confidence
- optimize on the full dataset without walk-forward separation
- use raw Kelly sizing in live trading
- justify live automation before demo forward testing

The system should become mathematically stricter, not more reckless.
