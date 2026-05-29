# Decision log

Architectural and project-structure choices made over the life of class-notes-rag, in reverse chronological order. Use this for "why did we pick X?" questions. The original baseline lives in [design.md](design.md); this file captures deviations and additions.

Each entry: what was decided, why, trade-offs, and fallback if it goes wrong.

---

## 2026-05-14 — Day 2

### Embeddings provider: Voyage → local sentence-transformers (final pivot of the day)

- **Decision:** Drop Voyage entirely. Use `BAAI/bge-large-en-v1.5` via `sentence-transformers` running on Zaid's CPU.
- **Why:** Free-tier Voyage required either (a) 15+ minutes of batching/sleep per ingest due to 10K TPM, or (b) a $5 minimum prepaid deposit to lift to Tier 1. Zaid rejected both. Local embeddings remove the rate limit and the payment relationship in one move.
- **Model choice:** `BAAI/bge-large-en-v1.5` because it outputs 1024-dim vectors — matches our existing `vector(1024)` schema column with no DDL change. Strong on MTEB; ~5-10% lower than Voyage on retrieval benchmarks but not detectable on a 266-chunk portfolio corpus.
- **Trade-offs accepted:**
  - One-time ~1.3 GB model download on first encode.
  - `.venv` size grows (~800 MB for `torch` transitive dep).
  - Slightly lower retrieval quality vs Voyage — acceptable for the project; revisit if eval scores disappoint.
  - Loses the "two-vendor split" portfolio narrative (Voyage retrieval + Gemini synthesis was a real-world pattern). New narrative: "local embeddings + Gemini synthesis = $0 dev loop." Arguably equally strong.
- **Fallback if local model is too slow / quality is too low:** Revisit Gemini's `gemini-embedding-001` (would require schema change for dim mismatch) or accept the Voyage $5 deposit. Both off the table for now.
- **Updates needed (carried into Day 3 since not implemented today):**
  - `pyproject.toml`: add `sentence-transformers`, drop `voyageai`.
  - `embedder.py`: swap Voyage client for `SentenceTransformer("BAAI/bge-large-en-v1.5").encode(...)`.
  - `AGENTS.md` + `design.md` stack tables: replace Voyage row.
- **Supersedes:** The earlier "stay on Voyage card-off, batch + sleep" entry below. Keep that entry as a record of the rate-limit findings, but the implementation decision is now this one.

### Voyage rate limits + payment-method decision (final)

- **Decision:** Stay on Voyage's no-payment-method free tier. Embedder batches chunks + sleeps between calls to fit the 10K TPM ceiling.
- **What the actual limits are (from a `RateLimitError` we hit at runtime — authoritative):**
  - **Without payment method (our state):** 3 RPM, **10K TPM**, 200M free voyage-3-series tokens.
  - **With payment method (Tier 1):** 2000 RPM, 8M TPM, same 200M free tokens.
- **Why card-off:** Voyage requires a $5 minimum prepaid deposit to add a card. Not a real charge — usage burns down the balance — but Zaid's pref is to avoid putting money down for a project that has no expected spend.
- **Implications for the embedder:**
  - 10K TPM is the binding constraint, not 3 RPM. TPM is a rolling 60-second window.
  - Batch size: ~18 chunks (assuming worst-case 500 tokens each → ~9K tokens, safety margin under 10K).
  - Sleep ~65s between batches (60s TPM window + 5s buffer).
  - Expected full-corpus ingest runtime: ~15 minutes for 266 chunks.
- **Corrections to earlier statements in this project:**
  - Day 1 `status.md` said "21s sleep between batches to respect 3 RPM" — that was for 3 RPM only and ignored TPM. Real wait is ~65s.
  - The Day 2 docs lookup earlier today concluded "single batch covers the whole corpus, no inter-batch sleep needed" — wrong; that was the Tier 1 number, not the without-card tier we're actually on.

### Embedding model: `voyage-3` → `voyage-3.5`

- **Decision:** Switch embedding model from `voyage-3` (design doc default) to `voyage-3.5`.
- **Why:** During the Day 2 docs lookup, the current Voyage API reference no longer prominently lists plain `voyage-3` — the live model strings are `voyage-3.5`, `voyage-3-large`, and the `voyage-4-*` family. The `tokenize` endpoint's documented model list explicitly includes `voyage-3.5` and excludes `voyage-3`. Both pull from the same 200M-token shared free pool, so cost is identical ($0).
- **Trade-off:** None functionally — same 1024-dim output by default, same provider, same SDK call shape. Tiny risk that we're "newer than the design doc said" but that's the right direction.
- **Fallback:** If `voyage-3.5` ever rate-limits unexpectedly, `voyage-3-large` is in the same free pool.
- **Bonus correction:** Day 1's planned "21s sleep between batches to respect 3 RPM" was based on a wrong RPM assumption. Voyage Tier 1 = 2000 RPM / 8M TPM; even the strictest free-tier ceiling we found in error responses is 20 RPM. For ~430 chunks total (< 1000 batch cap), a single embed call covers the whole corpus — no inter-batch sleep needed.
- **Updated:** [design.md](design.md), project `AGENTS.md`.

---

## 2026-05-12 — Day 1

### Design doc moved into the project

- **Decision:** Moved design doc from `Executive Assistant/projects/class-notes-rag-design.md` to `class-notes-rag/docs/design.md`.
- **Why:** Project should be self-contained — easier to navigate, easier to share with recruiters via the public repo. EA's role narrowed to "holds bootcamp transcripts + schedules time slots."
- **Implication:** Any future links to the design doc should use the project-local path, not the EA path.

### Planning and project state live in this project

- **Decision:** Project state (status, learning curriculum, weaknesses, teaching style, decisions) all go in `class-notes-rag/docs/`. EA is not the planning hub for this project anymore.
- **Why:** Self-contained projects ship cleaner. Recruiters reviewing the repo see the full history without external context.
- **Updated:** Project `AGENTS.md` to reflect the new EA boundary ("stay out of EA except for reading transcripts").

### Synthesis LLM: Anthropic → Gemini

- **Decision:** Use Gemini 2.5 Flash for synthesis and Gemini 2.5 Pro for the eval judge, instead of the AI assistant Sonnet 4.7 / Opus 4.7.
- **Why:** Anthropic's free signup credit was already exhausted on a prior project. This project must stay $0 per Zaid's budget. Google AI Studio's Gemini free tier requires no payment method.
- **Trade-off:** Loses direct Anthropic SDK practice (relevant for AI Engineer interviews). Mitigated by Gemini's SDK having the same shape (client → `generate_content`); the conceptual pattern transfers. The Voyage + pgvector retrieval pipeline is identical regardless of LLM.
- **Fallback if Gemini rate-limits become painful:** swap to local Ollama for synthesis. Retrieval pipeline unchanged.
- **Updated:** [design.md](design.md), project `AGENTS.md`, home `AGENTS.md`, `pyproject.toml`, `.env.example`.

### Postgres hosting: local Docker for development

- **Decision:** Use a local Docker Compose Postgres + pgvector during Phase 1-3 (development + eval). Supabase considered for Phase 4 if/when the demo deploys to Streamlit Cloud.
- **Why:** Local Docker is free, fast to iterate, no signup. Supabase adds friction during dev without value — no need for a public URL until the demo is real.

### Citations format: inline `[Week N Day M]`

- **Decision:** Inline labels in answers, like `[Week 3 Day 2]`, instead of footnote-style `[1][2]` with previews below.
- **Why:** Simpler prompt template, easier to eyeball groundedness during eval. Session label is human-meaningful where chunk index isn't.

### Embedding + LLM stay split across two vendors

- **Decision:** Keep Voyage for embeddings AND Gemini for synthesis, even though Gemini has its own embedding model.
- **Why:** Three reasons — (1) Voyage's retrieval quality is strong, important for `recall@5`; (2) splitting providers means each free tier covers a different phase (Voyage = one-shot ingest, Gemini = per-query synthesis); (3) the vendor split is the real-world production pattern and signals understanding in a portfolio review.

### `uv` as package manager

- **Decision:** Use `uv` for dependency management and venv (`pyproject.toml`, `.venv/`, `uv sync`).
- **Why:** Modern, fast, what the Python ecosystem trended to in 2024-2025. Single tool replaces `pip` + `venv` + `pip-tools`.
- **Fallback if uv breaks:** plain `python -m venv` + `pip install -e .` still works (need to add a `[build-system]` block to `pyproject.toml`).
