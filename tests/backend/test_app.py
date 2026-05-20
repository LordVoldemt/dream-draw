from fastapi.testclient import TestClient

from app.main import create_app


def test_healthcheck_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_all_core_modules_are_registered() -> None:
    client = TestClient(create_app())

    module_paths = [
        "/api/auth/_module",
        "/api/user/_module",
        "/api/points/_module",
        "/api/generate/_module",
        "/api/works/_module",
        "/api/pay/_module",
        "/api/admin/_module",
        "/api/admin/model-providers/_module",
        "/api/admin/model-monitoring/_module",
    ]

    for path in module_paths:
        response = client.get(path)
        assert response.status_code == 200
