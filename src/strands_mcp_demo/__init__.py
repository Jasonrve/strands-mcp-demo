"""Strands MCP demo package.

The package intentionally keeps the building blocks small:
- pure helper functions for deterministic local demos
- Kubernetes-aware helpers for cluster introspection
- an MCP server that exposes the same tools any MCP client can load
"""

from .tools import build_checklist, count_cluster_pods, draft_brief, list_deployments

__all__ = ["draft_brief", "build_checklist", "count_cluster_pods", "list_deployments"]
__version__ = "0.1.0"
