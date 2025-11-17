"""
Complete Orchestration Example.

Demonstrates the full orchestration system with:
- Orchestrator coordinating tasks
- TaskQueue managing task priority and dependencies
- AgentRegistry for agent discovery
- DependencyGraph for execution order
- ResultAggregator for combining results
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import Orchestrator
from core.task_queue import TaskPriority
from core.result_aggregator import ResultAggregator, AgentResult, AggregationStrategy
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent


# Mock LLM for demo
class MockLLM:
    """Mock LLM for demonstration."""

    def generate(self, prompt):
        if "research" in prompt.lower():
            return "Research findings: AI is transforming industries. Key trends include automation, ML advances, and ethical considerations."
        elif "analy" in prompt.lower():
            return "Analysis shows high quality data with positive trends in AI adoption across sectors."
        elif "write" in prompt.lower() or "report" in prompt.lower():
            return "# AI Trends Report\n\nBased on comprehensive research and analysis, AI continues to show strong growth."
        return "Mock response"

    def chat(self, messages, **kwargs):
        return self.generate(messages[-1]["content"] if messages else "")


def main():
    """Run orchestration example."""
    print("=" * 70)
    print("ORCHESTRATION SYSTEM - COMPLETE DEMONSTRATION")
    print("=" * 70)

    # Step 1: Initialize Orchestrator
    print("\n--- Step 1: Initialize Orchestrator ---")
    orchestrator = Orchestrator()
    mock_llm = MockLLM()

    print("✓ Orchestrator initialized")
    print(f"  {orchestrator}")

    # Step 2: Create and Register Agents
    print("\n--- Step 2: Create and Register Agents ---")

    # Create multiple instances of each type for load balancing
    researcher1 = ResearcherAgent(llm=mock_llm)
    researcher2 = ResearcherAgent(llm=mock_llm)
    researcher2.name = "Researcher2"

    analyst = AnalystAgent(llm=mock_llm)
    writer = WriterAgent(llm=mock_llm)

    agents = [researcher1, researcher2, analyst, writer]

    for agent in agents:
        orchestrator.register_agent(agent)

    print(f"✓ Registered {len(agents)} agents")

    # Step 3: Add Tasks with Dependencies
    print("\n--- Step 3: Add Tasks with Dependencies ---")

    # Research tasks (can run in parallel)
    task1 = orchestrator.add_task(
        agent_type="Researcher",
        action="research",
        input_data="AI trends in healthcare",
        priority=TaskPriority.HIGH,
        metadata={"topic": "healthcare"}
    )
    print(f"✓ Added research task 1: {task1.task_id[:8]}...")

    task2 = orchestrator.add_task(
        agent_type="Researcher",
        action="research",
        input_data="AI trends in finance",
        priority=TaskPriority.HIGH,
        metadata={"topic": "finance"}
    )
    print(f"✓ Added research task 2: {task2.task_id[:8]}...")

    # Analysis task (depends on both research tasks)
    task3 = orchestrator.add_task(
        agent_type="Analyst",
        action="analyze",
        input_data="Analyze combined research",
        priority=TaskPriority.MEDIUM,
        dependencies=[task1.task_id, task2.task_id],
        metadata={"analysis_type": "comprehensive"}
    )
    print(f"✓ Added analysis task: {task3.task_id[:8]}... (depends on tasks 1 & 2)")

    # Writing task (depends on analysis)
    task4 = orchestrator.add_task(
        agent_type="Writer",
        action="write",
        input_data="Write final report",
        priority=TaskPriority.MEDIUM,
        dependencies=[task3.task_id],
        metadata={"style": "professional"}
    )
    print(f"✓ Added writing task: {task4.task_id[:8]}... (depends on task 3)")

    # Step 4: View Execution Plan
    print("\n--- Step 4: View Execution Plan ---")

    execution_plan = orchestrator.get_execution_plan()
    print("Execution layers (tasks in same layer can run in parallel):")
    for i, layer in enumerate(execution_plan, 1):
        print(f"  Layer {i}: {len(layer)} task(s)")
        for task_id in layer:
            task = orchestrator.task_queue.get_task(task_id)
            if task:
                print(f"    - {task.agent_type}: {task.action} (priority: {task.priority})")

    # Step 5: Check System Status Before Execution
    print("\n--- Step 5: System Status Before Execution ---")

    status = orchestrator.get_system_status()
    print("System Status:")
    print(f"  Agents:")
    print(f"    - Total: {status['agent_registry']['total_agents']}")
    print(f"    - Idle: {status['agent_registry']['idle_agents']}")
    print(f"    - Busy: {status['agent_registry']['busy_agents']}")
    print(f"  Tasks:")
    print(f"    - Total: {status['task_queue']['total_tasks']}")
    print(f"    - Pending: {status['task_queue']['pending_tasks']}")
    print(f"    - In Progress: {status['task_queue']['in_progress_tasks']}")
    print(f"  Dependencies:")
    print(f"    - Total Nodes: {status['dependency_graph']['total_nodes']}")
    print(f"    - Total Edges: {status['dependency_graph']['total_edges']}")

    # Step 6: Demonstrate Agent Selection
    print("\n--- Step 6: Agent Discovery and Load Balancing ---")

    # Find all researchers
    researchers = orchestrator.agent_registry.find_by_type("Researcher")
    print(f"Found {len(researchers)} Researcher agents:")
    for r in researchers:
        print(f"  - {r.name} (workload: {r.workload}, status: {r.status})")

    # Find available agent for research
    available = orchestrator.agent_registry.find_available_agent(agent_type="Researcher")
    if available:
        print(f"✓ Best available researcher: {available.name}")

    # Step 7: Demonstrate ResultAggregator
    print("\n--- Step 7: Result Aggregation Demonstration ---")

    aggregator = ResultAggregator()

    # Simulate multiple agent results
    mock_results = [
        AgentResult("agent1", "Researcher", 85, confidence=0.9),
        AgentResult("agent2", "Researcher", 82, confidence=0.85),
        AgentResult("agent3", "Researcher", 85, confidence=0.8),
    ]

    print("Simulated results from 3 agents: [85, 82, 85]")

    # Try different aggregation strategies
    consensus = aggregator.aggregate(mock_results, AggregationStrategy.CONSENSUS)
    print(f"  - Consensus: {consensus}")

    weighted = aggregator.aggregate(mock_results, AggregationStrategy.WEIGHTED)
    print(f"  - Weighted: {weighted:.2f}")

    best = aggregator.aggregate(mock_results, AggregationStrategy.BEST)
    print(f"  - Best: {best}")

    # Analyze agreement
    agreement = aggregator.analyze_agreement(mock_results)
    print(f"  - Agreement level: {agreement['agreement_level']:.1%}")
    print(f"  - Majority value: {agreement['majority_value']}")

    # Step 8: Get Task Information
    print("\n--- Step 8: Task Details ---")

    print("\nAll tasks in queue:")
    for task_id, task in orchestrator.task_queue.tasks.items():
        deps = ", ".join([d[:8] + "..." for d in task.dependencies]) if task.dependencies else "none"
        print(f"  {task.task_id[:8]}... | {task.agent_type:12} | {task.action:20} | deps: {deps}")

    # Step 9: Statistics
    print("\n--- Step 9: System Statistics ---")

    print("\nAgent Registry Statistics:")
    agent_stats = orchestrator.agent_registry.get_statistics()
    for key, value in agent_stats.items():
        print(f"  {key}: {value}")

    print("\nTask Queue Statistics:")
    queue_stats = orchestrator.task_queue.get_statistics()
    for key, value in queue_stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}" if "rate" in key else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\nDependency Graph Statistics:")
    dep_stats = orchestrator.dependency_graph.get_statistics()
    for key, value in dep_stats.items():
        print(f"  {key}: {value}")

    # Step 10: Summary
    print("\n--- Step 10: Summary ---")

    print("\n✓ Orchestration System Capabilities Demonstrated:")
    print("  1. Task Queue: Priority-based scheduling")
    print("  2. Dependency Graph: Task dependency resolution")
    print("  3. Agent Registry: Agent discovery and load balancing")
    print("  4. Result Aggregator: Multiple aggregation strategies")
    print("  5. Orchestrator: Centralized coordination")

    print("\n" + "=" * 70)
    print("✓ ORCHESTRATION DEMONSTRATION COMPLETE!")
    print("=" * 70)

    print("\n💡 What was demonstrated:")
    print("  • 4 agents registered (2 Researchers, 1 Analyst, 1 Writer)")
    print("  • 4 tasks added with dependency chain")
    print("  • Execution plan created (2 parallel, then sequential)")
    print("  • Agent discovery and load balancing")
    print("  • Result aggregation with multiple strategies")
    print("  • Comprehensive system statistics")

    print("\n🚀 The orchestration system is ready for production use!")

    # Optional: Show how to actually execute
    print("\n--- Optional: Task Execution ---")
    print("To actually execute tasks, you would call:")
    print("  orchestrator.execute_all()")
    print("\nThis would:")
    print("  1. Get next task from queue (respecting dependencies)")
    print("  2. Find available agent")
    print("  3. Send task to agent via message bus")
    print("  4. Collect result")
    print("  5. Repeat until all tasks complete")

    # Clean system status
    final_status = orchestrator.get_system_status()
    print(f"\n📊 Final System State:")
    print(f"  • Total agents: {final_status['agent_registry']['total_agents']}")
    print(f"  • Total tasks: {final_status['task_queue']['total_tasks']}")
    print(f"  • Pending tasks: {final_status['task_queue']['pending_tasks']}")
    print(f"  • Dependency nodes: {final_status['dependency_graph']['total_nodes']}")


if __name__ == "__main__":
    main()
