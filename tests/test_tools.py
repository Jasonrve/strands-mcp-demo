from types import SimpleNamespace

from strands_mcp_demo.tools import build_checklist, count_cluster_pods, draft_brief, list_deployments


def test_draft_brief_renders_expected_sections():
    summary = draft_brief("MCP demo", "MCP client")
    rendered = summary.render()
    assert "Brief for MCP client: MCP demo" in rendered
    assert "- Goal: explain MCP demo in plain language." in rendered
    assert "- End with one clear next action." in rendered


def test_build_checklist_caps_steps_and_includes_goal():
    rendered = build_checklist("load kagent", steps=10)
    assert rendered.startswith("Checklist for: load kagent")
    assert rendered.count("\n") == 6  # title + 6 numbered items
    assert "1. Move load kagent one step closer." in rendered


def test_count_cluster_pods_reports_cluster_total(monkeypatch):
    class FakeCoreApi:
        def list_pod_for_all_namespaces(self, *_args, **_kwargs):
            return SimpleNamespace(items=[object(), object(), object()])

    monkeypatch.setattr(
        "strands_mcp_demo.tools._load_kubernetes_clients",
        lambda: (FakeCoreApi(), object()),
    )

    assert count_cluster_pods() == "Cluster pod count: 3"


def test_list_deployments_formats_namespace_results(monkeypatch):
    class FakeAppsApi:
        def list_namespaced_deployment(self, namespace, *_args, **_kwargs):
            assert namespace == "payments"
            deployments = [
                SimpleNamespace(metadata=SimpleNamespace(name="api")),
                SimpleNamespace(metadata=SimpleNamespace(name="worker")),
            ]
            return SimpleNamespace(items=deployments)

    monkeypatch.setattr(
        "strands_mcp_demo.tools._load_kubernetes_clients",
        lambda: (object(), FakeAppsApi()),
    )

    rendered = list_deployments("payments")
    assert rendered == "Deployments in namespace payments (2):\n- api\n- worker"
