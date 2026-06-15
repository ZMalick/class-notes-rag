"""Observability: structured tracing + metrics for the agent pipeline.

Two complementary layers:
  - `ObservabilityPlugin` — in-process structured logs + the metrics dict the
    FastAPI app returns (the rubric's observability requirement).
  - `setup_phoenix` — optional Phoenix/OpenTelemetry trace UI for the demo
    (flag-gated, eval-group deps; no-op in production).
"""
from .plugin import ObservabilityPlugin, Step
from .phoenix_setup import phoenix_enabled, setup_phoenix

__all__ = ["ObservabilityPlugin", "Step", "setup_phoenix", "phoenix_enabled"]
