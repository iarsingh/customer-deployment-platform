#!/usr/bin/env bash
# Optional. Requires a current kubectl context from scripts/kind-up.sh.
set -euo pipefail
VERSION="${ARGOCD_VERSION:-v2.13.3}"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f "https://raw.githubusercontent.com/argoproj/argo-cd/${VERSION}/manifests/install.yaml"
echo "Argo CD ${VERSION} requested. Sync gitops/applications only after the install is ready."
