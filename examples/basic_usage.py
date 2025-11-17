"""
Basic usage example of the Multi-Agent System - Phase 1 Components.

This example demonstrates:
1. Creating agents
2. Setting up MessageBus and SharedMemory
3. Agent communication via messages
4. Shared memory usage
5. Observer pattern
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import Message, BaseAgent
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory


# Define two simple agents for demonstration
class CollectorAgent(BaseAgent):
    """Agent that collects data and shares it."""

    def __init__(self):
        super().__init__(name="Collector", capabilities=["data_collection"])

    def process(self, input_data):
        """Collect data and store in shared memory."""
        print(f"\n[{self.name}] Collecting data: {input_data}")

        # Simulate data collection
        collected_data = {
            "source": input_data,
            "data": [f"item_{i}" for i in range(1, 6)],
            "count": 5,
        }

        # Store in shared memory
        self.write_shared_memory("collected_data", collected_data)

        print(f"[{self.name}] Stored {collected_data['count']} items in shared memory")

        return collected_data


class AnalyzerAgent(BaseAgent):
    """Agent that analyzes data from shared memory."""

    def __init__(self):
        super().__init__(name="Analyzer", capabilities=["data_analysis"])

    def process(self, input_data):
        """Read data from shared memory and analyze it."""
        print(f"\n[{self.name}] Analyzing data...")

        # Read from shared memory
        data = self.read_shared_memory("collected_data")

        if not data:
            print(f"[{self.name}] No data found in shared memory!")
            return None

        # Simulate analysis
        analysis = {
            "source": data.get("source"),
            "total_items": data.get("count"),
            "summary": f"Analyzed {data.get('count')} items",
            "status": "complete",
        }

        # Store analysis results
        self.write_shared_memory("analysis_results", analysis)

        print(f"[{self.name}] Analysis complete: {analysis['summary']}")

        return analysis


def main():
    """Main demonstration."""
    print("=" * 70)
    print("MULTI-AGENT SYSTEM - BASIC USAGE EXAMPLE")
    print("=" * 70)

    # 1. Create infrastructure
    print("\n--- Step 1: Create Infrastructure ---")
    message_bus = MessageBus()
    shared_memory = SharedMemory()
    print("✓ MessageBus created")
    print("✓ SharedMemory created")

    # 2. Create agents
    print("\n--- Step 2: Create Agents ---")
    collector = CollectorAgent()
    analyzer = AnalyzerAgent()
    print(f"✓ Created {collector.name} agent (ID: {collector.agent_id[:8]}...)")
    print(f"✓ Created {analyzer.name} agent (ID: {analyzer.agent_id[:8]}...)")

    # 3. Connect agents to infrastructure
    print("\n--- Step 3: Connect Agents to Infrastructure ---")

    # Connect collector
    collector.message_bus = message_bus
    collector.shared_memory = shared_memory
    message_bus.register_agent(collector.agent_id)

    # Connect analyzer
    analyzer.message_bus = message_bus
    analyzer.shared_memory = shared_memory
    message_bus.register_agent(analyzer.agent_id)

    print(f"✓ {collector.name} connected to MessageBus and SharedMemory")
    print(f"✓ {analyzer.name} connected to MessageBus and SharedMemory")

    # 4. Set up observer for shared memory changes
    print("\n--- Step 4: Set Up Observers ---")

    def on_data_collected(key, entry):
        print(f"\n[OBSERVER] Data collected by {entry.author[:8]}... at {entry.timestamp.strftime('%H:%M:%S')}")
        print(f"[OBSERVER] Data count: {entry.value.get('count')} items")

    def on_analysis_complete(key, entry):
        print(f"\n[OBSERVER] Analysis completed by {entry.author[:8]}...")
        print(f"[OBSERVER] Status: {entry.value.get('status')}")

    shared_memory.subscribe("collected_data", on_data_collected)
    shared_memory.subscribe("analysis_results", on_analysis_complete)

    print("✓ Observers subscribed to shared memory changes")

    # 5. Collector collects data
    print("\n--- Step 5: Collector Gathers Data ---")
    collection_result = collector.process("web_source_1")

    # 6. Collector sends message to Analyzer
    print("\n--- Step 6: Collector Notifies Analyzer ---")
    collector.send_message(
        receiver=analyzer.agent_id,
        msg_type="task",
        content="Please analyze the collected data",
        metadata={"priority": "high", "task_type": "analysis"},
    )
    print(f"✓ {collector.name} sent task to {analyzer.name}")

    # 7. Analyzer receives message
    print("\n--- Step 7: Analyzer Receives Message ---")
    message = analyzer.receive_message(timeout=1)

    if message:
        print(f"✓ {analyzer.name} received message:")
        print(f"  - Type: {message.msg_type}")
        print(f"  - Content: {message.content}")
        print(f"  - Priority: {message.metadata.get('priority')}")

    # 8. Analyzer processes data
    print("\n--- Step 8: Analyzer Processes Data ---")
    analysis_result = analyzer.process(None)

    # 9. Analyzer sends results back
    print("\n--- Step 9: Analyzer Sends Results ---")
    analyzer.send_message(
        receiver=collector.agent_id,
        msg_type="result",
        content=analysis_result,
        metadata={"task_completed": True},
    )
    print(f"✓ {analyzer.name} sent results to {collector.name}")

    # 10. Collector receives results
    print("\n--- Step 10: Collector Receives Results ---")
    result_message = collector.receive_message(timeout=1)

    if result_message:
        print(f"✓ {collector.name} received results:")
        print(f"  - Summary: {result_message.content.get('summary')}")
        print(f"  - Status: {result_message.content.get('status')}")

    # 11. Show statistics
    print("\n--- Step 11: System Statistics ---")

    bus_stats = message_bus.get_statistics()
    print("\nMessageBus Statistics:")
    print(f"  - Messages sent: {bus_stats['messages_sent']}")
    print(f"  - Messages received: {bus_stats['messages_received']}")
    print(f"  - Registered agents: {bus_stats['registered_agents']}")

    memory_stats = shared_memory.get_statistics()
    print("\nSharedMemory Statistics:")
    print(f"  - Total keys: {memory_stats['total_keys']}")
    print(f"  - Reads: {memory_stats['reads']}")
    print(f"  - Writes: {memory_stats['writes']}")
    print(f"  - Notifications sent: {memory_stats['notifications_sent']}")

    print("\nAgent Metrics:")
    collector_metrics = collector.get_metrics()
    analyzer_metrics = analyzer.get_metrics()
    print(f"  - {collector.name}: {collector_metrics['tasks_completed']} tasks completed")
    print(f"  - {analyzer.name}: {analyzer_metrics['tasks_completed']} tasks completed")

    # 12. Show shared memory contents
    print("\n--- Step 12: Shared Memory Contents ---")
    print(f"\nKeys in shared memory: {shared_memory.keys()}")

    for key in shared_memory.keys():
        entry = shared_memory.read_entry(key)
        print(f"\nKey: {key}")
        print(f"  - Author: {entry.author[:8]}...")
        print(f"  - Version: {entry.version}")
        print(f"  - Timestamp: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - Value: {entry.value}")

    print("\n" + "=" * 70)
    print("✓ EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
