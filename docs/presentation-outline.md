# Presentation Outline — Research Assistant (Multi-Agent ADK)

A slide-by-slide outline for the cert capstone deck (~12 slides, ~8–10 min talk).
Each slide lists the headline, the bullets to show, and a speaker note. Rubric
pillar tagged where relevant. Build it in PowerPoint/Google Slides; reuse the
README architecture diagram and screenshots from the demo recording.

---

### Slide 1 — Title
- **Research Assistant — Multi-Agent Intelligence System (Google ADK)**
- Subtitle: RAG over AI/ML papers + live web search, with grounded review and observability
- Your name · Synapse "Master Agentic AI" capstone · date · GitHub + live URL
- *Note:* one line on what it does — "ask a research question, get a cited, fact-checked answer."

### Slide 2 — Problem & goal
- LLMs hallucinate and go stale; research answers need **sources** and **freshness**.
- Goal: an agent system that routes between a **paper corpus** and the **live web**, and **verifies groundedness** before answering.
- Success = cited answers, smart routing, measured quality, deployed live.
- *Note:* frame it as a real applied-AI problem, not a toy.

### Slide 3 — Architecture (the centerpiece) — **40%**
- Show the diagram: Orchestrator → LoopAgent[ Researcher → Reviewer → ReviewGate ].
- Callouts: 3 Gemini agents; ADK session state carries route/context/draft/verdict.
- *Note:* walk the flow once, end to end, in plain language.

### Slide 4 — The 3 agents — **40%**
| Agent | Job |
|---|---|
| Orchestrator | classifies the query → CORPUS / WEB / BOTH |
| Researcher | calls `rag_search` (FAISS) + `web_search` (Tavily), drafts a cited answer |
| Reviewer/QA | checks every claim against retrieved evidence; PASS/FAIL |
- *Note:* mention `ReviewGate` is a tiny deterministic control node, not a 4th LLM — it makes the loop exit reliable.

### Slide 5 — Communication patterns (2+ required; built 4) — **40%**
- **Hierarchical delegation** — Orchestrator's route drives the Researcher.
- **Sequential flow** — orchestrate → research → review.
- **Feedback loop** — Reviewer FAIL → Researcher revises (LoopAgent, max 2).
- **Parallel execution** — RAG + web fire concurrently on BOTH.
- *Note:* this slide directly answers the rubric; say "two required, I implemented four."

### Slide 6 — RAG pipeline — **25%**
- `pypdf` → 500-token chunks (50 overlap) + page metadata → Vertex `text-embedding-005` (768-d) → FAISS `IndexFlatIP`.
- 15 arXiv papers, ~1,140 chunks; query-time top-k with `Title [p.N]` citations.
- *Note:* emphasize the inline page citations — that's what makes answers verifiable.

### Slide 7 — Routing & web search — **15%**
- Corpus facts → RAG; "latest / 2026 / recent" → Tavily; ambiguous → both.
- Show a one-line example of each route.
- *Note:* tie back to "freshness" from Slide 2.

### Slide 8 — Observability — **20%**
- Two layers: `ObservabilityPlugin` (structured JSONL + latency/tokens/retrieval metrics, returned by the API) **+** Arize Phoenix OpenTelemetry trace UI.
- Insert the Phoenix trace-waterfall screenshot.
- *Note:* "I can see how the agents collaborated and what every step cost."

### Slide 9 — Evaluation
- Ragas (Gemini 2.5 Pro judge): **faithfulness 0.98 · answer_relevancy 0.83 · context_precision 0.81 · context_recall 0.93**.
- **Routing accuracy: 19/19 (100%)** across corpus/web/both.
- *Note:* "measured, not vibes" — name each metric in one phrase.

### Slide 10 — Deployment — **20%**
- FastAPI → Docker → **Cloud Run** (built via Cloud Build, `--source`).
- FAISS index baked into the image; Vertex auth via service identity (no keys in image).
- Live URL: https://research-assistant-969189630215.us-central1.run.app
- *Note:* mention scale-to-zero + max-instances cap as cost-awareness.

### Slide 11 — Key decisions & challenges
- Deterministic loop exit (`ReviewGate`) instead of an LLM `exit_loop` — fixed a bug where a good answer got overwritten.
- Groundedness checks **retrieved evidence**, not the draft's word — caught a real hallucination in testing.
- Ragas ↔ langchain 1.x incompatibility → pinned the eval deps, isolated from the served app.
- *Note:* these show engineering judgment — interviewers love this slide.

### Slide 12 — Rubric mapping + close
| Pillar | Weight | Evidence |
|---|---|---|
| Multi-agent (ADK) | 40% | 3 agents, 4 patterns, session state |
| RAG | 25% | Vertex embeddings + FAISS + citations |
| Web search | 15% | Tavily + routing |
| Observability/deploy/presentation | 20% | Plugin + Phoenix, Cloud Run, this deck + demo |
- Links: GitHub repo · live URL · demo video.
- *Note:* end on "evaluated, observable, and live — not just a prototype."

---

## Speaking tips
- Lead with the demo if the format allows — show it working, then explain.
- Keep each slide to ~45s; the architecture (3) and patterns (5) slides earn the 40%, so linger there.
- Have the live URL open as a backup in case the recording glitches.
