# Quant, Indicators, and Indexing References

**Date:** 2026-05-19
**Status:** Added as future references
**Current priority remains:** Phase 1 SMC core + backtester + dashboard

This document records three additional repositories that can help the SMC AI project later.
They do not replace the WinWorld SMC core.

---

## 1. cinar/indicator

Repository: `cinar/indicator`

Role: technical-indicator, strategy-composition, and backtesting reference.

Important framing: we do not care that this repository is implemented in Go. The useful part is
not the language, it is the architecture and the trading patterns we can translate into our own
Python infrastructure.

Useful aspects:

- large catalog of indicators across trend, momentum, volatility, volume, and valuation
- built-in strategy and backtesting concepts
- compound strategies such as majority / AND / OR logic
- strategy decorators and filters such as stop-loss, no-loss, inverse, and action transforms
- multi-symbol / multi-strategy backtest reporting ideas
- MCP support, which is interesting for future AI tooling ideas

How it can help us:

- inspiration for indicator taxonomy
- reference list for volatility, momentum, and volume features
- reusable strategy-composition patterns:
  - `AND`: only validate an entry when all required confirmations agree
  - `OR`: validate when at least one of several optional confirmations agrees
  - `Majority`: validate when a minimum number of independent confirmations agree
  - `Split`: separate detection, filtering, sizing, and execution actions
- reusable filter/decorator patterns:
  - structural stop-loss layer
  - no-loss / breakeven logic after partial progress
  - inverse strategy for testing whether a signal is genuinely directional
  - action transform from raw signal to `BUY`, `SELL`, `WAIT`, or `REJECT`
- volatility/displacement feature candidates:
  - ATR for structural stop distance and displacement strength
  - Bollinger Band Width for compression/expansion context
  - Choppiness Index for trend vs range filtering
  - Donchian Channel for breakout context
  - Keltner Channel / SuperTrend as optional regime filters
  - Ulcer Index for drawdown pressure and risk stress
- benchmark/reference for future indicator behavior and CSV fixture testing
- MCP OHLCV -> strategy -> action pattern for future agent interfaces

Boundary:

- not a Phase 1 dependency
- should not replace `smartmoneyconcepts` or our SMC-specific logic
- do not copy the implementation language or force a Go bridge
- extract the patterns and re-implement only the useful parts in our Python architecture
- use as reference/inspiration, not as core implementation unless a clear bridge is justified

Design impact:

`cinar/indicator` reinforces that our project should be a strategy research infrastructure, not
a one-strategy codebase. WinWorld SMC is the first strategy profile, but the engine must later
accept ICT, Simple Markets Swing Trading Plan, or any other documented strategy without rewriting
data loading, backtesting, reporting, dashboards, or research memory.

Target abstraction:

```text
DataProvider
  -> FeaturePipeline
  -> StrategyProfile
  -> SignalComposer
  -> RiskModel
  -> BacktestRunner
  -> Report/Dashboard/Brain
```

Strategy profiles should define their own:

- required timeframes
- setup rules
- entry triggers
- invalidation rules
- risk model defaults
- reporting labels
- experiment parameters

This prevents the system from becoming "the WinWorld app". It becomes a clean trading research
platform where WinWorld SMC is Strategy Profile 001.

See also: `docs/architecture-strategy-profiles.md`

---

## 2. hudson-and-thames/mlfinlab

Repository: `hudson-and-thames/mlfinlab`

Role: serious financial machine-learning and quant research reference.

Useful modules/concepts:

- data structures
- labeling
- sampling
- feature engineering
- backtest overfitting tools
- cross-validation
- feature importance
- bet sizing
- codependence measures
- clustering and networks

How it can help us:

- design robust labels for SMC trade outcomes
- avoid lookahead bias and backtest overfitting
- validate the Signal Conviction Engine statistically
- study bet sizing and uncertainty-adjusted risk
- measure codependence/correlation between signal families
- support later Qlib/quant research lab comparisons

Boundary:

- licensing must be checked before using code directly
- treat primarily as conceptual/research reference unless license and access are clear
- not Phase 1
- no ML layer should be trusted before SMC pure has serious walk-forward backtests

---

## 3. cocoindex-io/cocoindex

Repository: `cocoindex-io/cocoindex`

Role: incremental indexing engine for long-horizon agents and knowledge pipelines.

Useful aspects:

- incremental indexing mindset
- useful for long-running agent systems where project knowledge changes over time
- fits our future `brain/`, GBrain, and LLM Wiki direction
- can help avoid reprocessing every source from scratch

How it can help us:

- index backtest reports, weekly reviews, and strategy notes as they change
- keep a knowledge pipeline current for ARIS/Hermes/agentic research
- support future source-to-wiki or source-to-brain workflows
- make long-term research memory more operational

Boundary:

- not a trading dependency
- not Phase 1
- no access to broker credentials or live execution
- evaluate later against simpler `brain/` + GBrain + LLM Wiki workflow

---

## Roadmap Placement

```text
Phase 1
  SMC core, sample backtest, dashboard

Phase 2
  real data, serious backtests, VPS dashboard

Phase 2.5
  Signal Conviction Engine
  - use cinar/indicator as feature taxonomy reference
  - use mlfinlab concepts for labeling, codependence, feature importance, bet sizing

Phase 4
  Quant Research Lab
  - evaluate mlfinlab-style methods and Qlib workflows
  - validate overfitting, cross-validation, and bet sizing discipline

Phase 4+
  Knowledge Pipeline
  - evaluate cocoindex for incremental indexing
  - compare with GBrain and LLM Wiki
```

---

## Decision

Add all three as references:

- `cinar/indicator`: indicator/backtesting taxonomy and composition reference
- `hudson-and-thames/mlfinlab`: quant ML methodology reference
- `cocoindex-io/cocoindex`: future incremental knowledge indexing reference

None of them enters the current implementation path until SMC pure and the first dashboard loop
are stable.
