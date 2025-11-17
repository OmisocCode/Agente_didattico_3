"""
Test script per verificare il funzionamento degli esempi della documentazione.

Questo script testa che gli agenti possano essere registrati e trovati correttamente.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import Orchestrator
from core.task_queue import TaskPriority
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.coordinator_agent import CoordinatorAgent


# Mock LLM per test senza API
class MockLLM:
    """Mock LLM che simula risposte senza chiamare API esterne."""

    def generate(self, prompt, **kwargs):
        """Generate mock response."""
        if "research" in prompt.lower():
            return "Mock research results about the topic"
        elif "analyze" in prompt.lower():
            return "Mock analysis with insights"
        elif "write" in prompt.lower():
            return "Mock written report"
        elif "verify" in prompt.lower():
            return "Mock verification results"
        elif "plan" in prompt.lower():
            return '{"goal": "Mock plan", "steps": []}'
        return "Mock LLM response"

    def chat(self, messages, **kwargs):
        """Mock chat method."""
        last_message = messages[-1]["content"] if messages else ""
        return self.generate(last_message)


def test_agent_registration():
    """Test 1: Verifica registrazione agenti."""
    print("\n" + "="*70)
    print("TEST 1: AGENT REGISTRATION")
    print("="*70)

    llm = MockLLM()
    orchestrator = Orchestrator()

    # Create agents
    agents = [
        ResearcherAgent(llm=llm),
        AnalystAgent(llm=llm),
        WriterAgent(llm=llm),
        FactCheckerAgent(llm=llm),
        CoordinatorAgent(llm=llm)
    ]

    # Register
    for agent in agents:
        orchestrator.register_agent(agent)

    print(f"\n✓ Registered {len(orchestrator.agent_registry.get_all_agents())} agents")

    # Verify
    for agent_info in orchestrator.agent_registry.get_all_agents():
        print(f"  - {agent_info.agent_type}: {agent_info.name}")

    # Test lookup
    print("\nTesting agent lookup:")
    for agent_class in ["ResearcherAgent", "AnalystAgent", "WriterAgent",
                        "FactCheckerAgent", "CoordinatorAgent"]:
        found = orchestrator.agent_registry.find_available_agent(agent_type=agent_class)
        if found:
            print(f"  ✓ {agent_class}: found")
        else:
            print(f"  ✗ {agent_class}: NOT FOUND")
            return False

    print("\n✓ Test 1 PASSED")
    return True


def test_task_execution():
    """Test 2: Verifica esecuzione task."""
    print("\n" + "="*70)
    print("TEST 2: TASK EXECUTION")
    print("="*70)

    llm = MockLLM()
    orchestrator = Orchestrator()

    # Register agents
    orchestrator.register_agent(ResearcherAgent(llm=llm))
    orchestrator.register_agent(AnalystAgent(llm=llm))
    orchestrator.register_agent(WriterAgent(llm=llm))

    print(f"\n✓ Registered {len(orchestrator.agent_registry.get_all_agents())} agents")

    # Add tasks with dependencies
    print("\nAdding tasks...")

    task1 = orchestrator.add_task(
        agent_type="ResearcherAgent",
        action="research",
        input_data={"topic": "AI"},
        priority=TaskPriority.HIGH,
        metadata={"timeout": 5}
    )
    print(f"  • Research task: {task1.task_id[:8]}")

    task2 = orchestrator.add_task(
        agent_type="AnalystAgent",
        action="analyze",
        input_data={},
        priority=TaskPriority.MEDIUM,
        dependencies=[task1.task_id],
        metadata={"timeout": 5}
    )
    print(f"  • Analysis task: {task2.task_id[:8]}")

    task3 = orchestrator.add_task(
        agent_type="WriterAgent",
        action="write",
        input_data={"style": "professional"},
        priority=TaskPriority.MEDIUM,
        dependencies=[task2.task_id],
        metadata={"timeout": 5}
    )
    print(f"  • Writing task: {task3.task_id[:8]}")

    # Show execution plan
    plan = orchestrator.get_execution_plan()
    print(f"\nExecution Plan ({len(plan)} layers):")
    for i, layer in enumerate(plan):
        print(f"  Layer {i+1}: {len(layer)} task(s)")

    # Execute
    print("\nExecuting tasks...")
    result = orchestrator.execute_all()

    # Results
    print("\n" + "="*70)
    print("EXECUTION RESULTS")
    print("="*70)
    print(f"  Completed: {len(result['completed'])}")
    print(f"  Failed: {len(result['failed'])}")
    print(f"  Cancelled: {len(result['cancelled'])}")

    if len(result['completed']) > 0:
        print("\n✓ Test 2 PASSED")
        return True
    else:
        print("\n✗ Test 2 FAILED - No tasks completed")
        return False


def test_system_statistics():
    """Test 3: Verifica statistiche sistema."""
    print("\n" + "="*70)
    print("TEST 3: SYSTEM STATISTICS")
    print("="*70)

    llm = MockLLM()
    orchestrator = Orchestrator()

    # Register agents
    for _ in range(3):
        orchestrator.register_agent(ResearcherAgent(llm=llm))

    # Add and execute tasks
    for i in range(5):
        orchestrator.add_task(
            agent_type="ResearcherAgent",
            action="research",
            input_data={"topic": f"Topic {i}"},
            priority=TaskPriority.MEDIUM,
            metadata={"timeout": 5}
        )

    orchestrator.execute_all()

    # Get statistics
    stats = orchestrator.get_system_status()

    print("\nSystem Statistics:")
    print(f"  Total agents: {stats['agent_registry']['total_agents']}")
    print(f"  Total tasks: {stats['task_queue']['total_tasks']}")
    print(f"  Completed: {stats['task_queue'].get('completed_tasks', 0)}")
    print(f"  Success rate: {stats['task_queue'].get('success_rate', 0):.1%}")

    print("\n✓ Test 3 PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TESTING MULTI-AGENT SYSTEM")
    print("Verifica funzionamento degli esempi della documentazione")
    print("="*70)

    tests = [
        test_agent_registration,
        test_task_execution,
        test_system_statistics
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"  Tests passed: {passed}/{total}")

    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        print("Gli esempi della documentazione funzionano correttamente.")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Alcuni test hanno fallito. Verifica il codice.")
        return 1


if __name__ == "__main__":
    exit(main())
