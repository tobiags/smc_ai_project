# Direction de déploiement VPS

Le premier déploiement VPS héberge uniquement le tableau de bord FastAPI et les fichiers exportés
dans `results/`.

## Forme initiale

```text
VPS
|-- smc_ai_project/
|-- .venv/
|-- results/
`-- systemd, Coolify, ou autre gestionnaire de process lançant uvicorn/gunicorn
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Commande de lancement

```powershell
uvicorn smc_ai.dashboard.app:app --host 0.0.0.0 --port 8000
```

## Reverse proxy

Utiliser Coolify, Caddy ou Nginx pour router le trafic HTTPS vers le port `8000`.

## Synchronisation des résultats

L'accès aux données MT5 reste local sur Windows au début. Le tableau de bord VPS consomme les
résultats JSON exportés. Plus tard, un job de synchronisation pourra envoyer `results/*.json`
depuis la machine Windows vers le VPS.

## Limite importante

Le tableau de bord VPS est en lecture seule dans le premier déploiement. Il ne doit pas :

- envoyer des ordres MT5
- stocker des mots de passe broker
- modifier les paramètres de stratégie sans validation humaine
- lancer une exécution live autonome
