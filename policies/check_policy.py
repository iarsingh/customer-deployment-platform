#!/usr/bin/env python3
"""Local stand-in for policies/kyverno. A cluster still enforces those files."""

import sys
from pathlib import Path

import yaml


def check_documents(documents: list) -> list[str]:
    failures = []
    for document in documents:
        if not isinstance(document, dict):
            continue
        kind = document.get("kind", "object")
        metadata = document.get("metadata") or {}
        name = metadata.get("name", "unnamed")
        if metadata.get("namespace") == "kube-system":
            failures.append(f"{kind} {name} must not target kube-system")
        if kind != "Deployment":
            continue
        containers = (
            document.get("spec", {})
            .get("template", {})
            .get("spec", {})
            .get("containers", [])
        )
        for container in containers:
            container_name = container.get("name", name)
            image = str(container.get("image", ""))
            if ":" not in image or image.endswith(":latest"):
                failures.append(f"{container_name} image tag latest is refused")
            resources = container.get("resources") or {}
            for section in ("requests", "limits"):
                values = resources.get(section) or {}
                for key in ("cpu", "memory"):
                    if not values.get(key):
                        failures.append(f"{container_name} missing {section}.{key}")
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_policy.py <manifest.yaml>", file=sys.stderr)
        return 2
    documents = list(yaml.safe_load_all(Path(argv[1]).read_text(encoding="utf-8")))
    failures = check_documents(documents)
    if not failures:
        print(f"policy passed: {argv[1]}")
        return 0
    for failure in failures:
        print(f"policy refused: {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
