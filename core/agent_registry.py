"""
Agent Registry module for Multi-Agent System.

Centralized registry for discovering and managing agents.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """
    Information about a registered agent.

    Attributes:
        agent_id: Unique agent identifier
        agent_type: Type of agent (researcher, analyst, etc.)
        name: Human-readable agent name
        capabilities: List of agent capabilities
        status: Current status (idle, busy, offline)
        workload: Current workload (number of active tasks)
        total_tasks_completed: Total tasks completed
        total_tasks_failed: Total tasks failed
        registered_at: Registration timestamp
        last_active: Last activity timestamp
    """
    agent_id: str
    agent_type: str
    name: str
    capabilities: List[str]
    status: str = "idle"  # idle, busy, offline
    workload: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    registered_at: datetime = None
    last_active: datetime = None

    def __post_init__(self):
        """Set default timestamps."""
        if self.registered_at is None:
            self.registered_at = datetime.now()
        if self.last_active is None:
            self.last_active = datetime.now()

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_active = datetime.now()

    def increment_workload(self):
        """Increment workload counter."""
        self.workload += 1
        self.status = "busy"
        self.update_activity()

    def decrement_workload(self):
        """Decrement workload counter."""
        self.workload = max(0, self.workload - 1)
        if self.workload == 0:
            self.status = "idle"
        self.update_activity()

    def complete_task(self):
        """Record task completion."""
        self.total_tasks_completed += 1
        self.decrement_workload()

    def fail_task(self):
        """Record task failure."""
        self.total_tasks_failed += 1
        self.decrement_workload()

    def get_success_rate(self) -> float:
        """
        Get task success rate.

        Returns:
            Success rate (0-1)
        """
        total = self.total_tasks_completed + self.total_tasks_failed
        if total == 0:
            return 0.0
        return self.total_tasks_completed / total

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status,
            "workload": self.workload,
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "success_rate": self.get_success_rate(),
            "registered_at": self.registered_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }


class AgentRegistry:
    """
    Centralized registry for agent discovery and management.

    Features:
    - Register and unregister agents
    - Find agents by type or capabilities
    - Track agent status and workload
    - Load balancing (find least loaded agent)
    """

    def __init__(self):
        """Initialize agent registry."""
        self.agents: Dict[str, AgentInfo] = {}
        self.agents_by_type: Dict[str, Set[str]] = {}
        self.agents_by_capability: Dict[str, Set[str]] = {}

        logger.info("AgentRegistry initialized")

    def register(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        capabilities: List[str]
    ) -> AgentInfo:
        """
        Register an agent.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type
            name: Agent name
            capabilities: Agent capabilities

        Returns:
            AgentInfo object
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered, updating info")

        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name,
            capabilities=capabilities
        )

        self.agents[agent_id] = agent_info

        # Index by type
        if agent_type not in self.agents_by_type:
            self.agents_by_type[agent_type] = set()
        self.agents_by_type[agent_type].add(agent_id)

        # Index by capabilities
        for capability in capabilities:
            if capability not in self.agents_by_capability:
                self.agents_by_capability[capability] = set()
            self.agents_by_capability[capability].add(agent_id)

        logger.info(f"Agent registered: {name} ({agent_type}, ID: {agent_id[:8]}...)")

        return agent_info

    def unregister(self, agent_id: str):
        """
        Unregister an agent.

        Args:
            agent_id: Agent identifier
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not registered")
            return

        agent_info = self.agents[agent_id]

        # Remove from type index
        if agent_info.agent_type in self.agents_by_type:
            self.agents_by_type[agent_info.agent_type].discard(agent_id)

        # Remove from capability index
        for capability in agent_info.capabilities:
            if capability in self.agents_by_capability:
                self.agents_by_capability[capability].discard(agent_id)

        # Remove agent
        del self.agents[agent_id]

        logger.info(f"Agent unregistered: {agent_info.name} ({agent_id[:8]}...)")

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """
        Get agent info by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentInfo or None
        """
        return self.agents.get(agent_id)

    def find_by_type(self, agent_type: str) -> List[AgentInfo]:
        """
        Find all agents of a specific type.

        Args:
            agent_type: Agent type

        Returns:
            List of AgentInfo objects
        """
        agent_ids = self.agents_by_type.get(agent_type, set())
        return [self.agents[aid] for aid in agent_ids]

    def find_by_capability(self, capability: str) -> List[AgentInfo]:
        """
        Find all agents with a specific capability.

        Args:
            capability: Required capability

        Returns:
            List of AgentInfo objects
        """
        agent_ids = self.agents_by_capability.get(capability, set())
        return [self.agents[aid] for aid in agent_ids]

    def find_available_agent(
        self,
        agent_type: Optional[str] = None,
        capability: Optional[str] = None
    ) -> Optional[AgentInfo]:
        """
        Find an available (least loaded) agent.

        Args:
            agent_type: Required agent type (optional)
            capability: Required capability (optional)

        Returns:
            AgentInfo of least loaded agent or None
        """
        candidates = []

        if agent_type:
            candidates = self.find_by_type(agent_type)
        elif capability:
            candidates = self.find_by_capability(capability)
        else:
            candidates = list(self.agents.values())

        if not candidates:
            return None

        # Filter only idle or busy (not offline)
        candidates = [a for a in candidates if a.status in ["idle", "busy"]]

        if not candidates:
            return None

        # Return least loaded agent
        return min(candidates, key=lambda a: a.workload)

    def get_all_agents(self) -> List[AgentInfo]:
        """
        Get all registered agents.

        Returns:
            List of all AgentInfo objects
        """
        return list(self.agents.values())

    def get_agent_types(self) -> List[str]:
        """
        Get all agent types.

        Returns:
            List of agent type strings
        """
        return list(self.agents_by_type.keys())

    def get_capabilities(self) -> List[str]:
        """
        Get all capabilities across all agents.

        Returns:
            List of capability strings
        """
        return list(self.agents_by_capability.keys())

    def update_agent_status(self, agent_id: str, status: str):
        """
        Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status (idle, busy, offline)
        """
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].update_activity()
            logger.debug(f"Agent {agent_id[:8]} status updated to: {status}")

    def increment_agent_workload(self, agent_id: str):
        """
        Increment agent workload.

        Args:
            agent_id: Agent identifier
        """
        if agent_id in self.agents:
            self.agents[agent_id].increment_workload()
            logger.debug(f"Agent {agent_id[:8]} workload incremented to: {self.agents[agent_id].workload}")

    def decrement_agent_workload(self, agent_id: str):
        """
        Decrement agent workload.

        Args:
            agent_id: Agent identifier
        """
        if agent_id in self.agents:
            self.agents[agent_id].decrement_workload()
            logger.debug(f"Agent {agent_id[:8]} workload decremented to: {self.agents[agent_id].workload}")

    def record_task_completion(self, agent_id: str, success: bool = True):
        """
        Record task completion for an agent.

        Args:
            agent_id: Agent identifier
            success: Whether task was successful
        """
        if agent_id in self.agents:
            if success:
                self.agents[agent_id].complete_task()
                logger.debug(f"Agent {agent_id[:8]} completed task successfully")
            else:
                self.agents[agent_id].fail_task()
                logger.debug(f"Agent {agent_id[:8]} failed task")

    def get_statistics(self) -> Dict:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics
        """
        total_agents = len(self.agents)
        idle_agents = sum(1 for a in self.agents.values() if a.status == "idle")
        busy_agents = sum(1 for a in self.agents.values() if a.status == "busy")
        offline_agents = sum(1 for a in self.agents.values() if a.status == "offline")

        total_tasks = sum(
            a.total_tasks_completed + a.total_tasks_failed
            for a in self.agents.values()
        )
        total_completed = sum(a.total_tasks_completed for a in self.agents.values())

        return {
            "total_agents": total_agents,
            "idle_agents": idle_agents,
            "busy_agents": busy_agents,
            "offline_agents": offline_agents,
            "total_agent_types": len(self.agents_by_type),
            "total_capabilities": len(self.agents_by_capability),
            "total_tasks_processed": total_tasks,
            "total_tasks_completed": total_completed,
            "system_success_rate": total_completed / total_tasks if total_tasks > 0 else 0.0
        }

    def clear(self):
        """Clear all agents from registry."""
        self.agents.clear()
        self.agents_by_type.clear()
        self.agents_by_capability.clear()
        logger.info("AgentRegistry cleared")

    def __len__(self) -> int:
        """Number of registered agents."""
        return len(self.agents)

    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self.agents

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"AgentRegistry("
            f"agents={stats['total_agents']}, "
            f"types={stats['total_agent_types']}, "
            f"idle={stats['idle_agents']}, "
            f"busy={stats['busy_agents']})"
        )
