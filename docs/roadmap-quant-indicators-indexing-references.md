# Quant, Indicators, and Indexing References

**Date:** 2026-05-19
**Status:** Added as future references
**Current priority remains:** Phase 1 SMC core + backtester + dashboard

This document records three additional repositories that can help the SMC AI project later.
They do not replace the WinWorld SMC core.

---

## 1. cinar/indicator

Repository: `cinar/indicator`

Role: technical-indicator and backtesting reference.

Useful aspects:

- large catalog of indicators across trend, momentum, volatility, volume, and valuation
- built-in strategy and backtesting concepts
- compound strategies such as majority / AND / OR logic
- streaming-oriented design in Go
- MCP support, which is interesting for future AI tooling ideas

How it can help us:

- inspiration for indicator taxonomy
- reference list for volatility, momentum, and volume features
- ideas for compound strategy composition
- possible benchmark/reference for future indicator behavior

Boundary:

- not a Phase 1 dependency
- not Python-native
- should not replace `smartmoneyconcepts` or our SMC-specific logic
- use as reference/inspiration, not as core implementation unless a clear bridge is justified

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
