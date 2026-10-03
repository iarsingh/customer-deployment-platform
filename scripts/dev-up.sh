#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r platform-api/requirements.txt
export PYTHONPATH=platform-api
exec uvicorn app.main:app --app-dir platform-api --reload --host 127.0.0.1 --port 8000
