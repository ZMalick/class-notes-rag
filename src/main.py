"""FastAPI service exposing the multi-agent Research Assistant.

`POST /ask {question}` -> `{answer, route, review_verdict, metrics}`. It wraps the
same `root_agent` the CLI runs. Deploy target: Docker -> Cloud Run, where Vertex /
Gemini auth comes from the service's GCP identity (ADC), not a checked-in key.

Run locally:  uvicorn src.main:app --reload --port 8080
"""
from fastapi import FastAPI
from pydantic import BaseModel

from src.pipeline import run_query

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description=(
        "Routes research questions across a FAISS corpus of AI/ML papers (RAG) and "
        "live web search (Tavily), with a groundedness reviewer. Built on Google ADK."
    ),
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str | None
    route: str | None
    review_verdict: str | None
    metrics: dict


@app.get("/health")
def health() -> dict:
    """Liveness probe (no model calls) — used by Cloud Run / load checks."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> dict:
    """Answer a research question end-to-end through the agent pipeline."""
    return await run_query(req.question)
