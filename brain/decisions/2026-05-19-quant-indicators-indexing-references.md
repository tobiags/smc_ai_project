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

Use as an indicator taxonomy and strategy-composition reference.

Useful for:

- volatility, momentum, trend, and volume feature ideas
- compound strategy patterns
- backtesting architecture inspiration
- future MCP/agent tooling ideas

Do not use as a core dependency now because it is Go-based and the project core is Python.

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
