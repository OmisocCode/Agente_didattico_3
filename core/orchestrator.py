"""
Orchestrator module for Multi-Agent System.

Central orchestrator that coordinates task execution, agent assignment,
and result aggregation.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from core.task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from core.dependency_graph import DependencyGraph
from core.agent_registry import AgentRegistry
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central orchestrator for the multi-agent system.

    Responsibilities:
    - Task management and scheduling
    - Agent discovery and assignment
    - Dependency resolution
    - Result aggregation
    - System monitoring

    Components:
    - TaskQueue: Manages task scheduling and prioritization
    - DependencyGraph: Tracks task dependencies
    - AgentRegistry: Manages agent discovery and load balancing
    - MessageBus: Facilitates agent communication
    - SharedMemory: Shared data store
    """

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        shared_memory: Optional[SharedMemory] = None
    ):
        """
        Initialize orchestrator.

        Args:
            message_bus: MessageBus instance (creates new if None)
            shared_memory: SharedMemory instance (creates new if None)
        """
        self.task_queue = TaskQueue()
        self.dependency_graph = DependencyGraph()
        self.agent_registry = AgentRegistry()
        self.message_bus = message_bus or MessageBus()
        self.shared_memory = shared_memory or SharedMemory()

        # Execution state
        self.running = False

        logger.info("Orchestrator initialized")

    def register_agent(self, agent: BaseAgent):
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent instance to register
        """
        # Register with agent registry
        self.agent_registry.register(
            agent_id=agent.agent_id,
            agent_type=agent.name,
            name=agent.name,
            capabilities=agent.capabilities
        )

        # Connect agent to infrastructure
        agent.message_bus = self.message_bus
        agent.shared_memory = self.shared_memory

        # Register with message bus
        self.message_bus.register_agent(agent.agent_id)

        logger.info(f"Agent registered with orchestrator: {agent.name}")

    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent.

        Args:
            agent_id: Agent identifier
        """
        self.agent_registry.unregister(agent_id)
        self.message_bus.unregister_agent(agent_id)

        logger.info(f"Agent unregistered: {agent_id[:8]}")

    def add_task(
        self,
        agent_type: str,
        action: str,
        input_data: Any = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Add a task to the queue.

        Args:
            agent_type: Type of agent required
            action: Action to perform
            input_data: Input data for the task
            priority: Task priority
            dependencies: List of task IDs this task depends on
            metadata: Additional metadata

        Returns:
            Created Task object
        """
        # Add to task queue
        task = self.task_queue.add_task(
            agent_type=agent_type,
            action=action,
            input_data=input_data,
            priority=priority,
            dependencies=dependencies,
            metadata=metadata
        )

        # Add to dependency graph
        self.dependency_graph.add_node(task.task_id)
        for dep_id in (dependencies or []):
            self.dependency_graph.add_dependency(task.task_id, dep_id)

        logger.info(f"Task added: {task.task_id[:8]} (type: {agent_type}, action: {action})")

        return task

    def execute_task(self, task: Task) -> bool:
        """
        Execute a single task.

        Args:
            task: Task to execute

        Returns:
            True if task was executed successfully
        """
        # Find available agent
        agent_info = self.agent_registry.find_available_agent(agent_type=task.agent_type)

        if not agent_info:
            logger.warning(f"No available agent found for task {task.task_id[:8]} (type: {task.agent_type})")
            return False

        logger.info(f"Assigning task {task.task_id[:8]} to agent {agent_info.name}")

        # Update agent workload
        self.agent_registry.increment_agent_workload(agent_info.agent_id)

        # Store task in shared memory
        self.shared_memory.write(f"task_{task.task_id}", task.to_dict(), "orchestrator")

        # Send task to agent via message bus
        from agents.base_agent import Message
        message = Message(
            sender="orchestrator",
            receiver=agent_info.agent_id,
            msg_type="task",
            content={
                "task_id": task.task_id,
                "action": task.action,
                "input_data": task.input_data,
                "metadata": task.metadata
            }
        )

        self.message_bus.send(message)

        # Wait for response (with timeout)
        response = self.message_bus.receive("orchestrator", timeout=task.metadata.get("timeout", 60))

        if response and response.msg_type == "result":
            # Task completed successfully
            result = response.content
            self.task_queue.complete_task(task.task_id, result)
            self.agent_registry.record_task_completion(agent_info.agent_id, success=True)

            # Store result in shared memory
            self.shared_memory.write(f"result_{task.task_id}", result, agent_info.agent_id)

            logger.info(f"Task {task.task_id[:8]} completed successfully")
            return True

        else:
            # Task failed or timed out
            error = "Agent did not respond in time" if not response else "Unexpected response"
            self.task_queue.fail_task(task.task_id, error)
            self.agent_registry.record_task_completion(agent_info.agent_id, success=False)

            logger.error(f"Task {task.task_id[:8]} failed: {error}")
            return False

    def execute_all(self, max_iterations: int = 100) -> Dict[str, Any]:
        """
        Execute all tasks in the queue.

        Args:
            max_iterations: Maximum iterations to prevent infinite loops

        Returns:
            Execution summary
        """
        logger.info("Starting task execution...")

        iteration = 0
        results = {
            "total_tasks": len(self.task_queue.tasks),
            "completed": [],
            "failed": [],
            "cancelled": []
        }

        while iteration < max_iterations:
            iteration += 1

            # Get next task
            task = self.task_queue.get_next_task(timeout=1)

            if not task:
                # No more tasks available
                # Check if there are pending tasks blocked by dependencies
                pending_count = len(self.task_queue.pending)
                if pending_count == 0:
                    break
                else:
                    logger.debug(f"{pending_count} tasks still pending (blocked by dependencies)")
                    continue

            # Execute task
            success = self.execute_task(task)

            if success:
                results["completed"].append(task.task_id)
            else:
                results["failed"].append(task.task_id)

        # Add any cancelled/unexecuted tasks
        results["cancelled"] = list(self.task_queue.pending)

        logger.info(
            f"Execution completed: "
            f"{len(results['completed'])} succeeded, "
            f"{len(results['failed'])} failed, "
            f"{len(results['cancelled'])} cancelled"
        )

        return results

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """
        Get result of a completed task.

        Args:
            task_id: Task identifier

        Returns:
            Task result or None
        """
        task = self.task_queue.get_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result

        # Try shared memory
        return self.shared_memory.read(f"result_{task_id}")

    def get_execution_plan(self) -> List[List[str]]:
        """
        Get execution plan (tasks grouped by execution layers).

        Returns:
            List of execution layers
        """
        return self.dependency_graph.get_execution_layers()

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.

        Returns:
            Dictionary with system status
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_running": self.running,
            "task_queue": self.task_queue.get_statistics(),
            "agent_registry": self.agent_registry.get_statistics(),
            "message_bus": self.message_bus.get_statistics(),
            "shared_memory": self.shared_memory.get_statistics(),
            "dependency_graph": self.dependency_graph.get_statistics()
        }

    def reset(self):
        """Reset orchestrator state."""
        self.task_queue.clear()
        self.dependency_graph.clear()
        # Note: Don't clear agent_registry as agents may still be registered

        logger.info("Orchestrator reset")

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_system_status()
        return (
            f"Orchestrator("
            f"agents={stats['agent_registry']['total_agents']}, "
            f"tasks={stats['task_queue']['total_tasks']}, "
            f"pending={stats['task_queue']['pending_tasks']})"
        )
