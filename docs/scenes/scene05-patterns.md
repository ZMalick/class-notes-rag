# Scene 5 — Communication patterns (the 40% core)

- **Video file:** `scene05-patterns.mp4`
- **Face-cam:** OFF
- **Target:** ~1.5 min
- **Status:** LOCKED — drilled predict-first 2026-06-18, verified against `src/agents/agent.py` + README patterns table.

## What you display
**Deck slide 5 (Communication patterns).**
Code cameo: [src/agents/agent.py](../../src/agents/agent.py) — show the actual topology lines so the four patterns are visibly one structure.

## What you say (LOCKED — read in your own cadence)

**The two building blocks + the topology.**
> Everything I just walked through is built from two ADK (say "A-D-K") building blocks. A `SequentialAgent` runs its children in order, once. A `LoopAgent` runs its children in order over and over, until one of them raises a stop flag or it hits a cap. The whole system is a SequentialAgent that holds the Orchestrator and then a LoopAgent. That LoopAgent holds the Researcher, the Reviewer, and the ReviewGate, capped at two iterations.

**The four patterns (point at the code as you name them).**
> That single structure gives me four communication patterns, and the rubric only asks for two.
> - Sequential flow is the outer SequentialAgent: one agent after another, Orchestrator and then the loop.
> - Feedback loop is the LoopAgent: when the Reviewer fails the draft, it goes back to the Researcher to revise, up to two times.
> - Parallel execution is the Researcher firing both tools, `rag_search` and `web_search`, at the same time on a BOTH question.
> - Hierarchical delegation is the Orchestrator's routing decision controlling what the Researcher does, passed through session state.

**The tradeoff to defend.**
> The tradeoff I'd defend here is the coordination mechanism. The agents talk through shared session state, a whiteboard each one reads and writes. It's simple and keeps them decoupled, but it's implicit coupling: an agent silently depends on a key another agent set. That's fine at four agents. At a larger scale I'd want stricter contracts between them.

## Interview notes (say only if pushed)
- **Hierarchical delegation is the softest of the four claims.** Strict ADK "delegation" means a parent agent actively hands off control to a child (`transfer_to_agent` / `AgentTool`). Here the Orchestrator doesn't call the Researcher — it writes a label to session state and the Researcher reads it. Concede the precise version: "it's delegation *through shared state*, not a direct handoff. The higher-level agent's decision still governs the lower-level one's behavior."
- **Parallel = the tool calls, not the agents.** The agents still run in sequence; it's Gemini issuing two function calls in one turn that ADK executes concurrently.

## Pronunciation cues used
ADK = "A-D-K" (spell it).

## Full topology (reference)
`SequentialAgent[ Orchestrator, LoopAgent(max_iterations=2)[ Researcher, Reviewer, ReviewGate ] ]`
