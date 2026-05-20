# OpenStock Dashboard / Watchlist / Alertes

**Date :** 2026-05-20
**Décision :** accepté comme référence future

## Repository

`Open-Dev-Society/OpenStock`

## Rôle dans notre projet

OpenStock est ajouté comme référence pour :

- dashboard marché
- watchlist multi-actifs
- alertes personnalisées
- fiches actifs
- future expérience utilisateur partageable

## Ce qu'on peut récupérer comme idées

- structure de watchlist
- suivi visuel de plusieurs actifs
- alertes utilisateur
- pages détail par actif
- inspiration UX pour une interface plus riche que notre dashboard Phase 1
- séparation entre données marché, interface, alertes et persistance

## Adaptation au SMC AI Project

La watchlist future doit suivre nos actifs prioritaires :

- Forex : `EURUSD`, `GBPUSD`, `XAUUSD`, `USDJPY`, `AUDUSD`
- Crypto : `BTCUSDT`, `ETHUSDT`

Chaque actif pourra afficher :

- biais D1/H4
- zone POI active
- statut setup SMC
- signal M15 éventuel
- dernier résultat de backtest
- alertes ouvertes
- santé locale de la stratégie

## Limites

- Ne pas utiliser OpenStock comme moteur trading.
- Ne pas remplacer MT5/Binance par des providers stocks.
- Ne pas entrer en Phase 1.
- Attention à la licence AGPL-3.0 avant toute copie directe de code.

## Décision finale

OpenStock est une référence produit/UX pour les couches `dashboard`, `watchlist` et `alertes`.
Le cœur SMC, le backtester et les règles WinWorld restent indépendants.
