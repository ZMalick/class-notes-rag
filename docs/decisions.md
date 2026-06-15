# Decision log

Architectural and project-structure choices made over the life of class-notes-rag, in reverse chronological order. Use this for "why did we pick X?" questions. The original baseline lives in [design.md](design.md); this file captures deviations and additions.

Each entry: what was decided, why, trade-offs, and fallback if it goes wrong.

---

## 2026-06-14 — Phase 5: serving shape (shared core, index baked into image)

- **Decision:** Extract `run_query()` into `src/pipeline.py` as the single request/response core; FastAPI (`src/main.py`) and Streamlit both call it. The CLI keeps its own live event-streaming loop — different UX (watch-it-work vs request/response), so a little duplication is worth the clarity.
- **Decision:** Bake the prebuilt FAISS index into the Docker image (~5 MB, gitignored) rather than rebuild at container start or fetch at runtime — fast cold starts, no build-time Vertex calls, no runtime dependency on the corpus PDFs. The rebuild path stays `embedder.py` from `knowledge_base/`.
- **Decision:** uv-based image from `uv.lock` (`--frozen`), launched via `python -m uvicorn` (so `src.main` is importable without installing the project), `$PORT` honored for Cloud Run. Secrets never baked — Vertex via service-identity ADC; `TAVILY_API_KEY` + `GOOGLE_*` supplied as deploy env vars.
- **Deferred:** the actual `docker build` + Cloud Run deploy (credit + keyboard) per the "pause before deploy" decision; local FastAPI tested via uvicorn instead.

---

## 2026-06-14 — Phase 4: observability via a single ADK Plugin

- **Decision:** Instrument with one `ObservabilityPlugin(BasePlugin)` attached to the Runner (`plugins=[...]`), not per-agent callbacks or hand-parsing the event stream. One attachment point gives global before/after hooks for run/agent/tool/model with precise `perf_counter` timing and real `usage_metadata` token counts.
- **Why:** Cleanest, least-coupled seam, and reusable as-is by the Phase 5 FastAPI app (`plugin.metrics`). Matches design §7's "pragmatic, not enterprise" bar — structured JSONL logs + ADK-native traces + a small metrics summary, no OTel/Cloud Trace.
- **Timing pairing fix:** stack for agents (execution is strictly nested), name-key for tools (distinct names per turn) — because ADK passes a *fresh* `CallbackContext` to the before vs after hook, so object identity can't pair them (first version showed all-0ms latencies until this was found).
- **Honesty:** the runtime "retrieval" metric is cosine top/mean (a quality signal), NOT a hit-rate; true hit-rate is deferred to Phase 6 eval with labeled Q/A. The RAG-vs-web "split" is tool-call counts.

---

## 2026-06-14 — Phase 3: ADK multi-agent topology + deterministic loop exit

### Topology: SequentialAgent spine + LoopAgent feedback (not LLM-transfer orchestration)

- **Decision:** `root_agent = SequentialAgent[ Orchestrator, LoopAgent(max_iterations=2)[ Researcher, Reviewer, ReviewGate ] ]`.
- **Why:** A deterministic control spine is more reliable for a graded demo/video than a fully LLM-driven `transfer_to_agent` hierarchy (which can misfire). It still demonstrates **4** communication patterns (rubric needs 2+): Sequential Flow (root), Feedback Loop (the loop), Parallel Execution (Researcher issues `rag_search`+`web_search` concurrently when route=BOTH), Hierarchical Delegation (Orchestrator's `query_type` route drives the Researcher's tool choice via session state).
- **State flow:** `output_key` writes each agent's result to session state; downstream agents read it via `{key}` instruction templating (ADK `inject_session_state`; verified `bypass_state_injection=False` for plain-string instructions, and `{key?}` optional syntax for the first-iteration empty `review_verdict`). Keys centralized in `src/config.py` so the write side (`output_key=`) and read side (`{key}`) can't drift.

### Deterministic loop exit via ReviewGate (custom BaseAgent), NOT the LLM calling exit_loop

- **Decision:** The Reviewer emits a plain-text `PASS`/`FAIL` verdict only; a tiny custom `BaseAgent` (`ReviewGate`) reads it and yields `EventActions(escalate=True)` on PASS to stop the LoopAgent.
- **Why (bug found in smoke test):** The first version had the Reviewer call the built-in `exit_loop` tool. Gemini sometimes emitted the PASS *text* in one turn and the `exit_loop` *call* in the next — so the LoopAgent advanced and ran a needless second Researcher turn, which **overwrote a good answer** with a closing pleasantry ("Thank you for the feedback!"). Moving the exit decision out of the LLM's hands makes it deterministic, and making the Reviewer text-only also fixed `review_verdict` being `None` on PASS (the tool call had been swallowing the captured text).
- **Trade-off:** Adds a 4th node to the loop, but it's control-flow plumbing, not a reasoning agent — the three graded LLM agents remain Orchestrator/Researcher/Reviewer.

### Groundedness checks the retrieved evidence, not the draft's word

- **Decision:** `rag_search` and `web_search` append their raw hits to `state["retrieved_context"]`; the Reviewer is given that evidence as the *only* acceptable support.
- **Why:** This is what let the Reviewer catch an ungrounded claim naturally in the WEB smoke test — the first draft asserted specific 2026 model releases (GPT-5.5 Pro, the AI assistant Mythos, Gemma 4) that weren't in the Tavily snippets (the LLM leaned on parametric knowledge); the Reviewer FAILed it and the Researcher revised to evidence-only. The user-facing answer is surfaced from `state["draft_answer"]` (the reviewed draft), not the pipeline's last event (which is the QA verdict).

---

## 2026-06-14 — PIVOT: project repurposed into the Agentic AI cert capstone

### Project repurposed: transcript-RAG learn-by-doing → Multi-Agent Research Assistant (ADK)

- **Decision:** Repurpose `class-notes-rag` from a learn-by-doing RAG over bootcamp transcripts into the **Synapse "Master Agentic AI" certification capstone** — a 3-agent Research Assistant (Orchestrator / Researcher / Reviewer) on **Google ADK**, over a corpus of AI/ML papers (RAG) + live web (Tavily), deployed to Cloud Run.
- **Why:** Two goals collapse into one build — (1) the cert requires submitting this capstone by the **hard deadline 2026-06-25**; (2) it doubles as the AI-Engineer portfolio centerpiece. The transcript-RAG project had no external deadline and was redundant with the cert work.
- **Authoritative docs:** [`cert-capstone-design.md`](cert-capstone-design.md) (architecture + graded rubric), [`cert-capstone-build-prompt.md`](cert-capstone-build-prompt.md) (ordered Step 0→Phase 6 plan). These supersede `design.md`/`status.md` as current direction.
- **Committed:** `b251928` (AGENTS.md rewrite + the two cert docs).

### Stack changes (Google-native, rubric-mandated)

- **Embeddings:** local `BAAI/bge-large-en-v1.5` → **Vertex AI `text-embedding-005`** (rubric requires Vertex). Dimension TBD at smoke test — FAISS index must match it (bge was 1024).
- **Vector store:** pgvector (Postgres/Docker) → **FAISS on-disk** (rubric-mandated; no DB service to run/deploy).
- **Agent framework:** none → **Google ADK** + Gemini 2.5 Flash (the 40% graded core; new surface for Zaid).
- **Web search:** added **Tavily** (15% of rubric).
- **Serving:** Streamlit-only → **FastAPI → Docker → Cloud Run** (rubric deploy target), thin Streamlit for the demo.
- **Reuse:** ~30% salvage (chunking/embedding/retrieval *patterns*, repo shell, Gemini choice), ~70% new. Full file-by-file verdict in design doc §9.

### Working mode: learn-by-doing → build + narrate

- **Decision:** Retire the "Zaid writes every line" micro-step rule for this build. the AI assistant writes full implementations and narrates architecture + key decisions tightly.
- **Why:** The 6/25 deadline doesn't allow line-by-line teaching. Understanding is still required (interview defense), so narration stays — just at the architecture level, not the syntax level.

### Trade-off flagged: this REVERSES the Day 1–2 "$0 / no-payment-method" stance

- Day 1–2 decisions (below) all optimized for $0 and card-off: Voyage rejected over a $5 deposit, local bge chosen to avoid any payment relationship.
- The cert rubric **mandates Vertex AI + Cloud Run**, both of which require a **billing-enabled GCP project** (credit card on file). This is unavoidable for a submittable cert — actual spend is a few dollars and new accounts get $300 free credit, but the card requirement itself is the friction.
- **Fallback if GCP billing is a hard blocker:** the salvaged local-bge + FAISS path could run embeddings $0, but it would **not satisfy the rubric** (no Vertex, and Cloud Run still needs billing). So billing is a true prerequisite, not a preference. Surfaced to Zaid at Step 0.

### Colab orientation: package-first + thin driver notebook (NOT notebook-as-code)

- **Decision:** Code lives in the `src/` package (matches the cert SPEC's own sample structure: `src/{agents,rag,tools,observability}/main.py`). Colab's role is **demo + easy-run only** — a thin driver notebook in `notebooks/` that `import`s from `src/` and runs the pipeline cell-by-cell, plus `auth.authenticate_user()` for zero-friction GCP auth. The `src/` modules are NOT cell-annotated.
- **Why:** The cert's graded deliverables are Code + ppt + demo video — *not* a notebook. Two hard constraints forbid notebook-as-code: (1) Cloud Run deploys a containerized app, not a `.ipynb`; (2) the portfolio centerpiece must read as clean modular code. A module that doubles as a linear notebook fights itself (top-level cell code runs on `import`). Cells should *call* modules, not *contain* them.
- **Driver file form:** `notebooks/` driver written as a `# %%` jupytext "percent" `.py` (clean diffs, versionable) that Colab/VS Code render as cells and convert to `.ipynb`. This is the "sections in a file" idea — applied only to the driver, not the core modules.
- **Auth path (Step 0):** local `gcloud` ADC, not Colab auth — so the AI assistant can run/verify the pipeline locally as it builds, and because Cloud Run needs that same ADC. Colab auth (`auth.authenticate_user()`) stays available as the demo-notebook path. (Zaid's pick, 2026-06-14.)

### Step 0 (GCP gate) — RESOLVED 2026-06-14

- **GCP project:** reused existing `gen-lang-client-0465370954` (was "RAG Class Notes Project", renamed display name → "Research Assistant"; ID immutable, internal-only). Linked to the already-open billing account `0152F7-72D563-C7DDEF` — so **no new card needed**, the friction was smaller than feared. APIs `aiplatform`/`run`/`cloudbuild` enabled. ADC saved (quota project auto-set).
- **Embedding dimension = 768** (`text-embedding-005`, Vertex, `us-central1`) — confirmed by a live smoke test, not assumed. **FAISS must be 768-dim.** Resolves the design doc §10 open question (and supersedes the pre-pivot bge 1024-dim).
- **Windows gotcha (for any future GCP/CLI work):** the Cloud SDK here is a Unix-style install — only the extension-less `gcloud` bash script exists, no `gcloud.cmd`. **Run all gcloud from Git Bash, not PowerShell** (PowerShell can't exec the extension-less file and tries to "open" it). Git Bash pastes with right-click / Shift+Insert, not Ctrl+V.

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
