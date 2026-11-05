"""Optional single-host deployment: FastAPI serving the built React SPA."""

from fastapi.testclient import TestClient

from backend.core.config import Settings
from backend.core.container import build_resources
from backend.main import create_app


def _app_with_dist(tmp_path, fake_llm):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<html><body><div id='root'>spa</div></body></html>")
    (assets / "app.js").write_text("console.log('app')")

    settings = Settings(
        OPENROUTER_API_KEY="test-key", ENVIRONMENT="test", LOG_LEVEL="WARNING",
        DATABASE_PATH=str(tmp_path / "spa.sqlite3"),
        FRONTEND_DIST_DIR=str(dist), _env_file=None,
    )
    resources = build_resources(settings=settings, llm_client=fake_llm)
    app = create_app(settings=settings, resources=resources)
    return TestClient(app)


def test_spa_index_and_assets_are_served(tmp_path, fake_llm):
    with _app_with_dist(tmp_path, fake_llm) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "spa" in root.text
        assert "text/html" in root.headers["content-type"]

        asset = client.get("/assets/app.js")
        assert asset.status_code == 200
        assert "console.log" in asset.text


def test_spa_fallback_serves_index_for_client_routes(tmp_path, fake_llm):
    with _app_with_dist(tmp_path, fake_llm) as client:
        response = client.get("/reports/some-session-id")
        assert response.status_code == 200
        assert "spa" in response.text


def test_root_static_files_are_served_and_traversal_is_blocked(tmp_path, fake_llm):
    dist = tmp_path / "dist"
    with _app_with_dist(tmp_path, fake_llm) as client:
        # A real root-level file (e.g. favicon) is served rather than index.html.
        (dist / "favicon.svg").write_text("<svg></svg>")
        favicon = client.get("/favicon.svg")
        assert favicon.status_code == 200
        assert "svg" in favicon.text

        # Path traversal must never escape the build directory -> SPA/404 only.
        traversal = client.get("/../etc/passwd")
        assert traversal.status_code in (200, 404)
        assert "root:" not in traversal.text


def test_api_routes_take_precedence_over_spa(tmp_path, fake_llm):
    with _app_with_dist(tmp_path, fake_llm) as client:
        assert client.get("/api/health").json() == {"status": "healthy"}

        # Unknown API routes must 404 as JSON, never return the SPA document.
        missing = client.get("/api/does-not-exist")
        assert missing.status_code == 404
        assert "spa" not in missing.text


def test_app_without_dist_keeps_json_root(tmp_path, fake_llm):
    settings = Settings(
        OPENROUTER_API_KEY="test-key", ENVIRONMENT="test", LOG_LEVEL="WARNING",
        DATABASE_PATH=str(tmp_path / "nodist.sqlite3"),
        FRONTEND_DIST_DIR=str(tmp_path / "missing-dist"), _env_file=None,
    )
    resources = build_resources(settings=settings, llm_client=fake_llm)
    app = create_app(settings=settings, resources=resources)
    with TestClient(app) as client:
        body = client.get("/").json()
        assert body["status"] == "running"
