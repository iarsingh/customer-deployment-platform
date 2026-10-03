#!/usr/bin/env python3
"""Laptop proof for the Meridian metric. No cluster and no cloud login."""

import shutil
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from policies.check_policy import check_documents
import yaml


def main() -> int:
    started = time.monotonic()
    data_dir = Path(tempfile.mkdtemp(prefix="meridian-demo-"))
    root = Path(__file__).resolve().parents[1]
    client = TestClient(create_app(data_dir=data_dir, portal_dir=root / "portal"))
    try:
        accepted = client.post(
            "/services",
            json={
                "name": "billing-callback",
                "team": "payments",
                "runtime": "python",
                "environment": "dev",
                "idempotency_key": "demo-accept",
            },
        )
        refused = client.post(
            "/services",
            json={
                "name": "billing-callback",
                "team": "payments",
                "runtime": "python",
                "environment": "prod",
                "idempotency_key": "demo-prod",
            },
        )
        if accepted.status_code != 200:
            print(accepted.text)
            return 1
        body = accepted.json()
        source = (data_dir / body["artifacts"]["repository"] / "app" / "main.py").read_text()
        bad = list(yaml.safe_load_all((root / "demo" / "failure" / "billing-callback-bad.yaml").read_text()))
        failures = check_documents(bad)
        elapsed = time.monotonic() - started
        print(f"accepted {body['id']} in {elapsed:.2f}s")
        print(f"repository {body['artifacts']['repository']}")
        print(f"helm values {body['artifacts']['helm_values']}")
        print(f"gitops {body['artifacts']['gitops_application']}")
        print("rendered service name is present:" , "billing-callback" in source)
        print(f"prod status {refused.status_code}")
        for reason in refused.json()["detail"]["refusals"]:
            print(f"prod refusal: {reason}")
        print(f"bad manifest refusals: {len(failures)}")
        for failure in failures:
            print(f"policy refusal: {failure}")
        if "billing-callback" not in source or refused.status_code != 422 or not failures:
            return 1
        if elapsed > 120:
            print("over the two minute laptop target")
            return 1
        print("laptop metric met: request, render, prod refusal, policy refusal")
        return 0
    finally:
        shutil.rmtree(data_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
