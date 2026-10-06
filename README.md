# Customer self-service deployment platform

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`platform-api/app/main.py`](platform-api/app/main.py) | HTTP handlers: `GET /healthz`, `GET /metrics`, `GET /`, `GET /services`, `GET /services/{request_id}` |
| [`templates/python-service/app/main.py`](templates/python-service/app/main.py) | HTTP handlers: `GET /healthz`, `GET /readyz` |
| [`platform-api/app/generate.py`](platform-api/app/generate.py) | Functions: `_fill`, `render_service` |
| [`policies/check_policy.py`](policies/check_policy.py) | Functions: `check_documents`, `main` |
| [`platform-api/app/validate.py`](platform-api/app/validate.py) | Functions: `_name_ok`, `refusals_for` |
| [`platform-api/app/store.py`](platform-api/app/store.py) | Functions: `__init__`, `_read`, `_write`, `find_by_key`, `get`, `list`, `add` |
| [`platform-api/requirements.txt`](platform-api/requirements.txt) | Implementation or supporting configuration |
| [`templates/python-service/requirements.txt`](templates/python-service/requirements.txt) | Implementation or supporting configuration |
| [`terraform/environments/local/main.tf`](terraform/environments/local/main.tf) | Terraform resource/module declarations |
| [`terraform/modules/service/main.tf`](terraform/modules/service/main.tf) | Terraform resource/module declarations |
| [`terraform/modules/service/outputs.tf`](terraform/modules/service/outputs.tf) | Terraform resource/module declarations |
| [`terraform/modules/service/variables.tf`](terraform/modules/service/variables.tf) | Terraform resource/module declarations |
| [`demo/run.sh`](demo/run.sh) | Implementation or supporting configuration |
| [`demo/run_demo.py`](demo/run_demo.py) | Functions: `main` |
| [`scripts/dev-up.sh`](scripts/dev-up.sh) | Implementation or supporting configuration |
| [`scripts/install-argocd.sh`](scripts/install-argocd.sh) | Implementation or supporting configuration |
| [`scripts/kind-up.sh`](scripts/kind-up.sh) | Implementation or supporting configuration |
| [`scripts/simulate-failure.sh`](scripts/simulate-failure.sh) | Implementation or supporting configuration |
| [`platform-api/app/__init__.py`](platform-api/app/__init__.py) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`platform-api/Dockerfile`](platform-api/Dockerfile) | Container build/service configuration |
| [`templates/python-service/Dockerfile`](templates/python-service/Dockerfile) | Container build/service configuration |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r platform-api/requirements.txt
PYTHONPATH=platform-api python -m pytest platform-api/tests -q
```

<!-- project-guide:end -->

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

## Run the laptop proof

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r platform-api/requirements.txt
PYTHONPATH=platform-api pytest platform-api/tests
./demo/run.sh
```

`./demo/run.sh` submits one dev service, renders the repository, refuses `prod`, and refuses the rehearsed bad manifest. The recording script is [demo/walkthrough.md](demo/walkthrough.md).

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

## Issues

Five milestones carry the 36 issues: Foundation, Platform API, Deployment Automation, Security and Observability, and Customer Demo. Each issue names the customer impact and the file that closed it.

https://github.com/iarsingh/customer-deployment-platform/issues

## Trade-off to say out loud

A self-service button that runs Terraform would have been shorter to demo and worse for Meridian. Their incident was a laptop apply. The API stops at files. That is the constraint, not a missing feature.

## Documentation checks

Project architecture, interview guides, and local source links are checked automatically on pushes and pull requests. Run the same check locally:

```bash
python3 .github/scripts/validate_project_docs.py
```
