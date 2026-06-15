"""Reusable request/response core: run one question through the agent pipeline.

The CLI (`src/cli.py`) streams events live for the demo; this module is the
collect-and-return path that the FastAPI app and the Streamlit UI share. It runs
the same `root_agent`, then returns the answer plus the route, the reviewer
verdict, and the observability metrics.
"""
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.agents import root_agent
from src.config import DRAFT_ANSWER, QUERY_TYPE, REVIEW_VERDICT
from src.observability import ObservabilityPlugin

load_dotenv()

APP_NAME = "research-assistant"
USER_ID = "api"


async def run_query(question: str, session_id: str = "api") -> dict:
    """Answer one question end-to-end and return a structured result."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )
    obs = ObservabilityPlugin(persist=False)  # no per-request trace files when serving
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        plugins=[obs],
    )

    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for _ in runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=message
    ):
        pass  # we read the result from session state, not the event stream

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )
    state = session.state
    return {
        "question": question,
        "answer": state.get(DRAFT_ANSWER),
        "route": state.get(QUERY_TYPE),
        "review_verdict": state.get(REVIEW_VERDICT),
        "metrics": obs.metrics,
    }
