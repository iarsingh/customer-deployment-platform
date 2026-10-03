# Customer self-service deployment platform

Meridian Labs came with a queue, not a tool request.

> It takes our developers 2–3 days and multiple tickets to deploy a new microservice. We want developers to create a production-ready service without understanding Terraform, Kubernetes, or CI/CD.

This repository is that engagement. The metric agreed before the build is local: a payments developer who has never written a Helm chart gets a repository tree, a Helm render, and a policy result in under two minutes, and can point at the refusal for `prod` and for an image tagged `latest`.

## Before

```text
Developer
   ↓
DevOps ticket
   ↓
Infrastructure team
   ↓
Kubernetes team
   ↓
Security
   ↓
Deployment
```

## After

```text
Developer
   ↓
Self-service platform
   ├── Repository
   ├── CI pipeline
   ├── Infrastructure
   ├── Kubernetes
   ├── Security policies
   ├── GitOps
   └── Observability
```

The platform renders those boxes. It does not apply them. Argo CD is the only writer to a cluster. `environment=prod` is a pull request, not a successful API call.

Read [docs/customer-scenario.md](docs/customer-scenario.md) before the code. The constraint that deleted the "Apply" button is in that file.

## Local entrypoints

GCP is not required. `scripts/dev-up.sh` starts the API once it exists. `scripts/kind-up.sh` creates an optional kind or k3d cluster and is not part of the laptop metric.

## Layout

```text
docs/            customer scenario, requirements, architecture, runbook
platform-api/    FastAPI validation, store, and template renderer
portal/          one-page request form
templates/       the Python service Meridian actually gets
terraform/       local modules; GKE is documented and not required
helm/            chart with requests, limits, and HPA
kubernetes/      namespace
gitops/          Argo CD Application
policies/        Kyverno policies and the local checker
monitoring/      Prometheus scrape and a Grafana dashboard
demo/            the two-minute walk and the broken manifest
```
