# LLM Wiki / Knowledge Wiki Roadmap

**Date:** 2026-05-19
**Status:** Validated by user as future knowledge-memory reference
**Repository:** `nashsu/llm_wiki`
**Current priority remains:** SMC core, backtester, dashboard, and clean markdown `brain/`

`llm_wiki` is a cross-platform desktop application that turns documents into an organized,
interlinked knowledge base. It is relevant to the SMC AI project because we are building a
research-heavy trading system that must remember what it has already learned.

---

## Verdict

Useful later.

Not part of Phase 1.

It should be treated as a future knowledge-memory reference, not as trading logic.

---

## Why It Fits

Our project will accumulate:

- SMC WinWorld rules
- NotebookLM/PDF findings
- trading research articles
- backtest results
- parameter decisions
- rejected experiments
- Markov/HMM/Kronos notes
- Signal Conviction Engine research
- weekly ARIS reviews
- forward-test incidents

`llm_wiki` is useful because it goes beyond simple RAG. Instead of answering from chunks every
time, it can help build a persistent wiki from sources.

The pattern matches our need:

```text
raw sources
-> structured wiki pages
-> links between concepts
-> graph / clusters / gaps
-> better agent recall
```

---

## Relationship With Existing Memory Plan

Current approved approach:

```text
brain/
-> markdown durable facts
-> later GBrain indexing/search
```

Future optional approach:

```text
raw/sources/
-> LLM Wiki ingest
-> wiki/
-> linked concepts/entities
-> graph insights
-> agent-readable knowledge base
```

GBrain and LLM Wiki are complementary:

- GBrain: lightweight query/index layer over our markdown memory.
- LLM Wiki: heavier system for generating and maintaining a structured concept wiki.

---

## Candidate Future Structure

```text
knowledge/
+-- raw/
|   +-- sources/
|       +-- winworld/
|       +-- articles/
|       +-- backtests/
|       +-- weekly-reviews/
+-- wiki/
|   +-- index.md
|   +-- log.md
|   +-- concepts/
|   +-- setups/
|   +-- experiments/
|   +-- decisions/
+-- schema/
    +-- purpose.md
    +-- rules.md
```

This should not replace `brain/` immediately. It can be tested later when the project has enough
material to justify a richer knowledge system.

---

## What We May Borrow

- raw sources stay immutable or traceable
- generated pages cite their sources
- wiki links connect concepts such as IDM, OB, FVG, HMM, Kronos, and conviction scoring
- ingest logs record what changed and when
- graph/community detection can reveal isolated ideas, missing research, or contradictory notes
- human validates major knowledge changes

---

## Future Experiment

After Phase 1 and initial real backtests:

1. Export project sources into a `knowledge/raw/sources/` folder.
2. Test `llm_wiki` locally on a copy of the project research material.
3. Inspect whether it produces useful pages and links.
4. Compare usefulness against plain `brain/` + GBrain.
5. Keep only if it reduces repeated analysis and improves research traceability.

Success criteria:

- clearer navigation across strategy rules and experiments
- source traceability preserved
- no hallucinated strategy rule accepted without human review
- useful links between rules, backtests, and research notes
- no dependency on live trading infrastructure

---

## Explicit Non-Goals

`llm_wiki` must not:

- replace the SMC backtester
- execute trades
- store broker credentials
- become required for Phase 1
- rewrite strategy rules without human validation
- create unverifiable facts from trading articles
