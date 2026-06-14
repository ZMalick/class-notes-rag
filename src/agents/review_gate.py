"""ReviewGate — deterministic exit for the research/review feedback loop.

A minimal custom BaseAgent (control-flow plumbing, not a reasoning agent). It reads
the Reviewer's `{review_verdict}` from session state and, when the verdict is a PASS,
yields an event with `actions.escalate=True` — which is the signal a LoopAgent checks
to stop iterating. On FAIL it escalates nothing, so the loop runs the Researcher
again to revise. Putting the exit decision here (not in the Reviewer's LLM turn)
guarantees a passed answer is never clobbered by an extra Researcher turn.
"""
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types

from src.config import REVIEW_VERDICT


class ReviewGate(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        verdict = str(ctx.session.state.get(REVIEW_VERDICT, "")).lstrip()
        passed = verdict.upper().startswith("PASS")
        note = "verdict=PASS -> exit loop" if passed else "verdict=FAIL -> revise"
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"[gate] {note}")]),
            actions=EventActions(escalate=passed),
        )
