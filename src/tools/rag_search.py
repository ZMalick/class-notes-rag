"""ADK tool: semantic search over the FAISS paper corpus.

Wraps `src.rag.retriever.retrieve()` so the Researcher agent can call it. The
function's docstring + signature ARE the tool spec the LLM sees (ADK builds the
function declaration from them), so the docstring doubles as routing guidance.

Side effect: every hit is appended to session state under `retrieved_context`,
giving the Reviewer the actual evidence to check groundedness against — not just
the draft's word for it. `tool_context: ToolContext` is auto-injected by ADK and
hidden from the LLM's view of the tool.
"""
from google.adk.tools import ToolContext

from src.config import RETRIEVED_CONTEXT
from src.rag.retriever import citation, retrieve

K = 5  # top-k passages per search


def rag_search(query: str, tool_context: ToolContext) -> dict:
    """Search the local corpus of AI/ML research papers for relevant passages.

    Use this for established concepts, methods, and results from the literature
    (e.g. attention, transformers, RAG, LoRA, ReAct, scaling laws). Returns the
    top passages, each with a citation ("Title [p.N]") and a relevance score.

    Args:
        query: A focused natural-language search query.

    Returns:
        A dict with `source` = "corpus" and `results`, a list of
        {citation, text, score} ordered most-relevant first.
    """
    hits = retrieve(query, k=K)
    results = [
        {
            "citation": citation(h),
            "text": h["text"],
            "score": round(h["score"], 3),
        }
        for h in hits
    ]
    # Accumulate evidence for the groundedness Reviewer. Rebuild the list (rather
    # than mutate in place) so ADK records the state delta on assignment.
    evidence = list(tool_context.state.get(RETRIEVED_CONTEXT, []))
    evidence.extend(
        {"origin": "corpus", "citation": r["citation"], "text": r["text"]}
        for r in results
    )
    tool_context.state[RETRIEVED_CONTEXT] = evidence
    return {"source": "corpus", "results": results}
