# Design-decision Q&A — interview answers & demo narration

> The "why" behind every major choice, written so you can **say it out loud** in
> a screen or demo. Each entry: the question an interviewer actually asks, a crisp
> spoken answer, and one tradeoff you can defend. Built up as we learn the project.
>
> Bar: explain each cold, no notes, and defend one tradeoff per component.

---

## Architecture & agents

### Q: How does your assistant decide whether to use the papers or the web?
A dedicated **Orchestrator** agent classifies each question *before* any retrieval:
**CORPUS** for established/paper knowledge, **WEB** for current/recent info (signals
like "latest" or a year such as 2026), **BOTH** for a mix. It's an LLM with a tight
instruction prompt; it outputs one word, which is written to shared session state,
and the Researcher reads that word to choose its tool.
- **Tradeoff to defend:** routing is an LLM classification, not hardcoded keyword
  rules. More flexible (handles phrasing it's never seen) but non-deterministic and
  costs a model call. I judged flexibility worth it for natural questions.

### Q: Is this one big model or several? What's actually in charge?
It's **one underlying model (Gemini 2.5 Flash) invoked in three scoped roles** —
Orchestrator, Researcher, Reviewer — each with its own instruction. There is **no
master LLM** delegating to the others. What's "in charge" of the order is a
**deterministic pipeline I defined in code** (a SequentialAgent), not a model. Each
agent is a station; the conveyor belt between them is plain code.
- **Tradeoff to defend:** multi-agent (vs. one big prompt) costs more latency and
  tokens — several model calls per question. I get separation of concerns,
  inspectable routing, and an independent review step in exchange.

### Q: Walk me through what happens when a request comes in — from the question to the first agent.
The front door (the CLI's `ask()`, or the FastAPI `/ask` route -> `run_query()` in
`pipeline.py`) does three things: creates an ADK **session**
(`InMemorySessionService`), **wraps** the question string in a
`types.Content(role="user", parts=[Part(text=...)])` message, and builds a
**`Runner(agent=root_agent)`**. Calling `runner.run_async(new_message=...)` appends
the message to the session and invokes `root_agent`.
- **Load-bearing point:** the Runner is wired to **`root_agent`, which is the
  `SequentialAgent` — not the Orchestrator.** The Runner doesn't know the Orchestrator
  exists. The `SequentialAgent` runs its `sub_agents` in order, so the Orchestrator
  (`sub_agents[0]`, an `LlmAgent`) is simply the first to run; ADK composes its
  INSTRUCTION + the user message and calls Gemini. *That* is when the question is first
  "seen."
- The **Orchestrator is the only agent whose *job* is to interpret the raw question**
  (it classifies it -> `query_type`). Agents pass their *results* to each other only
  through **session state**, never by reading each other's raw output. **Honest caveat
  (don't claim "only the Orchestrator sees the question"):** the raw user message stays
  in the shared session history, so the **Researcher also reads it** — it has to, to
  generate its tool search queries (the question is in neither a state key nor the
  Researcher's instruction template, so it comes from history). The Reviewer and
  ReviewGate work purely off state keys. What's "in charge" of ordering is plain code
  (the SequentialAgent), not a model.
- **Two ways the whiteboard gets written:** an LlmAgent's `output_key` (its text
  output -> `query_type` / `draft_answer` / `review_verdict`), AND a **tool writing to
  state directly** as a side effect — `rag_search`/`web_search` do
  `tool_context.state[RETRIEVED_CONTEXT] = ...`, so the Reviewer checks groundedness
  against evidence the *tools* captured, not the Researcher's word for it.
- **CLI vs deployed API:** same `root_agent`, same Runner, same `Content` wrapping.
  The CLI streams events live (`async for event`); the API drains the stream and reads
  the final answer from session state (`async for _: pass`).

### Q: Why multi-agent instead of a single prompt?
Separation of concerns + an independent check. One prompt that routes, retrieves,
answers, and self-verifies is hard to debug and tends to rubber-stamp its own work.
Splitting the job lets each agent do one thing well, and crucially lets a **separate**
Reviewer judge the Researcher's draft instead of the author grading itself.
- **Tradeoff to defend:** more moving parts and cost vs. a single call; justified by
  groundedness + debuggability, which matter for a *research* assistant.

### Q: What does the Reviewer actually check — and why?
It checks that **every claim in the draft is backed by the evidence that was
retrieved** (the papers or web snippets), and emits a PASS/FAIL verdict. The
*mechanism* is "is it grounded in the sources"; the *goal* is killing hallucination.
- **Important honesty point:** it verifies *grounded-in-its-sources*, not
  *true in the world*. If a web page is wrong, a faithfully-cited answer can still be
  wrong. The system guarantees groundedness, not omniscience.

### Q: What happens when the Reviewer rejects an answer?
It's a **feedback loop**: FAIL sends the draft back to the Researcher to revise,
capped at **2 attempts**; on the retry the Researcher is told to use *only* the
retrieved evidence so it stops reaching. A tiny non-LLM **ReviewGate** node reads the
verdict and stops the loop on PASS (keeping the stop decision out of the model's hands).
- **Tradeoff to defend:** the loop adds a second pass (cost/latency) but is what makes
  this more reliable than a single prompt. An alternative I'd consider: after the cap,
  explicitly answer "I couldn't ground this" instead of returning a best effort.

### Q: What communication patterns does the system use? (the 40% core)
Four — the rubric asks for 2+:
- **Sequential flow** — the outer `SequentialAgent`: orchestrate → research/review.
- **Feedback loop** — the `LoopAgent`: Reviewer FAIL → Researcher revises (max 2).
- **Parallel execution** — the Researcher runs `rag_search` + `web_search` concurrently on a BOTH query.
- **Hierarchical delegation** — the Orchestrator's route drives the Researcher's tool choice via session state.

The whole topology: `SequentialAgent[ Orchestrator, LoopAgent(max_iterations=2)[ Researcher, Reviewer, ReviewGate ] ]`.

### Q: How do the agents communicate / share data?
Through ADK **session state** — a per-request shared key/value store. Agents don't
call each other; they read/write keys: `query_type` (route), `retrieved_context`
(tool evidence), `draft_answer` (the draft), `review_verdict` (PASS/FAIL). The
Reviewer's prompt even injects `{draft_answer}` / `{retrieved_context}` straight from
state via templating.
- **Tradeoff:** shared state is simple and decoupled, but it's implicit coupling —
  an agent silently depending on a key another agent set. Fine at 4 agents; I'd want
  stricter contracts at larger scale.

---

## RAG: retrieval

### Q: Walk me through retrieval — how do you find the right chunks?
At query time: embed the question with the same model but in **query mode**
(`RETRIEVAL_QUERY`), then FAISS finds the k nearest stored vectors by **cosine
similarity** (`index.search`), and each hit is mapped back to its chunk text + page
via a **parallel array** — `chunks.json` is in the same order as the vectors, so
vector #237 ↔ chunk #237. Returns the top-5 with their cosine scores; the Researcher
cites them as `Title [p.N]`.
- **Tradeoff:** top-k by raw similarity has no reranking step, so a noisy chunk can
  occasionally slip into the 5. Fine at this corpus size; I'd add a reranker if
  precision mattered more.

### Q: Why chunk at 500 tokens / 50 overlap, per page?
500 is big enough to hold a coherent idea, small enough to be a precise retrieval
unit; the 50-token overlap stops an idea being lost at a chunk boundary; chunking
per page keeps page citations exact.
- **Tradeoff:** per-page chunking fragments a paragraph that straddles a page break.

## Embeddings & vector store

### Q: Why FAISS, and not a vector database (pgvector / Pinecone)?
FAISS is a lightweight **on-disk vector index** — no separate database server to run,
authenticate, or deploy. I bake the prebuilt index straight into the Cloud Run image,
so retrieval has zero external dependencies. At ~1,140 vectors, search is instant.
- **Tradeoff:** it's an index, not a database — no metadata filtering/SQL, no live
  writes. Fine because the corpus is static and small; a large, frequently-updated
  corpus would want a real vector DB.

### Q: Why `text-embedding-005`, and why two task types?
Google-native (fits the Vertex/ADK stack and the cert requirement) and strong 768-dim
retrieval embeddings. It supports **asymmetric retrieval** — documents embedded as
`RETRIEVAL_DOCUMENT`, queries as `RETRIEVAL_QUERY` — which is what it's tuned for, so
query↔document matching is sharper.
- **Tradeoff:** needs GCP/Vertex (cost + auth) vs. a free local model like bge. Chose
  it for Google-native consistency, quality, and the cert mandate.

### Q: How do you measure similarity — cosine? How exactly?
Cosine similarity. I **L2-normalize** every vector and use a FAISS **inner-product**
index (`IndexFlatIP`); on normalized vectors, inner product *is* cosine. `IndexFlatIP`
is exact (brute-force) search.
- **Tradeoff:** brute-force compares against every vector — instant at 1,140, but would
  need an approximate index (IVF / HNSW) at millions of vectors.
## Ragas evaluation

### Q: How do you evaluate a system whose output is prose (no single correct string)?
**LLM-as-judge**: a separate, stronger model (**Gemini 2.5 Pro**) reads
[question + answer + retrieved context] and scores it 0–1 on specific criteria, via
the Ragas library. Run over the 15 corpus questions that carry a reference answer, and averaged (the routing metric below covers all 19 rows).
- **Tradeoff:** using an LLM to grade an LLM is circular-ish; mitigated by a stronger
  judge, narrow per-metric prompts ("is *this claim* supported by *this context*?"),
  and averaging over many questions.

### Q: What does each Ragas metric measure?
Two grade the **answer**, two grade the **retrieval**:
- **Faithfulness** — every claim grounded in the context (= the Reviewer's check, scored). **0.98**
- **Answer relevancy** — the answer addresses the question. **0.83**
- **Context precision** — retrieved chunks are relevant / well-ranked. **0.81**
- **Context recall** — retrieval surfaced what the reference needed. **0.93**
Plus **routing accuracy** — deterministic exact-match of the Orchestrator's route
(no judge needed): **19/19 (100%)**.

### Q: Why Gemini 2.5 Pro for the judge but Flash for the agents?
The judge should be at least as capable as what it grades; Pro is the stronger model,
used offline where latency/cost matter less. Flash runs the live agents, where speed
and cost per request matter.
- **Tradeoff:** the Pro judge costs more per eval run — fine because eval is occasional,
  not per-user-request.

## Cloud Run deployment

### Q: How does it go from "runs on my laptop" to a live URL?
Three steps: (1) **wrap** the agent in a **FastAPI** web service (`/ask`, `/health`);
(2) **package** the code + dependencies + the prebuilt FAISS index into a **Docker**
container so it runs identically anywhere; (3) **deploy** the container to **Google
Cloud Run**, which runs it on an always-on server and gives a public URL. Users send
requests to the URL; nothing runs on their machine — like using a website.

### Q: Why Cloud Run (vs renting an always-on server / VM)?
Serverless container hosting — hand it a container, no server to manage. It **scales
to zero** when idle (no cost when unused) and scales up on demand. Built in-cloud via
Cloud Build straight from `--source`.
- **Tradeoff:** scaling to zero means **cold starts** — the first request after idle
  is slow. Capped `--max-instances` for cost safety. Fine for a demo; a high-traffic
  app would keep a warm instance.

### Q: How does the deployed app reach Vertex/Gemini without keys baked in?
Via the Cloud Run **service identity** (Application Default Credentials) — Google
injects credentials at runtime, so **no API keys live in the image**. The FAISS index
is baked into the container; the Tavily key is passed as an environment variable.
- **Tradeoff:** ties the deployment to GCP's identity model — simplest + most secure
  on Google's platform, but not portable to another cloud without rework.
