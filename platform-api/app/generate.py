import shutil
from pathlib import Path

IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".venv", "venv", ".git", "node_modules"}

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "python-service"


def _fill(text: str, row: dict) -> str:
    return (
        text.replace("__SERVICE_NAME__", row["name"])
        .replace("__TEAM__", row["team"])
        .replace("__ENVIRONMENT__", row["environment"])
        .replace("__PORT__", str(row["port"]))
    )


def render_service(row: dict, data_dir: Path) -> dict[str, str]:
    destination = Path(data_dir) / "renders" / row["id"] / row["name"]
    if destination.exists():
        shutil.rmtree(destination)
    for source in TEMPLATE_ROOT.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(TEMPLATE_ROOT)
        if any(part in IGNORED_PARTS for part in relative.parts) or source.suffix in {".pyc", ".pyo"}:
            continue
        if source.name == ".env" or (source.name.startswith(".env.") and source.name != ".env.example"):
            continue
        if source.is_symlink():
            continue
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
                "replicaCount: 2",
                "image:",
                f"  repository: {row['name']}",
                '  tag: "0.1.0"',
                "service:",
                f"  port: {row['port']}",
                "resources:",
                "  requests:",
                "    cpu: 100m",
                "    memory: 128Mi",
                "  limits:",
                "    cpu: 500m",
                "    memory: 256Mi",
                "autoscaling:",
                "  enabled: true",
                "  minReplicas: 2",
                "  maxReplicas: 5",
                "  targetCPUUtilizationPercentage: 70",
                "",
            ]
        ),
        encoding="utf-8",
    )
    application_path = destination.parent / "application.yaml"
    namespace = f"{row['team']}-{row['environment']}"
    application_path.write_text(
        "\n".join(
            [
                "apiVersion: argoproj.io/v1alpha1",
                "kind: Application",
                "metadata:",
                f"  name: {row['name']}",
                "  namespace: argocd",
                "spec:",
                "  project: default",
                "  source:",
                "    repoURL: https://github.com/iarsingh/customer-deployment-platform",
                "    targetRevision: main",
                "    path: helm/service",
                "  destination:",
                "    server: https://kubernetes.default.svc",
                f"    namespace: {namespace}",
                "  syncPolicy:",
                "    automated:",
                "      prune: true",
                "      selfHeal: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    base = Path(data_dir) / "renders" / row["id"]
    return {
        "repository": str(destination.relative_to(data_dir)),
        "helm_values": str(values_path.relative_to(data_dir)),
        "gitops_application": str(application_path.relative_to(data_dir)),
        "root": str(base.relative_to(data_dir)),
    }
