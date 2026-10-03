# Customer demo

Record this on a laptop with no `gcloud` login and no kubeconfig in the frame. The point of the recording is the refusal, not a green cluster.

## Before you start

Say this, in this order:

1. Meridian's payments developer waits two to three days and files several tickets to get one service out.
2. The metric we agreed is local. In under two minutes she gets a repository, a Helm values file, and a policy result. She has never written a Helm chart.
3. We are not claiming production is now ten minutes. That has not been measured.

## What to run

```bash
./demo/run.sh
```

Leave the output on screen. Then show three files, slowly:

- `docs/customer-scenario.md` — the sentence that deleted the Apply button.
- `helm/service/values.yaml` — tag `0.1.0`, requests, and limits.
- `demo/failure/billing-callback-bad.yaml` — the manifest the rehearsal refuses.

If you also start the API, submit `prod` from the portal at `http://127.0.0.1:8000` and read the refusal out loud.

```bash
./scripts/dev-up.sh
```

## What not to do

- Do not run `kubectl apply` to make the ending look finished.
- Do not switch the Kyverno policy to Audit.
- Do not open a GCP console. GKE is a later target, documented as optional, and it is not this demo.
- Do not say the platform deploys production. It renders files. Argo CD is the writer, after a review.

## Optional second minute

If kind is installed and you have already run `scripts/kind-up.sh` and `scripts/install-argocd.sh`, show the Application manifest in `gitops/applications/billing-callback.yaml` and say that syncing it is the platform group's action, not the developer's.

If kind is not installed, stop. The laptop metric is already on screen.
