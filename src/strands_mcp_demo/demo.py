"""Human-friendly CLI demos for the strands MCP example.

The CLI keeps the repository easy to explore without any agent runtime.
It only renders deterministic outputs from the local helper functions.
"""

from __future__ import annotations

import argparse

from .server import describe_server
from .tools import build_checklist, draft_brief


def _render_draft(topic: str, audience: str) -> str:
    return draft_brief(topic, audience).render()


def _render_checklist(goal: str, steps: int) -> str:
    return build_checklist(goal, steps)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft = subparsers.add_parser("draft", help="Create a short brief")
    draft.add_argument("topic", help="Topic to brief")
    draft.add_argument("--audience", default="the team")

    checklist = subparsers.add_parser("checklist", help="Create a short checklist")
    checklist.add_argument("goal", help="Goal to decompose")
    checklist.add_argument("--steps", type=int, default=3)

    server = subparsers.add_parser("server", help="Describe the MCP server")
    server.add_argument("--describe", action="store_true", default=True)

    args = parser.parse_args(argv)

    if args.command == "draft":
        print(_render_draft(args.topic, args.audience))
        return

    if args.command == "checklist":
        print(_render_checklist(args.goal, args.steps))
        return

    if args.command == "server":
        print(describe_server())
        return

if __name__ == "__main__":  # pragma: no cover - module entrypoint
    main()

