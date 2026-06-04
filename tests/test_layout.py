from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_CHART = REPO_ROOT / "server"
AGENT_CHART = REPO_ROOT / "agent"
DEPLOY_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-olympus.yml"


def test_component_folders_contain_helm_charts():
    assert (SERVER_CHART / "Chart.yaml").exists()
    assert (SERVER_CHART / "values.yaml").exists()
    assert (SERVER_CHART / "Dockerfile").exists()
    assert (SERVER_CHART / "templates" / "mcpserver.yaml").exists()
    assert (SERVER_CHART / "templates" / "toolservers.yaml").exists()
    assert (AGENT_CHART / "Chart.yaml").exists()
    assert (AGENT_CHART / "values.yaml").exists()
    assert (AGENT_CHART / "templates" / "agent.yaml").exists()


def test_server_chart_mentions_the_release_image_and_kagent_resources():
    template = (SERVER_CHART / "templates" / "mcpserver.yaml").read_text()
    values = (SERVER_CHART / "values.yaml").read_text()
    toolserver_template = (SERVER_CHART / "templates" / "toolservers.yaml").read_text()

    assert "kind: MCPServer" in template
    assert "ghcr.io/jasonrve/strands-mcp-demo-server" in values
    assert "draft_brief" in values
    assert "list_deployments" in values
    assert "streamableHttp" in toolserver_template


def test_agent_chart_wires_the_mcp_server_tool_names():
    text = (AGENT_CHART / "templates" / "agent.yaml").read_text()
    values = (AGENT_CHART / "values.yaml").read_text()

    assert "kind: Agent" in text
    assert "MCPServer" in text
    assert "toolNames" in text
    assert "strands-mcp-demo-mcp" in values
    assert "namespace: kagent" in values


def test_olympus_deploy_workflow_targets_the_kagent_namespace_and_cleans_old_releases():
    workflow = DEPLOY_WORKFLOW.read_text()

    assert "NAMESPACE: kagent" in workflow
    assert "helm upgrade --install \"$SERVER_RELEASE\" ./server" in workflow
    assert "helm upgrade --install \"$AGENT_RELEASE\" ./agent" in workflow
    assert "helm uninstall \"$release\" -n \"$NAMESPACE\"" in workflow
    assert "OLYMPUS_KUBECONFIG_B64" in workflow
