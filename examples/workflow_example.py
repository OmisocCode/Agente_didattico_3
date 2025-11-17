"""
Workflow Engine Example.

Demonstrates how to use the WorkflowEngine to execute predefined workflows
for multi-agent tasks with complex dependencies and parallel execution.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_engine import WorkflowEngine, WorkflowValidationError, WorkflowExecutionError
from core.orchestrator import Orchestrator
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.coordinator_agent import CoordinatorAgent


# Mock LLM for demonstration
class MockLLM:
    """Mock LLM for testing without API calls."""

    def generate(self, prompt):
        """Generate mock response based on prompt content."""
        if "research" in prompt.lower():
            return """
# Research Results

Machine Learning is transforming various industries through:
- Advanced neural networks and deep learning
- Natural language processing improvements
- Computer vision applications
- Reinforcement learning in robotics

Key trends include increased model efficiency and edge computing deployment.
"""
        elif "analyze" in prompt.lower():
            return """
# Analysis

Key insights from the research:
1. ML adoption is accelerating across industries
2. Focus on efficiency and sustainability
3. Edge computing enables new use cases
4. Ethical AI considerations are crucial

Confidence: High (85%)
Quality indicators: Strong evidence, recent data, expert consensus
"""
        elif "verify" in prompt.lower() or "fact" in prompt.lower():
            return """
# Verification Results

Claims verified:
- ML adoption acceleration: VERIFIED (multiple sources)
- Efficiency improvements: VERIFIED (recent research)
- Edge computing growth: VERIFIED (industry reports)

Overall credibility: HIGH
"""
        elif "write" in prompt.lower() or "report" in prompt.lower():
            return """
# Machine Learning Industry Report

## Executive Summary
Machine Learning continues to drive innovation across multiple sectors. Our analysis
reveals accelerating adoption rates, with particular emphasis on efficiency and
edge computing applications.

## Key Findings
1. **Adoption Growth**: 45% increase in ML implementations year-over-year
2. **Efficiency Focus**: New architectures reduce computational requirements by 60%
3. **Edge Computing**: 30% of deployments now targeting edge devices
4. **Ethical Considerations**: 78% of organizations have AI ethics policies

## Conclusions
The ML landscape is maturing with focus on practical, efficient, and responsible AI
deployment. Organizations should prioritize edge computing capabilities and ethical
frameworks to remain competitive.
"""
        else:
            return "Mock response for: " + prompt[:50]

    def chat(self, messages, **kwargs):
        """Mock chat method."""
        last_message = messages[-1]["content"] if messages else ""
        return self.generate(last_message)


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def setup_agents(orchestrator: Orchestrator, llm):
    """Setup and register all specialized agents."""
    print("Setting up agents...")

    # Create agents
    coordinator = CoordinatorAgent(llm=llm)
    researcher = ResearcherAgent(llm=llm)
    analyst = AnalystAgent(llm=llm)
    writer = WriterAgent(llm=llm)
    fact_checker = FactCheckerAgent(llm=llm)

    # Register with orchestrator
    orchestrator.register_agent(coordinator)
    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)
    orchestrator.register_agent(writer)
    orchestrator.register_agent(fact_checker)

    print(f"✓ Registered {len(orchestrator.agent_registry.list_agents())} agents")
    for agent_info in orchestrator.agent_registry.list_agents():
        print(f"  - {agent_info.agent_type}: {agent_info.agent_id[:8]}...")


def example_1_quick_analysis():
    """Example 1: Quick Analysis Workflow."""
    print_section("Example 1: Quick Analysis Workflow")

    # Setup
    message_bus = MessageBus()
    shared_memory = SharedMemory()
    orchestrator = Orchestrator(message_bus, shared_memory)
    llm = MockLLM()

    setup_agents(orchestrator, llm)

    # Create workflow engine
    engine = WorkflowEngine(orchestrator)

    # Load quick analysis workflow
    workflow_path = Path(__file__).parent.parent / "workflows" / "quick_analysis.yaml"

    if workflow_path.exists():
        print(f"\nLoading workflow: {workflow_path.name}")
        workflow = engine.load_workflow(workflow_path)

        print(f"✓ Loaded: {workflow['name']}")
        print(f"  Description: {workflow.get('description', 'N/A')}")
        print(f"  Steps: {len(workflow['steps'])}")

        # Display workflow info
        info = engine.get_workflow_info("Quick Analysis")
        print(f"\nWorkflow Info:")
        print(f"  Name: {info['name']}")
        print(f"  Version: {info['version']}")
        print(f"  Parameters: {', '.join(info['parameters'])}")
        print(f"  Number of steps: {info['num_steps']}")

        # Execute with custom parameters
        print("\nExecuting workflow with custom parameters...")
        result = engine.execute_workflow(
            "Quick Analysis",
            parameters={
                "topic": "Machine Learning Industry Trends 2025",
                "priority_level": "high",
                "max_time": 300
            }
        )

        # Display results
        print(f"\n✓ Workflow completed!")
        print(f"  Status: {result['status']}")
        print(f"  Execution time: {result['execution_time']:.2f}s")
        print(f"  Steps completed: {len(result['results'])}")

        print("\nStep Results:")
        for step_id, step_result in result['results'].items():
            print(f"  - {step_id}: {step_result['status']}")

        print("\nFinal Output:")
        print(f"  {result['output']}")

    else:
        print(f"⚠ Workflow file not found: {workflow_path}")


def example_2_deep_research():
    """Example 2: Deep Research Workflow."""
    print_section("Example 2: Deep Research Workflow")

    # Setup
    orchestrator = Orchestrator()
    llm = MockLLM()
    setup_agents(orchestrator, llm)

    engine = WorkflowEngine(orchestrator)

    # Load deep research workflow
    workflow_path = Path(__file__).parent.parent / "workflows" / "deep_research.yaml"

    if workflow_path.exists():
        print(f"Loading workflow: {workflow_path.name}")
        workflow = engine.load_workflow(workflow_path)

        print(f"✓ Loaded: {workflow['name']}")

        # Execute
        print("\nExecuting comprehensive research workflow...")
        result = engine.execute_workflow(
            "Deep Research Report",
            parameters={
                "topic": "Quantum Computing Applications",
                "depth": "deep",
                "max_sources": 10
            }
        )

        print(f"\n✓ Research workflow completed!")
        print(f"  Total steps: {len(result['results'])}")
        print(f"  Execution time: {result['execution_time']:.2f}s")

        # Show workflow execution context
        context = engine.get_execution_context()
        print(f"\nExecution Context:")
        print(f"  Workflow: {context['workflow_name']}")
        print(f"  Status: {context['status']}")
        print(f"  Parameters: {context['parameters']}")

    else:
        print(f"⚠ Workflow file not found: {workflow_path}")


def example_3_parallel_research():
    """Example 3: Parallel Research Workflow."""
    print_section("Example 3: Parallel Research Workflow")

    orchestrator = Orchestrator()
    llm = MockLLM()
    setup_agents(orchestrator, llm)

    engine = WorkflowEngine(orchestrator)

    # Load parallel research workflow
    workflow_path = Path(__file__).parent.parent / "workflows" / "parallel_research.yaml"

    if workflow_path.exists():
        print(f"Loading workflow: {workflow_path.name}")
        workflow = engine.load_workflow(workflow_path)

        print(f"✓ Loaded: {workflow['name']}")
        print(f"  This workflow uses parallel execution for multiple research tasks")

        # Execute
        print("\nExecuting parallel research workflow...")
        result = engine.execute_workflow(
            "Parallel Multi-Source Research",
            parameters={
                "main_topic": "Artificial General Intelligence",
                "research_depth": "deep"
            }
        )

        print(f"\n✓ Parallel research completed!")
        print(f"  Steps executed: {len(result['results'])}")
        print(f"  Execution time: {result['execution_time']:.2f}s")

        print("\nParallel Steps (executed simultaneously):")
        parallel_steps = ["research_academic", "research_industry", "research_news"]
        for step_id in parallel_steps:
            if step_id in result['results']:
                print(f"  - {step_id}: {result['results'][step_id]['status']}")

    else:
        print(f"⚠ Workflow file not found: {workflow_path}")


def example_4_custom_workflow():
    """Example 4: Creating a Custom Workflow Programmatically."""
    print_section("Example 4: Custom Workflow Creation")

    orchestrator = Orchestrator()
    llm = MockLLM()
    setup_agents(orchestrator, llm)

    engine = WorkflowEngine(orchestrator)

    # Define custom workflow as dictionary
    custom_workflow = {
        "name": "Custom Analysis Pipeline",
        "description": "A simple custom workflow for demonstration",
        "version": "1.0",
        "parameters": {
            "subject": "Blockchain Technology",
            "analysis_focus": "security"
        },
        "steps": [
            {
                "id": "initial_research",
                "agent_type": "Researcher",
                "action": "research",
                "params": {
                    "topic": "{{ parameters.subject }}",
                    "depth": "medium"
                },
                "priority": "high",
                "description": "Gather initial information"
            },
            {
                "id": "security_analysis",
                "agent_type": "Analyst",
                "action": "analyze",
                "depends_on": ["initial_research"],
                "input": "{{ steps.initial_research.output }}",
                "params": {
                    "focus": "{{ parameters.analysis_focus }}"
                },
                "priority": "high",
                "description": "Analyze security aspects"
            },
            {
                "id": "verification",
                "agent_type": "FactChecker",
                "action": "verify",
                "depends_on": ["initial_research"],
                "priority": "medium",
                "description": "Verify findings"
            },
            {
                "id": "final_report",
                "agent_type": "Writer",
                "action": "write",
                "depends_on": ["security_analysis", "verification"],
                "params": {
                    "style": "technical",
                    "max_length": 1000
                },
                "priority": "medium",
                "description": "Generate final report"
            }
        ],
        "output": {
            "report": "{{ steps.final_report.output }}",
            "analysis": "{{ steps.security_analysis.output }}",
            "verification_status": "{{ steps.verification.output }}"
        }
    }

    # Load custom workflow
    print("Creating custom workflow from dictionary...")
    engine.load_workflow_from_dict(custom_workflow)

    print(f"✓ Custom workflow loaded: {custom_workflow['name']}")
    print(f"  Steps: {len(custom_workflow['steps'])}")

    # Validate workflow
    try:
        engine._validate_workflow(custom_workflow)
        print("✓ Workflow validation passed")
    except WorkflowValidationError as e:
        print(f"✗ Validation failed: {e}")
        return

    # Execute
    print("\nExecuting custom workflow...")
    result = engine.execute_workflow(
        "Custom Analysis Pipeline",
        parameters={
            "subject": "Blockchain in Healthcare",
            "analysis_focus": "privacy"
        }
    )

    print(f"\n✓ Custom workflow completed!")
    print(f"  Status: {result['status']}")
    print(f"  Execution time: {result['execution_time']:.2f}s")

    print("\nWorkflow Output Structure:")
    for key in result['output'].keys():
        print(f"  - {key}")


def example_5_workflow_management():
    """Example 5: Workflow Management Operations."""
    print_section("Example 5: Workflow Management")

    orchestrator = Orchestrator()
    engine = WorkflowEngine(orchestrator)

    # Load multiple workflows
    workflows_dir = Path(__file__).parent.parent / "workflows"

    if workflows_dir.exists():
        print("Loading all available workflows...")

        for workflow_file in workflows_dir.glob("*.yaml"):
            try:
                workflow = engine.load_workflow(workflow_file)
                print(f"✓ Loaded: {workflow['name']}")
            except WorkflowValidationError as e:
                print(f"✗ Failed to load {workflow_file.name}: {e}")

        # List all workflows
        print(f"\nAvailable workflows: {len(engine.list_workflows())}")
        for workflow_name in engine.list_workflows():
            info = engine.get_workflow_info(workflow_name)
            print(f"\n  {info['name']} (v{info['version']})")
            print(f"    Description: {info['description']}")
            print(f"    Steps: {info['num_steps']}")
            print(f"    Parameters: {', '.join(info['parameters']) or 'None'}")

    else:
        print(f"⚠ Workflows directory not found: {workflows_dir}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  WORKFLOW ENGINE EXAMPLES")
    print("  Multi-Agent System with YAML Workflows")
    print("=" * 70)

    try:
        # Run examples
        example_1_quick_analysis()
        example_2_deep_research()
        example_3_parallel_research()
        example_4_custom_workflow()
        example_5_workflow_management()

        print_section("Examples Completed Successfully!")
        print("Key Takeaways:")
        print("  1. Workflows can be defined in YAML files")
        print("  2. Parameter substitution with {{ parameters.name }}")
        print("  3. Dependencies ensure correct execution order")
        print("  4. Parallel execution for independent tasks")
        print("  5. Custom workflows can be created programmatically")
        print("  6. WorkflowEngine provides easy workflow management")

    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
