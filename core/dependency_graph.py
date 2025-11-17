"""
Dependency Graph module for Multi-Agent System.

Manages task dependencies and determines execution order.
"""

import logging
from typing import Dict, List, Set, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected."""
    pass


class DependencyGraph:
    """
    Directed acyclic graph (DAG) for managing task dependencies.

    Features:
    - Add and remove dependencies
    - Topological sort for execution order
    - Circular dependency detection
    - Find ready tasks (no pending dependencies)
    """

    def __init__(self):
        """Initialize dependency graph."""
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.nodes: Set[str] = set()

        logger.info("DependencyGraph initialized")

    def add_node(self, node_id: str):
        """
        Add a node to the graph.

        Args:
            node_id: Node identifier
        """
        self.nodes.add(node_id)
        if node_id not in self.graph:
            self.graph[node_id] = set()
        if node_id not in self.reverse_graph:
            self.reverse_graph[node_id] = set()

        logger.debug(f"Node added: {node_id}")

    def add_dependency(self, node_id: str, depends_on: str):
        """
        Add dependency: node_id depends on depends_on.

        Args:
            node_id: The dependent node
            depends_on: The node it depends on

        Raises:
            CircularDependencyError: If adding this dependency creates a cycle
        """
        # Add nodes if they don't exist
        self.add_node(node_id)
        self.add_node(depends_on)

        # Check for circular dependency
        if self._would_create_cycle(node_id, depends_on):
            raise CircularDependencyError(
                f"Adding dependency {node_id} -> {depends_on} would create a cycle"
            )

        # Add dependency
        self.graph[node_id].add(depends_on)
        self.reverse_graph[depends_on].add(node_id)

        logger.debug(f"Dependency added: {node_id} depends on {depends_on}")

    def remove_dependency(self, node_id: str, depends_on: str):
        """
        Remove a dependency.

        Args:
            node_id: The dependent node
            depends_on: The node it depends on
        """
        if node_id in self.graph:
            self.graph[node_id].discard(depends_on)

        if depends_on in self.reverse_graph:
            self.reverse_graph[depends_on].discard(node_id)

        logger.debug(f"Dependency removed: {node_id} no longer depends on {depends_on}")

    def get_dependencies(self, node_id: str) -> Set[str]:
        """
        Get all dependencies for a node.

        Args:
            node_id: Node identifier

        Returns:
            Set of node IDs this node depends on
        """
        return self.graph.get(node_id, set()).copy()

    def get_dependents(self, node_id: str) -> Set[str]:
        """
        Get all nodes that depend on this node.

        Args:
            node_id: Node identifier

        Returns:
            Set of node IDs that depend on this node
        """
        return self.reverse_graph.get(node_id, set()).copy()

    def can_execute(self, node_id: str, completed: Set[str]) -> bool:
        """
        Check if a node can be executed given completed nodes.

        Args:
            node_id: Node to check
            completed: Set of completed node IDs

        Returns:
            True if all dependencies are completed
        """
        dependencies = self.graph.get(node_id, set())
        return dependencies.issubset(completed)

    def get_ready_nodes(self, completed: Set[str]) -> List[str]:
        """
        Get all nodes that can be executed now.

        Args:
            completed: Set of completed node IDs

        Returns:
            List of node IDs ready for execution
        """
        ready = []
        for node_id in self.nodes:
            if node_id not in completed and self.can_execute(node_id, completed):
                ready.append(node_id)

        return ready

    def topological_sort(self) -> List[str]:
        """
        Get topological sort of the graph (execution order).

        Returns:
            List of node IDs in execution order

        Raises:
            CircularDependencyError: If graph contains cycles
        """
        # Kahn's algorithm for topological sort
        in_degree = {node: len(self.graph[node]) for node in self.nodes}
        queue = deque([node for node in self.nodes if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Reduce in-degree for dependent nodes
            for dependent in self.reverse_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check if all nodes are in result
        if len(result) != len(self.nodes):
            raise CircularDependencyError("Graph contains a cycle")

        return result

    def _would_create_cycle(self, from_node: str, to_node: str) -> bool:
        """
        Check if adding edge from_node -> to_node would create a cycle.

        Args:
            from_node: Source node
            to_node: Target node

        Returns:
            True if it would create a cycle
        """
        # If to_node can reach from_node, adding this edge creates a cycle
        visited = set()
        queue = deque([to_node])

        while queue:
            current = queue.popleft()
            if current == from_node:
                return True

            if current in visited:
                continue

            visited.add(current)

            # Add all nodes that current depends on
            for dependency in self.graph.get(current, set()):
                queue.append(dependency)

        return False

    def has_cycle(self) -> bool:
        """
        Check if graph has a cycle.

        Returns:
            True if graph has a cycle
        """
        try:
            self.topological_sort()
            return False
        except CircularDependencyError:
            return True

    def get_execution_layers(self) -> List[List[str]]:
        """
        Get nodes grouped by execution layer.

        Nodes in the same layer can be executed in parallel.

        Returns:
            List of layers, each layer is a list of node IDs
        """
        layers = []
        completed = set()
        remaining = self.nodes.copy()

        while remaining:
            # Get nodes that can execute now
            ready = [
                node for node in remaining
                if self.can_execute(node, completed)
            ]

            if not ready:
                # Shouldn't happen unless there's a cycle
                raise CircularDependencyError("Cannot create execution layers - graph may have cycle")

            layers.append(ready)
            completed.update(ready)
            remaining -= set(ready)

        return layers

    def get_statistics(self) -> Dict[str, int]:
        """
        Get graph statistics.

        Returns:
            Dictionary with statistics
        """
        total_edges = sum(len(deps) for deps in self.graph.values())

        return {
            "total_nodes": len(self.nodes),
            "total_edges": total_edges,
            "nodes_without_dependencies": sum(
                1 for node in self.nodes if len(self.graph[node]) == 0
            ),
            "nodes_without_dependents": sum(
                1 for node in self.nodes if len(self.reverse_graph[node]) == 0
            ),
        }

    def clear(self):
        """Clear the graph."""
        self.graph.clear()
        self.reverse_graph.clear()
        self.nodes.clear()
        logger.info("DependencyGraph cleared")

    def __len__(self) -> int:
        """Number of nodes in graph."""
        return len(self.nodes)

    def __contains__(self, node_id: str) -> bool:
        """Check if node is in graph."""
        return node_id in self.nodes

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"DependencyGraph("
            f"nodes={stats['total_nodes']}, "
            f"edges={stats['total_edges']})"
        )
