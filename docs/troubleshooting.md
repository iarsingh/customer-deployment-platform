# Troubleshooting

Use this when a Meridian developer says the service "did not deploy." Start with the decision, not with the cluster.

## 1. Read the API decision

```bash
curl -s http://127.0.0.1:8000/services
```

If `status` is `refused` and a reason mentions `prod`, the platform did what it was built to do. Production is a pull request on `gitops/`. Do not work around it with a kubeconfig.

If there is no row, the request never reached the API. Check `GET /healthz` before debugging Argo CD.

## 2. A manifest that policy will reject

`demo/failure/billing-callback-bad.yaml` is the incident we rehearse: image tag `latest`, no CPU or memory. The local checker and the Kyverno policies in `policies/kyverno` both exist to stop it.

```bash
python policies/check_policy.py demo/failure/billing-callback-bad.yaml
```

The command exits 1 and names the missing fields. That is the successful outcome of the rehearsal. Fix the manifest, or re-render from `POST /services`, which writes tag `0.1.0` and the default requests and limits.

On a cluster, the same rules are `policies/kyverno/disallow-latest-tag.yaml` and `policies/kyverno/require-cpu-memory.yaml`. A pod that violates them stays out. Do not set the policy to `Audit` to make a demo green.

## 3. GitOps is the writer

The API never applies a manifest. If the files exist and the pod does not, look at Argo CD, not at a laptop `kubectl apply`.

- Application missing: the rendered `application.yaml` was not merged.
- Application out of sync: the Git revision and the cluster differ. Sync from the Application.
- Application healthy but the pod is pending: describe the pod. A missing limit that slipped past a local skip will show as a Kyverno event.

## 4. Rollback

Rollback is reverting the Git commit that added the Application, then letting Argo CD prune. It is not a Terraform destroy from a developer laptop, and the API has no delete-cluster action.

## 5. What healthy looks like

The rendered service answers `/healthz` and `/readyz`. The platform API exposes `/metrics` with `meridian_service_requests_total`. Grafana, when Compose is up, reads that series from Prometheus at `http://prometheus:9090`.
