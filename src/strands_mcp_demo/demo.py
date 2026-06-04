"""Human-friendly CLI demos for the strands MCP example.

The CLI keeps the repository easy to explore without model credentials. It can
run fully deterministic examples or, when STRANDS_DEMO_MODEL is set, forward the
same prompt through a real strands Agent.
"""

from __future__ import annotations

import argparse
import os
from typing import Callable

from .agent import run_agent
from .tools import build_checklist, draft_brief


def _render_draft(topic: str, audience: str, use_agent: bool) -> str:
    if use_agent and os.getenv("STRANDS_DEMO_MODEL"):
        return run_agent(f"Draft a brief for {audience}: {topic}")
    return draft_brief(topic, audience).render()


def _render_checklist(goal: str, steps: int, use_agent: bool) -> str:
    if use_agent and os.getenv("STRANDS_DEMO_MODEL"):
        return run_agent(f"Build a checklist for: {goal}")
    return build_checklist(goal, steps)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft = subparsers.add_parser("draft", help="Create a short brief")
    draft.add_argument("topic", help="Topic to brief")
    draft.add_argument("--audience", default="the team")
    draft.add_argument("--use-agent", action="store_true")

    checklist = subparsers.add_parser("checklist", help="Create a short checklist")
    checklist.add_argument("goal", help="Goal to decompose")
    checklist.add_argument("--steps", type=int, default=3)
    checklist.add_argument("--use-agent", action="store_true")

    server = subparsers.add_parser("server", help="Describe the MCP server")
    server.add_argument("--describe", action="store_true", default=True)

    args = parser.parse_args(argv)

    if args.command == "draft":
        print(_render_draft(args.topic, args.audience, args.use_agent))
        return

    if args.command == "checklist":
        print(_render_checklist(args.goal, args.steps, args.use_agent))
        return

    if args.command == "server":
        from .server import describe_server

        print(describe_server())
        return


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    main()
