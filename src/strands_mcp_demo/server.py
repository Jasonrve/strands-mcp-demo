"""MCP server for the demo.

The server exposes the same deterministic helpers that power the CLI.
That makes the MCP surface easy to consume from kagent or any other MCP client.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from .tools import build_checklist, count_cluster_pods, draft_brief, list_deployments

SERVER_NAME = "strands-mcp-demo-mcp"
SERVER_PORT = 3000
TOOL_NAMES = ("draft_brief", "build_checklist", "count_cluster_pods", "list_deployments")
TOOL_DESCRIPTIONS = {
    "draft_brief": "Create a short brief for a topic.",
    "build_checklist": "Create a numbered checklist for a goal.",
    "count_cluster_pods": "Report how many pods exist in the active cluster context.",
    "list_deployments": "List deployments in the requested namespace.",
}


def build_server_card(base_url: str) -> dict:
    """Return a small MCP server card that kagent can fetch over HTTP."""

    return {
        "protocolVersion": "0.3.0",
        "name": SERVER_NAME,
        "description": "GitHub-backed strands MCP demo exposing brief, checklist, and Kubernetes introspection tools.",
        "url": base_url,
        "version": "0.1.0",
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "skills": [
            {
                "id": "draft_brief",
                "name": "Draft Brief",
                "description": TOOL_DESCRIPTIONS["draft_brief"],
                "tags": ["brief", "summary"],
                "examples": ["Draft a brief about the MCP demo"],
                "inputModes": ["text"],
                "outputModes": ["text"],
                "security": [],
            },
            {
                "id": "build_checklist",
                "name": "Build Checklist",
                "description": TOOL_DESCRIPTIONS["build_checklist"],
                "tags": ["checklist", "planning"],
                "examples": ["Build a checklist for loading the demo in kagent"],
                "inputModes": ["text"],
                "outputModes": ["text"],
                "security": [],
            },
            {
                "id": "count_cluster_pods",
                "name": "Count Cluster Pods",
                "description": TOOL_DESCRIPTIONS["count_cluster_pods"],
                "tags": ["kubernetes", "cluster", "pods"],
                "examples": ["How many pods are running in the current cluster?"],
                "inputModes": ["text"],
                "outputModes": ["text"],
                "security": [],
            },
            {
                "id": "list_deployments",
                "name": "List Deployments",
                "description": TOOL_DESCRIPTIONS["list_deployments"],
                "tags": ["kubernetes", "cluster", "deployments"],
                "examples": ["List deployments in the kube-system namespace"],
                "inputModes": ["text"],
                "outputModes": ["text"],
                "security": [],
            },
        ],
        "capabilities": {"streaming": True},
        "securitySchemes": {},
        "security": [],
        "supportsAuthenticatedExtendedCard": True,
        "preferredTransport": "http",
    }


def resolve_public_base_url(request: Request) -> str:
    """Return the canonical public URL for the demo server.

    When kagent fetches the card through a proxy, ``request.base_url`` can point
    at the proxy origin instead of the service's own address. An explicit env
    override keeps the advertised card URL stable so downstream discovery can
    reach the server directly.
    """

    return os.getenv("STRANDS_MCP_DEMO_PUBLIC_URL", str(request.base_url).rstrip("/"))


def build_server() -> FastMCP:
    server = FastMCP(
        name=SERVER_NAME,
        instructions=(
            "A minimal strands MCP demo exposing two deterministic text tools and "
            "two Kubernetes introspection tools: draft_brief, build_checklist, "
            "count_cluster_pods, and list_deployments."
        ),
        host="0.0.0.0",
        port=SERVER_PORT,
    )

    @server.tool(name="draft_brief", description=TOOL_DESCRIPTIONS["draft_brief"])
    def draft_brief_tool(topic: str, audience: str = "the team") -> str:
        """Create a short brief for a topic."""

        return draft_brief(topic, audience).render()

    @server.tool(name="build_checklist", description=TOOL_DESCRIPTIONS["build_checklist"])
    def build_checklist_tool(goal: str, steps: int = 3) -> str:
        """Create a numbered checklist for a goal."""

        return build_checklist(goal, steps)

    @server.tool(name="count_cluster_pods", description=TOOL_DESCRIPTIONS["count_cluster_pods"])
    def count_cluster_pods_tool() -> str:
        """Report how many pods exist in the active cluster context."""

        return count_cluster_pods()

    @server.tool(name="list_deployments", description=TOOL_DESCRIPTIONS["list_deployments"])
    def list_deployments_tool(namespace: str) -> str:
        """List deployments in the requested namespace."""

        return list_deployments(namespace)

    @server.custom_route("/", methods=["GET"])
    async def root_route(request: Request) -> JSONResponse:
        base_url = resolve_public_base_url(request)
        return JSONResponse(build_server_card(base_url))

    @server.custom_route("/health", methods=["GET"])
    async def health_route(request: Request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    @server.custom_route("/.well-known/agent-card.json", methods=["GET"])
    async def agent_card_route(request: Request) -> JSONResponse:
        base_url = resolve_public_base_url(request)
        return JSONResponse(build_server_card(base_url))

    @server.custom_route("/agent-card.json", methods=["GET"])
    async def legacy_agent_card_route(request: Request) -> JSONResponse:
        base_url = resolve_public_base_url(request)
        return JSONResponse(build_server_card(base_url))

    @server.custom_route("/agent.json", methods=["GET"])
    async def agent_json_route(request: Request) -> JSONResponse:
        base_url = resolve_public_base_url(request)
        return JSONResponse(build_server_card(base_url))

    return server


def describe_server() -> str:
    return f"{SERVER_NAME}: tools={', '.join(TOOL_NAMES)}"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the server name and tool list instead of starting MCP.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default="stdio",
        help="MCP transport to use when launching the server.",
    )
    args = parser.parse_args(argv)

    if args.describe:
        print(describe_server())
        return

    build_server().run(transport=args.transport)


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    main()
