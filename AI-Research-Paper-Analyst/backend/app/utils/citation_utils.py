"""Citation validation: only citations that point to real retrieved sources survive."""
import re

TAG_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")


def build_context(chunks: list[dict], max_chars: int | None = None) -> tuple[str, dict[str, dict]]:
    sources: dict[str, dict] = {}
    blocks = []
    for i, c in enumerate(chunks, start=1):
        label = f"S{i}"
        sources[label] = c
        pages = f"{c['page_start']}" if c["page_start"] == c["page_end"] else f"{c['page_start']}-{c['page_end']}"
        text = c["text"] if not max_chars else c["text"][:max_chars]
        blocks.append(f"[{label}] Paper: {c['paper_title']} | Pages: {pages} | Section: {c['section']}\n{text}")
    return "\n\n".join(blocks), sources


def validate_citations(answer: str, sources: dict[str, dict]):
    """Strip invalid [S#] tags; return (clean_answer, ordered citation dicts)."""
    used: list[str] = []

    def repl(m: re.Match) -> str:
        labels = [x.strip() for x in m.group(1).split(",")]
        good = [x for x in labels if x in sources]
        for g in good:
            if g not in used:
                used.append(g)
        return f"[{', '.join(good)}]" if good else ""

    clean = TAG_RE.sub(repl, answer)
    clean = re.sub(r"[ \t]{2,}", " ", clean)
    citations = []
    for label in used:
        c = sources[label]
        citations.append(
            {
                "label": label,
                "chunk_id": c["chunk_id"],
                "paper_id": c["paper_id"],
                "paper_title": c["paper_title"],
                "filename": c["filename"],
                "page_start": c["page_start"],
                "page_end": c["page_end"],
                "section": c["section"],
                "snippet": c["text"][:350],
            }
        )
    return clean.strip(), citations
