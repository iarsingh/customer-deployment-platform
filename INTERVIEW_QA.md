# customer-deployment-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does customer-deployment-platform address, and what can you demonstrate?

Meridian Labs came with a queue, not a tool request.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`platform-api/app/main.py`](platform-api/app/main.py): Implementation or supporting configuration.
- [`templates/python-service/app/main.py`](templates/python-service/app/main.py): Implementation or supporting configuration.
- [`platform-api/app/generate.py`](platform-api/app/generate.py): Implementation or supporting configuration.
- [`policies/check_policy.py`](policies/check_policy.py): Implementation or supporting configuration.
- [`platform-api/app/validate.py`](platform-api/app/validate.py): Implementation or supporting configuration.
- [`platform-api/app/store.py`](platform-api/app/store.py): Implementation or supporting configuration.
- [`platform-api/requirements.txt`](platform-api/requirements.txt): Implementation or supporting configuration.
- [`templates/python-service/requirements.txt`](templates/python-service/requirements.txt): Implementation or supporting configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `render_service` and explain the decision it makes?

The main walkthrough here is `render_service(row: dict, data_dir: Path)` in [`platform-api/app/generate.py`](platform-api/app/generate.py#L16).

```python
def render_service(row: dict, data_dir: Path) -> dict[str, str]:
    destination = Path(data_dir) / "renders" / row["id"] / row["name"]
    if destination.exists():
        shutil.rmtree(destination)
    for source in TEMPLATE_ROOT.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(TEMPLATE_ROOT)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_fill(source.read_text(encoding="utf-8"), row), encoding="utf-8")

    values_path = destination.parent / f"{row['name']}-values.yaml"
    values_path.write_text(
        "\n".join(
            [
                f"name: {row['name']}",
                f"team: {row['team']}",
                f"environment: {row['environment']}",
                f"namespace: {row['team']}-{row['environment']}",
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `'\n'.join`, `Path`, `TEMPLATE_ROOT.rglob`, `_fill`, `application_path.relative_to`, `application_path.write_text`, `base.relative_to`, `destination.exists`, `destination.relative_to`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `create_app` have?

`create_app(data_dir: Path | None=None, portal_dir: Path | None=None)` is defined in [`platform-api/app/main.py`](platform-api/app/main.py#L22).

Its return expressions include:

- `app`
- `{'status': 'ok'}`
- `PlainTextResponse(body)`

It uses `'\n'.join`, `FastAPI`, `FileResponse`, `HTTPException`, `Path`, `Path(__file__).resolve`, `PlainTextResponse`, `Store`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `SystemExit(main())` in [`demo/run_demo.py`](demo/run_demo.py#L73).
- `SystemExit(main(sys.argv))` in [`policies/check_policy.py`](policies/check_policy.py#L57).
- `HTTPException(status_code=404, detail='unknown request')` in [`platform-api/app/main.py`](platform-api/app/main.py#L63).
- `HTTPException(status_code=422, detail=row)` in [`platform-api/app/main.py`](platform-api/app/main.py#L88).
- `KeyError(request_id)` in [`platform-api/app/store.py`](platform-api/app/store.py#L50).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`platform-api/tests/test_api.py`](platform-api/tests/test_api.py#L10) contains `test_accepts_a_dev_python_service`:

```python
def test_accepts_a_dev_python_service(tmp_path):
    client = client_for(tmp_path)
    response = client.post(
        "/services",
        json={
            "name": "billing-callback",
            "team": "payments",
            "runtime": "python",
            "environment": "dev",
            "idempotency_key": "evt-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["refusals"] == []
    assert body["id"].startswith("svc-")
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`platform-api/app/main.py`](platform-api/app/main.py#L29).
- `GET /metrics` → `metrics` in [`platform-api/app/main.py`](platform-api/app/main.py#L33).
- `GET /` → `portal` in [`platform-api/app/main.py`](platform-api/app/main.py#L49).
- `GET /services` → `list_services` in [`platform-api/app/main.py`](platform-api/app/main.py#L56).
- `GET /services/{request_id}` → `get_service` in [`platform-api/app/main.py`](platform-api/app/main.py#L60).
- `POST /services` → `create_service` in [`platform-api/app/main.py`](platform-api/app/main.py#L67).
- `GET /healthz` → `healthz` in [`templates/python-service/app/main.py`](templates/python-service/app/main.py#L7).
- `GET /readyz` → `readyz` in [`templates/python-service/app/main.py`](templates/python-service/app/main.py#L12).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `ALLOWED_RUNTIMES`, `SELF_SERVE_ENVIRONMENTS` in [`platform-api/app/validate.py`](platform-api/app/validate.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r platform-api/requirements.txt
PYTHONPATH=platform-api python -m pytest platform-api/tests -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml), [`.github/workflows/scan.yml`](.github/workflows/scan.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `render_service`?

In [`platform-api/app/generate.py`](platform-api/app/generate.py#L16), `render_service(row: dict, data_dir: Path)` receives the inputs. The function computes these intermediate values:

- `destination = Path(data_dir) / 'renders' / row['id'] / row['name']`
- `values_path = destination.parent / f"{row['name']}-values.yaml"`
- `application_path = destination.parent / 'application.yaml'`
- `namespace = f"{row['team']}-{row['environment']}"`
- `base = Path(data_dir) / 'renders' / row['id']`

Its result is defined by:

- `{'repository': str(destination.relative_to(data_dir)), 'helm_values': str(values_path.relative_to(data_dir)), 'gitops_application': str(application_path.relative_to(data_dir)), 'root': str(base.relative_to(data_dir))}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`platform-api/app/generate.py`](platform-api/app/generate.py#L16) branches on:

- `destination.exists()`
- `not source.is_file()`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. Which Terraform modules compose the environment?

- `module.billing_callback` uses `../../modules/service` in [`terraform/environments/local/main.tf`](terraform/environments/local/main.tf).

Review each module’s variable and output contracts. Different environment declarations may reuse a module with different inputs; state and provider configuration determine the actual deployment boundary.
