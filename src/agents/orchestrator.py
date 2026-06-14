"""Orchestrator agent — the router.

The first agent in the pipeline. Its only job: classify the user's question into a
retrieval strategy and write the label to session state via `output_key`. This is
the "how does your agent decide to search the web?" decision — a corpus-fact
question goes to RAG, a "latest/2026" question to web, a hybrid to both. The
Researcher reads `{query_type}` and acts on it (hierarchical delegation).
"""
from google.adk.agents import LlmAgent

from src.config import MODEL, QUERY_TYPE

INSTRUCTION = """You are the Orchestrator of a research assistant. Classify the
user's question into the single best retrieval strategy.

Pick exactly one label:
- CORPUS — answerable from established AI/ML research papers: concepts, methods,
  results (e.g. attention, transformers, RAG, LoRA, ReAct, scaling laws).
- WEB — needs current or post-publication information. Signals: "latest", "recent",
  "newest", "today", a year like 2025/2026, or named products/events that post-date
  the academic literature.
- BOTH — needs foundational grounding AND a current update (e.g. "how has X evolved
  since the original paper", or comparing a classic method to recent systems).

Respond with ONLY the single label: CORPUS, WEB, or BOTH. No other text."""

orchestrator = LlmAgent(
    name="Orchestrator",
    model=MODEL,
    description="Classifies a research question into a CORPUS / WEB / BOTH retrieval strategy.",
    instruction=INSTRUCTION,
    output_key=QUERY_TYPE,
)
