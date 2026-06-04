from strands_mcp_demo.server import TOOL_DESCRIPTIONS, TOOL_NAMES, build_agent_card, build_server, describe_server, resolve_public_base_url


def test_server_description_lists_tools():
    assert describe_server() == "strands-mcp-demo-mcp: tools=draft_brief, build_checklist, count_cluster_pods, list_deployments"
    assert TOOL_NAMES == ("draft_brief", "build_checklist", "count_cluster_pods", "list_deployments")


def test_agent_card_exposes_tools_and_http_preference():
    card = build_agent_card("https://example.invalid")
    assert card["name"] == "strands-mcp-demo-mcp"
    assert card["url"] == "https://example.invalid"
    assert card["preferredTransport"] == "http"
    assert [skill["id"] for skill in card["skills"]] == [
        "draft_brief",
        "build_checklist",
        "count_cluster_pods",
        "list_deployments",
    ]


def test_server_registers_kagent_agent_card_alias(monkeypatch):
    routes = []

    def fake_custom_route(self, path, methods=None):
        routes.append((path, tuple(methods or [])))

        def decorator(fn):
            return fn

        return decorator

    monkeypatch.setattr("mcp.server.fastmcp.FastMCP.custom_route", fake_custom_route)

    build_server()

    assert ("/agent-card.json", ("GET",)) in routes


def test_resolve_public_base_url_prefers_env_override(monkeypatch):
    monkeypatch.setenv("STRANDS_MCP_DEMO_PUBLIC_URL", "https://demo.example")
    request = type("Req", (), {"base_url": "https://fallback.invalid/"})()
    assert resolve_public_base_url(request) == "https://demo.example"  # type: ignore[arg-type]


def test_server_registers_tool_descriptions_explicitly(monkeypatch):
    registrations = []

    def fake_tool(self, *args, **kwargs):
        registrations.append(kwargs)

        def decorator(fn):
            return fn

        return decorator

    monkeypatch.setattr("mcp.server.fastmcp.FastMCP.tool", fake_tool)

    build_server()

    assert registrations == [
        {"name": "draft_brief", "description": TOOL_DESCRIPTIONS["draft_brief"]},
        {"name": "build_checklist", "description": TOOL_DESCRIPTIONS["build_checklist"]},
        {"name": "count_cluster_pods", "description": TOOL_DESCRIPTIONS["count_cluster_pods"]},
        {"name": "list_deployments", "description": TOOL_DESCRIPTIONS["list_deployments"]},
    ]
