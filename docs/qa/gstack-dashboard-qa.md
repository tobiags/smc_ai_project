# QA GSTACK du tableau de bord

GSTACK sert à vérifier le tableau de bord. Il ne fait pas partie du moteur de trading SMC.

## Flux QA local

1. Générer un résultat sample :

```powershell
rtk python -m smc_ai.main
```

2. Démarrer le tableau de bord :

```powershell
rtk uvicorn smc_ai.dashboard.app:app --reload
```

3. Inspecter ces pages avec Browser/GSTACK :

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/runs/{run_id}
```

## Vérifications visuelles

- L'en-tête et la navigation sont visibles.
- Le dernier backtest apparaît sur la page d'accueil.
- Les cartes KPI sont lisibles.
- La courbe d'equity Plotly s'affiche sur la page détail.
- Le tableau des trades ne déborde pas en largeur desktop.
- La page santé affiche le taux de réussite, le facteur de profit et le drawdown max.

## Vérifications canary futures sur VPS

Après déploiement, utiliser GSTACK pour vérifier :

- page d'accueil en HTTP 200
- aucune erreur console
- graphique visible
- page santé visible
- lien du dernier backtest fonctionnel

## Limite

GSTACK peut inspecter le tableau de bord et aider à détecter les régressions visuelles. Il ne doit
recevoir aucun identifiant broker et aucun accès direct à l'exécution MT5.
