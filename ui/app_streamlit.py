"""Streamlit chat UI for the Multi-Agent Research Assistant demo.

A thin HTTP client over the FastAPI ``/ask`` endpoint. Holds no GCP credentials,
no FAISS index, and no ``src/`` code — it only POSTs questions and renders answers,
so it deploys as its own lightweight Cloud Run service.

Point it at the API with the ``API_URL`` env var (default ``http://localhost:8080``).

Run locally (API must be up):
    API_URL=http://localhost:8080 streamlit run ui/app_streamlit.py
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")
REQUEST_TIMEOUT_S = 240  # matches the API's worst-case multi-agent latency (incl. cold start)

st.set_page_config(page_title="Research Assistant")
st.title("Multi-Agent Research Assistant")
st.caption("AI/ML papers (RAG) + live web (Tavily), routed and groundedness-checked — Google ADK.")

with st.sidebar:
    st.subheader("How it works")
    st.write(
        "An Orchestrator routes each question CORPUS / WEB / BOTH; a Researcher "
        "retrieves evidence and drafts a cited answer; a Reviewer checks every "
        "claim against the retrieved sources before it's returned."
    )
    st.write("**API endpoint**")
    st.code(API_URL)
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


def render_assistant(msg: dict) -> None:
    """Render one assistant turn — used for both fresh and replayed turns.

    The structured fields (not a pre-rendered string) are stored in history so the
    route caption and the verdict/metrics expander survive every Streamlit rerun.
    """
    if msg.get("error"):
        st.error(msg["content"])
        return
    route = msg.get("route")
    if route:
        st.markdown(f"**Route chosen:** `{route}`")
    st.markdown(msg.get("content") or "_(no answer produced)_")
    with st.expander("Reviewer verdict + run metrics"):
        st.write(msg.get("verdict"))
        st.json(msg.get("metrics") or {})


# --- conversation history -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the full conversation on every rerun.
for past in st.session_state.messages:
    with st.chat_message(past["role"]):
        if past["role"] == "user":
            st.markdown(past["content"])
        else:
            render_assistant(past)

# --- new turn -------------------------------------------------------------
prompt = st.chat_input("Ask a research question…")
if prompt and prompt.strip():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching…"):
            try:
                resp = requests.post(
                    f"{API_URL}/ask",
                    json={"question": prompt},
                    timeout=REQUEST_TIMEOUT_S,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.Timeout:
                msg = {
                    "role": "assistant",
                    "error": True,
                    "content": (
                        f"The request timed out after {REQUEST_TIMEOUT_S}s. "
                        "The API may be cold-starting — please try the question again."
                    ),
                }
            except requests.exceptions.ConnectionError:
                msg = {
                    "role": "assistant",
                    "error": True,
                    "content": (
                        f"Could not reach the API at `{API_URL}`. "
                        "Check that the service is up and API_URL is correct."
                    ),
                }
            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "?"
                body = exc.response.text[:500] if exc.response is not None else ""
                msg = {
                    "role": "assistant",
                    "error": True,
                    "content": f"API returned HTTP {status}.\n\n```\n{body}\n```",
                }
            except Exception as exc:  # JSON decode, etc. — never crash the UI
                msg = {
                    "role": "assistant",
                    "error": True,
                    "content": f"Unexpected error talking to the API: {exc}",
                }
            else:
                msg = {
                    "role": "assistant",
                    "error": False,
                    "content": data.get("answer"),
                    "route": data.get("route"),
                    "verdict": data.get("review_verdict"),
                    "metrics": data.get("metrics") or {},
                }
        render_assistant(msg)

    st.session_state.messages.append(msg)
