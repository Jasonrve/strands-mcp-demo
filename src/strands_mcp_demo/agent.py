"""Factory for a strands Agent that uses the demo tools.

The agent is intentionally lightweight: it is ready to be pointed at any
configured Strands-compatible model provider, but the repository does not force
one specific backend.
"""

from __future__ import annotations

import os
from typing import Iterable

from strands import Agent

from .tools import build_checklist, count_cluster_pods, draft_brief, list_deployments

DEFAULT_SYSTEM_PROMPT = """You are the strands MCP demo assistant.

Use the provided tools to turn short prompts into short, useful outputs.
Keep responses grounded, concise, and practical.
"""


def build_agent(model: str | None = None, *, tools: Iterable | None = None) -> Agent:
    """Return a configured strands Agent.

    The model can be supplied explicitly or via STRANDS_DEMO_MODEL. If neither
    is present, the Agent is still constructed so the repository can document the
    integration, but the caller is responsible for choosing a runnable model
    before invoking it.
    """

    resolved_model = model or os.getenv("STRANDS_DEMO_MODEL")
    resolved_tools = list(tools) if tools is not None else [
        draft_brief,
        build_checklist,
        count_cluster_pods,
        list_deployments,
    ]
    return Agent(
        model=resolved_model,
        tools=resolved_tools,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        name="strands-mcp-demo-agent",
        description="Demo agent that turns short prompts into briefs, checklists, and cluster lookups.",
    )


def run_agent(prompt: str, model: str | None = None) -> str:
    """Invoke the agent and normalize the return value to plain text.

    This helper is used only when a model is configured. If the caller has not
    configured a runnable model, the CLI falls back to deterministic local
    output instead of failing the demo.
    """

    agent = build_agent(model=model)
    result = agent(prompt)
    structured = getattr(result, "structured_output", None)
    if structured is not None:
        return str(structured)
    message = getattr(result, "message", None)
    if message is not None:
        return str(message)
    return str(result)
