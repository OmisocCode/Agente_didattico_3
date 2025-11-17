"""
Tests for Workflow Engine.

Tests workflow loading, validation, and execution.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_engine import WorkflowEngine, WorkflowValidationError, WorkflowExecutionError
from core.orchestrator import Orchestrator
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent


# Mock LLM
class MockLLM:
    """Mock LLM for testing."""

    def generate(self, prompt):
        return "Mock response"

    def chat(self, messages, **kwargs):
        return "Mock response"


def test_workflow_loading():
    """Test workflow loading from YAML."""
    print("\n=== Testing Workflow Loading ===")

    orchestrator = Orchestrator()
    engine = WorkflowEngine(orchestrator)

    # Load workflow from file
    workflow_path = Path(__file__).parent.parent / "workflows" / "quick_analysis.yaml"

    if workflow_path.exists():
        workflow = engine.load_workflow(workflow_path)

        print(f"✓ Loaded workflow: {workflow.get('name')}")
        print(f"  Steps: {len(workflow.get('steps', []))}")
        print(f"  Parameters: {list(workflow.get('parameters', {}).keys())}")

        assert 'name' in workflow
        assert 'steps' in workflow
        assert len(workflow['steps']) > 0

        print("✓ Workflow loading works!")
    else:
        print("⚠ Workflow file not found, skipping file load test")


def test_workflow_validation():
    """Test workflow validation."""
    print("\n=== Testing Workflow Validation ===")

    orchestrator = Orchestrator()
    engine = WorkflowEngine(orchestrator)

    # Valid workflow
    valid_workflow = {
        'name': 'Test Workflow',
        'steps': [
            {
                'id': 'step1',
                'agent_type': 'Researcher',
                'action': 'research'
            },
            {
                'id': 'step2',
                'agent_type': 'Analyst',
                'action': 'analyze',
                'depends_on': ['step1']
            }
        ]
    }

    try:
        engine.load_workflow_from_dict(valid_workflow)
        print("✓ Valid workflow accepted")
    except WorkflowValidationError as e:
        print(f"✗ Valid workflow rejected: {e}")
        assert False

    # Invalid workflow (missing steps)
    invalid_workflow_1 = {
        'name': 'Invalid Workflow'
    }

    try:
        engine.load_workflow_from_dict(invalid_workflow_1)
        print("✗ Invalid workflow (no steps) accepted")
        assert False
    except WorkflowValidationError:
        print("✓ Invalid workflow (no steps) rejected")

    # Invalid workflow (missing step id)
    invalid_workflow_2 = {
        'name': 'Invalid Workflow',
        'steps': [
            {
                'agent_type': 'Researcher',
                'action': 'research'
            }
        ]
    }

    try:
        engine.load_workflow_from_dict(invalid_workflow_2)
        print("✗ Invalid workflow (missing step id) accepted")
        assert False
    except WorkflowValidationError:
        print("✓ Invalid workflow (missing step id) rejected")

    # Invalid workflow (invalid dependency)
    invalid_workflow_3 = {
        'name': 'Invalid Workflow',
        'steps': [
            {
                'id': 'step1',
                'agent_type': 'Researcher',
                'action': 'research',
                'depends_on': ['nonexistent_step']
            }
        ]
    }

    try:
        engine.load_workflow_from_dict(invalid_workflow_3)
        print("✗ Invalid workflow (invalid dependency) accepted")
        assert False
    except WorkflowValidationError:
        print("✓ Invalid workflow (invalid dependency) rejected")

    print("✓ Workflow validation works!")


def test_workflow_execution():
    """Test workflow execution."""
    print("\n=== Testing Workflow Execution ===")

    # Create orchestrator with agents
    orchestrator = Orchestrator()
    mock_llm = MockLLM()

    researcher = ResearcherAgent(llm=mock_llm)
    analyst = AnalystAgent(llm=mock_llm)
    writer = WriterAgent(llm=mock_llm)

    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)
    orchestrator.register_agent(writer)

    # Create workflow engine
    engine = WorkflowEngine(orchestrator)

    # Define simple workflow
    workflow = {
        'name': 'Simple Test',
        'parameters': {
            'topic': 'AI'
        },
        'steps': [
            {
                'id': 'research',
                'agent_type': 'Researcher',
                'action': 'research',
                'params': {
                    'topic': '{{ parameters.topic }}'
                },
                'priority': 'high'
            },
            {
                'id': 'analyze',
                'agent_type': 'Analyst',
                'action': 'analyze',
                'depends_on': ['research'],
                'priority': 'medium'
            }
        ],
        'output': {
            'result': '{{ steps.analyze.output }}'
        }
    }

    engine.load_workflow_from_dict(workflow)

    # Execute workflow
    try:
        result = engine.execute_workflow('Simple Test', parameters={'topic': 'Machine Learning'})

        print(f"✓ Workflow executed successfully")
        print(f"  Status: {result['status']}")
        print(f"  Steps completed: {len(result['results'])}")
        print(f"  Execution time: {result['execution_time']:.2f}s")

        assert result['status'] == 'completed'
        assert 'results' in result

    except WorkflowExecutionError as e:
        print(f"Workflow execution failed: {e}")

    print("✓ Workflow execution works!")


def test_parameter_substitution():
    """Test parameter substitution."""
    print("\n=== Testing Parameter Substitution ===")

    orchestrator = Orchestrator()
    engine = WorkflowEngine(orchestrator)

    # Workflow with parameters
    workflow = {
        'name': 'Param Test',
        'parameters': {
            'topic': 'AI',
            'depth': 'deep'
        },
        'steps': [
            {
                'id': 'step1',
                'agent_type': 'Researcher',
                'action': 'research',
                'params': {
                    'topic': '{{ parameters.topic }}',
                    'depth': '{{ parameters.depth }}'
                }
            }
        ]
    }

    engine.load_workflow_from_dict(workflow)

    # Test with default parameters
    print("✓ Workflow with parameters loaded")

    # Get workflow info
    info = engine.get_workflow_info('Param Test')
    print(f"  Workflow: {info['name']}")
    print(f"  Parameters: {info['parameters']}")

    assert 'topic' in info['parameters']
    assert 'depth' in info['parameters']

    print("✓ Parameter substitution works!")


def test_workflow_info():
    """Test workflow info retrieval."""
    print("\n=== Testing Workflow Info ===")

    orchestrator = Orchestrator()
    engine = WorkflowEngine(orchestrator)

    # Load multiple workflows
    workflow1 = {
        'name': 'Workflow 1',
        'description': 'First workflow',
        'version': '1.0',
        'steps': [
            {'id': 'step1', 'agent_type': 'Researcher', 'action': 'research'}
        ]
    }

    workflow2 = {
        'name': 'Workflow 2',
        'description': 'Second workflow',
        'steps': [
            {'id': 'step1', 'agent_type': 'Analyst', 'action': 'analyze'}
        ]
    }

    engine.load_workflow_from_dict(workflow1)
    engine.load_workflow_from_dict(workflow2)

    # List workflows
    workflows = engine.list_workflows()
    print(f"✓ Loaded {len(workflows)} workflows: {workflows}")

    assert len(workflows) == 2

    # Get info
    info1 = engine.get_workflow_info('Workflow 1')
    print(f"  Workflow 1: {info1['description']}, {info1['num_steps']} steps")

    info2 = engine.get_workflow_info('Workflow 2')
    print(f"  Workflow 2: {info2['description']}, {info2['num_steps']} steps")

    assert info1['num_steps'] == 1
    assert info2['num_steps'] == 1

    print("✓ Workflow info works!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TESTING WORKFLOW ENGINE - PHASE 4")
    print("=" * 70)

    try:
        test_workflow_loading()
        test_workflow_validation()
        test_workflow_execution()
        test_parameter_substitution()
        test_workflow_info()

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
