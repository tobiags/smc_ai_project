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

## Roadmap Placement

```text
Phase 1
  SMC core + sample backtest + FastAPI dashboard

Phase 2
  Real historical data + serious backtests + VPS dashboard

Phase 2.5
  Markov/HMM Regime Intelligence

Phase 3
  TradingView MCP + TradingAgents-style real-time decision assistant

Phase 4
  ARIS weekly/night research + Qlib/Kronos/TradingEconomics research lab

Phase 5
  AI-Trader-inspired sharing/signal layer
```
