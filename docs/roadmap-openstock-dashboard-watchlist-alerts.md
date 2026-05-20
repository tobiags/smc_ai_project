# OpenStock — Référence Dashboard, Watchlist et Alertes

**Date :** 2026-05-20
**Statut :** accepté comme référence future
**Priorité actuelle :** ne remplace pas la Phase 1 SMC core + dashboard FastAPI/Jinja2/Plotly

Repository : `Open-Dev-Society/OpenStock`

## Décision

Ajouter OpenStock comme référence d'inspiration pour :

- dashboard marché
- watchlist multi-actifs
- alertes personnalisées
- fiches actifs
- future expérience utilisateur si le système devient partageable

OpenStock ne devient pas une dépendance du moteur SMC.

## Ce qui nous intéresse

### Dashboard marché

OpenStock est utile pour observer comment une application marché présente :

- prix en temps réel ou quasi temps réel
- vues par actif
- informations synthétiques
- navigation claire entre instruments
- interface moderne orientée utilisateur final

Pour notre projet, cela peut inspirer plus tard :

- une page "Marché"
- une page "Paire Forex"
- une page "Crypto"
- une page "Setup en attente"
- une page "Historique des alertes"

### Watchlist

La logique watchlist est intéressante pour suivre :

- `EURUSD`
- `GBPUSD`
- `XAUUSD`
- `USDJPY`
- `AUDUSD`
- `BTCUSDT`
- `ETHUSDT`

Chaque actif pourrait afficher :

- dernier prix connu
- timeframe principal suivi
- biais D1/H4
- setup SMC actif ou non
- distance à la zone POI
- dernier signal généré
- statut : `À surveiller`, `Setup proche`, `Signal valide`, `Rejeté`

### Alertes

OpenStock est aussi utile comme inspiration pour les alertes personnalisées.

Dans notre système, les alertes futures pourraient porter sur :

- arrivée du prix dans une zone OB/FVG
- sweep de liquidité
- confirmation M15
- RR minimum atteint
- confluence H4 présente
- setup rejeté avec raison
- drawdown ou santé stratégie dégradée

Les alertes ne doivent pas exécuter de trade toutes seules. Elles aident d'abord à la décision.

### Fiches actifs

OpenStock peut inspirer une fiche par actif avec :

- résumé du marché
- statut stratégie
- derniers signaux
- derniers backtests
- win rate local
- profit factor local
- drawdown local
- alertes ouvertes

## Limites

- OpenStock est orienté stocks, pas Forex/SMC.
- Le moteur de trading reste Python et indépendant.
- Les données Forex/MT5 ne doivent pas être remplacées par les providers stock d'OpenStock.
- La licence AGPL-3.0 impose de faire attention avant toute réutilisation directe de code.
- Utiliser comme référence produit/UX, pas comme dépendance Phase 1.

## Placement roadmap

```text
Phase 1
  Non : garder FastAPI/Jinja2/Plotly simple.

Phase 2
  Oui : inspiration watchlist et pages par actif.

Phase 3
  Oui : alertes de setup et aide à la décision live.

Phase 5
  Oui : inspiration produit si le système devient partageable.
```

## Décision finale

OpenStock est ajouté comme référence future `dashboard/watchlist/alertes`.

Il aide à penser l'expérience utilisateur, mais ne modifie pas le cœur SMC, le backtester, les
connecteurs MT5/Binance, ni les règles WinWorld.
