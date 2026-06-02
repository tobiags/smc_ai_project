# Références ZiadFrancis — SMC, Sentiment, RL, Génétique, Transformers

**Date :** 2026-06-02
**Statut :** accepté comme lot de références futures
**Priorité actuelle :** ne remplace pas la Phase 1 SMC core + dashboard FastAPI/Jinja2/Plotly

Ce document classe les repos `ZiadFrancis/*` ajoutés au projet.

Règle : ces repos servent de références d'étude et de comparaison. Aucun ne remplace les règles
WinWorld SMC, le backtester personnel, MT5/Binance, ou la validation humaine.

---

## 1. BreakOutLiquiditySweep

Repository : `ZiadFrancis/BreakOutLiquiditySweep`

Rôle : référence la plus proche de notre logique SMC.

Contenu observé :

- notebook `BreakOut_Liquidity_Sweep.ipynb`
- dataset `EURUSD_Candlestick_1_Hour_BID_04.05.2003-15.04.2023.csv`

À récupérer comme idées :

- détection breakout + sweep de liquidité
- dataset EURUSD long historique pour comparaison
- approche notebook simple pour valider une règle avant industrialisation
- cas de test externe pour notre future logique `sweep != BOS`

Utilisation dans notre projet :

- Phase 2.5 : comparer notre détection de sweep/liquidity avec une approche externe
- renforcer tests SMC autour de :
  - wick-only break
  - sweep de high/low
  - rejet ou confirmation après sweep
  - différence entre sweep, BOS valide et liquidity trap

Limite :

- ne pas copier la logique comme vérité SMC
- WinWorld reste prioritaire
- timeframe du repo en H1, alors que notre entrée prioritaire reste M15 avec contexte D1/H4

---

## 2. NewsSentimentScanner

Repository : `ZiadFrancis/NewsSentimentScanner`

Rôle : référence légère pour analyste news/sentiment.

Contenu observé :

- `sentiment_analysis.py`
- notebook `test.ipynb`

À récupérer comme idées :

- scanner news/sentiment minimal
- scoring sentiment pour contexte macro/news
- structure simple pour un futur module `news_sentiment`

Utilisation dans notre projet :

- Phase 3/4 : alimenter le futur `News/Macro Analyst`
- compléter Trading Economics, calendrier macro, et contexte risk-on/risk-off
- jamais autoriser un trade seul ; seulement confirmer, réduire ou bloquer un setup

Limite :

- sentiment news bruité
- besoin de sources fiables, dates, langues, latence
- pas Phase 1

---

## 3. AscendingTrianglesBacktest

Repository : `ZiadFrancis/AscendingTrianglesBacktest`

Rôle : référence StrategyProfile future pour pattern chartiste.

Contenu observé :

- notebook `Flag_Pattern_5min.ipynb`
- `utilities.py`

À récupérer comme idées :

- backtest de pattern chartiste
- détection de structure géométrique
- séparation notebook + utilities
- exemple de stratégie non-SMC que notre architecture devrait pouvoir accueillir

Utilisation dans notre projet :

- tester l'idée `StrategyProfile` remplaçable
- prouver que l'infrastructure peut accueillir autre chose que WinWorld SMC
- référence secondaire pour ICT / Simple Markets / patterns plus classiques

Limite :

- pas prioritaire pour la logique WinWorld
- patterns chartistes peuvent être très sensibles à l'overfitting

---

## 4. ReinforcementTrading_Part_1

Repository : `ZiadFrancis/ReinforcementTrading_Part_1`

Rôle : référence RL simple, plus légère que TradeMaster.

Contenu observé :

- `trading_env.py`
- `train_agent.py`
- `test_agent.py`
- `indicators.py`
- dossier `data`

À récupérer comme idées :

- structure minimale environnement / agent / train / test
- séparation indicateurs et environnement
- exemple pédagogique plus léger que TradeMaster

Utilisation dans notre projet :

- Phase 4+ : comprendre rapidement un setup RL trading
- inspiration possible pour optimiser sortie, trade management ou sizing
- jamais pour décision live directe

Limite :

- RL très propice à l'overfitting
- aucun accès MT5 live
- paper trading obligatoire si expérimentation

---

## 5. Genetics_Trading_Part_1

Repository : `ZiadFrancis/Genetics_Trading_Part_1`

Rôle : référence optimisation génétique / ARIS.

Contenu observé :

- `gp_strategy_progress.py`
- `gp_strategy_progress_vectorbt.py`
- `strategy_01.ipynb`
- `trading_system_Load_Infer.py`
- fichiers `best_individual*.dill`

À récupérer comme idées :

- genetic programming pour générer ou optimiser règles
- suivi de progression de stratégie
- version vectorbt comme référence expérimentale
- chargement/inférence d'un individu sélectionné

Utilisation dans notre projet :

- Phase 4 : ARIS/autoresearch, mais sous garde-fous
- optimiser uniquement des paramètres ou règles candidates déjà testables
- garder / rejeter chaque changement selon backtest walk-forward + journal review

Limite :

- danger majeur d'overfitting
- ne pas laisser une stratégie générée remplacer WinWorld sans validation
- ne pas stocker ou charger des fichiers pickle/dill externes sans prudence sécurité

---

## 6. Transformers_Trading_01

Repository : `ZiadFrancis/Transformers_Trading_01`

Rôle : référence modèle séquentiel / Transformer sur Forex.

Contenu observé :

- `Transformer_Trading.ipynb`
- dataset `EURUSD_Candlestick_1_Hour_BID_01.07.2020-15.07.2023.csv`

À récupérer comme idées :

- modélisation séquentielle sur EURUSD
- préparation de séries temporelles pour transformer
- benchmark recherche pour Phase 4

Utilisation dans notre projet :

- Phase 4 Quant ML Lab
- comparaison éventuelle avec Markov/HMM/Kronos
- seulement comme confirmation probabiliste ou recherche, pas décision automatique

Limite :

- modèle lourd
- risque lookahead/overfitting élevé
- pas Phase 1/2

---

## Placement Roadmap

```text
Phase 2.5
  BreakOutLiquiditySweep
  - comparaison sweep/liquidity externe
  - tests wick-only break vs BOS valide

Phase 3
  NewsSentimentScanner
  - analyste news/sentiment pour contexte décisionnel

Phase 4
  Genetics_Trading_Part_1
  - ARIS/autoresearch sous garde-fous

  Transformers_Trading_01
  - recherche modèle séquentiel Forex

  ReinforcementTrading_Part_1
  - RL pédagogique, plus léger que TradeMaster

StrategyProfile future
  AscendingTrianglesBacktest
  - exemple stratégie pattern remplaçable
```

## Décision finale

Ajouter le lot ZiadFrancis comme références futures.

Priorité dans ce lot :

1. `BreakOutLiquiditySweep` parce qu'il touche directement liquidity/sweep/SMC.
2. `NewsSentimentScanner` pour le futur analyste news.
3. `Genetics_Trading_Part_1` pour ARIS, mais uniquement avec garde-fous anti-overfitting.
4. `Transformers_Trading_01` et `ReinforcementTrading_Part_1` pour Phase 4 recherche.
5. `AscendingTrianglesBacktest` comme exemple `StrategyProfile` non-SMC.
