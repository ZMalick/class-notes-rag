"""Reviewer / QA agent — the groundedness gate.

Judges the Researcher's `{draft_answer}` against the actual `{retrieved_context}`
evidence the tools stashed: is every claim supported, is every citation real? It
emits a plain-text verdict starting with PASS or FAIL into `{review_verdict}`.

Loop control is deterministic and lives in ReviewGate (review_gate.py), NOT in this
agent: an earlier version let the Reviewer call `exit_loop` itself, but the LLM
sometimes split the PASS text and the tool call across turns, letting a needless
extra Researcher turn overwrite a good answer. Keeping the Reviewer text-only makes
both the verdict capture and the loop exit reliable.
"""
from google.adk.agents import LlmAgent

from src.config import MODEL, REVIEW_VERDICT

INSTRUCTION = """You are the Reviewer (QA). Decide whether the draft answer is fully
grounded in the retrieved evidence — nothing fabricated, every claim supported, and
every citation actually present in the evidence.

Draft answer:
{draft_answer}

Retrieved evidence (the ONLY acceptable support):
{retrieved_context}

Reply with a verdict:
- If every claim is supported and all citations are valid: begin your reply with
  "PASS" on the first line, then one sentence of justification.
- If anything is unsupported, fabricated, or mis-cited: begin your reply with "FAIL"
  on the first line, then a short bulleted list of exactly what the Researcher must
  fix or remove.

Be strict: a confident-sounding claim with no matching evidence is a FAIL. Your
reply MUST start with the word PASS or FAIL — nothing before it."""

reviewer = LlmAgent(
    name="Reviewer",
    model=MODEL,
    description="Groundedness/citation QA; emits a PASS/FAIL verdict on the draft answer.",
    instruction=INSTRUCTION,
    output_key=REVIEW_VERDICT,
)
