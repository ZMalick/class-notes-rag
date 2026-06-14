"""ObservabilityPlugin — single-attachment-point instrumentation for an agent run.

Attached to the Runner via `plugins=[...]`, it receives ADK's global callbacks for
the whole run, each agent step, each tool call, and each model call. From those it:
  - emits one structured JSON record per step (persisted to logs/trace-<session>.jsonl),
  - times every agent / tool / model call with perf_counter,
  - accumulates Gemini token usage (prompt / output / thinking / total),
  - records retrieval cosine scores and the RAG-vs-web tool split,
  - captures the Orchestrator's route,
and exposes a compact `summary()` + `metrics` dict for the CLI, demo, and FastAPI.

Pragmatic by design (cert design doc §7): structured logs + ADK-native traces + a
small metrics summary — not an enterprise OTel / Cloud Trace stack.
"""
from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

from google.adk.plugins.base_plugin import BasePlugin

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"


@dataclass
class Step:
    kind: str                       # "agent" | "tool" | "model"
    name: str
    ms: float | None                # latency in milliseconds
    extra: dict = field(default_factory=dict)


class ObservabilityPlugin(BasePlugin):
    def __init__(self, name: str = "observability", echo: bool = False, persist: bool = True):
        super().__init__(name=name)
        self.echo = echo            # also print each JSON record to the console
        self.persist = persist      # write the per-run JSONL trace file
        self._reset()

    # ------------------------------------------------------------------ state
    def _reset(self) -> None:
        self._t0 = time.perf_counter()
        # Agent runs are strictly nested (a tree) -> a stack pairs before/after.
        # ADK builds a fresh CallbackContext per hook, so object identity can't pair them.
        self._agent_stack: list[float] = []
        # Tools in one turn have distinct names (rag_search vs web_search) -> key by name.
        self._tool_starts: dict[str, float] = {}
        self.records: list[dict] = []           # JSON-able step records (the trace)
        self.steps: list[Step] = []             # structured steps for the summary
        self.tokens = {"prompt": 0, "candidates": 0, "thoughts": 0, "total": 0}
        self.tool_calls: dict[str, int] = {}    # tool name -> call count
        self.retrieval_scores: list[float] = []
        self.route: str | None = None
        self.total_ms: float = 0.0
        self.trace_path: Path | None = None

    def _t(self) -> float:
        return round((time.perf_counter() - self._t0) * 1000, 1)

    @staticmethod
    def _ms_since(t: float | None) -> float | None:
        return round((time.perf_counter() - t) * 1000, 1) if t is not None else None

    def _emit(self, rec: dict) -> None:
        rec = {"t_ms": self._t(), **rec}
        self.records.append(rec)
        if self.echo:
            print(f"  [obs] {json.dumps(rec, default=str)}")

    # -------------------------------------------------------------- run hooks
    async def before_run_callback(self, *, invocation_context):
        self._reset()
        self._sid = getattr(getattr(invocation_context, "session", None), "id", "run")
        self._emit({"kind": "run", "event": "start"})

    async def after_run_callback(self, *, invocation_context):
        self.total_ms = self._t()
        self._emit({"kind": "run", "event": "end",
                    "total_ms": self.total_ms, "tokens": self.tokens})
        if self.persist:
            LOG_DIR.mkdir(exist_ok=True)
            self.trace_path = LOG_DIR / f"trace-{self._sid}.jsonl"
            self.trace_path.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False, default=str) for r in self.records) + "\n",
                encoding="utf-8",
            )

    # ------------------------------------------------------------ agent hooks
    async def before_agent_callback(self, *, agent, callback_context):
        self._agent_stack.append(time.perf_counter())

    async def after_agent_callback(self, *, agent, callback_context):
        ms = self._ms_since(self._agent_stack.pop() if self._agent_stack else None)
        self.steps.append(Step("agent", agent.name, ms))
        self._emit({"kind": "agent", "name": agent.name, "ms": ms})
        # Opportunistically capture the route once it lands in session state.
        state = getattr(callback_context, "state", None)
        if state is not None:
            try:
                qt = state.get("query_type")
                if qt:
                    self.route = str(qt).strip()
            except Exception:
                pass

    # ------------------------------------------------------------- tool hooks
    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        self._tool_starts[tool.name] = time.perf_counter()

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        ms = self._ms_since(self._tool_starts.pop(tool.name, None))
        self.tool_calls[tool.name] = self.tool_calls.get(tool.name, 0) + 1
        extra: dict = {"args": tool_args}
        if isinstance(result, dict) and result.get("source") == "corpus":
            scores = [r.get("score") for r in result.get("results", []) if r.get("score") is not None]
            self.retrieval_scores.extend(scores)
            extra.update(n_results=len(scores), top_score=(max(scores) if scores else None))
        elif isinstance(result, dict) and result.get("source") == "web":
            extra.update(n_results=len(result.get("results", [])))
        self.steps.append(Step("tool", tool.name, ms, extra))
        self._emit({"kind": "tool", "name": tool.name, "ms": ms, **extra})

    # ------------------------------------------------------------ model hooks
    async def after_model_callback(self, *, callback_context, llm_response):
        um = getattr(llm_response, "usage_metadata", None)
        if not um:
            return
        p = um.prompt_token_count or 0
        c = um.candidates_token_count or 0
        th = um.thoughts_token_count or 0
        tot = um.total_token_count or (p + c + th)
        self.tokens["prompt"] += p
        self.tokens["candidates"] += c
        self.tokens["thoughts"] += th
        self.tokens["total"] += tot
        self._emit({"kind": "model", "prompt": p, "candidates": c, "total": tot})

    # ---------------------------------------------------------------- outputs
    @property
    def metrics(self) -> dict:
        rs = self.retrieval_scores
        return {
            "route": self.route,
            "total_ms": round(self.total_ms, 1),
            "tokens": dict(self.tokens),
            "tool_calls": dict(self.tool_calls),
            "retrieval": {
                "n": len(rs),
                "top": round(max(rs), 3) if rs else None,
                "mean": round(statistics.mean(rs), 3) if rs else None,
            },
            "n_steps": len(self.steps),
        }

    def summary(self) -> str:
        agent_ms: dict[str, float] = {}
        for s in self.steps:
            if s.kind == "agent":
                agent_ms[s.name] = agent_ms.get(s.name, 0.0) + (s.ms or 0.0)
        lines = ["METRICS",
                 f"  route:          {self.route}",
                 f"  total latency:  {self.total_ms:.0f} ms"]
        if agent_ms:
            lines.append("  agent latency:  " + ", ".join(f"{k} {v:.0f}ms" for k, v in agent_ms.items()))
        if self.tool_calls:
            lines.append("  tool calls:     " + ", ".join(f"{k}x{v}" for k, v in self.tool_calls.items())
                         + "   (RAG-vs-web split)")
            tool_ms = ", ".join(f"{s.name} {s.ms:.0f}ms" for s in self.steps
                                if s.kind == "tool" and s.ms is not None)
            if tool_ms:
                lines.append("  tool latency:   " + tool_ms)
        if self.retrieval_scores:
            lines.append(f"  retrieval:      {len(self.retrieval_scores)} chunks, "
                         f"top {max(self.retrieval_scores):.3f}, "
                         f"mean {statistics.mean(self.retrieval_scores):.3f} (cosine)")
        lines.append(f"  tokens:         {self.tokens['total']} total "
                     f"({self.tokens['prompt']} in / {self.tokens['candidates']} out"
                     + (f" / {self.tokens['thoughts']} thinking" if self.tokens['thoughts'] else "") + ")")
        if self.trace_path:
            lines.append(f"  trace:          {self.trace_path}")
        return "\n".join(lines)
