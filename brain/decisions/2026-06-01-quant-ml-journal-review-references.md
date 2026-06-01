# Références Quant ML, Markov et Journal Review

**Date :** 2026-06-01
**Décision :** accepté comme références futures de recherche et d'amélioration

## Références ajoutées

- `stefan-jansen/machine-learning-for-trading`
- article Markov regimes J4nt4nCrypto
- texte collé Markov Chains + Quant Framework
- `TradeMaster-NTU/TradeMaster`
- `jpmorganchase/python-training`
- `GriffinAustin/pynance`
- `RomanMichaelPaolucci/Q-Fin`
- `federicomariamassari/financial-engineering`
- image `Journal Review + Claude / ZCT`

## Décision par famille

### Machine Learning for Trading

Référence majeure pour Phase 4 Quant Research Lab.

À utiliser pour structurer :

- features
- labels
- validation
- overfitting controls
- ML workflow
- notebooks de recherche

Ne remplace pas WinWorld SMC.

### TradeMaster

Référence RL trading.

À garder pour :

- environnement expérimental
- evaluation loop
- visualisation RL
- trade management ou sizing futur

Pas Phase 1/2. Pas d'accès live.

### Markov / Market Regimes

À intégrer plus tard dans `Regime Intelligence`.

Règles à retenir :

- matrice de transition
- minimum 20-30 transitions observées
- Monte Carlo possible
- walk-forward obligatoire
- recalibrage périodique
- probabilités de contexte, pas certitude

### Journal Review

Très utile pour améliorer la stratégie sans dériver.

Cadence cible :

- tous les 30 trades
- ou chaque mois
- ou après un lot de backtests sérieux

Diagnostics principaux :

- win rate trop bas -> sélection setup
- avg loss trop grand -> gestion / invalidation
- avg win trop petit -> sorties / objectifs
- fréquence trop faible/trop élevée -> conditions ou surtrading

Pipeline :

```text
Observer -> Hypothèse -> Règle testable -> Tracking -> Évaluation 30 trades plus tard
```

### JPM Python Training

Référence pédagogique Python / data viz / finance.

### PyNance

Référence légère features/labels/wrappers pandas.

### Q-Fin

Référence maths financières, Monte Carlo, stochastic processes, options.

### Financial Engineering

Référence Monte Carlo, Merton Jump Diffusion, stress/risk simulation.

## Limites

- Pas de dépendance Phase 1.
- Pas de remplacement du moteur SMC.
- Pas de RL live.
- Pas de ML qui autorise un trade SMC invalidé.
- Toute règle issue du journal doit être testable et falsifiable.

## Doc principale

`docs/roadmap-quant-ml-journal-review-references.md`
