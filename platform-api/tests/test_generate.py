from app import generate


def test_render_excludes_local_cache_artifacts(tmp_path, monkeypatch):
    template = tmp_path / "template"
    (template / "__pycache__").mkdir(parents=True)
    (template / "__pycache__/module.pyc").write_bytes(b"\xff\x00cached")
    (template / "app.py").write_text("name = '__SERVICE_NAME__'\n")
    (tmp_path / "outside.txt").write_text("external file")
    (template / "outside.py").symlink_to(tmp_path / "outside.txt")
    (template / ".env").write_text("LOCAL_SETTING=private-fixture")
    monkeypatch.setattr(generate, "TEMPLATE_ROOT", template)
    output = generate.render_service({"id": "svc-test", "name": "demo", "team": "team", "environment": "dev", "port": 8080}, tmp_path)
    repository = tmp_path / output["repository"]
    assert (repository / "app.py").read_text() == "name = 'demo'\n"
    assert not (repository / "__pycache__").exists()
    assert not (repository / "outside.py").exists()
    assert not (repository / ".env").exists()
