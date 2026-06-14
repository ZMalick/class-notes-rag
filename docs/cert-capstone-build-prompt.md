# Cert Capstone — Build Prompt / Execution Plan

**Read first:** [`AGENTS.md`](../AGENTS.md) (working mode + stack) and [`cert-capstone-design.md`](cert-capstone-design.md) (architecture + rubric). This file is the ordered plan.

**Deadline:** 2026-06-25. **Mode:** Build + narrate (you write the code; explain architecture + key decisions briefly as you go). **Target:** ~8 focused days; front-load, keep Net+ light.

---

## KICKOFF (paste this to start the fresh session in `class-notes-rag/`)

> Read `AGENTS.md` + `docs/cert-capstone-design.md` + `docs/cert-capstone-build-prompt.md`. We're reshaping this project into the Agentic AI cert capstone (Multi-Agent Research Assistant on Google ADK). Start with **Step 0 (GCP gate)**, then work the phases in order. Build + narrate mode. Log each session to `docs/sessions.md` and decisions to `docs/decisions.md`. Verify ADK/Vertex package + API names against current docs before writing against them — don't trust names from memory.

---

## Step 0 — GCP gate (BLOCKS everything; do first)

Vertex embeddings + Cloud Run both need a billing-enabled GCP project and finished `gcloud` ADC auth. Zaid is unsure if this exists.

- [ ] `gcloud auth list` + `gcloud config list` — is an account + project set?
- [ ] If no project: create one (`gcloud projects create` or console), **enable billing** (new accounts have $300 free credit; real cost here is a few dollars).
- [ ] Enable APIs: `aiplatform.googleapis.com` (Vertex), `run.googleapis.com` (Cloud Run), `cloudbuild.googleapis.com`.
- [ ] Finish ADC auth — Zaid at keyboard: `gcloud auth application-default login --no-launch-browser` (the `--no-launch-browser` flag avoids the misfire logged in EA planner row 50), then `gcloud config set project <ID>`.
- [ ] Set env vars in `.env`: `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT=<id>`, `GOOGLE_CLOUD_LOCATION=us-central1`, `TAVILY_API_KEY=...`.
- [ ] **Smoke test:** one Vertex `text-embedding-005` call returns a vector. Record its dimension — FAISS must match it.

**Gate:** do not start Phase 2 until a Vertex embedding call succeeds.

## Phase 1 — Reshape / cleanup (the full rework sweep)

Migrate the repo off the old pgvector/bge/transcript stack and into the cert layout. Reference table: design doc §9.

- [ ] Create new layout: `src/{agents,rag,tools,observability}/`, `src/main.py`, `knowledge_base/`, `tests/`, `deployment/`, `notebooks/`.
- [ ] **Move + rework** `ingest/chunker.py` → `src/rag/chunker.py` (PDF input via `pypdf`, semantic chunking, paper/page metadata — keep the token-window logic as a fallback).
- [ ] **Move + rework** `ingest/embedder.py` → `src/rag/embedder.py` (Vertex embed → FAISS; delete psycopg/pgvector code).
- [ ] **Move + rework** `app/retriever.py` → `src/rag/retriever.py` (Vertex query-embed + FAISS top-k).
- [ ] **Delete** `db/schema.sql` and `docker-compose.yml` (pgvector-specific; archive to `docs/_archive/` if you want history).
- [ ] **Rework** `.env.example`: drop `DATABASE_URL`; add the GCP + Tavily vars from Step 0.
- [ ] **Rework** `pyproject.toml`: add `google-adk`, Vertex/`google-genai`, `faiss-cpu`, `pypdf`, `tavily-python`, `fastapi`, `uvicorn`; remove `psycopg`, `sqlalchemy`, `pgvector`, `sentence-transformers`; update `name`/`description`. Re-lock the venv.
- [ ] **Update** `.gitignore`: add `faiss_index/`, `*.faiss`, GCP creds `*.json`; reconsider the `data/` rule (corpus is `knowledge_base/` now).
- [ ] **Banner** `docs/design.md` + `docs/status.md` with a one-line "SUPERSEDED 2026-06-14 by cert-capstone-design.md" note (leave the rest as history).
- [ ] **Log** the pivot in `docs/decisions.md`.

**Gate:** `python -c "import google.adk, faiss, pypdf, tavily"` (or equivalent) imports clean; old pgvector imports gone.

## Phase 2 — RAG pipeline (25%)

- [ ] Curate ~15-25 AI/ML arXiv PDFs into `knowledge_base/`.
- [ ] `chunker.py`: PDF → semantic chunks + metadata. Smoke-test on one PDF.
- [ ] `embedder.py`: chunks → Vertex embeddings → build + persist FAISS index to `faiss_index/`.
- [ ] `retriever.py`: `retrieve(query, k) -> list[chunk+meta]`. Smoke-test 3-5 hand queries; eyeball relevance.

**Gate:** ask a corpus question at the CLI, get sensible top-k chunks with citations.

## Phase 3 — ADK multi-agent system (40%)

- [ ] `src/tools/rag_search.py` + `src/tools/web_search.py` (Tavily) as ADK tools.
- [ ] **Researcher** agent — Gemini + both tools; can call RAG and web (parallel when "both").
- [ ] **Orchestrator** agent — classifies query, delegates (hierarchical).
- [ ] **Reviewer/QA** agent — groundedness/citation check; fail → loop back to Researcher (feedback loop).
- [ ] Wire ADK session state (`query_type`, `retrieved_context`, `draft_answer`, `review_verdict`, `sources`).
- [ ] End-to-end run via `adk web` or a CLI runner.

**Gate:** a corpus question routes to RAG; a "latest 2026" question routes to web; a mixed question uses both; reviewer catches an ungrounded claim at least once. (These become demo-video moments.)

## Phase 4 — Observability (~part of 20%)

- [ ] Structured logging per agent step (route decision, tool calls, latency).
- [ ] Capture the ADK event/trace stream; expose it (CLI or UI) for the demo.
- [ ] Metrics summary: latency, token counts, retrieval hit-rate, RAG-vs-web split.

**Gate:** one run prints a clean trace + metrics summary.

## Phase 5 — Deploy + demo UI (~part of 20%)

- [ ] `src/main.py`: FastAPI `/ask` endpoint wrapping the agent.
- [ ] `deployment/Dockerfile`; build + run locally.
- [ ] Deploy to **Cloud Run** (Zaid confirms before deploy — it spends credit). Capture the live URL.
- [ ] Thin **Streamlit** chat UI (or `adk web`) for the demo video.

**Gate:** live Cloud Run URL answers a question end-to-end.

## Phase 6 — Eval, docs, deliverables

- [ ] `tests/eval.py`: ~15-20 Q/A pairs → groundedness (LLM-judge) + retrieval hit-rate. Put the table in the README.
- [ ] README: overview, architecture diagram, setup, eval numbers, demo GIF/link.
- [ ] **Presentation (ppt)** — architecture, design decisions, rubric mapping, eval/observability screenshots. (EA can help draft this.)
- [ ] **Demo video** — script the routing moments from Phase 3's gate; record; upload to Drive.
- [ ] **Submit** code + ppt + demo video to the Synapse community before 6/25.

---

## Standing rules for this build

- **Verify, don't guess:** confirm ADK/Vertex/Tavily package names + API signatures against current docs at install. The frameworks move fast.
- **Permissions:** ask Zaid before `gcloud` browser auth, Cloud Run deploy, anything spending real credit, git push, or deletes.
- **Log every session** to `docs/sessions.md` (what shipped, decisions, blockers) and decisions to `docs/decisions.md` — so a fresh session always knows the state.
- **Scope guard:** if you're reaching for LangChain, a JS frontend, fine-tuning, or a second corpus — stop, that's a non-goal (design doc §11).
