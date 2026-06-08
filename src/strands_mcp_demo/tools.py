"""Demo helpers shared by the CLI and MCP server.

The text-generation helpers are deterministic so the repository can be tested
without an external model. The cluster-introspection helpers talk to the active
Kubernetes context so the MCP surface shows a couple of realistic tools too.
"""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import wrap

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


@dataclass(frozen=True)
class DemoSummary:
    """A tiny structured shape that keeps tool output predictable."""

    title: str
    bullets: tuple[str, ...]

    def render(self) -> str:
        lines = [f"{self.title}"]
        for bullet in self.bullets:
            lines.append(f"- {bullet}")
        return "\n".join(lines)


def draft_brief(topic: str, audience: str = "the team") -> DemoSummary:
    """Turn a topic into a short, human-friendly brief.

    The function is deterministic on purpose: it is easy to test and serves as a
    concrete example of a strands tool that can be exposed over MCP.
    """

    trimmed = topic.strip() or "the demo"
    title = f"Brief for {audience}: {trimmed}"
    bullets = (
        f"Goal: explain {trimmed} in plain language.",
        "Keep the tone practical and concise.",
        "End with one clear next action.",
    )
    return DemoSummary(title=title, bullets=bullets)


def build_checklist(goal: str, steps: int = 3) -> str:
    """Create a numbered action checklist from a goal."""

    trimmed = goal.strip() or "finish the demo"
    steps = max(1, min(steps, 6))
    lines = [f"Checklist for: {trimmed}"]
    for index in range(1, steps + 1):
        lines.append(f"{index}. Move {trimmed} one step closer.")
    return "\n".join(lines)


def snippet(text: str, width: int = 72) -> str:
    """Wrap long text for the README and CLI output."""

    return "\n".join(wrap(text, width=width))


def _load_kubernetes_clients() -> tuple[client.CoreV1Api, client.AppsV1Api]:
    """Load Kubernetes API clients for the current cluster context.

    Prefer in-cluster config for the live demo, then fall back to local kubeconfig
    for developers running the repository outside the cluster.
    """

    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api()


def count_cluster_pods() -> str:
    """Report how many pods exist in the active cluster context."""

    core_api, _ = _load_kubernetes_clients()
    pod_list = core_api.list_pod_for_all_namespaces(timeout_seconds=30)
    return f"Cluster pod count: {len(pod_list.items)}"


def list_deployments(namespace: str) -> str:
    """List deployments in the requested namespace."""

    target_namespace = namespace.strip() or "default"
    _, apps_api = _load_kubernetes_clients()
    deployment_list = apps_api.list_namespaced_deployment(
        namespace=target_namespace,
        timeout_seconds=30,
    )
    names = sorted(
        deployment.metadata.name
        for deployment in deployment_list.items
        if getattr(deployment, "metadata", None) and getattr(deployment.metadata, "name", None)
    )
    rendered = "\n".join(f"- {name}" for name in names) if names else "- none"
    return f"Deployments in namespace {target_namespace} ({len(names)}):\n{rendered}"
