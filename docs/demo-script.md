# Demo Video — Full Walkthrough Script (~18–22 min)

> **Format (calibrated to a real peer submission — Khalid's ~28-min walkthrough +
> 16-page report):** the cert video is a **thorough narrated walkthrough**, not a
> 4–5 min demo reel. Structure below mirrors that proven format: business framing
> up front, then architecture → agents → patterns → RAG → live demo → observability
> → eval → deploy. The "why" lines are pulled from
> [design-decision-qa.md](design-decision-qa.md) — this script doubles as your
> **Phase 2 rehearsal sheet**.
>
> **How to use it:** these are *talking points*, not a teleprompter — you understand
> this now, so speak naturally. Record in segments if you want; stitch later. Aim for
> coverage and clarity over hitting a runtime. Pre-flight (env, warm the service,
> window layout) is in [recording-run-sheet.md](recording-run-sheet.md).

---

## 0 · Pre-flight (off camera)
- Env live (`.env`, FAISS index built), Cloud Run warmed (`curl …/health` once).
- Terminal A (large font), Terminal B running `phoenix serve`, browser tabs: Phoenix (localhost:6006), GitHub repo, live URL. `eval/results.md` open.
- Dry-run the WEB query a couple times so you can catch the Reviewer-FAIL take live (Scene 6).
- **Never show `.env` on camera.**

---

## 1 · Hook — the problem (business framing) (~1.5 min)
**On screen:** the README / architecture diagram, or just you talking.

**Say:** → canonical read-script in [`scenes/scene01-hook.md`](scenes/scene01-hook.md) — **LOCKED, approved 2026-06-18**. Read from that file on camera. The per-scene files in [`scenes/`](scenes/) are the source of truth for what you *say*; this overview doc keeps scene ordering and the "on screen" cues only.

---

## 2 · What I built — the headline (~1.5 min)
**On screen:** README "Highlights" + stack table.

**Say:**
> "Three collaborating agents on Gemini 2.5, wired on a deterministic control spine. Four ADK communication patterns — the rubric asks for two. RAG over 15 arXiv papers using Vertex embeddings and a FAISS index, with page-level citations. Live web search via Tavily, with smart routing between the two. It's evaluated with Ragas, observable through both an in-process metrics plugin and an Arize Phoenix trace UI, and deployed live on Cloud Run. I'll hit each of those."

---

## 3 · Architecture overview (~2 min)
**On screen:** the architecture diagram in the README.

**Say:**
> "Here's the shape. A user question enters a fixed pipeline. First, an **Orchestrator** agent classifies it — corpus, web, or both. Then a **Researcher** agent gathers evidence using tools and drafts a cited answer. Then a **Reviewer** agent checks that every claim is grounded in what was retrieved. If it passes, you get the answer; if it fails, it loops back and the Researcher revises.
>
> Two things to flag up front. First, there's no single 'master' LLM running the show — it's the *same* Gemini model invoked in three different roles, and the thing that runs them in order is plain code, a deterministic pipeline. Second, the agents never call each other directly — they coordinate through **ADK session state**, a shared scratchpad each agent reads and writes. That keeps them decoupled."

---

## 4 · The agents, one by one (~3 min)
**On screen:** open `src/agents/orchestrator.py`, then `researcher`, `reviewer`, `review_gate.py`.

**Say (per agent):**
- **Orchestrator** — "Its only job is to classify. It reads the question and an instruction that defines CORPUS / WEB / BOTH with signal words — things like 'latest' or a year like 2026 push it to web — and it outputs a single label to session state. No tools, no retrieval. It's the receptionist that routes you to a department."
- **Researcher** — "The only agent with tools: `rag_search` over the FAISS index, and `web_search` via Tavily. It reads the route, requests the right tool — both at once on a BOTH query — and writes a cited draft. Worth being precise: the LLM doesn't run the search itself; it *requests* the tool, and ADK runs the function and feeds the results back."
- **Reviewer** — "Groundedness QA. Its prompt injects the draft and the retrieved evidence from session state, and it checks every claim is actually supported — then emits a PASS or FAIL verdict. It's enforcing groundedness, not absolute truth: it verifies claims match the sources we retrieved."
- **ReviewGate** — "A tiny *non-LLM* control node — twelve lines. It reads the verdict and stops the loop on PASS. **Design decision worth calling out:** I deliberately kept the loop-exit decision out of the LLM's hands. An earlier version let the Reviewer stop the loop itself, but the model sometimes split its 'PASS' and the stop signal across turns, and a needless second pass overwrote a good answer. Moving the stop into deterministic code fixed it."

---

## 5 · Communication patterns (the 40% core) (~1.5 min)
**On screen:** `src/agents/agent.py` (the topology) + the README patterns table.

**Say:**
> "The whole thing is a `SequentialAgent` containing the Orchestrator and then a `LoopAgent` of Researcher → Reviewer → ReviewGate, capped at two iterations. That single structure demonstrates four communication patterns: **sequential flow** is the outer pipeline; **feedback loop** is the LoopAgent; **parallel execution** is the Researcher firing both tools at once on a BOTH query; and **hierarchical delegation** is the Orchestrator's route driving the Researcher's tool choice through session state. The rubric asks for two — this has four."

---

## 6 · RAG pipeline (~2 min)
**On screen:** `src/rag/chunker.py` → `embedder.py` → `retriever.py`.

**Say:**
> "RAG is the fix for hallucination — instead of answering from memory, the model answers from real pages I hand it. Build time: I take 15 arXiv PDFs, chunk each page into ~500-token windows with overlap, embed each chunk with Vertex `text-embedding-005` into 768-dimensional vectors, and store them in a FAISS index — about 1,140 chunks. Each chunk keeps its paper title and page number, which is where the citations come from.
>
> Query time: the question gets embedded the same way, FAISS finds the closest chunks by **cosine similarity** — not probability, *similarity*, how alike in meaning — and those passages go to the Researcher, which answers only from them. One detail I'm proud of: I normalize the vectors so a FAISS inner-product search *is* cosine similarity."

---

## 7 · Live demo — the routing moments (~4 min)
> This is the proof it works. Clear the terminal between runs.

**CORPUS** — `PYTHONIOENCODING=utf-8 uv run python -m src.cli "What is scaled dot-product attention?"`
> "A textbook question routes to CORPUS, searches the papers, answers with a page citation — `[Attention Is All You Need p.4]` — and the Reviewer passes it. Notice the metrics at the bottom: route, per-agent latency, tokens, retrieval scores, captured every run."

**WEB** — `… "What are the most recent large language model releases in 2026?"`
> "Ask about something after the papers were written and the Orchestrator routes to live web search instead. Same pipeline, different source, chosen automatically."

**FEEDBACK LOOP** (re-run the WEB query until it fires)
> "Here's the differentiator. The first draft made a claim the web snippets didn't support, so the Reviewer **failed** it — and the system looped back, the Researcher revised using only the retrieved evidence, and the second pass passed. Groundedness is enforced, not assumed."

**BOTH** — `… "Compare retrieval-augmented generation in the papers with the latest 2026 RAG techniques."`
> "A question needing both sources fires RAG and web search **in parallel**, then blends paper citations with live web URLs in one answer."

---

## 8 · Observability (~2 min)
**On screen:** the CLI metrics block, then switch to Phoenix (localhost:6006).

**Say:**
> "Two layers. In-process: a single ADK plugin on the runner captures route, per-agent and per-tool latency, token counts, and retrieval scores every run, and the API returns that metrics dict with every answer. And a trace UI: with OpenTelemetry I export the whole run into Arize Phoenix, where you can see the waterfall — Orchestrator, Researcher with its tool call, Reviewer, ReviewGate — each span with its latency and tokens. Great for debugging and for proving the agents actually collaborated the way I claim."

**On screen:** run one traced query → expand the trace.

---

## 9 · Evaluation (~2 min)
**On screen:** `eval/results.md`, or run `uv run python -m eval.run_eval --skip-ragas` for live routing.

**Say:**
> "I didn't want to just say 'it looks right.' The hard part is that the output is prose — there's no single correct string to match. So I use **LLM-as-judge**: the Ragas library has a stronger model, Gemini 2.5 Pro, grade each answer 0 to 1 against the evidence, over the 15 corpus questions that have a reference answer. Faithfulness 0.98 — is every claim grounded; answer relevancy 0.83; context precision 0.81 and recall 0.93 — those two grade the retrieval. Plus 100% routing accuracy — that one's a deterministic exact-match, no judge needed. So: measured quality, not vibes."

---

## 10 · Deployment (~2 min)
**On screen:** `Dockerfile`, `src/main.py`, then `curl` the live URL.

**Say:**
> "To make it usable by anyone, the code has to run on an always-on, reachable computer — not my laptop. Three steps: I wrap the agent in a FastAPI service with an `/ask` endpoint; I package it plus the prebuilt FAISS index into a Docker container so it runs identically anywhere; and I deploy that container to Google Cloud Run, which runs it on Google's servers and gives a public URL. Users send a question to the URL and get an answer — nothing runs on their machine. Auth to Vertex is via the Cloud Run service identity, so there are no keys baked into the image. Here it is answering live in the cloud."

`curl -s https://research-assistant-969189630215.us-central1.run.app/health`

---

## 11 · Close (~1 min)
**On screen:** the GitHub repo.

**Say:**
> "So: Google ADK, Gemini 2.5, Vertex embeddings, FAISS, Tavily, FastAPI on Cloud Run — three agents, four communication patterns, grounded RAG with citations, smart routing, an independent review loop, evaluated with Ragas and fully observable. It's not a prototype — it's measured, traced, and live. Code's on GitHub. Thanks for watching."

---

## Rubric coverage checklist (the final cut must hit all of these)
- [ ] 3 agents named + roles shown (Scenes 3–4) — **40%**
- [ ] 2+ communication patterns shown live: feedback loop (Scene 7) + parallel (Scene 7) — **40%**
- [ ] RAG: chunk → embed → FAISS retrieval with citations (Scenes 6–7) — **25%**
- [ ] Web search + routing (Scene 7) — **15%**
- [ ] Observability (Scene 8) + deployment (Scene 10) — **20%**
- [ ] Eval numbers shown (Scene 9) — polish
- [ ] Business framing up front (Scene 1) — presentation polish (borrowed from the peer example)
