# Project Memory / GBrain Roadmap

**Date:** 2026-05-18
**Status:** Validated by user as future memory layer
**Current priority remains:** independent SMC core, backtester, and FastAPI dashboard

This document records the memory-layer decision for the SMC AI project.

The project will accumulate durable facts: validated WinWorld rules, architecture choices,
tested parameters, backtest outcomes, failed variants, kept/rejected changes, forward-test
incidents, VPS notes, MT5 constraints, dashboard decisions, and weekly ARIS conclusions.

Without a structured memory layer, the project will re-answer the same questions every few
weeks. The memory layer exists to prevent that drift.

---

## Verdict

GBrain is useful for this project.

Lossless is useful conceptually, but it is not part of the stack now.

Hermes Agent may become the future agent runtime around this memory layer, but the trading
core must not depend on Hermes, OpenClaw, Claude, Codex, or any other agent runtime.

---

## Role of GBrain

GBrain is treated as a future index/search layer over a local markdown brain.

It should help answer questions such as:

- Why was M15 chosen as the entry timeframe?
- Which Markov parameters were rejected and why?
- Which SMC setups fail most often on XAUUSD?
- Which strategy version had the best profit factor?
- Why is Kronos excluded from Phase 1?
- Which OHLCV validation bugs have already been fixed?
- Which changes were kept or reverted by weekly research loops?

The first step is not to install a runtime. The first step is to keep high-quality markdown
facts in a stable `brain/` directory.

---

## Approved Repository Structure

```text
brain/
+-- decisions/
+-- experiments/
|   +-- backtests/
|   +-- autoresearch/
|   +-- regime-intelligence/
+-- strategy/
+-- operations/
+-- weekly-reviews/
```

Each note should be short, dated when relevant, and written as a factual project record.

Recommended format for decision notes:

```markdown
# Decision Title

**Date:** YYYY-MM-DD
**Status:** accepted | rejected | superseded

## Decision

What we decided.

## Reason

Why we decided it.

## Consequences

What this changes for implementation, testing, or live operation.
```

---

## Lossless Decision

Lossless is not integrated now.

Reasons:

- the project already has git commits, docs, specs, plans, and local memory files
- Lossless depends on runtime-specific context engines such as OpenClaw or Hermes paths
- switching runtime only for conversation recall would add complexity too early

Future use is allowed if:

- Hermes Agent becomes the runtime for long overnight sessions
- agentic sessions become long enough that important raw details are lost
- the context engine can run isolated from live trading credentials and broker execution

---

## Hermes / OpenClaw Boundary

OpenClaw is not a required runtime for this project.

Hermes Agent can be evaluated later as an agentic research layer:

```text
SMC reports
-> brain/ markdown memory
-> Hermes Agent research/review
-> proposed change
-> backtest
-> keep/revert
-> human validation
```

The SMC trading core remains independent:

```text
smc_ai core + backtester + dashboard + MT5 adapters
!= agent runtime dependency
```

---

## Security Rules

No autonomous runtime should receive uncontrolled access to live trading execution.

Rules:

- no OpenClaw or Hermes runtime on a live trading machine without strict sandboxing
- no autonomous agent with direct MT5 live execution rights in early phases
- no strategy parameter changes in real trading without human validation
- no broker/API credentials stored in markdown memory
- agents may read/write notes and propose changes; the backtester and human review decide

The safe path is:

```text
local markdown brain
-> optional GBrain index
-> agents read/write notes
-> backtests measure changes
-> human approves strategy changes
```

The unsafe path is:

```text
full autonomous agent
+ broker live access
+ uncontrolled memory
+ no human approval
```

That path is explicitly rejected.

---

## Roadmap Placement

```text
Phase 1
  SMC core + sample backtest + FastAPI dashboard

Phase 2
  real historical data + serious backtests + VPS dashboard

Phase 2+
  Project Memory / Knowledge Layer
  - brain/ markdown repo
  - decisions, experiments, backtests, weekly reviews
  - later: GBrain indexes this folder

Phase 3
  TradingView MCP + TradingAgents-style real-time decision assistant

Phase 4
  ARIS weekly/night research + Qlib/Kronos/TradingEconomics research lab
  - Hermes Agent can be evaluated here as a research runtime

Future Optional
  Lossless-style runtime memory if long agent sessions start losing detail
```
