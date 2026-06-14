"""Shared config: the agent model + the session-state keys.

These keys are load-bearing. An LlmAgent writes its result with
`output_key=<KEY>`, and a downstream agent's instruction reads it with `{<KEY>}`
templating (ADK's `inject_session_state`). A typo between the write side and the
read side silently breaks the handoff, so BOTH sides import the name from here.
The instruction strings use the literal `{query_type}` / `{draft_answer}` / etc.
braces, which must match these constant values.
"""
import os

# Gemini model for all three agents (override via env if needed). 2.5 Flash is
# the cost/latency sweet spot per the design; Reviewer could be bumped to Pro.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- Session-state keys (shared across the agent pipeline) ---
QUERY_TYPE = "query_type"                 # Orchestrator route: CORPUS | WEB | BOTH
DRAFT_ANSWER = "draft_answer"             # Researcher's cited draft
REVIEW_VERDICT = "review_verdict"         # Reviewer's PASS/FAIL + reasons
RETRIEVED_CONTEXT = "retrieved_context"   # raw evidence the tools stash for QA
