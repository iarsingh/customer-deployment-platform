#!/usr/bin/env bash
# Optional. The laptop demo does not need a cluster.
# kind is preferred. k3d is accepted when kind is absent.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER_NAME="${CLUSTER_NAME:-meridian}"

if command -v kind >/dev/null 2>&1; then
  if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
    kind create cluster --name "$CLUSTER_NAME"
  fi
  kubectl cluster-info --context "kind-${CLUSTER_NAME}"
  echo "Cluster ${CLUSTER_NAME} is up. Install Argo CD only when you are ready to sync gitops/."
  exit 0
fi

if command -v k3d >/dev/null 2>&1; then
  if ! k3d cluster list -o json | grep -q "\"name\":\"${CLUSTER_NAME}\""; then
    k3d cluster create "$CLUSTER_NAME" --agents 1
  fi
  kubectl cluster-info
  exit 0
fi

echo "Neither kind nor k3d is installed. The API demo still runs with ./demo/run.sh." >&2
exit 1
