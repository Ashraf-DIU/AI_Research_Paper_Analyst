EMBEDDING_MODELS = {
    "bge-small": "BAAI/bge-small-en-v1.5",   # default: light enough for a small server
    "bge-base": "BAAI/bge-base-en-v1.5",
    "bge-large": "BAAI/bge-large-en-v1.5",
}
# Switch with: EMBEDDING_MODEL=BAAI/bge-base-en-v1.5  (then rebuild indexes with scripts/rebuild_index.py)
