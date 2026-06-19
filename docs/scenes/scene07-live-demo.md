# Scene 7 — Live demo (the routing moments) — CENTERPIECE

- **Video file:** `scene07-live-demo.mp4`
- **Face-cam:** OFF
- **Target:** ~4 min
- **Status:** LOCKED — drilled live 2026-06-18 against real CLI output (all four runs captured + verified). This is the proof; keep it live, never slides.

## What you display
**Live Terminal A** (large font, cleared between runs, Git Bash). Four runs, in order. Narrate over the streaming trace — each run is 25–75s and the wait is filled by you talking through the lines as they appear. Point at: the route label, the tool call(s), the citation, the Reviewer verdict + ReviewGate line, and the metrics block.

```bash
# CORPUS
PYTHONWARNINGS=ignore PYTHONIOENCODING=utf-8 uv run python -m src.cli "What is scaled dot-product attention?"

# WEB
PYTHONWARNINGS=ignore PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"

# FEEDBACK LOOP — re-run the WEB query until the Reviewer FAILs, then revises (probabilistic; keep the take where it fires)
PYTHONWARNINGS=ignore PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"

# BOTH
PYTHONWARNINGS=ignore PYTHONIOENCODING=utf-8 uv run python -m src.cli "Compare retrieval-augmented generation in the papers with the latest 2026 RAG techniques."
```
(`PYTHONWARNINGS=ignore` suppresses ADK's experimental-feature warning line for a clean take. `clear` between runs.)

## Run 1 — CORPUS — proves FOUR things at once
**Point at:** `[Orchestrator] CORPUS` · `-> tool rag_search` · the `[... p.4]` citation in the answer · `[Reviewer] PASS` then `[ReviewGate] ... exit loop` (two separate lines) · the `METRICS` block.
**Say:**
> A textbook question. The Orchestrator routes it to the corpus, the Researcher calls `rag_search`, and the answer is cited to a real page, Attention Is All You Need page 4. So it's grounded, not invented. The Reviewer passes it, and this gate line underneath is the deterministic node that actually exits the loop. And every run prints these metrics: the route, the latency per agent, the retrieval cosine scores, the token counts.

This run quietly proves all four pillars: **routing**, a **grounded cited answer**, an **independent review** (Reviewer judges, ReviewGate controls), and **observability**.

## Run 2 — WEB — proves routing flips automatically
**Point at:** `[Orchestrator] WEB` · `-> tool web_search` · the **URL** citations · metrics `route: WEB`, `web_search`.
**Say:**
> Ask about something after the papers were written, and the same pipeline routes to live web search instead. Same machinery, different source, chosen automatically. And the citations are now URLs instead of page numbers.

## Run 3 — FEEDBACK LOOP — the differentiator
*(May fire on the run-2 WEB query itself. It's probabilistic: re-run until the Reviewer FAILs, and keep that take.)*
**Point at:** `[Reviewer] FAIL` + its bullet reasons · `[ReviewGate] verdict=FAIL -> revise` · the **second** `-> tool web_search` (it searched again) · the revised, hedged draft · `[Reviewer] PASS` · metrics `web_search x2` (the loop ran twice).
**Say:**
> Here's the differentiator. The first draft claimed these models were released in 2026, but the sources only listed them as top models in 2026 with no release year, and it misattributed a multimodal capability to the wrong model. The Reviewer failed it with specific reasons, the gate sent it back, and the Researcher searched again and revised to say only what the evidence actually supports. The metrics show `web_search` ran twice. That's the loop. And one honest point: some of those claims may even be true in the real world. The Reviewer fails them anyway, because it checks groundedness in the retrieved sources, not truth.

**Why re-run:** the draft is an LLM generation, so it's nondeterministic. Sometimes the first draft is careful and passes with no loop; sometimes it over-reaches and fails. You can't guarantee the FAIL on a given take, so you keep the one where it fires.

## Run 4 — BOTH — proves parallel execution
**Point at:** `[Orchestrator] BOTH` · the **two `-> tool` lines (rag_search AND web_search) back-to-back BEFORE either `<- returned` line** — that ordering is the proof of parallelism · the **blended citations** (paper `[p.N]` in the first half, web URLs in the 2026 half) · metrics `rag_search x1, web_search x1`.
**Say:**
> A question that needs both sources. The Researcher fires `rag_search` and `web_search` in the same turn. You can see it in the trace: both calls go out before either one comes back. If they ran one after the other, you'd see each call return before the next started. The final answer blends page citations from the papers with live URLs from the web.

## Interview notes (say only if pushed)
- **Parallel proof = trace ordering** (both requests before either response). The agents themselves still run in sequence; it's the two tool calls inside the Researcher's single turn that run concurrently.
- **Feedback loop = groundedness, not truth**, capped at 2 iterations. The Reviewer can fail a claim that happens to be true, because the retrieved evidence didn't support it.
- **Reviewer vs ReviewGate** — the Reviewer writes PASS/FAIL (judgment); the ReviewGate reads it and exits the loop (control). Two separate trace lines; never say "the Reviewer ended the loop."
- **Latency** — runs ran 27s / 76s / 43s live. The feedback-loop run is longest (two passes). Narrate over the streaming trace.
