from fastapi import FastAPI

app = FastAPI(title="__SERVICE_NAME__")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "__SERVICE_NAME__", "team": "__TEAM__"}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "service": "__SERVICE_NAME__", "environment": "__ENVIRONMENT__"}
