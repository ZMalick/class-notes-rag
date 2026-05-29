# Class Notes RAG — Design Doc (Skeleton)

**Status:** Skeleton drafted 2026-05-10. Stack revised 2026-05-12 Day 1: synthesis + eval-judge LLM swapped from the AI assistant (Sonnet 4.7 / Opus 4.7) to Gemini (2.5 Flash / 2.5 Pro) because Anthropic signup credit was already used. Voyage embeddings unchanged.

**Owner:** Zaid Malick
**Target ship date:** Mid-July 2026 (Phase 2 deliverable per `projects/summer-2026-activities.md` Lever 1)
**Cadence:** 5–6 hrs/week × 6–8 weeks

---

## Goal

Ship a production-quality Retrieval-Augmented Generation (RAG) system that lets a user ask natural-language questions over the **Agentic AI Bootcamp transcripts** and returns grounded, citation-backed answers. Public repo + live demo + tweet thread. The point is portfolio differentiation for AI Engineer / FDE roles — *built* RAG, not just "studied" it.

Success criteria:
- Public GitHub repo with clean README + architecture diagram
- Live demo (Streamlit Cloud or Vercel)
- Eval harness with measurable scores (groundedness, recall@5)
- 1-tweet thread walking through the design decisions

---

## Data source

Whisper-transcribed audio from 6 Agentic AI Bootcamp sessions at `data/learning/agentic-ai-bootcamp/<session>/audio_tiny.txt`:

| Session | Folder | Date |
|---|---|---|
| Week 2 Day 1 | `2026-04-20-week2-day1/` | 2026-04-20 |
| Week 2 Day 2 | `2026-04-22-week2-day2/` | 2026-04-22 |
| Week 3 Day 1 | `2026-04-27-week3-day1/` | 2026-04-27 |
| Week 3 Day 2 | `2026-04-29-week3-day2/` | 2026-04-29 |
| Week 4 Day 1 | `2026-05-04-week4-day1/` | 2026-05-04 |
| Week 4 Day 2 | `2026-05-06-week4-day2/` | 2026-05-06 |

Each folder also has `audio.mp3` (source) and `teaching-brief.md` (auto-generated summary). Total corpus: ~18 hrs of audio → est. 150-300 pages of transcript text.

**Optional second source (Phase 2):** Linked Colab notebooks (.ipynb) for each session. Adds code context — useful for "how do you implement X" questions where the answer is in the notebook, not the lecture.

---

## Stack (recommended picks — override any before May 12)

| Layer | Pick | Why | Alternative considered |
|---|---|---|---|
| **Vector DB** | **pgvector** (in Postgres) | Single service, free tier on Supabase or local Docker, no separate vector infra. Hiring managers recognize Postgres. | Qdrant (faster, purpose-built) — adds a second service for a 6-session corpus that doesn't need it |
| **Embeddings** | **Local `BAAI/bge-large-en-v1.5`** via `sentence-transformers` (Day 2 final pivot — replaced Voyage after rate-limit + $5-deposit friction; see [`decisions.md`](decisions.md)) | $0 forever, no rate limits, 1024-dim matches existing schema column. ~5-10% lower than Voyage on MTEB but undetectable at this corpus size. | Voyage `voyage-3.5` (better quality, but friction); Gemini embeddings (would require schema dim change) |
| **LLM (synthesis)** | **Gemini 2.5 Flash** | Free tier on Google AI Studio (no card required). Plenty smart for RAG synthesis. | Gemini 2.5 Pro for "high-stakes" queries (auto-route, Phase 2 polish) |
| **Framework** | **Direct Google Gemini SDK** (no LangChain / LlamaIndex) | Shows understanding of RAG primitives. Easier to debug. Exact package name verified at install time. | LlamaIndex (cleaner abstractions but adds dep, hides what's happening) |
| **Frontend** | **Streamlit** (v1) → **Next.js** (v2 polish if time) | 50 LOC for working demo. Streamlit Cloud free hosting. | Next.js for "real" frontend but 4-5x more time |
| **Chunking** | **500-token chunks, 50-token overlap** + per-chunk metadata (session date, timestamp range, source file) | Standard middle ground. Overlap prevents cross-chunk semantic loss. | Paragraph-based — risky on Whisper transcripts (poor punctuation) |
| **Eval** | **Custom Python harness**, 20-30 hand-labeled Q/A pairs, two metrics: groundedness (LLM-as-judge) + recall@5 | Recruiter-impressive ("I built an eval harness, here are the numbers"). | Ragas / TruLens — overkill for portfolio scope |

---

## Architecture

### Ingest path (run once, then on new transcripts)

```
audio_tiny.txt × 6
        │
        ▼
[ chunker.py ]
  - split into 500-token chunks (50-token overlap)
  - attach metadata: session_date, session_label, chunk_idx, char_offset
        │
        ▼
[ embedder.py ]
  - BAAI/bge-large-en-v1.5 (local) → 1024-dim vector per chunk
        │
        ▼
[ pgvector ]
  table: chunks
  cols: id, text, embedding (vector(1024)),
        session_date, session_label, chunk_idx
  index: HNSW on embedding column
```

### Query path (per user question)

```
User question
        │
        ▼
[ BAAI/bge-large-en-v1.5 ]  → query embedding (local)
        │
        ▼
[ pgvector kNN search ]
  - retrieve top-5 chunks by cosine similarity
        │
        ▼
[ prompt builder ]
  - inject chunks as <context> XML tags
  - include session_date + session_label in each chunk for citation
        │
        ▼
[ Gemini 2.5 Flash ]
  - synthesize answer with inline citations like [Week 3 Day 2]
        │
        ▼
[ Streamlit UI ]
  - render answer + show retrieved chunks below for transparency
```

---

## Eval harness

**Labeled Q/A set:** 20-30 hand-written pairs covering 4-5 question types:
1. **Factual lookup** ("What model did Harry recommend for embeddings?")
2. **Cross-session synthesis** ("How does the agent loop in Week 3 differ from Week 4?")
3. **Quoted-fact retrieval** ("What did Harry say about certs?")
4. **Negative test** ("What did Harry say about Kubernetes?" — should respond "not covered" if absent)
5. **Multi-hop** ("Which session covered the same topic as the Colab notebook for Week 4?")

**Metric 1 — Groundedness (LLM-as-judge):**
For each (question, answer, retrieved_chunks) tuple, ask Gemini 2.5 Pro: "Is every claim in the answer supported by the retrieved chunks? Output 1 (yes) / 0 (no) / 0.5 (partial)." Aim: >0.85 average.

**Metric 2 — Recall@5:**
For each question, the labeled answer cites which chunks SHOULD be retrieved. Check: was the gold chunk in the top-5? Aim: >0.80.

**Output format:** `eval_results.json` + a CSV-friendly summary table for the README.

---

## Phase 1 Day 1 (Mon May 12) deliverables

Single 90-min focused block. Goal: end the day with a working `ingest.py` + the corpus in pgvector.

- [ ] Repo init: `class-notes-rag/` with README placeholder, .gitignore, MIT LICENSE
- [ ] `pyproject.toml` with dependencies: anthropic, voyageai, psycopg, sqlalchemy, streamlit, python-dotenv
- [ ] `.env.example` with placeholder keys: ANTHROPIC_API_KEY, VOYAGE_API_KEY, DATABASE_URL
- [ ] Local pgvector: docker-compose.yml with Postgres + pgvector extension
- [ ] `db/schema.sql` with chunks table + HNSW index
- [ ] `ingest/chunker.py` — split a single transcript, no embedding yet
- [ ] Manual smoke test: chunk one transcript, print to stdout, verify chunks look reasonable

Day 2 (Tue): embed + insert all 6 transcripts. Day 3 (Wed): query path skeleton. Day 4 (Thu): Streamlit demo wired up. Day 5 (Fri): first eval run.

---

## 4-week milestones

| Week | Goal | Demo state |
|---|---|---|
| 1 (May 12-18) | Ingest works, query path works, basic Streamlit UI | "Ask any question, get an answer + cited chunks. Looks ugly." |
| 2 (May 19-25) | Eval harness + 20 labeled Q/A + first scores. Iterate on chunking strategy. | "Numbers in README." |
| 3 (May 26-Jun 1) | Polish UI, add citation links, improve prompt template, possibly add Opus auto-route | "Looks shippable." |
| 4 (Jun 2-8) | Deploy to Streamlit Cloud, write tweet thread, push to repo with full README + architecture diagram | "Public, demo-able, ready to share." |

Anything beyond Week 4 is Phase 2 (Next.js, Colab notebook integration, multi-corpus, etc.) — only if Phase 1-4 are clean.

---

## Open decisions / questions for Monday

1. **Hosting for Postgres**: local Docker (free, dev-only) vs Supabase (free tier, real URL for demo)? Supabase is probably the right move once demo is live.
2. **Embedding cost monitoring**: $0 expected from Voyage free tier, but watch the dashboard the first week.
3. **Should the Colab notebooks be in the corpus from Day 1, or wait until Week 4?** Suggest waiting — keep v1 simple.
4. **Do we add a "no answer found" fallback?** Yes for Negative tests in eval. Threshold: if top retrieval similarity < 0.3, respond "not covered in the transcripts."
5. **Citations format**: inline `[Week 3 Day 2]` vs footnote-style `[1][2]` with chunk previews shown below the answer. Pick one before building the prompt.

---

## What this doc is NOT

- Not a final spec — picks are recommendations to override
- Not the README — that gets written Week 4 when there's something to describe
- Not a sales doc for the project — that's the tweet thread + LinkedIn post when it ships

---

**Next session:** override any stack pick that's wrong, then start the Phase 1 Day 1 checklist on May 12 morning.
