"""Retrieval metrics at page level: Recall@k, MRR, nDCG@k, plus a synthetic-question bootstrap.

Eval file format (JSON list):
[{"question": "...", "relevant": [{"filename": "paper.pdf", "page": 5}]}]
"""
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

CONFIGS = {
    "dense (BGE+FAISS)": dict(mode="dense", rerank=False),
    "bm25": dict(mode="bm25", rerank=False),
    "hybrid (RRF)": dict(mode="hybrid", rerank=False),
    "hybrid + rerank": dict(mode="hybrid", rerank=True),
}


def _hits(results, relevant):
    """For each ranked result: set of relevant item indices it covers."""
    out = []
    for r in results:
        out.append({i for i, rel in enumerate(relevant)
                    if r["filename"] == rel["filename"] and r["page_start"] <= rel["page"] <= r["page_end"]})
    return out


def score_question(results, relevant, ks=(5, 10)):
    hits = _hits(results, relevant)
    m = {}
    first = next((i for i, h in enumerate(hits) if h), None)
    m["mrr"] = 1.0 / (first + 1) if first is not None else 0.0
    for k in ks:
        covered = set().union(*hits[:k]) if hits[:k] else set()
        m[f"recall@{k}"] = len(covered) / max(1, len(relevant))
        dcg = sum((1.0 if h else 0.0) / math.log2(i + 2) for i, h in enumerate(hits[:k]))
        ideal = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant), k)))
        m[f"ndcg@{k}"] = dcg / ideal if ideal else 0.0
    return m


def evaluate(db, workspace_id, questions, ks=(5, 10), configs=CONFIGS):
    from app.services.retrieval_service import retrieve

    table = {}
    for name, cfg in configs.items():
        agg = {}
        for q in questions:
            res = retrieve(db, workspace_id, q["question"], k=max(ks), **cfg)
            for key, val in score_question(res, q["relevant"], ks).items():
                agg[key] = agg.get(key, 0.0) + val
        table[name] = {k: round(v / max(1, len(questions)), 4) for k, v in agg.items()}
    return table


def generate_synthetic_questions(db, workspace_id, n=30, seed=0):
    """Bootstrap an eval set: ask the LLM to write a question answerable by one chunk.
    Labels are noisy; use for quick comparisons, then replace with manual annotation."""
    from app.models.paper import Chunk, Paper
    from app.services.llm_service import complete

    rows = (db.query(Chunk, Paper).join(Paper, Paper.id == Chunk.paper_id)
            .filter(Chunk.workspace_id == workspace_id).all())
    rows = [r for r in rows if len(r[0].text) > 600 and r[0].section not in ("Preamble",)]
    random.Random(seed).shuffle(rows)
    out = []
    for c, p in rows[:n]:
        q = complete("Write ONE specific question that this passage answers. Do not copy phrases verbatim. "
                     "Output only the question.", c.text[:1800], temperature=0.3)
        out.append({"question": q.strip(), "relevant": [{"filename": p.filename, "page": c.page_start}]})
    return out


def load_questions(path):
    return json.loads(Path(path).read_text())
