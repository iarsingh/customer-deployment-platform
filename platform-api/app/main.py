import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.generate import render_service
from app.store import Store
from app.validate import refusals_for


class ServiceRequest(BaseModel):
    name: str
    team: str
    runtime: str = "python"
    environment: str = "dev"
    port: int = 8080
    idempotency_key: str = Field(default="", max_length=80)


def create_app(data_dir: Path | None = None, portal_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="Meridian service platform", version="0.1.0")
    root = Path(__file__).resolve().parents[2]
    app.state.store = Store(data_dir or Path(os.environ.get("PLATFORM_DATA_DIR", root / "generated")))
    app.state.portal = portal_dir or Path(os.environ.get("PLATFORM_PORTAL", root / "portal"))

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/")
    def portal():
        page = app.state.portal / "index.html"
        if not page.exists():
            return {"service": "meridian-platform", "portal": "missing"}
        return FileResponse(page)

    @app.get("/services")
    def list_services():
        return {"services": app.state.store.list()}

    @app.get("/services/{request_id}")
    def get_service(request_id: str):
        row = app.state.store.get(request_id)
        if row is None:
            raise HTTPException(status_code=404, detail="unknown request")
        return row

    @app.post("/services")
    def create_service(body: ServiceRequest):
        existing = app.state.store.find_by_key(body.idempotency_key)
        if existing is not None:
            return existing

        payload = body.model_dump()
        reasons = refusals_for(payload)
        row = app.state.store.add(
            {
                "name": payload["name"].strip(),
                "team": payload["team"].strip(),
                "runtime": payload["runtime"].strip().lower(),
                "environment": payload["environment"].strip().lower(),
                "port": payload["port"],
                "idempotency_key": payload["idempotency_key"],
                "status": "refused" if reasons else "accepted",
                "refusals": reasons,
                "artifacts": {},
            }
        )
        if reasons:
            raise HTTPException(status_code=422, detail=row)
        artifacts = render_service(row, app.state.store.path.parent)
        return app.state.store.update(row["id"], {"artifacts": artifacts})

    return app


app = create_app()
