"""Optional FastAPI transport for the CryptoPulse AI dashboard service."""

from __future__ import annotations

import argparse
from pathlib import Path

from .service import DashboardService


def create_app(project_root: Path | None = None, database_path: Path | None = None):
    try:
        from fastapi import FastAPI, HTTPException, Query
    except ImportError as error:
        raise RuntimeError(
            "API dependencies are not installed. Run: python -m pip install -e .[api]"
        ) from error
    root = (project_root or Path.cwd()).resolve()
    service = DashboardService(root, database_path or root / "var" / "cryptopulse.db")
    app = FastAPI(
        title="CryptoPulse AI API",
        version="1.0.0",
        description="Read-only explainable crypto market-intelligence API",
    )

    @app.get("/health")
    def health():
        return service.health()

    @app.get("/ready")
    def ready():
        return service.readiness()

    @app.get("/api/v1/indices")
    def indices(asset: str | None = None, resolution: str | None = None):
        try:
            return service.indices(asset, resolution)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/events")
    def events(asset: str | None = None):
        try:
            return service.events(asset)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/research-summary")
    def research_summary():
        return service.research_summary()

    @app.get("/api/v1/runs")
    def recent_runs(limit: int = Query(default=10, ge=1, le=100)):
        return service.recent_runs(limit)

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the CryptoPulse AI development API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        import uvicorn
    except ImportError as error:
        raise RuntimeError(
            "API dependencies are not installed. Run: python -m pip install -e .[api]"
        ) from error
    uvicorn.run("cryptopulse.api:create_app", host=args.host, port=args.port, factory=True)


if __name__ == "__main__":
    main()
