# Projet SMC AI

Backtester Advanced SMC personnel et tableau de bord de suivi.

## Première installation locale

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Premier lancement du tableau de bord

Génère d'abord un résultat de backtest sample déterministe :

```powershell
python -m smc_ai.main
```

Puis démarre le tableau de bord :

```powershell
uvicorn smc_ai.dashboard.app:app --reload
```

Ouvre :

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
```

## Architecture

Le moteur SMC est indépendant du tableau de bord. Le tableau de bord lit les résultats JSON
depuis `results/`.

Flux actuellement implémenté :

```text
OHLCV sample -> signaux sample -> backtest sample -> résultat JSON -> tableau de bord FastAPI
```

Le détecteur de signaux est volontairement simple pour l'instant. Il sert de socle stable pour
la boucle dashboard, export et backtest avant l'implémentation complète du moteur WinWorld SMC.

## Notes QA et VPS

- Checklist QA du tableau de bord : `docs/qa/gstack-dashboard-qa.md`
- Direction de déploiement VPS : `docs/vps/deployment.md`

## Mémoire projet

La mémoire durable de stratégie et d'architecture vit dans `brain/`. Elle est en markdown simple
aujourd'hui et pourra être indexée plus tard par GBrain. Ne stocke jamais d'identifiants broker
ou de secrets dans ce dossier.
