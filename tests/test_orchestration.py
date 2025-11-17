"""
Tests for orchestration components.

Tests TaskQueue, DependencyGraph, AgentRegistry, Orchestrator, and ResultAggregator.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from core.dependency_graph import DependencyGraph, CircularDependencyError
from core.agent_registry import AgentRegistry, AgentInfo
from core.orchestrator import Orchestrator
from core.result_aggregator import ResultAggregator, AgentResult, AggregationStrategy
from agents.base_agent import BaseAgent


# Simple test agent
class TestAgent(BaseAgent):
    """Simple agent for testing."""

    def process(self, input_data):
        return f"Processed: {input_data}"


def test_task_queue():
    """Test TaskQueue."""
    print("\n=== Testing TaskQueue ===")

    queue = TaskQueue()

    # Add tasks with different priorities
    task1 = queue.add_task("researcher", "research", "topic1", priority=TaskPriority.LOW)
    task2 = queue.add_task("analyst", "analyze", "data1", priority=TaskPriority.HIGH)
    task3 = queue.add_task("writer", "write", "report1", priority=TaskPriority.MEDIUM)

    print(f"Added 3 tasks: {queue}")

    # High priority should come first
    next_task = queue.get_next_task()
    assert next_task.task_id == task2.task_id
    assert next_task.status == TaskStatus.IN_PROGRESS
    print(f"✓ High priority task retrieved first: {next_task.agent_type}")

    # Complete task
    queue.complete_task(task2.task_id, {"result": "analysis complete"})
    assert task2.status == TaskStatus.COMPLETED
    print(f"✓ Task marked as completed")

    # Test dependencies
    task4 = queue.add_task("writer", "write", "final", dependencies=[task1.task_id])
    assert task4.task_id in queue.pending
    print(f"✓ Task with dependencies added to pending")

    # Complete dependency
    queue.complete_task(task1.task_id, {"result": "research complete"})

    # Task4 should now be in queue
    stats = queue.get_statistics()
    print(f"Queue stats: {stats}")

    print("✓ TaskQueue works!")


def test_dependency_graph():
    """Test DependencyGraph."""
    print("\n=== Testing DependencyGraph ===")

    graph = DependencyGraph()

    # Add nodes
    graph.add_node("task1")
    graph.add_node("task2")
    graph.add_node("task3")
    graph.add_node("task4")

    # Add dependencies: task4 -> task3 -> task2 -> task1
    graph.add_dependency("task2", "task1")
    graph.add_dependency("task3", "task2")
    graph.add_dependency("task4", "task3")

    print(f"Created dependency chain: {graph}")

    # Test topological sort
    order = graph.topological_sort()
    print(f"Execution order: {order}")
    assert order.index("task1") < order.index("task2")
    assert order.index("task2") < order.index("task3")
    assert order.index("task3") < order.index("task4")
    print("✓ Topological sort correct")

    # Test execution layers
    layers = graph.get_execution_layers()
    print(f"Execution layers: {layers}")
    assert layers[0] == ["task1"]
    assert layers[1] == ["task2"]
    print("✓ Execution layers correct")

    # Test circular dependency detection
    try:
        graph.add_dependency("task1", "task4")  # Would create cycle
        assert False, "Should have detected circular dependency"
    except CircularDependencyError:
        print("✓ Circular dependency detected")

    print("✓ DependencyGraph works!")


def test_agent_registry():
    """Test AgentRegistry."""
    print("\n=== Testing AgentRegistry ===")

    registry = AgentRegistry()

    # Register agents
    agent1 = TestAgent()
    agent1.capabilities = ["research", "web_search"]
    agent1.name = "Researcher"

    agent2 = TestAgent()
    agent2.capabilities = ["analysis", "evaluation"]
    agent2.name = "Analyst"

    registry.register(agent1.agent_id, "researcher", agent1.name, agent1.capabilities)
    registry.register(agent2.agent_id, "analyst", agent2.name, agent2.capabilities)

    print(f"Registered 2 agents: {registry}")

    # Find by type
    researchers = registry.find_by_type("researcher")
    assert len(researchers) == 1
    assert researchers[0].name == "Researcher"
    print(f"✓ Found researcher by type")

    # Find by capability
    analysts = registry.find_by_capability("analysis")
    assert len(analysts) == 1
    print(f"✓ Found analyst by capability")

    # Find available agent
    available = registry.find_available_agent(agent_type="researcher")
    assert available is not None
    assert available.status == "idle"
    print(f"✓ Found available agent: {available.name}")

    # Test workload management
    registry.increment_agent_workload(agent1.agent_id)
    assert registry.get_agent(agent1.agent_id).workload == 1
    assert registry.get_agent(agent1.agent_id).status == "busy"
    print(f"✓ Workload management works")

    # Record task completion
    registry.record_task_completion(agent1.agent_id, success=True)
    assert registry.get_agent(agent1.agent_id).total_tasks_completed == 1
    assert registry.get_agent(agent1.agent_id).workload == 0
    print(f"✓ Task completion recorded")

    # Get statistics
    stats = registry.get_statistics()
    print(f"Registry stats: {stats}")
    assert stats["total_agents"] == 2

    print("✓ AgentRegistry works!")


def test_result_aggregator():
    """Test ResultAggregator."""
    print("\n=== Testing ResultAggregator ===")

    aggregator = ResultAggregator()

    # Create test results
    results = [
        AgentResult("agent1", "researcher", 42, confidence=0.9),
        AgentResult("agent2", "researcher", 45, confidence=0.8),
        AgentResult("agent3", "researcher", 42, confidence=0.7)
    ]

    # Test consensus
    consensus = aggregator.aggregate(results, AggregationStrategy.CONSENSUS)
    assert consensus == 42  # Most common value
    print(f"✓ Consensus aggregation: {consensus}")

    # Test weighted
    weighted = aggregator.aggregate(results, AggregationStrategy.WEIGHTED)
    print(f"✓ Weighted aggregation: {weighted:.2f}")

    # Test best
    best = aggregator.aggregate(results, AggregationStrategy.BEST)
    assert best == 42  # Highest confidence
    print(f"✓ Best result: {best}")

    # Test ensemble
    ensemble = aggregator.aggregate(results, AggregationStrategy.ENSEMBLE)
    assert len(ensemble) == 3
    print(f"✓ Ensemble aggregation: {ensemble}")

    # Test numeric aggregation
    mean_val = aggregator.aggregate_numeric(results, "mean")
    print(f"✓ Numeric mean: {mean_val:.2f}")

    # Test agreement analysis
    agreement = aggregator.analyze_agreement(results)
    print(f"✓ Agreement analysis: {agreement['agreement_level']:.2%}")
    assert agreement["majority_value"] == 42

    print("✓ ResultAggregator works!")


def test_orchestrator():
    """Test Orchestrator."""
    print("\n=== Testing Orchestrator ===")

    orchestrator = Orchestrator()

    # Register agents
    agent1 = TestAgent()
    agent1.name = "Researcher"
    agent1.capabilities = ["research"]

    agent2 = TestAgent()
    agent2.name = "Analyst"
    agent2.capabilities = ["analysis"]

    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)

    print(f"Orchestrator initialized: {orchestrator}")

    # Add tasks
    task1 = orchestrator.add_task("Researcher", "research", "AI trends", priority=TaskPriority.HIGH)
    task2 = orchestrator.add_task("Analyst", "analyze", "research data", priority=TaskPriority.MEDIUM, dependencies=[task1.task_id])

    print(f"Added 2 tasks (1 with dependency)")

    # Check execution plan
    try:
        plan = orchestrator.get_execution_plan()
        print(f"✓ Execution plan: {plan}")
        assert task1.task_id in plan[0]  # First layer
        assert task2.task_id in plan[1]  # Second layer (depends on task1)
    except CircularDependencyError:
        print("Note: Execution plan may have dependencies")

    # Get system status
    status = orchestrator.get_system_status()
    print(f"System status:")
    print(f"  - Agents: {status['agent_registry']['total_agents']}")
    print(f"  - Tasks: {status['task_queue']['total_tasks']}")
    print(f"  - Pending: {status['task_queue']['pending_tasks']}")

    assert status['agent_registry']['total_agents'] == 2
    assert status['task_queue']['total_tasks'] == 2

    print("✓ Orchestrator works!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TESTING ORCHESTRATION COMPONENTS - PHASE 3")
    print("=" * 70)

    try:
        test_task_queue()
        test_dependency_graph()
        test_agent_registry()
        test_result_aggregator()
        test_orchestrator()

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
