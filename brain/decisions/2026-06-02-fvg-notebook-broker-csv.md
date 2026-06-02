# FVG Notebook et CSV Broker EURUSD H1

**Date :** 2026-06-02
**Décision :** intégrer les idées utiles au moteur Phase 1

## Sources locales

- `C:\Users\tobid\Downloads\FVG.ipynb`
- `C:\Users\tobid\Downloads\EURUSD_Candlestick_1_Hour_BID_01.07.2020-15.07.2023.csv`

## Ce qui a été récupéré

### Loader CSV

Le CSV utilise le format broker :

- colonne temps : `Gmt time`
- colonnes OHLCV en majuscules
- timestamp : `dd.mm.yyyy HH:MM:SS.mmm`

Le loader accepte maintenant ce format en plus du format `time` standard.

### FVG

Le notebook détecte les Fair Value Gaps avec une condition supplémentaire :

- gap bullish : `third_low > first_high`
- gap bearish : `third_high < first_low`
- la bougie du milieu doit avoir un body significatif
- body significatif = body milieu > moyenne body récente * multiplicateur

Le moteur conserve le FVG mécanique par défaut, mais peut maintenant activer le filtre :

```python
calculate_fvg(df, lookback_period=10, body_multiplier=1.5)
```

## Limite

Cette règle FVG est une confirmation de qualité, pas une règle WinWorld complète. Elle ne remplace
pas les validations POI / IDM / OB / BOS / ChoCh.
