# Agentic Research & Platform Roadmap

**Date:** 2026-05-17
**Status:** Validated by user as future roadmap
**Current priority remains:** Phase 1 SMC core + FastAPI/Jinja2/Plotly dashboard

This document records future research/platform references. These projects guide later architecture, but none replace the WinWorld SMC core.

---

## Core Principle

The system must never become static.

Approved continuous improvement loop:

```text
SMC setup
-> backtest
-> report
-> critique
-> improvement proposal
-> re-test
-> keep/revert
```

This loop runs before real trading, then continues weekly during live operation. Strategy changes must remain auditable and should require human approval before touching live/semi-auto parameters.

---

## 1. ARIS — Overnight Research / Optimization

Repository: `wanshuiyin/Auto-claude-code-research-in-sleep`

Decision: validated.

Role:

- autonomous overnight research after the system and demo forward test exist
- detect weak spots, failure clusters, and "potholes"
- propose targeted fixes
- re-run backtests
- keep/revert based on measured improvement
- continue weekly during real operation

Target workflow:

```text
weekly run
-> analyze last trades + backtest variants
-> identify worst failure category
-> propose one change
-> test same dataset
-> keep only if score improves without hidden tradeoffs
```

This extends the Karpathy-style Autoresearch process already validated.

---

## 2. TradingAgents — Real-Time Decision Committee

Repository: `TauricResearch/TradingAgents`

Decision: validated for the real trading assistant.

Adapted roles:

- Technical Analyst: validates SMC structure, OB/FVG/IDM, entry schema
- Regime Analyst: validates Markov/HMM/Kronos agreement
- News/Macro Analyst: checks macro/news/calendar context
- Risk Manager: validates RR, SL/TP, drawdown, exposure, session
- Portfolio Manager: final accept/reject/tier decision

Future live decision flow:

```text
SMC signal
-> technical validation
-> regime validation
-> macro/news check
-> risk check
-> quality tier A/B/C or reject
```

---

## 3. QuantDinger — Platform Architecture Reference

Repository: `brokermr810/QuantDinger`

Decision: validated as architecture inspiration after the WinWorld logic is stable.

Patterns to borrow:

- strategy tracking dashboard
- broker account views
- market data vs execution separation
- audit logs for agent decisions
- paper-only safety defaults
- MCP / agent gateway
- Docker / VPS deployment patterns

Do not adopt directly before the SMC core is stable. It is a reference for the full platform, not Phase 1 code.

---

## 4. Qlib — Quant Research Lab

Repository: `microsoft/qlib`

Decision: validated for Phase 4.

Use cases:

- serious quant/ML experimentation
- compare our regime models against established research workflows
- factor and model research
- possible benchmark environment for Markov/HMM/Kronos ideas

Not part of Phase 1/2. It is too heavy before the SMC engine is validated.

---

## 5. AI-Trader — Future Sharing / Signal System

Repository: `HKUDS/AI-Trader`

Decision: validated for a future product/community layer.

Use cases:

- signal feed
- agent-native trading interface
- paper trading first
- separate human control from agent recommendations
- future sharing/copy/signal model for people who want to benefit from the system

This is not part of the private backtester core. It belongs after the system proves itself.

---

## 6. Scientific Agent Skills — Research Skill Discipline

Repository: `K-Dense-AI/scientific-agent-skills`

Decision: validated for future structured research workflows.

Potential internal skills:

- `/smc-backtest-review`
- `/smc-signal-audit`
- `/smc-regime-research`
- `/smc-night-research`

Goal: keep research rigorous, auditable, and less hallucination-prone.

---

## 7. Dash — Advanced Analytical Dashboard Option

Repository: `plotly/dash`

Decision: validated as a future option, not Phase 1.

Current dashboard choice remains:

```text
FastAPI + Jinja2 + Plotly
```

Dash becomes interesting if the dashboard needs:

- dynamic filters
- parameter sliders
- interactive trade crossfiltering
- live simulation panels
- advanced analyst workbench

Do not switch to Dash until the simple FastAPI dashboard feels limiting.

---

## 8. GBrain — Project Memory / Knowledge Layer

Repository: `garrytan/gbrain`

Decision: validated as a future project memory layer.

Role:

- index the local markdown `brain/` directory
- let agents query durable project facts before proposing changes
- prevent repeated analysis of already-decided strategy and architecture questions
- preserve reasons for kept/rejected experiments
- support ARIS weekly reviews and Hermes Agent research later

Approved memory base:

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

GBrain is not a trading dependency. It is a future search/index layer over markdown notes.

Lossless-style runtime memory is postponed. It may become useful later if Hermes Agent or
another long-running agent runtime loses important details during overnight sessions.

Security boundary:

- no broker credentials in `brain/`
- no agent runtime receives direct MT5 live execution rights without strict safeguards
- strategy changes proposed by agents must be measured by backtest and validated by a human

See: `docs/roadmap-project-memory-gbrain.md`

---

## 9. Signal Ensemble / Conviction Engine

Decision: validated as a future statistical, probabilistic, and mathematical layer.

Role:

- estimate whether SMC confirmations are genuinely independent
- penalize correlated confirmations that create false confidence
- score valid setups into trade tiers such as A+, A, B, C, or Reject
- support conservative position sizing recommendations
- improve expected value, not just directional accuracy

Core principle:

```text
IR = IC * sqrt(Breadth) * TC
```

For this project:

- `IC` measures whether a signal family predicts future trade outcome
- `Breadth` is the effective number of independent confirmations after correlation penalty
- `TC` represents execution quality after spread, slippage, timing, and practical constraints

Candidate signal families:

- SMC structure: BOS, ChoCh, IDM, sweep quality
- POI quality: OB, FVG, H4 confluence
- session context: Asia, London, New York
- volatility/displacement: ATR, candle body strength, impulse quality
- regime intelligence: Markov, HMM, macro
- forecast confirmation: Kronos or equivalent
- execution quality: RR, SL distance, target distance, spread/slippage proxy

Boundary:

- this layer does not replace WinWorld SMC validity
- raw Kelly sizing is rejected for live trading
- all weights and tiers must be tested walk-forward

See: `docs/roadmap-signal-conviction-engine.md`

---

## 10. LLM Wiki — Structured Knowledge Wiki

Repository: `nashsu/llm_wiki`

Decision: validated as a future knowledge-memory reference.

Role:

- transform raw research sources into a linked wiki
- keep source traceability between raw documents and generated pages
- connect concepts such as IDM, OB, FVG, Markov, HMM, Kronos, and conviction scoring
- surface knowledge gaps, isolated concepts, and useful research clusters
- complement `brain/` and future GBrain indexing

Relationship to current memory:

```text
brain/ = lightweight durable markdown memory
GBrain = future search/index over markdown facts
LLM Wiki = optional heavier generated concept wiki from raw sources
```

Boundary:

- not part of Phase 1
- not a trading engine
- no broker credentials or live execution access
- generated knowledge must remain human-reviewed before it changes strategy rules

See: `docs/roadmap-llm-wiki-knowledge-layer.md`

---

## 11. Quant / Indicator / Indexing References

Decision: accepted as future references.

Repositories:

- `cinar/indicator`
- `hudson-and-thames/mlfinlab`
- `cocoindex-io/cocoindex`

Roles:

- `cinar/indicator`: language-independent indicator taxonomy, strategy-composition,
  decorator/filter, MCP action, and backtesting inspiration
- `mlfinlab`: quant methodology reference for labeling, cross-validation, codependence,
  feature importance, backtest overfitting, and bet sizing
- `cocoindex`: future incremental indexing reference for long-horizon agent memory and
  changing project knowledge

Boundary:

- none of these replaces WinWorld SMC rules
- none enters Phase 1 implementation
- `mlfinlab` licensing must be checked before direct code use
- `cinar/indicator` should be mined for reusable trading patterns, not adopted because of
  its implementation language
- `cocoindex` belongs to knowledge infrastructure, not trading execution

Architecture principle:

The platform must support replaceable strategy profiles. WinWorld SMC is the first strategy,
but the same infrastructure should later run ICT, Simple Markets Swing Trading Plan, or another
documented methodology through the same data, backtest, dashboard, report, and memory layers.

See: `docs/architecture-strategy-profiles.md`

See: `docs/roadmap-quant-indicators-indexing-references.md`

---

## Roadmap Placement

```text
Phase 1
  SMC core + sample backtest + FastAPI dashboard

Phase 2
  Real historical data + serious backtests + VPS dashboard

Phase 2+
  Project Memory / Knowledge Layer
  - brain/ markdown repo
  - later: GBrain index/search
  - optional LLM Wiki trial when sources/results justify it

Phase 2.5
  Markov/HMM Regime Intelligence
  Signal Ensemble / Conviction Engine
  Indicator taxonomy and codependence research references

Phase 3
  TradingView MCP + TradingAgents-style real-time decision assistant

Phase 4
  ARIS weekly/night research + Qlib/Kronos/TradingEconomics research lab
  SMC + regime + Kronos + conviction engine comparative research
  LLM Wiki / Knowledge Wiki evaluation for research memory
  mlfinlab-style validation, overfitting checks, and bet sizing research

Phase 4+
  Incremental knowledge indexing
  - evaluate cocoindex against GBrain / LLM Wiki

Phase 5
  AI-Trader-inspired sharing/signal layer
```
