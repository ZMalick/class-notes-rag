"""Researcher agent — the worker.

Reads the Orchestrator's route from `{query_type}` and runs the matching tool(s):
rag_search over the FAISS corpus, web_search via Tavily, or BOTH together (Gemini
issues the two function calls in one turn = parallel execution). Writes a cited
draft to `{draft_answer}`. On a feedback-loop re-run it also sees the Reviewer's
`{review_verdict?}` and revises to fix what the Reviewer flagged.
"""
from google.adk.agents import LlmAgent

from src.config import DRAFT_ANSWER, MODEL
from src.tools.rag_search import rag_search
from src.tools.web_search import web_search

INSTRUCTION = """You are the Researcher. Answer the user's question using ONLY
evidence returned by your tools — never your own background knowledge.

The Orchestrator classified this question as:
    query_type = {query_type}

Route accordingly:
- CORPUS -> call rag_search.
- WEB    -> call web_search.
- BOTH   -> call BOTH rag_search and web_search (issue both calls together).

Then write a concise, well-structured answer that:
- States the answer directly.
- Cites every claim inline using the citations the tools return — corpus hits as
  "Title [p.N]", web hits as the full source URL in brackets, e.g.
  [https://example.com/article]. Use the real URL from the tool result; never write
  a placeholder like [URL], and never invent or guess a citation.
- If the retrieved evidence is insufficient, say so plainly instead of guessing.

Reviewer feedback on your previous attempt (revise to fully address it; this is
empty on your first attempt):
{review_verdict?}"""

researcher = LlmAgent(
    name="Researcher",
    model=MODEL,
    description="Retrieves evidence (corpus RAG and/or live web) and drafts a fully cited answer.",
    instruction=INSTRUCTION,
    tools=[rag_search, web_search],
    output_key=DRAFT_ANSWER,
)
