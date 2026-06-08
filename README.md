# strands-mcp-demo

A small demo repo focused on the MCP offering in `src/strands_mcp_demo`.

- `src/strands_mcp_demo/` — deterministic helper tools plus the MCP server surface
- `server/` — the MCP server Helm chart and container image
- `agent/` — the repo-root home for agent-specific work and the kagent Agent chart

The Python package is MCP-only: it exposes deterministic helper tools and the MCP server surface, but no agent factory or agent runtime.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Local demo

Run the deterministic examples without any model credentials:

```bash
python -m strands_mcp_demo.demo draft "launching the MCP demo" --audience "MCP client users"
python -m strands_mcp_demo.demo checklist "load the MCP server in kagent"
```

## MCP server

Start the MCP server over stdio:

```bash
python -m strands_mcp_demo.server
```

For a quick sanity check without blocking on stdio, ask the server to describe itself:

```bash
python -m strands_mcp_demo.server --describe
```

The server exposes these tools:

- `draft_brief(topic, audience='the team')`
- `build_checklist(goal, steps=3)`
- `count_cluster_pods()`
- `list_deployments(namespace)`

## kagent / MCP client load path

The repository includes ready-to-copy load paths:

- `kagent.mcp.json` for local MCP client configs
- `kagent.mcpserver.yaml` for the backend cluster-side MCPServer deployment (`strands-mcp-demo-mcp`)
- `kagent.mcpserver.rbac.yaml` for the backend ServiceAccount and read-only cluster RBAC
- `kagent.toolserver.yaml` plus the three capability-specific ToolServer files for the four MCP tools
- `kagent.agent.yaml` for the repo-backed kagent Agent card that points back to this GitHub repo and references the backend MCPServer
- `kagent.modelconfig.yaml` for the repo-backed OpenAI-compatible ModelConfig wired to Bifrost
- `agent/` and `server/` for the Helm charts that render the same Agent/ModelConfig and MCPServer/RBAC objects as separate Rancher catalog entries
- `helm/agents/k8s/` for the shared Helm chart scaffold used by the test suite

The cluster ends up with two distinct objects:

- `strands-mcp-demo-agent` — the kagent Agent users interact with
- `strands-mcp-demo-mcp` — the backend MCPServer that serves the four demo tools

The JSON file follows the common MCP launch shape used by standard MCP clients:

```json
{
  "mcpServers": {
    "strands-mcp-demo-mcp": {
      "command": "python",
      "args": ["-m", "strands_mcp_demo.server"],
      "cwd": "/GIT/strands-mcp-demo"
    }
  }
}
```

To use it in kagent, import or paste that stanza into the MCP server list that your kagent build reads. The important parts are the command, the repo cwd, and stdio transport.

## ToolServer inventory

`kagent.toolserver.yaml` and the three capability-specific ToolServer files together define the four ToolServer objects. Each file points at the same streamable HTTP endpoint, but the names and tool-name labels keep the deployment model aligned with the four MCP capabilities:

- `strands-mcp-demo-draft-brief` → `draft_brief`
- `strands-mcp-demo-build-checklist` → `build_checklist`
- `strands-mcp-demo-count-cluster-pods` → `count_cluster_pods`
- `strands-mcp-demo-list-deployments` → `list_deployments`

Because all four ToolServer objects point at the same MCP endpoint, any client that can query the kagent inventory can resolve the resource name it wants and then call the shared server to execute the matching tool.

## Notes

- The demo helpers are deterministic so the repository can be tested without an external model.
- The Kubernetes helpers talk to the active cluster context, so they work best when the server runs in a cluster or with a configured local kubeconfig.
- `kagent.mcp.json` is the concrete load-path artifact you can copy into a client config.
