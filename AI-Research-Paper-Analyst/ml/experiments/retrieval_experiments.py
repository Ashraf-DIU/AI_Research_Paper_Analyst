"""Usage (from repo root, after papers are ingested):
    python ml/experiments/retrieval_experiments.py <workspace_id> [eval.json]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))

from retrieval_evaluation import evaluate, generate_synthetic_questions, load_questions  # noqa: E402

from app.database import SessionLocal  # noqa: E402

if __name__ == "__main__":
    ws = sys.argv[1]
    db = SessionLocal()
    qs = load_questions(sys.argv[2]) if len(sys.argv) > 2 else generate_synthetic_questions(db, ws, 30)
    print(json.dumps(evaluate(db, ws, qs), indent=2))
