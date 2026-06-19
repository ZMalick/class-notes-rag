# Synapse submission post

> Draft text to post to the Synapse "Master Agentic AI" community for the cert
> capstone. Fill the three **[ ]** placeholders (video link, ppt attachment note,
> your name/cohort handle) before posting. Two versions below: a full post and a
> short version if the channel prefers brevity.

---

## Full version

**Capstone — Research Assistant: a Multi-Agent Intelligence System on Google ADK**

Submitting my capstone for the Master Agentic AI certification.

**What it is.** A multi-agent research assistant that answers questions over a
curated corpus of AI/ML papers (RAG) and the live web (Tavily). An Orchestrator
routes each query, a Researcher gathers evidence, and a Reviewer enforces
groundedness before any answer is returned — with full observability and a live
Cloud Run deployment.

**Architecture (Google ADK + Gemini 2.5 Flash).**
- **3 agents** — Orchestrator (routes CORPUS / WEB / BOTH), Researcher (calls
  `rag_search` over FAISS + `web_search` via Tavily), Reviewer/QA (groundedness +
  citation check). A tiny deterministic `ReviewGate` node makes the loop-exit
  reliable instead of leaving it to the LLM.
- **4 communication patterns** (rubric asks for 2+): hierarchical delegation,
  sequential flow, feedback loop (Reviewer FAIL → Researcher revises), and
  parallel execution (RAG + web fire concurrently on BOTH).
- **RAG** — 15 arXiv papers → Vertex `text-embedding-005` (768-dim) → FAISS,
  with inline page-level citations.

**Evaluated, observable, deployed.**
- **Eval (Ragas, Gemini 2.5 Pro judge):** faithfulness **0.98**, answer relevancy
  **0.83**, context precision **0.81**, context recall **0.93**; routing accuracy
  **19/19 (100%)** across corpus, web, and mixed questions.
- **Observability:** an in-process ADK `BasePlugin` (per-step latency, tokens,
  retrieval scores, route) plus an Arize Phoenix OpenTelemetry trace UI.
- **Deploy:** FastAPI → Docker → **Cloud Run** (live, public, scales to zero).

**Stack.** Google ADK · Gemini 2.5 Flash/Pro · Vertex AI embeddings · FAISS ·
Tavily · FastAPI · Cloud Run · Streamlit · Ragas · Arize Phoenix. The agent core
deliberately avoids LangChain/LlamaIndex to show the RAG primitives directly
(LangChain appears only as an isolated, eval-only dependency for Ragas).

**Links.**
- Live demo: https://research-assistant-969189630215.us-central1.run.app
  (`GET /health`, or `POST /ask {"question": "..."}`)
- Code: https://github.com/ZMalick/multi-agent-research-assistant
- Demo video: **[ paste link ]**
- Presentation: **[ attach Research-Assistant-Capstone.pptx ]**

Happy to answer questions on the routing logic, the deterministic loop exit, or
the eval setup. — **[ your name / cohort handle ]**

---

## Short version

**Capstone: Research Assistant — Multi-Agent Intelligence System (Google ADK)**

A 3-agent system on Google ADK + Gemini 2.5 that answers research questions over
a corpus of AI/ML papers (RAG over Vertex embeddings + FAISS) and the live web
(Tavily). An Orchestrator routes CORPUS / WEB / BOTH, a Researcher gathers cited
evidence, and a Reviewer enforces groundedness in a feedback loop. Four ADK
communication patterns, evaluated with Ragas (faithfulness 0.98 · routing 19/19),
fully observable (ADK plugin + Arize Phoenix traces), and deployed live on
Cloud Run.

- Live: https://research-assistant-969189630215.us-central1.run.app
- Code: https://github.com/ZMalick/multi-agent-research-assistant
- Video: **[ link ]** · Deck: **[ attached ]**

---

## Pre-post checklist

- [ ] Demo video recorded + uploaded; link pasted in both versions.
- [ ] `Research-Assistant-Capstone.pptx` attached (or its link added).
- [ ] Repo is public and the README renders (incl. the Phoenix screenshot).
- [ ] Live URL responds — `curl .../health` returns `{"status":"ok"}`
      (the service scales to zero, so the first call after idle is slow; warm it
      once before anyone clicks).
- [ ] Your name / cohort handle filled in.
- [ ] Posted before the **2026-06-25** deadline.
