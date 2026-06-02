# Références ZiadFrancis

**Date :** 2026-06-02
**Décision :** accepté comme références futures de recherche, comparaison et inspiration

## Repos ajoutés

- `ZiadFrancis/ReinforcementTrading_Part_1`
- `ZiadFrancis/NewsSentimentScanner`
- `ZiadFrancis/AscendingTrianglesBacktest`
- `ZiadFrancis/BreakOutLiquiditySweep`
- `ZiadFrancis/Genetics_Trading_Part_1`
- `ZiadFrancis/Transformers_Trading_01`

## Classement

### Priorité la plus proche SMC

`BreakOutLiquiditySweep`

À utiliser plus tard pour comparer :

- breakout
- liquidity sweep
- wick-only break
- sweep vs BOS
- logique externe sur EURUSD H1

### Analyste news / sentiment

`NewsSentimentScanner`

À garder pour le futur `News/Macro Analyst`.

### StrategyProfile future

`AscendingTrianglesBacktest`

À garder comme exemple de stratégie pattern chartiste pouvant entrer dans notre architecture
`StrategyProfile`, sans remplacer WinWorld.

### RL léger

`ReinforcementTrading_Part_1`

Référence pédagogique plus légère que TradeMaster.

### Optimisation génétique / ARIS

`Genetics_Trading_Part_1`

À garder pour ARIS/autoresearch, mais seulement sous garde-fous anti-overfitting.

### Transformers Forex

`Transformers_Trading_01`

Référence Phase 4 pour modèle séquentiel Forex, recherche uniquement.

## Limites

- Aucun repo ne remplace WinWorld SMC.
- Pas de dépendance Phase 1.
- Pas d'accès MT5 live.
- Pas de modèle RL/Transformer/génétique autorisant un trade invalidé par les règles SMC.
- Prudence sécurité avec les fichiers `pickle` / `dill`.

## Doc principale

`docs/roadmap-ziadfrancis-references.md`
