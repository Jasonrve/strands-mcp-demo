# strands-mcp-demo

A small demo repo that keeps the two concepts separate:

- **`server/`** — the MCP server, its Helm chart, and the container image used by the server deployment
- **`agent/`** — the repo-backed kagent Agent Helm chart
- **`src/strands_mcp_demo/`** — the shared Python package used by the CLI, agent factory, and MCP server

The repository now treats the server and the agent as distinct deployment units, while still sharing the same deterministic helper code.

## Repository layout

```text
.
├── agent/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/agent.yaml
├── server/
│   ├── Chart.yaml
│   ├── Dockerfile
│   ├── values.yaml
│   └── templates/
│       ├── mcpserver.yaml
│       ├── rbac.yaml
│       ├── serviceaccount.yaml
│       └── toolservers.yaml
├── src/strands_mcp_demo/
├── tests/
└── .github/workflows/
```

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Run the deterministic demo CLI:

```bash
python -m strands_mcp_demo.demo draft "launching the MCP demo" --audience "MCP client users"
python -m strands_mcp_demo.demo checklist "load the MCP server in kagent"
```

Start the MCP server locally:

```bash
python -m strands_mcp_demo.server --transport streamable-http
```

## Docker image

The server image lives in `server/Dockerfile` and is what the container release workflow publishes to GHCR.

Build it locally:

```bash
docker build -f server/Dockerfile -t strands-mcp-demo-server:local .
```

Run it:

```bash
docker run --rm -p 3000:3000 strands-mcp-demo-server:local
```

## Helm charts

The repo ships two Helm charts:

- `server/` — installs the `MCPServer`, ServiceAccount, RBAC, and ToolServer records
- `agent/` — installs the repo-backed `Agent` resource that points at the MCP server

Example install commands:

```bash
helm install strands-mcp-demo-server ./server -n kagent --create-namespace
helm install strands-mcp-demo-agent ./agent -n kagent --create-namespace
```

The default values assume the server image is published to:

```text
ghcr.io/jasonrve/strands-mcp-demo-server
```

## GitHub workflows

The repo includes four workflows:

- `ci.yml` — Python tests plus `helm lint` for both charts
- `container-release.yml` — builds and pushes the server image to GHCR for version tags
- `helm-release.yml` — packages both charts and uploads them to the GitHub release assets for version tags
- `deploy-olympus.yml` — deploys both charts into the `kagent` namespace on Olympus, and clears older demo releases first

Olympus deployment expects a base64-encoded kubeconfig secret named `OLYMPUS_KUBECONFIG_B64` in GitHub Actions.

## Notes

- The Kubernetes helpers read the active cluster context, so the demo works best where kubeconfig or in-cluster config is available.
- The repo keeps the MCP server and agent concepts separate at the folder level while preserving a single shared Python package.
- The Git history should now be authored by Jason <jasonrve@gmail.com>.
