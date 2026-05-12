# Decision log

Architectural and project-structure choices made over the life of class-notes-rag, in reverse chronological order. Use this for "why did we pick X?" questions. The original baseline lives in [design.md](design.md); this file captures deviations and additions.

Each entry: what was decided, why, trade-offs, and fallback if it goes wrong.

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
