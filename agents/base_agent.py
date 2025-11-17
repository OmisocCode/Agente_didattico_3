"""
Base Agent module for Multi-Agent System.

Defines the Message class and BaseAgent abstract class that all specialized agents inherit from.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """
    Message class for inter-agent communication.

    Attributes:
        sender: ID of the agent sending the message
        receiver: ID of the agent receiving the message
        msg_type: Type of message (task, result, question, notification, error)
        content: The actual content of the message
        metadata: Additional metadata for the message
        id: Unique message identifier
        timestamp: When the message was created
    """

    sender: str
    receiver: str
    msg_type: Literal["task", "result", "question", "notification", "error"]
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        """String representation of the message."""
        return (
            f"Message(id={self.id[:8]}..., "
            f"type={self.msg_type}, "
            f"from={self.sender}, "
            f"to={self.receiver})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "msg_type": self.msg_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.

    All specialized agents (Researcher, Analyst, Writer, etc.) inherit from this class.

    Attributes:
        agent_id: Unique identifier for this agent
        name: Human-readable name for the agent
        capabilities: List of capabilities this agent has
        message_bus: Reference to the message bus for communication
        shared_memory: Reference to shared memory
        state: Current state of the agent
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique ID for the agent (auto-generated if not provided)
            name: Human-readable name (defaults to class name)
            capabilities: List of capabilities this agent has
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.capabilities = capabilities or []

        # References to system components (set by orchestrator)
        self.message_bus = None
        self.shared_memory = None

        # Agent state
        self.state: Dict[str, Any] = {
            "status": "idle",  # idle, busy, error
            "current_task": None,
            "workload": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

        # Performance metrics
        self.metrics: Dict[str, Any] = {
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "last_active": None,
        }

        logger.info(f"Agent initialized: {self.name} (ID: {self.agent_id[:8]}...)")

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Main processing method for the agent.

        This is the core method that each specialized agent must implement.
        It defines what the agent does with input data.

        Args:
            input_data: The data to process

        Returns:
            The processed result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement process() method")

    def send_message(
        self,
        receiver: str,
        msg_type: Literal["task", "result", "question", "notification", "error"],
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Send a message to another agent.

        Args:
            receiver: ID of the receiving agent
            msg_type: Type of message
            content: Message content
            metadata: Optional metadata

        Returns:
            The sent message

        Raises:
            RuntimeError: If message bus is not set
        """
        if self.message_bus is None:
            raise RuntimeError(
                f"Message bus not set for agent {self.name}. "
                "Agent must be registered with orchestrator first."
            )

        message = Message(
            sender=self.agent_id,
            receiver=receiver,
            msg_type=msg_type,
            content=content,
            metadata=metadata or {},
        )

        self.message_bus.send(message)
        logger.debug(f"{self.name} sent message: {message}")
        return message

    def receive_message(self, timeout: Optional[int] = None) -> Optional[Message]:
        """
        Receive a message from the message bus.

        Args:
            timeout: Maximum time to wait for a message (None = blocking)

        Returns:
            The received message, or None if timeout

        Raises:
            RuntimeError: If message bus is not set
        """
        if self.message_bus is None:
            raise RuntimeError(
                f"Message bus not set for agent {self.name}. "
                "Agent must be registered with orchestrator first."
            )

        try:
            message = self.message_bus.receive(self.agent_id, timeout=timeout)
            if message:
                logger.debug(f"{self.name} received message: {message}")
            return message
        except Exception as e:
            logger.error(f"{self.name} error receiving message: {e}")
            return None

    def broadcast(
        self,
        msg_type: Literal["task", "result", "question", "notification", "error"],
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Broadcast a message to all subscribed agents.

        Args:
            msg_type: Type of message
            content: Message content
            metadata: Optional metadata

        Raises:
            RuntimeError: If message bus is not set
        """
        if self.message_bus is None:
            raise RuntimeError(
                f"Message bus not set for agent {self.name}. "
                "Agent must be registered with orchestrator first."
            )

        message = Message(
            sender=self.agent_id,
            receiver="broadcast",
            msg_type=msg_type,
            content=content,
            metadata=metadata or {},
        )

        self.message_bus.broadcast(message)
        logger.debug(f"{self.name} broadcasted message: {message}")

    def read_shared_memory(self, key: str) -> Any:
        """
        Read a value from shared memory.

        Args:
            key: The key to read

        Returns:
            The value stored at the key, or None if not found

        Raises:
            RuntimeError: If shared memory is not set
        """
        if self.shared_memory is None:
            raise RuntimeError(
                f"Shared memory not set for agent {self.name}. "
                "Agent must be registered with orchestrator first."
            )

        value = self.shared_memory.read(key)
        logger.debug(f"{self.name} read from shared memory: {key}")
        return value

    def write_shared_memory(self, key: str, value: Any) -> None:
        """
        Write a value to shared memory.

        Args:
            key: The key to write to
            value: The value to store

        Raises:
            RuntimeError: If shared memory is not set
        """
        if self.shared_memory is None:
            raise RuntimeError(
                f"Shared memory not set for agent {self.name}. "
                "Agent must be registered with orchestrator first."
            )

        self.shared_memory.write(key, value, agent_id=self.agent_id)
        logger.debug(f"{self.name} wrote to shared memory: {key}")

    def update_state(self, **kwargs) -> None:
        """
        Update agent state.

        Args:
            **kwargs: State fields to update
        """
        self.state.update(kwargs)
        logger.debug(f"{self.name} state updated: {kwargs}")

    def get_state(self) -> Dict[str, Any]:
        """
        Get current agent state.

        Returns:
            Dictionary with current state
        """
        return self.state.copy()

    def update_metrics(self, processing_time: float) -> None:
        """
        Update performance metrics.

        Args:
            processing_time: Time taken to process last task
        """
        self.metrics["total_processing_time"] += processing_time
        self.metrics["last_active"] = datetime.now()

        total_tasks = self.state["tasks_completed"] + self.state["tasks_failed"]
        if total_tasks > 0:
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time"] / total_tasks
            )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        return {
            **self.metrics,
            "tasks_completed": self.state["tasks_completed"],
            "tasks_failed": self.state["tasks_failed"],
            "success_rate": (
                self.state["tasks_completed"] /
                (self.state["tasks_completed"] + self.state["tasks_failed"])
                if (self.state["tasks_completed"] + self.state["tasks_failed"]) > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.agent_id[:8]}..., "
            f"name={self.name}, "
            f"status={self.state['status']})"
        )
