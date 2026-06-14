"""The multi-agent Research Assistant package.

Re-exports `root_agent` so callers can `from src.agents import root_agent`, and
keeps the `agent` submodule importable for ADK's `adk web` / `adk run` discovery.
"""
from .agent import root_agent

__all__ = ["root_agent"]
