# SMC AI Project Brain

This directory is the long-term markdown memory for the SMC AI project.

It is intentionally simple:

- plain markdown files
- factual decisions
- experiment notes
- backtest summaries
- weekly reviews
- operational notes

Later, GBrain can index this directory so agents can ask what the project already knows
before proposing new work.

This directory is not a trading engine, not a broker interface, and not an autonomous
execution layer.

## Directories

- `decisions/` - accepted, rejected, or superseded project decisions.
- `experiments/backtests/` - measured backtest outcomes.
- `experiments/autoresearch/` - ARIS-style research loops and keep/revert results.
- `experiments/regime-intelligence/` - Markov, HMM, Kronos, macro research notes.
- `experiments/regime-intelligence/signal-conviction-engine.md` - future statistical
  scoring notes for IC, correlation, effective breadth, and conviction tiers.
- `strategy/` - durable WinWorld SMC rules and strategy definitions.
- `operations/` - VPS, MT5, dashboard, and deployment operating notes.
- `weekly-reviews/` - weekly strategy health and improvement reviews.

Future optional layer:

- `nashsu/llm_wiki` may be tested later to generate a richer linked concept wiki from raw
  sources, while `brain/` remains the lightweight durable memory.
- `cocoindex-io/cocoindex` may be evaluated later for incremental indexing of changing
  knowledge sources such as backtests, weekly reviews, and research notes.

## Note Rules

1. Record facts, decisions, and measurements.
2. Do not store broker credentials, API keys, account numbers, or private secrets.
3. Date experiment and decision notes.
4. Mark whether an idea was kept, rejected, or postponed.
5. Link to result files or commits when possible.
