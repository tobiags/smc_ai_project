# Quant, Indicators, and Indexing References

**Date:** 2026-05-19
**Status:** accepted as future references
**Scope:** roadmap/memory only, not Phase 1 implementation

## Decision

Add three repositories as future references:

- `cinar/indicator`
- `hudson-and-thames/mlfinlab`
- `cocoindex-io/cocoindex`

## Use in This Project

### cinar/indicator

Use as an indicator taxonomy, strategy-composition, and backtesting-pattern reference.

Do not judge this repo by its implementation language. The useful part for us is the design:
how indicators are grouped, how strategies are composed, how actions are produced, and how
backtests can compare multiple symbols and multiple strategies.

Useful for:

- volatility, momentum, trend, and volume feature ideas
- compound strategy patterns: AND, OR, Majority, Split
- strategy decorators / filters: stop-loss, no-loss, inverse, action transforms
- volatility/displacement candidates: ATR, Bollinger Band Width, Choppiness Index,
  Donchian Channel, Keltner Channel, SuperTrend, Ulcer Index
- backtesting architecture inspiration, especially symbol x strategy reporting
- deterministic CSV fixtures for future indicator tests
- future MCP/agent tooling ideas

Do not use as a core dependency now. Extract the useful patterns and re-implement them in
our Python architecture only when needed.

Key architecture consequence:

The project must remain a strategy research infrastructure, not a WinWorld-only application.
WinWorld SMC is the first strategy profile. Later profiles can include ICT, Simple Markets Swing
Trading Plan, or another documented strategy without rewriting data loading, backtesting,
dashboarding, reporting, or the project memory layer.

Target abstraction:

```text
DataProvider -> FeaturePipeline -> StrategyProfile -> SignalComposer
             -> RiskModel -> BacktestRunner -> Report/Dashboard/Brain
```

Every future strategy profile should define:

- required timeframes
- setup rules
- entry triggers
- invalidation rules
- risk model defaults
- reporting labels
- experiment parameters

### hudson-and-thames/mlfinlab

Use as a serious quant methodology reference.

Useful for:

- labeling SMC outcomes
- cross-validation
- backtest overfitting checks
- codependence and correlation measures
- feature importance
- bet sizing
- Signal Conviction Engine research

Check licensing before using code directly.

### cocoindex-io/cocoindex

Use as a future incremental indexing reference.

Useful for:

- long-horizon agent memory
- indexing changing backtest reports and weekly reviews
- future ARIS/Hermes/GBrain/LLM Wiki workflows
- avoiding full reprocessing of knowledge sources

## Boundary

None of these repositories replaces:

- WinWorld SMC rules
- `smartmoneyconcepts`
- the Python SMC backtester
- FastAPI dashboard
- human validation before strategy changes

They are references for later phases.
