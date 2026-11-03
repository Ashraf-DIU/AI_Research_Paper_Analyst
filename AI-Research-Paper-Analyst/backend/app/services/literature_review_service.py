import re

from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.prompts import REVIEW_SYSTEM
from app.services.llm_service import complete
from app.services.retrieval_service import retrieve
from app.utils.citation_utils import TAG_RE, build_context

DEFAULT_SECTIONS = [
    "Introduction", "Overview of Existing Research", "Dataset and Methodological Comparison",
    "Approaches and Models", "Performance and Evaluation", "Research Limitations",
    "Identified Research Gaps", "Future Research Directions", "Conclusion",
]


def generate_review(db: Session, workspace_id: str, topic: str, papers: list[Paper],
                    sections: list[str] | None, citation_style: str, word_count: int) -> dict:
    sections = sections or DEFAULT_SECTIONS
    ids = [p.id for p in papers]
    ref_no: dict[str, int] = {}
    body = [f"# Literature Review: {topic}\n"]
    per = max(80, word_count // len(sections))

    for sec in sections:
        chunks = retrieve(db, workspace_id, f"{topic} {sec}", k=6, paper_ids=ids)
        if not chunks:
            body.append(f"## {sec}\n\nThe uploaded papers give no retrievable evidence for this section.\n")
            continue
        context, sources = build_context(chunks)
        text = complete(REVIEW_SYSTEM.format(words=per),
                        f"Topic: {topic}\nSection: {sec}\n\nSources:\n{context}")

        def repl(m: re.Match) -> str:
            out = []
            for label in (x.strip() for x in m.group(1).split(",")):
                c = sources.get(label)
                if not c:
                    continue  # drop invalid tags
                n = ref_no.setdefault(c["paper_id"], len(ref_no) + 1)
                pg = c["page_start"] if c["page_start"] == c["page_end"] else f"{c['page_start']}-{c['page_end']}"
                out.append(f"{n}, p. {pg}" if citation_style == "numeric-page" else str(n))
            return f"[{'; '.join(out)}]" if out else ""

        body.append(f"## {sec}\n\n{TAG_RE.sub(repl, text)}\n")

    by_id = {p.id: p for p in papers}
    refs = ["## References\n"]
    for pid, n in sorted(ref_no.items(), key=lambda kv: kv[1]):
        p = by_id[pid]
        doi = f" https://doi.org/{p.doi}" if p.doi else ""
        refs.append(f"[{n}] {p.title or p.filename} ({p.filename}).{doi}")
    return {"markdown": "\n".join(body) + "\n" + "\n".join(refs),
            "references": [{"number": n, "paper_id": pid} for pid, n in ref_no.items()]}
