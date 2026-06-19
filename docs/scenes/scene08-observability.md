# Scene 8 — Observability

- **Video file:** `scene08-observability.mp4`
- **Face-cam:** OFF
- **Target:** ~2 min
- **Status:** LOCKED — drilled predict-first 2026-06-18. Verified against `src/observability/{plugin,phoenix_setup}.py`.

## What you display
1. The **CLI metrics block** from a run (route, per-agent/per-tool latency, tokens, retrieval cosine scores) — you've already shown this in Scene 7; call back to it.
2. Switch to **Arize Phoenix** at `http://localhost:6006` — open the trace, expand the waterfall (Orchestrator → Researcher + tool → Reviewer → ReviewGate).

**Setup before recording (Terminal B):**
```bash
# Phoenix is already installed (v17.5.0). Only if you ever rebuild .venv: uv sync --group eval
# Start the server with the MODULE form. NOT `phoenix serve` — the console script
# hits a uv trampoline bug on this Windows/OneDrive path.
uv run python -m phoenix.server.main serve     # leave running in Terminal B (serves http://localhost:6006)
```
Then run a traced query in Terminal A:
```bash
PHOENIX_ENABLED=true PYTHONWARNINGS=ignore PYTHONIOENCODING=utf-8 uv run python -m src.cli "How does LoRA make fine-tuning efficient?"
```
(Deck slide 8 holds the same trace screenshot as a fallback if Phoenix won't cooperate live.)

## What you say (LOCKED — read in your own cadence)

**The two layers.**
> Observability here is two layers, for two different audiences.

**Layer 1 — the plugin (always on, machine-readable, ships in the product).**
> The first is in-process. It's a single plugin I attach to the ADK (say "A-D-K") Runner, and ADK calls it on every step: every agent, every tool, every model call. It captures the route, the latency per agent and per tool, the token counts, and the retrieval cosine scores. That's the metrics block you saw print at the bottom of every run. It exposes two things: a human-readable summary, and a metrics dictionary that the deployed API returns with every answer. So anyone calling the service gets the metrics right alongside the answer, with no external service. It also writes one JSON line per step to a trace file on disk.

**Layer 2 — Phoenix (a visual trace UI you turn on).**
> The second layer is a visual trace UI. With OpenTelemetry (say "open-tuh-LEM-uh-tree") I export the whole run into Arize Phoenix (say "uh-RISE FEE-niks") at localhost port 6006. It renders the run as a waterfall: Orchestrator, then Researcher with its tool call, then Reviewer, then ReviewGate, each as a span with its own latency and tokens. This is the one I turn on to debug, and to actually show that the agents collaborated in the order I claim.

**The tradeoff.**
> Phoenix is flag-gated, and it lives in an eval-only dependency group, so it's never in the Cloud Run image. Production never imports it. The trace UI is a dev and demo tool, not a runtime dependency, which keeps the deployed container lean.

## Interview notes (say only if pushed)
- **Why two:** the plugin is always-on and machine-readable, so it rides along in the API response (production monitoring, provable numbers). Phoenix is a human visual you turn on (debugging, and showing the collaboration order in the demo). Different jobs.
- **One attachment point:** the plugin is a single `BasePlugin` on the Runner (`plugins=[...]`); it gets ADK's global callbacks for the whole run, so it's not scattered across the agents.
- **Honesty:** the per-run "retrieval" metric is cosine top/mean (a quality signal), not a hit-rate; true hit-rate is the labeled-eval job in Scene 9.

## Pronunciation cues used
ADK = "A-D-K" · OpenTelemetry = "open-tuh-LEM-uh-tree" · Arize Phoenix = "uh-RISE FEE-niks".
