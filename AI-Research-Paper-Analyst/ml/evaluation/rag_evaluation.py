"""Citation-quality metrics for RAG answers (needs an annotated set with expected pages)."""


def citation_metrics(answer_result: dict, relevant: list[dict]) -> dict:
    cites = answer_result.get("citations", [])
    def ok(c):
        return any(c["filename"] == r["filename"] and c["page_start"] <= r["page"] <= c["page_end"] for r in relevant)
    good = sum(1 for c in cites if ok(c))
    return {
        "citation_precision": good / len(cites) if cites else 0.0,
        "page_accuracy": float(any(ok(c) for c in cites)),
        "has_citation": float(bool(cites)),
        "abstained": float("do not contain enough evidence" in answer_result.get("answer", "").lower()),
    }


def aggregate(rows: list[dict]) -> dict:
    keys = rows[0].keys() if rows else []
    return {k: round(sum(r[k] for r in rows) / len(rows), 4) for k in keys}
