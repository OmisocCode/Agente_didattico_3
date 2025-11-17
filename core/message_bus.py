"""
Message Bus module for inter-agent communication.

Implements a message passing system that allows agents to send messages to each other
and broadcast messages to multiple agents.

Supports both in-memory queues and Redis-backed queues for distributed systems.
"""

import logging
from queue import Queue, Empty
from typing import Dict, List, Set, Optional
from collections import defaultdict

from agents.base_agent import Message

logger = logging.getLogger(__name__)


class MessageBus:
    """
    Message bus for agent communication.

    Implements a publish-subscribe pattern where agents can:
    - Send direct messages to specific agents
    - Broadcast messages to all subscribed agents
    - Subscribe to specific message types

    Uses in-memory queues by default. Can be extended to use Redis for distributed systems.
    """

    def __init__(self, queue_type: str = "memory"):
        """
        Initialize the message bus.

        Args:
            queue_type: Type of queue to use ("memory" or "redis")
        """
        self.queue_type = queue_type

        # Message queues for each agent (agent_id -> Queue)
        self.queues: Dict[str, Queue] = {}

        # Subscriptions for broadcast messages (msg_type -> set of agent_ids)
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Message history for debugging/logging
        self.message_history: List[Message] = []
        self.max_history_size = 1000

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "broadcasts_sent": 0,
        }

        logger.info(f"MessageBus initialized with queue_type: {queue_type}")

    def register_agent(self, agent_id: str) -> None:
        """
        Register an agent with the message bus.

        Creates a message queue for the agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        if agent_id not in self.queues:
            self.queues[agent_id] = Queue()
            logger.debug(f"Agent registered with MessageBus: {agent_id}")
        else:
            logger.warning(f"Agent {agent_id} already registered")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the message bus.

        Removes the agent's queue and all subscriptions.

        Args:
            agent_id: Unique identifier for the agent
        """
        # Remove queue
        if agent_id in self.queues:
            del self.queues[agent_id]

        # Remove from subscriptions
        for msg_type in self.subscriptions:
            self.subscriptions[msg_type].discard(agent_id)

        logger.debug(f"Agent unregistered from MessageBus: {agent_id}")

    def send(self, message: Message) -> None:
        """
        Send a message to a specific agent.

        Args:
            message: The message to send

        Raises:
            ValueError: If receiver agent is not registered
        """
        if message.receiver not in self.queues:
            # Auto-register the receiver if not already registered
            self.register_agent(message.receiver)
            logger.warning(
                f"Auto-registered receiver {message.receiver} "
                f"(sender: {message.sender})"
            )

        # Put message in receiver's queue
        self.queues[message.receiver].put(message)

        # Update statistics
        self.stats["messages_sent"] += 1

        # Add to history
        self._add_to_history(message)

        logger.debug(
            f"Message sent: {message.sender} -> {message.receiver} "
            f"(type: {message.msg_type})"
        )

    def receive(self, agent_id: str, timeout: Optional[int] = None) -> Optional[Message]:
        """
        Receive the next message for an agent.

        Args:
            agent_id: The agent receiving the message
            timeout: Maximum time to wait for a message in seconds (None = blocking)

        Returns:
            The next message, or None if timeout

        Raises:
            ValueError: If agent is not registered
        """
        if agent_id not in self.queues:
            raise ValueError(f"Agent {agent_id} is not registered with MessageBus")

        try:
            message = self.queues[agent_id].get(timeout=timeout)
            self.stats["messages_received"] += 1

            logger.debug(
                f"Message received by {agent_id}: "
                f"from {message.sender} (type: {message.msg_type})"
            )

            return message

        except Empty:
            # Timeout occurred
            return None

    def broadcast(self, message: Message) -> None:
        """
        Broadcast a message to all agents subscribed to this message type.

        Args:
            message: The message to broadcast
        """
        msg_type = message.msg_type
        subscribers = self.subscriptions.get(msg_type, set())

        if not subscribers:
            logger.warning(
                f"Broadcast message type '{msg_type}' has no subscribers "
                f"(sender: {message.sender})"
            )
            return

        # Send to all subscribers
        for agent_id in subscribers:
            # Create a copy of the message for each subscriber
            subscriber_message = Message(
                sender=message.sender,
                receiver=agent_id,
                msg_type=message.msg_type,
                content=message.content,
                metadata=message.metadata,
            )
            self.send(subscriber_message)

        # Update statistics
        self.stats["broadcasts_sent"] += 1

        logger.debug(
            f"Broadcast sent by {message.sender}: "
            f"type={msg_type}, subscribers={len(subscribers)}"
        )

    def subscribe(self, agent_id: str, msg_type: str) -> None:
        """
        Subscribe an agent to a message type for broadcasts.

        Args:
            agent_id: The agent to subscribe
            msg_type: The message type to subscribe to
        """
        self.subscriptions[msg_type].add(agent_id)
        logger.debug(f"Agent {agent_id} subscribed to message type: {msg_type}")

    def unsubscribe(self, agent_id: str, msg_type: str) -> None:
        """
        Unsubscribe an agent from a message type.

        Args:
            agent_id: The agent to unsubscribe
            msg_type: The message type to unsubscribe from
        """
        self.subscriptions[msg_type].discard(agent_id)
        logger.debug(f"Agent {agent_id} unsubscribed from message type: {msg_type}")

    def has_messages(self, agent_id: str) -> bool:
        """
        Check if an agent has pending messages.

        Args:
            agent_id: The agent to check

        Returns:
            True if agent has pending messages, False otherwise
        """
        if agent_id not in self.queues:
            return False
        return not self.queues[agent_id].empty()

    def get_pending_count(self, agent_id: str) -> int:
        """
        Get the number of pending messages for an agent.

        Args:
            agent_id: The agent to check

        Returns:
            Number of pending messages
        """
        if agent_id not in self.queues:
            return 0
        return self.queues[agent_id].qsize()

    def clear_queue(self, agent_id: str) -> int:
        """
        Clear all pending messages for an agent.

        Args:
            agent_id: The agent whose queue to clear

        Returns:
            Number of messages cleared
        """
        if agent_id not in self.queues:
            return 0

        count = 0
        while not self.queues[agent_id].empty():
            try:
                self.queues[agent_id].get_nowait()
                count += 1
            except Empty:
                break

        logger.debug(f"Cleared {count} messages from {agent_id}'s queue")
        return count

    def get_statistics(self) -> Dict[str, int]:
        """
        Get message bus statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "registered_agents": len(self.queues),
            "active_subscriptions": sum(
                len(subs) for subs in self.subscriptions.values()
            ),
            "total_pending": sum(
                q.qsize() for q in self.queues.values()
            ),
        }

    def _add_to_history(self, message: Message) -> None:
        """
        Add a message to the history buffer.

        Args:
            message: The message to add
        """
        self.message_history.append(message)

        # Limit history size
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)

    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        msg_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Message]:
        """
        Get message history with optional filtering.

        Args:
            agent_id: Filter by sender or receiver (optional)
            msg_type: Filter by message type (optional)
            limit: Maximum number of messages to return

        Returns:
            List of messages matching the filters
        """
        messages = self.message_history

        # Filter by agent_id (sender or receiver)
        if agent_id:
            messages = [
                m for m in messages
                if m.sender == agent_id or m.receiver == agent_id
            ]

        # Filter by message type
        if msg_type:
            messages = [m for m in messages if m.msg_type == msg_type]

        # Limit results
        return messages[-limit:]

    def reset(self) -> None:
        """
        Reset the message bus.

        Clears all queues, subscriptions, history, and statistics.
        """
        self.queues.clear()
        self.subscriptions.clear()
        self.message_history.clear()
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "broadcasts_sent": 0,
        }
        logger.info("MessageBus reset")

    def __repr__(self) -> str:
        """String representation of the message bus."""
        return (
            f"MessageBus("
            f"agents={len(self.queues)}, "
            f"pending={sum(q.qsize() for q in self.queues.values())}, "
            f"sent={self.stats['messages_sent']}, "
            f"received={self.stats['messages_received']})"
        )
