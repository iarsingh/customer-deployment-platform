#!/usr/bin/env bash
# Rehearse the deployment Meridian must not ship.
set -euo pipefail
cd "$(dirname "$0")/.."
python policies/check_policy.py demo/failure/billing-callback-bad.yaml
