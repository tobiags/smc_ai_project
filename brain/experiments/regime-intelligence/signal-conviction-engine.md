# Signal Conviction Research Notes

**Status:** future research track

Research question:

```text
Can statistical combination of independent signal families improve SMC expected value without
overfitting or overcounting correlated confirmations?
```

## Initial Hypothesis

SMC setup validity should remain rule-based, but trade quality can be improved by measuring:

- signal family IC
- correlation between signal families
- effective breadth
- conviction score
- performance by pair/session/regime
- Monte Carlo robustness of edge estimates

## First Future Experiments

1. Label every historical SMC signal with outcome:
   - win/loss
   - RR captured
   - max adverse excursion
   - max favorable excursion
   - time to target

2. Add signal family features:
   - structure quality
   - POI quality
   - session score
   - volatility/displacement score
   - regime score
   - execution score

3. Measure correlation:
   - feature correlation matrix
   - per-pair redundancy
   - per-session redundancy

4. Test conviction tiers:
   - A+
   - A
   - B
   - C
   - Reject

5. Compare against SMC pure:
   - win rate
   - profit factor
   - max drawdown
   - average RR
   - stability over rolling windows

## Rule

Keep only changes that improve measured expected value without increasing hidden fragility.
