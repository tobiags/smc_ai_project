# Références Quant ML, Markov et Journal Review

**Date :** 2026-06-01
**Statut :** accepté comme lot de références futures
**Priorité actuelle :** ne remplace pas la Phase 1 SMC core + dashboard FastAPI/Jinja2/Plotly

Ce document classe les nouveaux repos et articles utiles pour la suite du SMC AI Project.

Règle de base : ces références enrichissent la recherche, l'évaluation, le journal et les
futures couches ML/RL. Elles ne remplacent pas WinWorld SMC, le backtester Phase 1, MT5, ni
les règles de validation humaines.

---

## 1. Machine Learning for Trading — Stefan Jansen

Repository : `stefan-jansen/machine-learning-for-trading`

Rôle : référence majeure pour le futur `Quant Research Lab`.

À récupérer comme idées :

- workflow ML trading complet
- formulation d'un problème prédictif
- feature engineering
- labels et targets
- cross-validation et réduction de l'overfitting
- backtest de stratégies pilotées par prédictions
- NLP / sentiment / textes financiers
- deep learning et autoencoders comme pistes de recherche tardive

Utilisation dans notre projet :

- Phase 4 seulement
- enrichir les futures features du Signal Conviction Engine
- structurer les notebooks de recherche
- comparer des modèles sans toucher au coeur SMC validé

Limite :

- pas de modèle ML qui autorise un trade si WinWorld SMC l'invalide
- pas de dépendance directe avant un plan expérimental clair

---

## 2. TradeMaster — RL Trading Lab

Repository : `TradeMaster-NTU/TradeMaster`

Rôle : référence Reinforcement Learning trading complète.

À récupérer comme idées :

- environnement d'entraînement trading
- séparation données / environnement / agent / évaluation
- visualisation des performances RL
- pipeline expérimental reproductible
- comparaison d'algorithmes

Utilisation dans notre projet :

- Phase 4+ uniquement
- inspiration pour l'environnement d'apprentissage, pas pour la prise d'entrée SMC actuelle
- possible étude future : optimiser trade management, sizing ou sortie, jamais entrée live directe

Limite :

- trop lourd pour Phase 1/2
- RL = risque élevé d'overfitting
- aucun agent RL ne doit accéder à MT5 live sans sandbox stricte, paper trading et validation humaine

---

## 3. Articles Markov / Market Regimes

Sources :

- `https://j4nt4ncrypto.medium.com/using-markov-chains-to-understand-market-regimes-5596baf99f50`
- texte collé du 2026-06-01 sur Markov Chains + Quant Framework

Rôle : renforcer notre module futur `Regime Intelligence`.

À récupérer :

- matrice de transition entre états
- discrétisation en états de régime
- minimum 20-30 transitions par état/cellule avant confiance
- Monte Carlo sur trajectoires futures
- walk-forward strict pour éviter le lookahead bias
- recalibrage périodique parce que les probabilités changent
- sizing prudent, type fractional Kelly ou sizing réduit par incertitude

Adaptation à notre projet :

- utiliser Markov comme filtre probabiliste de contexte, pas comme générateur magique de trades
- états possibles : `bull`, `bear`, `sideways`, `high_vol`, `low_vol`, `choppy`
- observations possibles : returns, ATR, body strength, displacement, sweeps, BOS récents, distance OB/FVG, session
- sortie : score de contexte qui confirme, réduit, ou bloque un setup SMC

Limite :

- ne pas reprendre le marketing "win every trade"
- pas de trade sans setup SMC valide
- Markov estime des probabilités de régime, pas une certitude directionnelle

---

## 4. Journal Review Mensuel

Source : image `Journal Review + Claude / ZCT`, 30 trades mensuels.

Rôle : transformer le journal de trading en boucle d'amélioration mesurable.

Cadence :

- revue mensuelle ou tous les 30 trades
- utilisable aussi après chaque batch de backtest sérieux
- alimentée par exports de trades, screenshots et tags

Inputs à stocker par trade :

- stratégie / profil
- marché / symbole
- direction
- session
- setup grade
- screenshot entrée
- screenshot sortie
- raison d'entrée
- raison de sortie
- émotion / contexte trader si manuel
- durée du trade
- risque initial
- gain/perte
- R multiple
- invalidation ou erreur principale

Étapes de revue :

1. Statistiques principales : expectancy, win rate, avg win, avg loss, RR, fréquence.
2. Filtre par stratégie et marché : trouver ce qui imprime vraiment.
3. Comparaison screenshots : gagnants vs perdants, bruit, volume, vitesse, approche de zone.
4. Réduction des pertes : taille, émotion, durée, stop, cut, FOMO, revenge.
5. Formalisation : transformer une observation en règle testable.

Diagnostics automatiques utiles :

- win rate trop bas : problème de sélection des setups
- avg loss trop grand : problème de gestion / invalidation / cut
- avg win trop petit : problème de sortie / objectifs / trailing
- fréquence trop faible : problème de marché, sessions ou critères trop stricts
- fréquence trop élevée : surtrading ou filtres trop permissifs

Pipeline d'amélioration :

```text
Observer -> Hypothèse -> Règle testable -> Tracking -> Évaluation après 30 trades
```

Critère important :

Une règle qu'on ne peut pas falsifier n'est pas une règle, c'est une préférence.

---

## 5. JPMorgan Python Training

Repository : `jpmorganchase/python-training`

Rôle : référence pédagogique Python / numerical computing / visualisation pour traders.

Utilisation :

- docs internes
- notebooks pédagogiques
- formation personnelle Python finance
- exemples de visualisation accessibles

Limite :

- pas une dépendance du moteur
- pas une référence stratégie

---

## 6. PyNance

Repository : `GriffinAustin/pynance`

Rôle : référence légère pour assemblage/analyse de données financières.

À regarder pour :

- features
- labels
- wrappers pandas
- organisation de petites utilities financières

Limite :

- vérifier maintenance avant dépendance
- probablement inspiration plutôt que package central

---

## 7. Q-Fin

Repository : `RomanMichaelPaolucci/Q-Fin`

Rôle : référence maths financières.

À regarder pour :

- Monte Carlo
- stochastic processes
- option pricing
- greeks
- calibration

Limite :

- utile pour culture risque / quant
- pas central pour Forex SMC spot
- pas Phase 1/2

---

## 8. Financial Engineering

Repository : `federicomariamassari/financial-engineering`

Rôle : référence Monte Carlo et finance engineering.

À regarder pour :

- Merton Jump Diffusion
- simulations de trajectoires
- modèles à queues épaisses / jumps
- culture risque et stress testing

Limite :

- pas dépendance trading
- utile surtout pour Phase 4 research et scénarios de risque

---

## Placement Roadmap

```text
Phase 1
  Non : garder moteur SMC + backtest sample + dashboard simple.

Phase 2
  Journal Review initial sur résultats de backtests et forward demo.

Phase 2.5
  Regime Intelligence Markov/HMM + validation walk-forward.

Phase 3
  Journal Review connecté aux alertes et à l'assistant décisionnel.

Phase 4
  Quant Research Lab :
  - Stefan Jansen
  - Qlib
  - mlfinlab
  - TradeMaster en observation RL
  - Q-Fin / Financial Engineering pour Monte Carlo et risque

Phase 4+
  RL expérimental et optimisation trade management seulement après validation SMC.
```

## Décision finale

Ajouter ce lot comme référence de recherche.

La priorité d'implémentation immédiate reste :

1. terminer le backtester Phase 1
2. remplacer le détecteur sample par les vraies règles WinWorld
3. produire des résultats backtest exploitables
4. ensuite ajouter Journal Review et Regime Intelligence
