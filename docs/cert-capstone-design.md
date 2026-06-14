# Cert Capstone — Design Doc

**Project:** Multi-Agent Intelligence System (Google ADK) — a **Research Assistant** over AI/ML papers + live web.
**Purpose:** Synapse "Master Agentic AI" certification capstone **and** AI Engineer portfolio centerpiece.
**Deadline:** 2026-06-25 (submit code + ppt + demo video to the Synapse community).
**Raw assignment spec:** `Executive Assistant/data/learning/agentic-ai-bootcamp/cert-assignment/SPEC.md`.
**Approved:** 2026-06-14 (Approach A — ADK-native, Gemini, FAISS-on-disk, FastAPI→Cloud Run, thin Streamlit demo; Build+narrate working mode).

> **Citation discipline:** ADK and Vertex APIs evolve. Treat every package name, model name, and method signature below as **verify-at-build**, not gospel. Confirm against current docs when you install. Where this doc names a dimension or class, it is a starting assumption to check, not a fact to trust blindly.

---

## 1. Goal & success criteria

Answer research questions over a curated corpus of AI/ML papers (RAG) and live web search (Tavily), with an orchestrator that routes intelligently between them, a reviewer that enforces groundedness, observability, and a live Cloud Run deployment.

**Done = cert-submittable AND portfolio-grade:**
- Public GitHub repo, clean README + architecture diagram.
- Runs end-to-end: question in → routed → retrieved/searched → reviewed → cited answer out.
- Deployed to Cloud Run (live URL).
- Short eval table (groundedness + retrieval hit-rate) in the README.
- 3 deliverables packaged: code (repo), presentation (ppt), demo video (Drive link).

## 2. Graded rubric → how each pillar is met

| Pillar | Weight | Implementation |
|--------|--------|----------------|
| **ADK multi-agent system** | 40% | 3 agents (Orchestrator, Researcher, Reviewer/QA) on Gemini; ADK session state; 2+ communication patterns |
| **RAG** | 25% | `pypdf` extract → semantic chunking → Vertex `text-embedding-005` → FAISS on-disk index |
| **Web search** | 15% | Tavily tool; orchestrator routes corpus-facts→RAG, "latest/recent/2026"→web, ambiguous→both |
| **Observability + deploy + presentation** | ~20% | structured logging + ADK event traces + metrics; Dockerfile→Cloud Run; ppt + demo video |

## 3. Architecture

```
user query
   │
   ▼
┌──────────────┐   Orchestrator (LlmAgent)
│ Orchestrator │   - classifies query: corpus-fact / latest-info / both
└──────┬───────┘   - delegates to Researcher (hierarchical delegation)
       ▼
┌──────────────┐   Researcher (LlmAgent + tools)
│  Researcher  │   - tool: rag_search(query)  → FAISS over paper corpus
│              │   - tool: web_search(query)  → Tavily
└──────┬───────┘   - RAG + web can run in parallel when "both"
       ▼ draft answer + sources
┌──────────────┐   Reviewer / QA (LlmAgent)
│ Reviewer/QA  │   - checks every claim is grounded in retrieved sources
└──────┬───────┘   - fail → return to Researcher to revise (feedback loop)
       ▼ pass
   final cited answer
```

- **3 agents** → satisfies the 40% minimum agent count.
- **Communication patterns (need 2+, we implement 3-4):**
  - *Hierarchical Delegation* — Orchestrator → Researcher/Reviewer.
  - *Feedback Loop* — Reviewer fails an answer → Researcher revises (ADK `LoopAgent` or explicit re-invoke).
  - *Sequential Flow* — research → review → finalize.
  - *Parallel Execution* — RAG and web search run concurrently when the query needs both (ADK `ParallelAgent` or concurrent tool calls).
- **State management:** ADK session state carries `query_type`, `retrieved_context`, `draft_answer`, `review_verdict`, `sources` between agents; session memory persists across turns.

## 4. Components (each one job, one interface)

| Unit | Path (new layout) | Does | Depends on |
|------|-------------------|------|------------|
| PDF loader + chunker | `src/rag/chunker.py` | PDF → text → semantic chunks + metadata (title, source, page) | `pypdf` |
| Embedder + index builder | `src/rag/embedder.py` | chunks → Vertex embeddings → FAISS index on disk | Vertex, `faiss-cpu` |
| Retriever | `src/rag/retriever.py` | query → Vertex embed → FAISS top-k + metadata | Vertex, `faiss-cpu` |
| RAG tool | `src/tools/rag_search.py` | wraps retriever as an ADK tool | retriever |
| Web tool | `src/tools/web_search.py` | Tavily search as an ADK tool | `tavily-python` |
| Agents | `src/agents/` | orchestrator, researcher, reviewer definitions | ADK, Gemini, tools |
| Observability | `src/observability/` | structured logging, trace hooks, metrics | logging, ADK events |
| Serving | `src/main.py` + `deployment/` | FastAPI app exposing the agent; Dockerfile for Cloud Run | FastAPI, uvicorn |
| Demo UI | `app_streamlit.py` (or `adk web`) | thin chat UI for the demo video | Streamlit |
| Eval | `tests/eval.py` | small Q/A set → groundedness + hit-rate | — |

## 5. Data flow (RAG path)

`knowledge_base/*.pdf` → `chunker` (semantic chunks + page/title metadata) → `embedder` (Vertex `text-embedding-005`, ~768-dim — **verify**) → FAISS index persisted to `faiss_index/`. Query time: `retriever` embeds the query with the same model, FAISS top-k, returns chunks + citations.

## 6. Corpus

~15-25 arXiv PDFs on LLMs / agents / RAG / embeddings, in `knowledge_base/`. Pick well-known papers (e.g. Attention Is All You Need, RAG, ReAct, Toolformer, FlashAttention, etc. — final list at build time). Web search complements with post-cutoff / "latest" questions the static corpus can't answer. Decide at build time whether to commit PDFs to the repo or `.gitignore` them and ship a download script (licensing + repo size).

## 7. Observability (part of final 20%)

Keep it pragmatic, not enterprise:
- **Logging:** structured (JSON) log lines per agent step — query, route decision, tool calls, latencies.
- **Tracing:** use ADK's built-in event/callback stream to capture the agent execution trace; surface it in the demo (great visual for "how the agents collaborated").
- **Metrics:** per-query latency, token counts, retrieval hit-rate, RAG-vs-web route split. Print a small run summary; optionally log to a file. Cloud Logging is a nice-to-have, not required.

## 8. Deployment (part of final 20%)

`FastAPI` app wraps the ADK agent (one `/ask` endpoint) → `Dockerfile` → **Cloud Run**. Streamlit demo points at the deployed URL (or runs the agent locally for the video). Gemini/Vertex auth on Cloud Run via the service's GCP identity (ADC), not a checked-in key.

## 9. Reuse + rework map (full-project sweep, 2026-06-14)

Every existing file was reviewed. Verdict per file:

| File | Now | Action in build |
|------|-----|-----------------|
| `AGENTS.md` | rewritten 6/14 ✓ | done |
| `ingest/chunker.py` | token chunks from `audio_tiny.txt`, hardcoded EA path | **rework → `src/rag/chunker.py`**: PDF input, semantic chunking, paper metadata |
| `ingest/embedder.py` | bge → pgvector INSERT, hardcoded EA path | **rework → `src/rag/embedder.py`**: Vertex embed → FAISS; drop psycopg |
| `app/retriever.py` | bge query-embed only (Shape A) | **rework → `src/rag/retriever.py`**: Vertex embed + FAISS top-k |
| `db/schema.sql` | pgvector table + HNSW | **delete** (FAISS needs no SQL); archive if desired |
| `docker-compose.yml` | Postgres/pgvector service | **delete**; replace with `deployment/Dockerfile` for Cloud Run |
| `.env.example` | `GEMINI_API_KEY`, `DATABASE_URL` | **rework**: drop DATABASE_URL; add `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `TAVILY_API_KEY` |
| `pyproject.toml` | sentence-transformers, psycopg, sqlalchemy, pgvector, tiktoken, streamlit | **rework deps**: +google-adk, +google-genai/vertex, +faiss-cpu, +pypdf, +tavily-python, +fastapi, +uvicorn; −psycopg, −sqlalchemy, −pgvector, −sentence-transformers; update name/description |
| `.gitignore` | ignores `.env`, `.venv`, `data/`, eval outputs | **add**: `faiss_index/`, `*.faiss`, GCP creds json; reconsider `data/` (corpus now `knowledge_base/`) |
| `ingest/`, `app/` dirs | old layout | **migrate** to cert's `src/{agents,rag,tools,observability}` + `main.py` |
| `docs/design.md`, `status.md`, `teaching-style.md`, `learning.md`, `shapes.md`, `weaknesses.md` | pre-pivot learn-by-doing / transcript-RAG | **historical** — leave; add a one-line "superseded by cert-capstone-design.md" banner to design.md + status.md |
| `docs/decisions.md`, `docs/sessions.md` | living logs | **keep appending** — log the pivot + each build session |
| new dirs | — | create `knowledge_base/`, `tests/`, `deployment/`, `notebooks/` |

**Net:** ~30% salvage (chunking/embedding/retrieval *patterns*, repo shell, git, Gemini choice, Streamlit), ~70% new (ADK layer, Tavily, Vertex+FAISS, observability, Cloud Run, directory restructure).

## 10. Open questions (resolve at build time)

- **GCP billing** — Zaid unsure if a billing-enabled project exists. Build Step 0 verifies/creates it. Blocks Vertex + Cloud Run.
- Final embedding dimension of `text-embedding-005` (size FAISS to match).
- Commit corpus PDFs vs `.gitignore` + download script (licensing/size).
- Cloud Run mandatory for the cert, or is a containerized local demo acceptable? (Spec lists Cloud Run; confirm in community if deploy slips.)
- ppt + demo-video format/length (confirm in community).

## 11. Non-goals (YAGNI)

No LangChain/LlamaIndex. No Next.js/JS frontend. No multi-corpus. No fine-tuning. No enterprise observability stack (OpenTelemetry/Cloud Trace) unless time is left over. Keep the corpus small (quality over volume).
