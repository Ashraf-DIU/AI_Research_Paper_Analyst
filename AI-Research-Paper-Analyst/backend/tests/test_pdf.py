from app.services.chunking_service import chunk_pages
from app.utils.text_utils import clean_pages


def _pages():
    pages = []
    for i in range(1, 6):
        body = f"Neural networks learn representations from {'abcde'[i - 1] * 6} data. " * 40
        text = f"Journal of Tests\n{i}\n"
        if i == 1:
            text += "Abstract\nWe study things.\n1 Introduction\n" + body
        elif i == 3:
            text += "3 Methodology\n" + body
        elif i == 5:
            text += "References\n[1] Someone. A paper.\n"
        else:
            text += body
        pages.append({"page_number": i, "text": text})
    return pages


def test_headers_footers_removed():
    cleaned = clean_pages(_pages())
    assert all("Journal of Tests" not in p["text"] for p in cleaned)


def test_chunks_keep_pages_and_sections():
    chunks = chunk_pages(clean_pages(_pages()))
    assert chunks
    assert all(1 <= c["page_start"] <= c["page_end"] <= 5 for c in chunks)
    assert any(c["section"] == "Methodology" for c in chunks)
    assert not any(c["section"] == "References" for c in chunks)
