# Strategy Profiles Architecture

**Date:** 2026-05-19
**Status:** accepted architecture principle

## Goal

The project must be a clean trading research infrastructure, not a single-strategy application.

Today the first strategy is WinWorld Advanced SMC. Later, the same infrastructure should support:

- ICT
- Simple Markets Swing Trading Plan
- other documented discretionary or systematic strategies

The strategy changes. The infrastructure stays stable.

## Core Principle

Separate reusable infrastructure from strategy-specific logic.

```text
DataProvider
  -> FeaturePipeline
  -> StrategyProfile
  -> SignalComposer
  -> RiskModel
  -> BacktestRunner
  -> Report/Dashboard/Brain
```

## Reusable Infrastructure

These components should not depend on WinWorld-specific rules:

- OHLCV data loading
- symbol and timeframe handling
- session calendars
- feature computation pipeline
- backtest runner
- risk accounting
- performance metrics
- dashboard visualization
- report generation
- experiment logging
- `brain/` knowledge memory
- ARIS weekly research loop

## StrategyProfile Contract

Each strategy profile should define:

- strategy id and version
- required timeframes
- required market sessions
- setup rules
- entry triggers
- invalidation rules
- stop-loss rules
- target rules
- risk model defaults
- signal labels
- rejection reasons
- experiment parameters

Example:

```text
StrategyProfile: winworld_smc_v1
  timeframes: D1, H4, M15
  setup: liquidity -> IDM -> valid POI -> BOS/ChoCh
  entry: M15 schema confirmation
  invalidation: sweep-only BOS, missing IDM, invalid OB, RR < 1:5
```

Future examples:

```text
StrategyProfile: ict_v1
StrategyProfile: simple_markets_swing_v1
```

## SignalComposer

The `SignalComposer` combines raw strategy signals and optional confirmations.

Useful composition patterns inspired by `cinar/indicator`:

- `AND`: all required confirmations must agree
- `OR`: one of several optional confirmations can validate
- `Majority`: a minimum number of independent confirmations must agree
- `Split`: detection, filtering, sizing, and execution are separated

This is where future confirmations can be plugged in without changing the strategy core:

- Markov/HMM regime confirmation
- Kronos confirmation
- volatility/displacement filters
- Signal Conviction Engine
- session quality filters

## Boundary

No future strategy should force a rewrite of:

- the data layer
- the dashboard
- the backtest runner
- the report format
- the project memory layer
- the VPS deployment structure

If a new strategy requires that, the abstraction is wrong and must be reviewed before coding.

## Decision

WinWorld SMC becomes Strategy Profile 001, not the whole platform.

The platform is designed to compare, replace, improve, and retire strategies over time.
