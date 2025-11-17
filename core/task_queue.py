"""
Task Queue module for Multi-Agent System.

Manages task scheduling, prioritization, and execution tracking.
"""

import uuid
import logging
from datetime import datetime
from enum import Enum
from queue import PriorityQueue, Empty
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0


@dataclass(order=True)
class Task:
    """
    Task representation for the multi-agent system.

    Attributes:
        priority: Task priority (lower number = higher priority)
        task_id: Unique task identifier
        agent_type: Type of agent required for this task
        action: Action to perform
        input_data: Input data for the task
        dependencies: List of task IDs this task depends on
        metadata: Additional metadata
        status: Current task status
        created_at: Task creation timestamp
        started_at: Task start timestamp
        completed_at: Task completion timestamp
        result: Task execution result
        error: Error message if task failed
    """
    priority: int = field(compare=True)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    agent_type: str = field(default="", compare=False)
    action: str = field(default="", compare=False)
    input_data: Any = field(default=None, compare=False)
    dependencies: List[str] = field(default_factory=list, compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    started_at: Optional[datetime] = field(default=None, compare=False)
    completed_at: Optional[datetime] = field(default=None, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)

    def __post_init__(self):
        """Post-initialization to ensure priority is an integer."""
        if isinstance(self.priority, TaskPriority):
            self.priority = self.priority.value

    def start(self):
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        logger.debug(f"Task {self.task_id[:8]} started")

    def complete(self, result: Any):
        """Mark task as completed with result."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        logger.debug(f"Task {self.task_id[:8]} completed")

    def fail(self, error: str):
        """Mark task as failed with error."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        logger.error(f"Task {self.task_id[:8]} failed: {error}")

    def cancel(self):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        logger.debug(f"Task {self.task_id[:8]} cancelled")

    def get_duration(self) -> Optional[float]:
        """Get task execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "action": self.action,
            "priority": self.priority,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.get_duration(),
            "metadata": self.metadata
        }


class TaskQueue:
    """
    Priority-based task queue with dependency tracking.

    Features:
    - Priority-based scheduling
    - Dependency management
    - Task status tracking
    - Statistics and monitoring
    """

    def __init__(self):
        """Initialize task queue."""
        self.queue = PriorityQueue()
        self.tasks: Dict[str, Task] = {}  # All tasks by ID
        self.pending: Set[str] = set()  # Pending task IDs
        self.in_progress: Set[str] = set()  # In-progress task IDs
        self.completed: Set[str] = set()  # Completed task IDs
        self.failed: Set[str] = set()  # Failed task IDs

        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
        }

        logger.info("TaskQueue initialized")

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
        Add a new task to the queue.

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
        task = Task(
            priority=priority.value if isinstance(priority, TaskPriority) else priority,
            agent_type=agent_type,
            action=action,
            input_data=input_data,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )

        self.tasks[task.task_id] = task
        self.pending.add(task.task_id)
        self.stats["total_tasks"] += 1

        # Add to priority queue if no dependencies or all satisfied
        if self._can_execute(task):
            self.queue.put(task)
            logger.info(f"Task {task.task_id[:8]} added to queue (priority: {task.priority})")
        else:
            logger.info(f"Task {task.task_id[:8]} added but blocked by dependencies")

        return task

    def get_next_task(self, timeout: Optional[int] = None) -> Optional[Task]:
        """
        Get next task from queue.

        Args:
            timeout: Maximum time to wait for a task (None = blocking)

        Returns:
            Next task or None if timeout/empty
        """
        try:
            task = self.queue.get(timeout=timeout)

            # Update status
            self.pending.discard(task.task_id)
            self.in_progress.add(task.task_id)
            task.start()

            logger.info(f"Task {task.task_id[:8]} retrieved from queue")
            return task

        except Empty:
            return None

    def complete_task(self, task_id: str, result: Any):
        """
        Mark task as completed.

        Args:
            task_id: Task ID
            result: Task result
        """
        if task_id not in self.tasks:
            logger.warning(f"Unknown task ID: {task_id}")
            return

        task = self.tasks[task_id]
        task.complete(result)

        self.in_progress.discard(task_id)
        self.completed.add(task_id)
        self.stats["completed_tasks"] += 1

        # Check if any dependent tasks can now be executed
        self._check_dependent_tasks(task_id)

        logger.info(f"Task {task_id[:8]} marked as completed")

    def fail_task(self, task_id: str, error: str):
        """
        Mark task as failed.

        Args:
            task_id: Task ID
            error: Error message
        """
        if task_id not in self.tasks:
            logger.warning(f"Unknown task ID: {task_id}")
            return

        task = self.tasks[task_id]
        task.fail(error)

        self.in_progress.discard(task_id)
        self.failed.add(task_id)
        self.stats["failed_tasks"] += 1

        logger.error(f"Task {task_id[:8]} marked as failed: {error}")

    def cancel_task(self, task_id: str):
        """
        Cancel a task.

        Args:
            task_id: Task ID
        """
        if task_id not in self.tasks:
            logger.warning(f"Unknown task ID: {task_id}")
            return

        task = self.tasks[task_id]
        task.cancel()

        self.pending.discard(task_id)
        self.in_progress.discard(task_id)
        self.stats["cancelled_tasks"] += 1

        logger.info(f"Task {task_id[:8]} cancelled")

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get all tasks with specific status.

        Args:
            status: Task status

        Returns:
            List of tasks
        """
        return [t for t in self.tasks.values() if t.status == status]

    def get_tasks_by_agent_type(self, agent_type: str) -> List[Task]:
        """
        Get all tasks for specific agent type.

        Args:
            agent_type: Agent type

        Returns:
            List of tasks
        """
        return [t for t in self.tasks.values() if t.agent_type == agent_type]

    def _can_execute(self, task: Task) -> bool:
        """
        Check if task can be executed (all dependencies completed).

        Args:
            task: Task to check

        Returns:
            True if task can be executed
        """
        if not task.dependencies:
            return True

        return all(dep_id in self.completed for dep_id in task.dependencies)

    def _check_dependent_tasks(self, completed_task_id: str):
        """
        Check if any pending tasks can now be executed.

        Args:
            completed_task_id: ID of completed task
        """
        for task_id in list(self.pending):
            task = self.tasks[task_id]
            if completed_task_id in task.dependencies and self._can_execute(task):
                self.queue.put(task)
                logger.info(f"Task {task_id[:8]} unblocked and added to queue")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get queue statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "pending_tasks": len(self.pending),
            "in_progress_tasks": len(self.in_progress),
            "queue_size": self.queue.qsize(),
            "success_rate": (
                self.stats["completed_tasks"] / self.stats["total_tasks"]
                if self.stats["total_tasks"] > 0 else 0.0
            )
        }

    def clear(self):
        """Clear all tasks from queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except Empty:
                break

        self.tasks.clear()
        self.pending.clear()
        self.in_progress.clear()
        self.completed.clear()
        self.failed.clear()

        logger.info("TaskQueue cleared")

    def __len__(self) -> int:
        """Number of tasks in queue."""
        return self.queue.qsize()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TaskQueue("
            f"pending={len(self.pending)}, "
            f"in_progress={len(self.in_progress)}, "
            f"completed={len(self.completed)}, "
            f"failed={len(self.failed)})"
        )
