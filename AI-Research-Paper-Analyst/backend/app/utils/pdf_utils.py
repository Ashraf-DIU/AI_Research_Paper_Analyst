import hashlib

MAX_FILENAME = 200


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_pdf(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def safe_filename(name: str) -> str:
    name = (name or "paper.pdf").replace("\\", "/").split("/")[-1]
    return name[:MAX_FILENAME] or "paper.pdf"
