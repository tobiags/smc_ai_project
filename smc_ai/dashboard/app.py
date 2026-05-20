from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from smc_ai.dashboard.views import router


def create_app() -> FastAPI:
    app = FastAPI(title="SMC AI Dashboard")
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.include_router(router)
    return app


app = create_app()
