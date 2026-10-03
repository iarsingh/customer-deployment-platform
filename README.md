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

## Run the API

GCP is not required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r platform-api/requirements.txt
PYTHONPATH=platform-api pytest platform-api/tests
./scripts/dev-up.sh
```

`POST /services` accepts `dev` and `staging` for `runtime=python`. `prod` is stored and returned as HTTP 422. The same `idempotency_key` returns the original decision.

`scripts/kind-up.sh` creates an optional kind or k3d cluster and is not part of the laptop metric. `scripts/install-argocd.sh` installs a pinned Argo CD into that cluster.

An accepted request renders a repository, Helm values, and an Argo CD Application under the data directory. Check the local infrastructure without a cloud login:

```bash
terraform fmt -check -recursive terraform
terraform -chdir=terraform/environments/local init -backend=false
terraform -chdir=terraform/environments/local validate
helm template billing-callback helm/service -f helm/service/values.yaml
python policies/check_policy.py demo/failure/billing-callback-bad.yaml
```

The last command is supposed to fail. That manifest uses the tag `latest` and sets no limits. The runbook is [docs/troubleshooting.md](docs/troubleshooting.md).

Prometheus and Grafana come up with the API:

```bash
docker compose up --build
```

Grafana is on port 3000 and already has the Meridian dashboard. The API metric is `meridian_service_requests_total`.

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
