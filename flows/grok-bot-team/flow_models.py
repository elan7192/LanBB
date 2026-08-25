"""Minimal FlowGraph schema matching semantica.flow.models (n8n-style).

Vendored so this LanBB artifact can be rebuilt without importing the
semantica submodule (upstream pin does not ship semantica.flow).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class FlowPort:
    id: str
    label: str
    direction: str = "output"
    data_type: str = "any"


@dataclass
class FlowNode:
    id: str
    type: str
    label: str
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    status: str = "idle"
    category: str = "general"
    description: str = ""
    ports: List[FlowPort] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class FlowEdge:
    id: str
    source: str
    target: str
    source_port: str = "out"
    target_port: str = "in"
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlowGraph:
    id: str
    name: str
    description: str = ""
    nodes: List[FlowNode] = field(default_factory=list)
    edges: List[FlowEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": self.metadata,
            "version": self.version,
        }

    @classmethod
    def new_id(cls, prefix: str = "flow") -> str:
        return f"{prefix}_{uuid4().hex[:8]}"
