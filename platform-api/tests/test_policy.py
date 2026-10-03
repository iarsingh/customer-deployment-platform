from policies.check_policy import check_documents


def _deployment(image: str, resources: dict | None, namespace: str = "payments-dev") -> dict:
    container = {"name": "billing-callback", "image": image}
    if resources is not None:
        container["resources"] = resources
    return {
        "kind": "Deployment",
        "metadata": {"name": "billing-callback", "namespace": namespace},
        "spec": {"template": {"spec": {"containers": [container]}}},
    }


GOOD_RESOURCES = {
    "requests": {"cpu": "100m", "memory": "128Mi"},
    "limits": {"cpu": "500m", "memory": "256Mi"},
}


def test_limited_image_passes():
    assert check_documents([_deployment("billing-callback:0.1.0", GOOD_RESOURCES)]) == []


def test_latest_without_limits_is_refused():
    failures = check_documents([_deployment("billing-callback:latest", None)])
    assert any("latest" in failure for failure in failures)
    assert any("requests.cpu" in failure for failure in failures)
    assert any("limits.memory" in failure for failure in failures)


def test_kube_system_is_refused():
    failures = check_documents(
        [_deployment("billing-callback:0.1.0", GOOD_RESOURCES, namespace="kube-system")]
    )
    assert any("kube-system" in failure for failure in failures)
