"""
Basic tests for core components of the multi-agent system.

Tests Message, BaseAgent, MessageBus, and SharedMemory.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import Message, BaseAgent
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory


# Simple test agent for testing
class TestAgent(BaseAgent):
    """Simple agent for testing purposes."""

    def __init__(self, agent_id=None, name=None):
        super().__init__(agent_id=agent_id, name=name, capabilities=["test"])

    def process(self, input_data):
        """Simple process method that echoes input."""
        return f"Processed: {input_data}"


def test_message_creation():
    """Test Message creation and serialization."""
    print("\n=== Testing Message ===")

    msg = Message(
        sender="agent_1",
        receiver="agent_2",
        msg_type="task",
        content="Test message",
        metadata={"priority": "high"},
    )

    print(f"Created message: {msg}")
    print(f"Message ID: {msg.id}")
    print(f"Message dict: {msg.to_dict()}")

    # Test serialization roundtrip
    msg_dict = msg.to_dict()
    msg_restored = Message.from_dict(msg_dict)
    assert msg_restored.sender == msg.sender
    assert msg_restored.content == msg.content

    print("✓ Message creation and serialization works!")


def test_base_agent():
    """Test BaseAgent functionality."""
    print("\n=== Testing BaseAgent ===")

    agent = TestAgent(name="TestAgent1")

    print(f"Created agent: {agent}")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent capabilities: {agent.capabilities}")
    print(f"Agent state: {agent.get_state()}")

    # Test process method
    result = agent.process("Hello")
    print(f"Process result: {result}")
    assert result == "Processed: Hello"

    # Test state update
    agent.update_state(status="busy", current_task="testing")
    print(f"Updated state: {agent.get_state()}")

    print("✓ BaseAgent works!")


def test_message_bus():
    """Test MessageBus functionality."""
    print("\n=== Testing MessageBus ===")

    bus = MessageBus()

    # Create test agents
    agent1 = TestAgent(name="Agent1")
    agent2 = TestAgent(name="Agent2")

    # Register agents with bus
    bus.register_agent(agent1.agent_id)
    bus.register_agent(agent2.agent_id)

    print(f"Registered agents: {list(bus.queues.keys())}")

    # Create and send message
    msg = Message(
        sender=agent1.agent_id,
        receiver=agent2.agent_id,
        msg_type="task",
        content="Hello Agent2!",
    )

    bus.send(msg)
    print(f"Sent message: {msg}")

    # Check pending messages
    pending = bus.get_pending_count(agent2.agent_id)
    print(f"Agent2 pending messages: {pending}")
    assert pending == 1

    # Receive message
    received = bus.receive(agent2.agent_id, timeout=1)
    print(f"Received message: {received}")
    assert received.content == "Hello Agent2!"

    # Test broadcast
    bus.subscribe(agent1.agent_id, "notification")
    bus.subscribe(agent2.agent_id, "notification")

    broadcast_msg = Message(
        sender="system",
        receiver="broadcast",
        msg_type="notification",
        content="Broadcast to all!",
    )

    bus.broadcast(broadcast_msg)
    print("Broadcasted message to all subscribers")

    # Check statistics
    stats = bus.get_statistics()
    print(f"MessageBus statistics: {stats}")

    print("✓ MessageBus works!")


def test_shared_memory():
    """Test SharedMemory functionality."""
    print("\n=== Testing SharedMemory ===")

    memory = SharedMemory()

    # Write some data
    memory.write("key1", "value1", agent_id="agent_1")
    memory.write("key2", {"data": "complex"}, agent_id="agent_2")

    print(f"Written 2 keys to shared memory")

    # Read data
    val1 = memory.read("key1")
    val2 = memory.read("key2")
    print(f"Read key1: {val1}")
    print(f"Read key2: {val2}")
    assert val1 == "value1"
    assert val2 == {"data": "complex"}

    # Check existence
    assert memory.exists("key1")
    assert not memory.exists("key3")

    # Get all keys
    keys = memory.keys()
    print(f"All keys: {keys}")
    assert len(keys) == 2

    # Test observer pattern
    notifications = []

    def observer(key, entry):
        notifications.append(f"Key '{key}' changed to '{entry.value}'")

    memory.subscribe("key1", observer)
    memory.write("key1", "new_value1", agent_id="agent_1")

    print(f"Notifications received: {notifications}")
    assert len(notifications) == 1

    # Get statistics
    stats = memory.get_statistics()
    print(f"SharedMemory statistics: {stats}")

    print("✓ SharedMemory works!")


def test_integration():
    """Test integration of all components."""
    print("\n=== Testing Integration ===")

    # Create components
    bus = MessageBus()
    memory = SharedMemory()

    # Create agents
    agent1 = TestAgent(name="Agent1")
    agent2 = TestAgent(name="Agent2")

    # Connect agents to bus and memory
    agent1.message_bus = bus
    agent1.shared_memory = memory
    agent2.message_bus = bus
    agent2.shared_memory = memory

    # Register with bus
    bus.register_agent(agent1.agent_id)
    bus.register_agent(agent2.agent_id)

    # Agent1 writes to shared memory
    agent1.write_shared_memory("research_results", {
        "topic": "AI",
        "findings": ["Finding 1", "Finding 2"]
    })

    print("Agent1 wrote to shared memory")

    # Agent2 reads from shared memory
    results = agent2.read_shared_memory("research_results")
    print(f"Agent2 read from shared memory: {results}")

    # Agent1 sends message to Agent2
    agent1.send_message(
        receiver=agent2.agent_id,
        msg_type="task",
        content="Please analyze the research results",
    )

    print("Agent1 sent message to Agent2")

    # Agent2 receives message
    msg = agent2.receive_message(timeout=1)
    print(f"Agent2 received message: {msg.content}")

    # Agent2 processes and responds
    response = agent2.process(results)
    print(f"Agent2 processed: {response}")

    agent2.send_message(
        receiver=agent1.agent_id,
        msg_type="result",
        content=response,
    )

    # Agent1 receives response
    response_msg = agent1.receive_message(timeout=1)
    print(f"Agent1 received response: {response_msg.content}")

    print("✓ Integration test passed!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TESTING MULTI-AGENT SYSTEM - PHASE 1 COMPONENTS")
    print("=" * 60)

    try:
        test_message_creation()
        test_base_agent()
        test_message_bus()
        test_shared_memory()
        test_integration()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
