import os

os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
os.environ["WARMUP_EMBEDDINGS"] = "false"
os.environ["STORAGE_DIR"] = "./data/test_storage"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

def test_health_and_workspaces():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "healthy"
        assert len(c.get("/api/workspaces").json()) >= 1
        ws = c.post("/api/workspaces", json={"name": "t"}).json()
        assert c.get(f"/api/papers?workspace_id={ws['id']}").json() == []


def test_rejects_non_pdf():
    with TestClient(app) as c:
        ws = c.get("/api/workspaces").json()[0]["id"]
        r = c.post("/api/papers/upload", data={"workspace_id": ws}, files={"files": ("x.pdf", b"not a pdf")})
        assert r.status_code == 400
