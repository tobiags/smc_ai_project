# Project Memory Layer / GBrain

**Date:** 2026-05-18
**Status:** accepted
**Scope:** future project memory layer, not Phase 1 trading logic

## Decision

Add a local markdown `brain/` directory as the long-term memory base for the project.

GBrain may later index this directory so agents can retrieve durable facts across sessions.

Lossless is not integrated now. It remains an optional future runtime feature if Hermes Agent
or another long-session agent runtime needs searchable raw conversation recall.

Hermes Agent may be evaluated later as a research/runtime layer, but the trading core remains
independent from Hermes, OpenClaw, Claude, Codex, and every other agent runtime.

## Reason

The project will accumulate facts that must not be rediscovered repeatedly:

- validated WinWorld SMC rules
- architecture decisions
- tested parameters
- backtest results
- failed variants and rejection reasons
- weekly ARIS conclusions
- forward-test incidents
- VPS, dashboard, and MT5 operating rules

A markdown-first brain gives the project a stable memory before any runtime-specific indexing
or agent framework is added.

## Consequences

- `brain/` becomes the source of durable project facts.
- Docs remain in `docs/`; durable operational/strategy memory is duplicated or summarized in
  `brain/` when it needs to be queryable later.
- GBrain is a future index/search layer, not an immediate dependency.
- Lossless is postponed.
- Agent runtimes may read/write notes, but they do not get direct live trading control.

## Security Boundary

No broker credentials, API keys, account numbers, or private secrets are allowed in `brain/`.

No autonomous agent can modify real trading parameters or execute live MT5 trades without
explicit human validation and safety gates.
