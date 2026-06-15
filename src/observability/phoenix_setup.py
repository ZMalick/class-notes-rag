"""Phoenix tracing for the ADK agent pipeline (the visual trace layer).

This is the demo-grade observability companion to `ObservabilityPlugin` (which
stays the source of truth for in-process metrics + the FastAPI metrics dict).
Phoenix adds a live OpenTelemetry trace UI: every agent step, tool call, LLM
prompt, and token count rendered as a waterfall at http://localhost:6006 — the
money shot for the demo video.

How it fits together:
  - `openinference-instrumentation-google-adk` auto-captures ADK spans.
  - `phoenix.otel.register(...)` wires an OTLP exporter at the local collector.
  - You run the collector + UI separately:  `phoenix serve`  (no signup, local).

Isolation: the Phoenix/OpenInference packages live in the `eval` dependency
group, NOT in the Cloud Run image (`uv sync --no-dev` excludes them). So the
imports here are LAZY (inside the function) and the whole thing is gated behind
`PHOENIX_ENABLED` — production never imports phoenix, and `setup_phoenix()` is a
safe no-op when the flag is off or the packages aren't installed.
"""
import os

# Module-level guard so a second call (e.g. CLI + an imported module) doesn't
# double-instrument ADK, which would emit duplicate spans.
_INSTRUMENTED = False

DEFAULT_ENDPOINT = "http://localhost:6006/v1/traces"
DEFAULT_PROJECT = "research-assistant"


def phoenix_enabled() -> bool:
    """True when PHOENIX_ENABLED is set to a truthy value."""
    return os.getenv("PHOENIX_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}


def setup_phoenix(
    project_name: str = DEFAULT_PROJECT,
    endpoint: str | None = None,
) -> object | None:
    """Instrument ADK for Phoenix tracing, if enabled. Returns the tracer
    provider (or None when disabled / not installed).

    Safe to call unconditionally at startup: it does nothing unless
    `PHOENIX_ENABLED` is truthy, and it imports phoenix lazily so environments
    without the `eval` group (Cloud Run, prod) are never affected.
    """
    global _INSTRUMENTED
    if not phoenix_enabled() or _INSTRUMENTED:
        return None

    try:
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor
        from phoenix.otel import register
    except ImportError as e:
        print(
            f"[phoenix] PHOENIX_ENABLED is set but tracing deps are missing ({e}). "
            "Install them with:  uv sync --group eval"
        )
        return None

    endpoint = endpoint or os.getenv("PHOENIX_COLLECTOR_ENDPOINT", DEFAULT_ENDPOINT)
    # register() builds a tracer provider + OTLP exporter aimed at the local
    # collector. auto_instrument=False: we instrument ADK explicitly below so the
    # wiring is obvious (and we never double-instrument).
    tracer_provider = register(
        project_name=project_name,
        endpoint=endpoint,
        auto_instrument=False,
        set_global_tracer_provider=False,
    )
    GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
    _INSTRUMENTED = True
    print(f"[phoenix] tracing -> {endpoint} (project='{project_name}'); UI at http://localhost:6006")
    return tracer_provider
