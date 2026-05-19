# LLM Wiki / Knowledge Wiki Layer

**Date:** 2026-05-19
**Status:** accepted as future knowledge-memory reference
**Scope:** Phase 2+ / Phase 4 research memory, not Phase 1 trading logic

## Decision

Add `nashsu/llm_wiki` as a future reference for building a structured research wiki from
project sources.

It complements the current `brain/` markdown memory and the future GBrain index/search layer.

## Reason

The project will keep accumulating heterogeneous sources:

- WinWorld PDFs
- trading articles
- backtest reports
- weekly reviews
- ARIS research loops
- strategy decisions
- forward-test incidents
- regime, Kronos, Markov/HMM, and conviction-engine research

A raw folder of notes can become difficult to navigate. `llm_wiki` is useful because it follows
a wiki-building pattern: sources are ingested once, converted into structured wiki pages, linked
through concepts/entities, and kept current.

## Relationship to GBrain

```text
brain/ markdown
-> GBrain indexes/searches durable facts
-> LLM Wiki may generate and maintain a richer concept wiki from raw sources
```

GBrain is the lightweight search/index layer.

LLM Wiki is a heavier optional knowledge-building layer.

## Useful Ideas to Borrow

- raw sources remain separate from generated wiki pages
- generated pages use frontmatter and source traceability
- `index.md` becomes a navigation entry point
- `log.md` records ingest/update history
- links between concepts/entities make knowledge easier to traverse
- graph/community detection can surface clusters and gaps
- human remains the curator; LLM maintains and proposes structure

## Boundary

This is not a trading engine, not an execution layer, and not required for Phase 1.

It should not touch MT5, broker credentials, or live execution.

Future trial is allowed after the core system has enough documents/results to justify it.
