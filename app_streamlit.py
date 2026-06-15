"""Thin Streamlit chat UI for the demo video.

Calls the FastAPI /ask endpoint (default http://localhost:8080; override with the
API_URL env var to point at the deployed Cloud Run service). Shows the chosen route,
the cited answer, the reviewer verdict, and the run metrics.

Run (API must be up):
    API_URL=http://localhost:8080 streamlit run app_streamlit.py
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")

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

question = st.text_input(
    "Ask a research question",
    placeholder="How has retrieval-augmented generation evolved since the original RAG paper?",
)

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Researching..."):
        try:
            resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=240)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            st.error(f"Request to {API_URL}/ask failed: {exc}")
            st.stop()

    st.markdown(f"**Route chosen:** `{data.get('route')}`")
    st.markdown(data.get("answer") or "_(no answer produced)_")
    with st.expander("Reviewer verdict + run metrics"):
        st.write(data.get("review_verdict"))
        st.json(data.get("metrics", {}))
