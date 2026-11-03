# Evaluation
`ml/evaluation/retrieval_evaluation.py` computes page-level Recall@5/10, MRR and nDCG@10 for: dense, BM25, hybrid, hybrid+rerank.
Eval file: `[{"question": "...", "relevant": [{"filename": "paper.pdf", "page": 5}]}]`. Write 50-100 manual questions for real results;
`generate_synthetic_questions` gives a quick (noisy) bootstrap. `rag_evaluation.py` measures citation precision and page accuracy.
Record your results table here.
