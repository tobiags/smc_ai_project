# WinWorld SMC Rules Memory

**Status:** living project memory
**Source:** user-provided WinWorld Advanced SMC PDFs via NotebookLM

This file is a durable memory index for rules that the implementation must preserve.

## Timeframe Hierarchy

```text
D1 -> H4 -> M15
```

- D1: directional bias and previous day high/low.
- H4: institutional confluence filter through active OB/FVG zones.
- M15: local structure, POI, and entry execution.

M15 is the validated entry timeframe for this project.

## Structure Rules

- BOS requires a candle body close beyond the structural point.
- Wick-only break is a sweep, not a BOS.
- ChoCh is a potential reversal signal, but IDM priority can override it.
- Structure without IDM is invalid.
- If IDM and ChoCh overlap, IDM takes priority and ChoCh is ignored.

## POI Rules

- A valid OB must take liquidity and be followed by valid imbalance.
- Only two true OBs exist per leg: OB IDM and OB Extreme.
- Middle OBs between those points are treated as liquidity traps.
- FVG/imbalance is a three-candle inefficiency where candle 1 and candle 3 do not overlap.

## Entry Rules

- Price must reach a valid M15 POI aligned with H4 confluence.
- Entry schemas are separated into IDM-based and IFC-based families.
- Minimum RR is 1:5. Trades below that threshold are rejected.

## Implementation Reminder

The first sample backtester may use simplified deterministic signals, but final strategy logic
must implement these WinWorld constraints before any serious performance claims.
