"""Page cleaning, section detection and offset mapping. Pure Python (easy to unit-test)."""
import bisect
import re
from collections import Counter

HEADING_RE = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.\s+)?"
    r"(abstract|introduction|related work|background|literature review|methods?|methodology|"
    r"materials and methods|proposed method|proposed approach|approach|datasets?|data|experiments?|"
    r"experimental setup|experimental results|results?|results and discussion|discussion|"
    r"limitations?|conclusions?|conclusion and future work|future work|references|bibliography)"
    r"\s*:?\s*$",
    re.IGNORECASE,
)

_CANON = [
    ("abstract", "Abstract"),
    ("introduction", "Introduction"),
    ("related", "Related Work"),
    ("background", "Related Work"),
    ("literature", "Related Work"),
    ("method", "Methodology"),
    ("approach", "Methodology"),
    ("dataset", "Dataset"),
    ("data", "Dataset"),
    ("experiment", "Experiments"),
    ("discussion", "Discussion"),
    ("result", "Results"),
    ("limitation", "Limitations"),
    ("conclusion", "Conclusion"),
    ("future", "Conclusion"),
    ("reference", "References"),
    ("bibliography", "References"),
]

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)


def canonical_section(heading: str) -> str:
    h = re.sub(r"^[\dIVX.\s]+", "", heading.strip().lower())
    for key, name in _CANON:
        if h.startswith(key):
            return name
    return heading.strip().title()


def _norm_line(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip().lower())


def clean_pages(pages: list[dict]) -> list[dict]:
    """Remove repeated headers/footers/page numbers, de-hyphenate, normalise whitespace."""
    n = len(pages)
    repeated: set[str] = set()
    if n >= 4:
        counter: Counter = Counter()
        for p in pages:
            lines = [ln for ln in p["text"].splitlines() if ln.strip()]
            counter.update({_norm_line(ln) for ln in lines[:3] + lines[-3:]})
        repeated = {k for k, c in counter.items() if c >= max(3, int(0.5 * n))}

    cleaned = []
    for p in pages:
        lines = [ln for ln in p["text"].splitlines() if _norm_line(ln) not in repeated or not ln.strip()]
        text = "\n".join(lines)
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        cleaned.append({"page_number": p["page_number"], "text": text})
    return cleaned


def build_document(pages: list[dict]):
    """Join pages into one string. Returns (text, page_offsets, section_marks)."""
    parts, offsets, pos = [], [], 0
    for p in pages:
        t = p["text"]
        offsets.append((pos, pos + len(t), p["page_number"]))
        parts.append(t)
        pos += len(t) + 2
    text = "\n\n".join(parts)

    marks: list[tuple[int, str]] = []
    for m in re.finditer(r"^.*$", text, re.MULTILINE):
        line = m.group(0)
        if 3 <= len(line.strip()) <= 60 and HEADING_RE.match(line):
            marks.append((m.start(), canonical_section(line)))
    return text, offsets, marks


def section_spans(text_len: int, marks: list[tuple[int, str]]) -> list[tuple[int, int, str]]:
    spans, prev_start, prev_name = [], 0, "Preamble"
    for start, name in marks:
        if start > prev_start:
            spans.append((prev_start, start, prev_name))
        prev_start, prev_name = start, name
    spans.append((prev_start, text_len, prev_name))
    return spans


def pages_for_range(offsets: list[tuple[int, int, int]], start: int, end: int) -> tuple[int, int]:
    hit = [pn for (s, e, pn) in offsets if s < end and e > start]
    if not hit:
        starts = [s for s, _, _ in offsets]
        i = max(0, bisect.bisect_right(starts, start) - 1)
        return offsets[i][2], offsets[i][2]
    return min(hit), max(hit)


def guess_title(pages: list[dict], meta_title: str | None) -> str | None:
    if meta_title and len(meta_title.strip()) > 8:
        return meta_title.strip()[:500]
    if pages:
        for line in pages[0]["text"].splitlines():
            line = line.strip()
            if len(line) >= 12 and not line.lower().startswith(("arxiv", "http", "preprint")):
                return line[:500]
    return None


def find_doi(pages: list[dict]) -> str | None:
    for p in pages[:2]:
        m = DOI_RE.search(p["text"])
        if m:
            return m.group(1).rstrip(".,;)")
    return None


def normalize_for_match(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()
