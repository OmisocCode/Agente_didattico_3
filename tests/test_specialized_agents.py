"""
Tests for specialized agents in the multi-agent system.

Tests all 5 specialized agents:
- CoordinatorAgent
- ResearcherAgent
- AnalystAgent
- WriterAgent
- FactCheckerAgent
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.coordinator_agent import CoordinatorAgent
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent
from agents.fact_checker_agent import FactCheckerAgent
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory


# Mock LLM for testing (doesn't require actual API)
class MockLLM:
    """Mock LLM for testing without API calls."""

    def generate(self, prompt):
        """Generate mock response."""
        if "plan" in prompt.lower() or "steps" in prompt.lower():
            # Return a simple plan
            return '''```json
{
    "steps": [
        {"id": "research", "agent_type": "researcher", "task": "Research topic", "depends_on": []},
        {"id": "analyze", "agent_type": "analyst", "task": "Analyze findings", "depends_on": ["research"]}
    ]
}
```'''
        elif "research" in prompt.lower():
            return "This is research content about the topic. It includes key findings and important information."
        elif "analy" in prompt.lower():
            return "Analysis shows high quality data with good credibility. Key insights identified."
        elif "report" in prompt.lower() or "write" in prompt.lower():
            return "# Professional Report\n\nThis is a well-structured report based on research and analysis."
        elif "verify" in prompt.lower() or "fact" in prompt.lower():
            return '```json\n{"verifiable": true, "status": "verified", "confidence": "high", "explanation": "Claim is supported by evidence."}\n```'
        else:
            return "Mock LLM response for testing purposes."

    def chat(self, messages, **kwargs):
        """Chat mock response."""
        last_message = messages[-1]["content"] if messages else ""
        return self.generate(last_message)


def test_coordinator_agent():
    """Test CoordinatorAgent."""
    print("\n=== Testing CoordinatorAgent ===")

    # Create mock LLM
    mock_llm = MockLLM()

    # Create coordinator
    coordinator = CoordinatorAgent(llm=mock_llm)

    print(f"Created: {coordinator}")
    print(f"Capabilities: {coordinator.capabilities}")

    # Register some mock agents
    coordinator.register_agent("researcher_123", "researcher", ["research"])
    coordinator.register_agent("analyst_456", "analyst", ["analysis"])

    print(f"Registered agents: {len(coordinator.available_agents)}")

    # Test create_plan
    plan = coordinator.create_plan("Research AI impact on jobs")
    print(f"Created plan with {len(plan.get('steps', []))} steps")

    assert "steps" in plan
    assert len(plan["steps"]) > 0

    print("✓ CoordinatorAgent works!")


def test_researcher_agent():
    """Test ResearcherAgent."""
    print("\n=== Testing ResearcherAgent ===")

    mock_llm = MockLLM()
    researcher = ResearcherAgent(llm=mock_llm)

    print(f"Created: {researcher}")

    # Test research
    result = researcher.process("Quantum computing")

    print(f"Research status: {result['status']}")
    print(f"Topic: {result.get('topic', 'N/A')}")

    assert result["status"] == "success"
    assert "findings" in result

    findings = result["findings"]
    print(f"Findings: {len(findings.get('key_points', []))} key points")
    print(f"Sources: {len(findings.get('sources', []))} sources")

    assert "key_points" in findings
    assert "sources" in findings

    print("✓ ResearcherAgent works!")


def test_analyst_agent():
    """Test AnalystAgent."""
    print("\n=== Testing AnalystAgent ===")

    mock_llm = MockLLM()
    analyst = AnalystAgent(llm=mock_llm)

    print(f"Created: {analyst}")

    # Create mock research data
    research_data = {
        "findings": {
            "main_content": "Research findings about AI",
            "sources": [
                {"title": "Source 1", "credibility": "high"},
                {"title": "Source 2", "credibility": "high"}
            ]
        }
    }

    # Test analysis
    result = analyst.process({"task": "Analyze", "dependencies": {"research": research_data}})

    print(f"Analysis status: {result['status']}")

    assert result["status"] == "success"
    assert "analysis" in result

    analysis = result["analysis"]
    print(f"Quality score: {analysis.get('quality_score', 'N/A')}")
    print(f"Insights: {len(analysis.get('insights', []))}")

    assert "quality_score" in analysis
    assert "insights" in analysis

    print("✓ AnalystAgent works!")


def test_writer_agent():
    """Test WriterAgent."""
    print("\n=== Testing WriterAgent ===")

    mock_llm = MockLLM()
    writer = WriterAgent(llm=mock_llm)

    print(f"Created: {writer}")

    # Create mock data
    research_data = {
        "findings": {
            "main_content": "Research about AI",
            "sources": [{"title": "Source 1"}]
        }
    }

    analysis_data = {
        "analysis": {
            "full_analysis": "Detailed analysis",
            "insights": ["Insight 1", "Insight 2"]
        }
    }

    # Test report writing
    result = writer.process({
        "task": "Write report",
        "dependencies": {
            "research": research_data,
            "analysis": analysis_data
        }
    })

    print(f"Writing status: {result['status']}")

    assert result["status"] == "success"
    assert "report" in result

    report = result["report"]
    print(f"Report length: {len(report)} characters")
    print(f"Report preview: {report[:100]}...")

    assert len(report) > 0
    assert "Report" in report or "report" in report

    print("✓ WriterAgent works!")


def test_fact_checker_agent():
    """Test FactCheckerAgent."""
    print("\n=== Testing FactCheckerAgent ===")

    mock_llm = MockLLM()
    fact_checker = FactCheckerAgent(llm=mock_llm)

    print(f"Created: {fact_checker}")

    # Test verification
    claims = ["AI will replace jobs", "Quantum computers are faster"]
    sources = [
        {"title": "Study on AI", "url": "http://example.com/1"},
        {"title": "Quantum computing research", "url": "http://example.com/2"}
    ]

    verification = fact_checker.verify_claims(claims, sources)

    print(f"Verified {verification['verified_claims']}/{verification['total_claims']} claims")
    print(f"Verification rate: {verification['verification_rate']:.2%}")
    print(f"Summary: {verification['summary']}")

    assert "verifications" in verification
    assert "verification_rate" in verification
    assert len(verification["verifications"]) > 0

    print("✓ FactCheckerAgent works!")


def test_agent_integration():
    """Test agents working together."""
    print("\n=== Testing Agent Integration ===")

    # Create infrastructure
    bus = MessageBus()
    memory = SharedMemory()
    mock_llm = MockLLM()

    # Create all agents
    researcher = ResearcherAgent(llm=mock_llm)
    analyst = AnalystAgent(llm=mock_llm)
    writer = WriterAgent(llm=mock_llm)

    # Connect to infrastructure
    for agent in [researcher, analyst, writer]:
        agent.message_bus = bus
        agent.shared_memory = memory
        bus.register_agent(agent.agent_id)

    print("✓ All agents connected to infrastructure")

    # Researcher gathers data
    research_result = researcher.process("AI impact")
    memory.write("research_data", research_result, researcher.agent_id)

    print(f"✓ Researcher completed: {research_result['status']}")

    # Analyst analyzes
    analysis_input = {
        "task": "Analyze research",
        "dependencies": {"research": research_result}
    }
    analysis_result = analyst.process(analysis_input)
    memory.write("analysis_data", analysis_result, analyst.agent_id)

    print(f"✓ Analyst completed: {analysis_result['status']}")

    # Writer creates report
    writer_input = {
        "task": "Write report",
        "dependencies": {
            "research": research_result,
            "analysis": analysis_result
        }
    }
    writer_result = writer.process(writer_input)

    print(f"✓ Writer completed: {writer_result['status']}")

    # Check shared memory
    keys = memory.keys()
    print(f"✓ Shared memory has {len(keys)} entries: {keys}")

    assert len(keys) >= 2  # At least research_data and analysis_data

    print("✓ Integration test passed!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TESTING SPECIALIZED AGENTS - PHASE 2")
    print("=" * 70)

    try:
        test_coordinator_agent()
        test_researcher_agent()
        test_analyst_agent()
        test_writer_agent()
        test_fact_checker_agent()
        test_agent_integration()

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
