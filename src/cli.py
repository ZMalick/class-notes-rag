"""CLI harness to run the multi-agent Research Assistant end-to-end.

Usage (from project root; force UTF-8 so paper math symbols don't crash cp1252):
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m src.cli "your question"

It streams the ADK event trace as the agents collaborate — the route decision,
each tool call, the reviewer verdict — then prints the final cited answer (read
from session state, since the pipeline's literal last message is the QA verdict).
This runner is also the seam Phase 4 (observability) and Phase 5 (FastAPI) reuse.
"""
import asyncio
import sys

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.agents import root_agent
from src.config import DRAFT_ANSWER, QUERY_TYPE, REVIEW_VERDICT

load_dotenv()

APP_NAME = "research-assistant"
USER_ID = "local"
SESSION_ID = "cli"


def _print_parts(author: str, event) -> None:
    """Render one event's parts as a readable trace line."""
    if not event.content or not event.content.parts:
        return
    for part in event.content.parts:
        if part.function_call:
            args = dict(part.function_call.args or {})
            print(f"  [{author}] -> tool {part.function_call.name}({args})")
        elif part.function_response:
            print(f"  [{author}] <- {part.function_response.name} returned")
        elif part.text and part.text.strip():
            print(f"  [{author}] {part.text.strip()}")


async def ask(question: str) -> dict:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )

    message = types.Content(role="user", parts=[types.Part(text=question)])
    print(f"\n=== QUESTION: {question}\n--- trace ---")
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        _print_parts(event.author, event)

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    state = session.state
    print("\n--- session state ---")
    print(f"  route ({QUERY_TYPE}): {state.get(QUERY_TYPE)!r}")
    print(f"  {REVIEW_VERDICT}: {state.get(REVIEW_VERDICT)!r}")
    print("\n=== ANSWER ===")
    print(state.get(DRAFT_ANSWER, "(no answer produced)"))
    return dict(state)


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is scaled dot-product attention?"
    asyncio.run(ask(q))
