import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ml" / "evaluation"))
from retrieval_evaluation import score_question  # noqa: E402

def test_metrics():
    results = [{"filename": "a.pdf", "page_start": 1, "page_end": 1},
               {"filename": "a.pdf", "page_start": 4, "page_end": 5}]
    m = score_question(results, [{"filename": "a.pdf", "page": 5}], ks=(1, 5))
    assert m["mrr"] == 0.5 and m["recall@1"] == 0.0 and m["recall@5"] == 1.0
