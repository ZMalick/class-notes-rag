# Demo Video Script — Research Assistant (Multi-Agent ADK)

**Target length:** 4–5 minutes. **Goal:** show every graded pillar live — the
multi-agent system (40%), RAG (25%), web search + routing (15%), and
observability + deploy (20%) — with the routing + feedback-loop "moments" that
prove the architecture actually works.

> Tip: record in 1080p, hide secrets (don't show `.env`), and keep the terminal
> font large. The whole thing can be one screen-recording with voiceover.

---

## Pre-record setup

- **Terminal A** (the star): project root, venv active. On Windows prefix runs with `PYTHONIOENCODING=utf-8` so paper symbols don't crash the console.
- **Terminal B** (for the Phoenix scene): `uv sync --group eval` then `phoenix serve` (UI at http://localhost:6006).
- **Browser tabs ready:** the Phoenix UI, the GitHub repo, and the live URL.
- **Files open:** `eval/results.md` (the eval table).
- Do a throwaway dry run of each query first — the Reviewer FAIL→revise moment (Scene 4) is probabilistic, so run the WEB query a couple times beforehand and capture the take where it fires.

---

## Scene 1 — Hook + architecture (≈30s)

**On screen:** the README architecture diagram (or the repo landing page).

**Voiceover:**
> "This is a multi-agent research assistant built on Google's Agent Development Kit. You ask a research question; an **Orchestrator** decides whether to answer from a corpus of AI/ML papers, the live web, or both; a **Researcher** gathers the evidence; and a **Reviewer** checks that every claim is grounded before you see the answer. Three agents on Gemini 2.5, four communication patterns, deployed live on Cloud Run. Let me show you."

---

## Scene 2 — CORPUS query: RAG + routing + citations (≈45s)

**Command (Terminal A):**
```bash
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What is scaled dot-product attention?"
```

**Point at, as the trace streams:**
- `[Orchestrator]` writes route → **CORPUS**.
- `[Researcher] -> tool rag_search(...)` — it searches the FAISS paper index.
- The final answer with an inline citation: **`[Attention Is All You Need p.4]`**.
- `[Reviewer] PASS`.
- The observability block: route, per-agent latency, token counts, retrieval cosine scores.

**Voiceover:**
> "A factual question about the literature routes to **RAG**. The Researcher searches a FAISS index of 15 papers, answers with a page-level citation, and the Reviewer confirms it's grounded. Notice the metrics at the bottom — latency, tokens, retrieval scores — captured for every run."

---

## Scene 3 — WEB query: live search + routing (≈30s)

**Command:**
```bash
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"
```

**Point at:** route → **WEB**, `web_search` (Tavily) tool call, an answer citing live URLs.

**Voiceover:**
> "Ask about something after the papers were written — 'latest 2026 releases' — and the Orchestrator routes to **live web search** instead. Same pipeline, different source, chosen automatically."

---

## Scene 4 — The feedback loop (the differentiator) (≈45s)

> This is the moment that separates a real multi-agent system from a single prompt. Capture the take where the Reviewer **FAILs** the first draft and the Researcher **revises**.

**Command (re-run the WEB or a BOTH query until it fires):**
```bash
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"
```

**Point at:** `[Reviewer] FAIL ...` (an ungrounded claim caught) → the loop runs the Researcher **again** → a second `[Reviewer] PASS` on the evidence-only revision.

**Voiceover:**
> "Here's the feedback loop. The first draft made a claim the web snippets didn't support, so the **Reviewer failed it** — and the system looped back, the Researcher revised using only the retrieved evidence, and the second pass was approved. Groundedness is enforced, not assumed."

---

## Scene 5 — BOTH query: parallel execution (≈25s)

**Command:**
```bash
PYTHONIOENCODING=utf-8 uv run python -m src.cli "Compare retrieval-augmented generation in the papers with the latest 2026 RAG techniques."
```

**Point at:** route → **BOTH**, `rag_search` **and** `web_search` both called, a blended answer with paper citations **and** web URLs.

**Voiceover:**
> "A question that needs both sources fires RAG and web search **in parallel**, then blends corpus citations with live web sources in one answer."

---

## Scene 6 — Observability: the Phoenix trace (≈30s)

**On screen:** switch to the Phoenix UI (localhost:6006). Run one query with tracing on:
```bash
# Terminal B already running: phoenix serve
PHOENIX_ENABLED=true PYTHONIOENCODING=utf-8 uv run python -m src.cli "How does LoRA make fine-tuning efficient?"
```

**Point at:** the trace waterfall — Orchestrator → Researcher → tool calls → Reviewer, with timings and token counts per span. Expand one LLM span to show the prompt.

**Voiceover:**
> "Every run is also traced with OpenTelemetry into Arize Phoenix. You can see exactly how the agents collaborated — each step, each tool call, each model call — with latency and tokens. Great for debugging and for proving the system does what it claims."

> Grab a screenshot here for the README's observability section.

---

## Scene 7 — Evaluation (≈25s)

**On screen:** `eval/results.md` (or run `uv run python -m eval.run_eval --skip-ragas` to show routing live).

**Voiceover:**
> "I evaluated it with **Ragas** over a labeled question set: faithfulness 0.98, answer relevancy 0.83, context precision 0.81, context recall 0.93 — plus **100% routing accuracy** across corpus, web, and mixed questions. Not just 'it runs' — measured quality."

---

## Scene 8 — It's live (≈20s)

**On screen:** browser or curl to the deployed service.
```bash
curl -s https://research-assistant-969189630215.us-central1.run.app/health
```

**Voiceover:**
> "And it's deployed on **Google Cloud Run** — FastAPI in a container, the FAISS index baked in, Vertex auth via the service identity. Here's the live endpoint answering in the cloud."

---

## Scene 9 — Close (≈15s)

**On screen:** the GitHub repo.

**Voiceover:**
> "Google ADK, Gemini 2.5, Vertex embeddings, FAISS, Tavily, FastAPI on Cloud Run — three agents, four communication patterns, evaluated and observable. Code's on GitHub. Thanks for watching."

---

## Rubric coverage checklist (make sure the final cut hits all of these)

- [ ] 3 agents named + their roles shown (Scenes 1–2) — **40%**
- [ ] 2+ communication patterns shown: feedback loop (Scene 4) + parallel (Scene 5) [+ sequential/hierarchical implied] — **40%**
- [ ] RAG: chunking→embed→FAISS retrieval with citations (Scene 2) — **25%**
- [ ] Web search routing (Scene 3) — **15%**
- [ ] Observability (Scene 6) + deployment (Scene 8) — **20%**
- [ ] Eval numbers shown (Scene 7) — polish
