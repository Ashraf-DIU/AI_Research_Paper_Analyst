# AI Research Paper Analyst

Multi-document research intelligence platform: upload papers, ask questions with **page-level citations**, extract structured
information, compare papers, discover evidence-backed research gaps and draft literature reviews.

**Stack:** Next.js + TypeScript + Tailwind · FastAPI · LangChain · BGE embeddings · FAISS + BM25 (RRF) · PostgreSQL · PyMuPDF · Render + Vercel

```
Next.js (Vercel) --HTTPS--> FastAPI (Render) --> PostgreSQL (metadata, chunks, analyses)
                                  |--> Object storage (PDFs + FAISS index)
                                  |--> BGE embeddings (local) + FAISS/BM25 retrieval
                                  '--> LLM (any OpenAI-compatible API)
```
## Run locally
```bash
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env        # set LLM_API_KEY (and LLM_MODEL / LLM_BASE_URL if not OpenAI)
uvicorn app.main:app --reload  # http://localhost:8000/docs

# frontend (new terminal)
cd frontend && cp .env.local.example .env.local && npm install && npm run dev   # http://localhost:3000
```
Tests: `cd backend && pip install -r requirements-dev.txt && pytest`

## Deployment (GitHub -> Render -> Vercel)
1. **GitHub:** push this folder as repo `AI-Research-Paper-Analyst` (never commit `.env`, PDFs, indexes).
2. **Object storage:** create an S3-compatible bucket (Cloudflare R2, AWS S3, Backblaze B2). Note bucket, endpoint, access key id/secret.
   *Alternative:* attach a Render persistent disk and set `STORAGE_BACKEND=local`, `STORAGE_DIR=/var/data`.
3. **Render (backend):** New -> Blueprint -> pick the repo (uses `render.yaml`), or New -> Web Service with Root Directory `backend`,
   Build `pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt`,
   Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, health check `/api/health`.
   Set env vars: `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL` (if not OpenAI), `DATABASE_URL` (Render Postgres connection string),
   `FRONTEND_URL` (fill after step 4), `STORAGE_BACKEND=s3` + `S3_*` variables.
   Use at least 1-2 GB RAM (torch + BGE-small). On a 512 MB plan set `EMBEDDING_PROVIDER=api` instead.
4. **Vercel (frontend):** Add New -> Project -> import repo, Root Directory `frontend`, env `NEXT_PUBLIC_API_URL=<your Render URL>`. Deploy.
5. **Connect:** set Render `FRONTEND_URL` to the Vercel domain (CORS), redeploy. Test `<render-url>/api/health` and `/docs`, then upload a PDF.
6. Every `git push` to the connected branch redeploys both services.
7. 
## Known limits (MVP)
- No user authentication yet; data is scoped by workspace id only. Add auth before exposing publicly with private data.
- Background processing uses FastAPI BackgroundTasks (lost if the server restarts mid-job). Use Redis + RQ/Celery for production.
- Scanned PDFs are rejected (no OCR). Add PaddleOCR as a fallback in `pdf_service.py`.
- Render free instances sleep and have an ephemeral disk: PDFs/indexes must live in object storage (already supported).
