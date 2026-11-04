from app.utils.citation_utils import build_context, validate_citations

def _chunk(i, page):
    return {"chunk_id": i, "paper_id": f"p{i}", "paper_title": f"Paper {i}", "filename": f"{i}.pdf",
            "page_start": page, "page_end": page, "section": "Results", "text": "x" * 50}


def test_invalid_citations_are_removed():
    _, sources = build_context([_chunk(1, 4), _chunk(2, 7)])
    clean, cites = validate_citations("A is true [S1]. B is true [S9]. C [S1, S2, S7].", sources)
    assert "S9" not in clean and "S7" not in clean
    assert [c["label"] for c in cites] == ["S1", "S2"]
