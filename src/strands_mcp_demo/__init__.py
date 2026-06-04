"""Strands MCP demo package.

The package intentionally keeps the building blocks small:
- pure helper functions for deterministic local demos
- Kubernetes-aware helpers for cluster introspection
- a strands Agent factory for real model-backed runs
- an MCP server that exposes the same tools any MCP client can load
"""

from .agent import build_agent
from .tools import build_checklist, count_cluster_pods, draft_brief, list_deployments

__all__ = ["build_agent", "draft_brief", "build_checklist", "count_cluster_pods", "list_deployments"]
__version__ = "0.1.0"
