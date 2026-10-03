# Requirements

Source: the Meridian Labs walk in [customer-scenario.md](customer-scenario.md). If a requirement does not change that walk, it is not in this release.

## Functional

1. A developer submits a service name, team, runtime, and environment.
2. The platform rejects an invalid name, an unknown runtime, a missing team, and `environment=prod`.
3. An accepted request is stored with the decision. The store does not keep cloud credentials, because the API never asks for them.
4. The platform renders a Python service repository from `templates/python-service`.
5. The render includes a Dockerfile, a Helm values overlay, and an Argo CD Application.
6. A local policy check fails the render when the image uses the tag `latest` or the pod has no CPU and memory limits.
7. `GET /services` returns prior decisions so a second developer can see why a name was refused.
8. The same request id submitted twice does not create a second service.

## Non-functional

| Requirement | Target | How it is judged |
| --- | --- | --- |
| No cloud account required for the demo | Docker Compose, or plain Python | `./demo/run.sh` never calls `gcloud` |
| Developer laptop has no cluster credential | API process has no kubeconfig mount | Compose file does not mount `~/.kube` |
| Validation stays local and fast | Under 300ms for a reject path on a laptop | Test covers the reject path; the demo prints the decision |
| Production change is reviewable | GitOps pull request, not an API call | `prod` returns HTTP 422 |
| Rollback is not a migration | Delete the Application manifest | Documented in the runbook; the API has no delete-namespace action |
| Audit | Request id, team, name, environment, decision | Response body and the JSON store |
| One template first | `runtime=python` only | Any other runtime returns HTTP 422 |

## Explicitly not in this release

- A GCP project, a GKE cluster, or a required `google` provider.
- A portal login. The local demo trusts the laptop.
- Java, Go, or Node templates.
- Automatic production promotion.
- Paging, on-call routing, or a cost estimate.

GKE is an optional later target. The local modules must still validate when that target is absent.
