# Scene 4 — The agents, one by one

- **Video file:** `scene04-agents.mp4`
- **Face-cam:** OFF
- **Target:** ~3 min
- **Status:** LOCKED — drilled predict-first 2026-06-18, verified against `src/agents/*.py`.

## What you display
**Deck slide 4 (The three agents).**
Code cameo: [src/agents/review_gate.py](../../src/agents/review_gate.py) — the ~12-line non-LLM control node is short and impressive on camera. Glance at it during the ReviewGate beat. (Optional quick glances at orchestrator/researcher/reviewer, but the deck slide carries the concept.)

## What you say (LOCKED — read in your own cadence)

**Orchestrator.**
> The first agent is the Orchestrator. Its only job is to classify the question. It reads the question and writes a single label to session state: CORPUS for something the papers already cover, WEB for anything current like a 2026 model release, or BOTH when the question needs the foundation and a current update. It has no tools and does no retrieval. It's the receptionist that routes you to the right department.

**Researcher.**
> The second agent is the Researcher, and it's the only agent with tools: `rag_search` (say "FACE") over the FAISS paper index, and `web_search` through Tavily (say "TAV-ih-lee"). It reads the Orchestrator's label from session state and fires the matching tool. On a BOTH question it issues both tool calls in one turn, and those run in parallel. Here's the part I want to get exactly right: the model doesn't run the search itself. It requests a tool. ADK (say "A-D-K") runs the actual function and feeds the results back to the model. ADK doesn't decide which tool to use. It executes what the model asks for. The Researcher then writes a cited draft answer to session state, and it's instructed to answer only from what the tools returned, never from its own background knowledge.

**Reviewer.**
> The third agent is the Reviewer. This is the groundedness check. Its prompt pulls two things straight from session state: the draft answer, and the evidence the tools actually retrieved. It checks that every claim in the draft is supported by that evidence and that every citation is real, then it emits a verdict that starts with PASS or FAIL. One honesty point I always make: the Reviewer checks that the answer is grounded in the sources we retrieved. It can't check whether those sources are true in the world. If a web page is wrong, a faithfully cited answer can still be wrong. The system guarantees the answer is grounded in its sources. It can't guarantee the sources are correct.

**ReviewGate (the tradeoff beat — slow down here, show the code).**
> The fourth piece is the ReviewGate, and this one is not an LLM. It's about twelve lines of plain Python, a control node. It reads the Reviewer's verdict from session state, checks whether it starts with PASS, and on a PASS it flips an escalate flag. That flag is the signal the LoopAgent watches to stop iterating. On a FAIL it does nothing, so the loop runs the Researcher again to revise, capped at two attempts.
>
> Here's the design decision I want to defend. I deliberately kept the loop-exit decision out of the model's hands. The judgment is the LLM's job: the Reviewer writes PASS or FAIL. The control is plain code: the ReviewGate acts on it. An earlier version let the Reviewer call the exit itself. The problem was that the model sometimes split the PASS text and the stop signal across two separate turns, so a needless extra Researcher turn would run and overwrite a good answer. Moving the stop into deterministic code made both the verdict capture and the loop exit reliable. That's the separation of judgment from control.

## Interview notes (defense points — say only if pushed, keep them out of the read)
- **Orchestrator "only agent that interprets the question" is wrong.** Its only *job* is to classify, but the Researcher also reads the raw question (from session history) to form its tool queries. Say "only agent whose job is to classify," never "only agent that sees it."
- **Two write-paths to session state:** an agent's `output_key` (text → `query_type` / `draft_answer` / `review_verdict`), AND a tool writing directly (`rag_search`/`web_search` stash `retrieved_context` via `tool_context.state`). The Reviewer checks groundedness against what the *tools* captured, not the Researcher's word for it.
- **Patterns this scene demonstrates** (full list is Scene 5): hierarchical delegation = the Orchestrator's route drives the Researcher's tool choice through state.

## Pronunciation cues used
FAISS = "FACE" · Tavily = "TAV-ih-lee" · ADK = "A-D-K" (spell it).
