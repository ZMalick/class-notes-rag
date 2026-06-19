# Scene 3 — Architecture overview

- **Video file:** `scene03-architecture.mp4`
- **Face-cam:** OFF
- **Target:** ~2 min
- **Status:** LOCKED — voice-matched 2026-06-18 (predict-first drill passed)

## What you display
**Deck slide 3 (Architecture)** — the flow diagram: User query → Orchestrator → LoopAgent[ Researcher → Reviewer → ReviewGate ] → final cited answer.
Optional 10-sec code cameo at the end: [src/agents/agent.py](../../src/agents/agent.py) to show the topology is real code.

## What you say (LOCKED — voice-matched from your own predict-first articulation)
_(the `(say "...")` bits are pronunciation cues — don't read them aloud)_

"Here's the shape of the system. A question comes in, and the first thing that happens is setup: I create a session, wrap the question as a message, and build the runner. The runner hands it to a SequentialAgent, which is the spine of the whole thing. It runs my agents in a fixed order.

First is the Orchestrator. Its job is to classify the question into one of three routes: the papers, the live web, or both. Then control moves into a loop. Inside that loop, the Researcher gathers evidence with its tools and drafts an answer with a citation on every claim. The Reviewer then checks that every claim is actually grounded in that evidence. If it passes, the answer goes out. If it fails, it loops back and the Researcher revises.

Two things I want to flag. First, there is no master model running the show. It's the same Gemini (say "JEM-in-eye") 2.5 model invoked in three different roles, and the thing that runs them in order is plain code I wrote, the SequentialAgent. Second, the agents never call each other directly. They communicate through ADK (say "A-D-K") session state, a shared whiteboard that gets created for each question, where every agent reads and writes. That keeps them decoupled.

The tradeoff I'd defend: doing this with multiple agents costs me more latency and more tokens than a single prompt would, because it's several model calls per question. What I get back is a separation of concerns and an independent review step, where a separate Reviewer grades the Researcher's draft instead of the model grading its own work."

## Delivery notes
- Optional concrete adds: name the buckets out loud ("CORPUS, WEB, or BOTH") and say *why* the review is independent (a separate Reviewer, not the author).
- Slight pause at "Two things I want to flag" — it signals the two load-bearing points.

**Tradeoff to defend:** multi-agent costs more latency/tokens than one prompt; you get separation of concerns, inspectable routing, and an independent review step.
