import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.database import init_db  # noqa: E402

init_db()
print("Database tables created.")
