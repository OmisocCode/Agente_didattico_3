"""
Complete Multi-Agent System Example.

This example demonstrates the full multi-agent system with:
- CoordinatorAgent orchestrating the workflow
- ResearcherAgent gathering information
- AnalystAgent analyzing data
- WriterAgent creating reports
- FactCheckerAgent verifying claims

Uses MockLLM for demonstration without requiring API keys.
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


# Mock LLM for demonstration (same as in tests)
class MockLLM:
    """Mock LLM that provides realistic responses without API calls."""

    def generate(self, prompt):
        """Generate contextual mock response."""
        prompt_lower = prompt.lower()

        if "plan" in prompt_lower and "steps" in prompt_lower:
            return '''```json
{
    "steps": [
        {
            "id": "research",
            "agent_type": "researcher",
            "task": "Research the topic comprehensively",
            "depends_on": []
        },
        {
            "id": "analyze",
            "agent_type": "analyst",
            "task": "Analyze research findings for quality and insights",
            "depends_on": ["research"]
        },
        {
            "id": "verify",
            "agent_type": "factchecker",
            "task": "Verify key claims from research",
            "depends_on": ["research", "analyze"]
        },
        {
            "id": "write",
            "agent_type": "writer",
            "task": "Write comprehensive final report",
            "depends_on": ["research", "analyze", "verify"]
        }
    ]
}
```'''

        elif "research" in prompt_lower:
            return """The impact of artificial intelligence on the job market is a complex and multifaceted topic.

Key findings show that AI is expected to automate certain job categories while creating new opportunities in others. According to industry analysis, repetitive and routine tasks are most susceptible to automation, while jobs requiring creativity, emotional intelligence, and complex decision-making are likely to remain human-dominated.

Studies indicate that AI could displace approximately 85 million jobs by 2025, but simultaneously create 97 million new roles adapted to the new division of labor between humans and machines. The net effect is projected to be positive, with more jobs created than lost, though the transition period will require significant workforce retraining and adaptation.

Key sectors affected include manufacturing, customer service, data entry, and transportation. Emerging opportunities are found in AI development, data science, robotics maintenance, and AI ethics oversight."""

        elif "analy" in prompt_lower:
            return """**Quality Assessment**: The research data demonstrates high credibility, drawing from multiple reputable sources with consistent findings across the board.

**Key Findings**:
1. AI will disrupt but not destroy the job market
2. Net job creation expected despite displacement
3. Transition will require significant retraining efforts
4. Human-AI collaboration is the most likely outcome

**Patterns**: Data shows a clear trend toward automation of routine tasks while human skills in creativity and emotional intelligence become more valuable. Historical precedents from previous technological revolutions support this pattern.

**Insights**: The most successful adaptation strategy involves continuous learning and skill development. Organizations and individuals who embrace AI as a tool rather than a replacement will thrive in the evolving landscape.

**Gaps**: Limited long-term data on AI's impact beyond 5-year projections. Regional variations and industry-specific effects need deeper analysis.

**Confidence**: High - findings are consistent across multiple authoritative sources."""

        elif "verify" in prompt_lower or "fact" in prompt_lower:
            return '''```json
{
    "verifiable": true,
    "status": "verified",
    "confidence": "high",
    "explanation": "The claim is supported by multiple credible sources including industry reports and academic studies."
}
```'''

        elif "report" in prompt_lower or "write" in prompt_lower:
            return """# The Impact of AI on the Job Market: A Comprehensive Analysis

## Executive Summary

Artificial Intelligence is reshaping the global job market in profound ways. While automation threatens certain job categories, the overall impact appears to be net positive, with more jobs being created than displaced. This report examines the evidence, analyzes the trends, and provides insights into navigating this transformative period.

## Current State of AI in Employment

The integration of AI into the workforce is accelerating across industries. Manufacturing, customer service, and data processing sectors are experiencing the most significant automation. However, this disruption is accompanied by the emergence of entirely new job categories that didn't exist a decade ago.

## Job Displacement vs. Creation

Research indicates that approximately 85 million jobs may be displaced by 2025 due to automation. However, this is counterbalanced by the projected creation of 97 million new roles. These new positions will be characterized by:

- Human-AI collaboration
- Data-driven decision making
- Creative and strategic thinking
- Emotional intelligence requirements

## The Transition Challenge

The critical issue isn't the quantity of jobs but the quality of the transition. Workers displaced from automated roles will need substantial retraining to fill newly created positions. This represents both a challenge and an opportunity for education systems and corporate training programs.

## Recommendations

1. **For Individuals**: Invest in continuous learning, focusing on skills that complement AI rather than compete with it
2. **For Organizations**: Develop comprehensive reskilling programs for affected employees
3. **For Policymakers**: Create supportive frameworks for workforce transitions

## Conclusion

The AI revolution in the job market is not a zero-sum game. With proper planning, education, and policy support, the transformation can lead to a more productive and fulfilling work environment for humanity. The key is managing the transition thoughtfully and ensuring that the benefits are widely distributed."""

        elif "synthesis" in prompt_lower or "final" in prompt_lower:
            return """Based on comprehensive multi-agent analysis, the impact of AI on the job market presents both challenges and opportunities. The research phase identified key trends in job displacement and creation, with approximately 85 million jobs at risk but 97 million new positions emerging.

The analysis confirmed high data quality and credibility across sources, with consistent patterns showing that routine tasks face automation while creative and interpersonal roles remain human-centric. Fact-checking verified the major claims with high confidence.

The final assessment indicates a net positive outcome, contingent on successful workforce transition strategies. Organizations and individuals who proactively adapt through continuous learning and AI collaboration will thrive in this evolving landscape. Policy support and education system reform are critical enablers for a smooth transition.

Key recommendation: View AI as a collaborative tool rather than a replacement, focusing human efforts on creativity, strategy, and emotional intelligence - areas where humans maintain clear advantages."""

        else:
            return "This is a contextual response based on the analysis performed by the multi-agent system."

    def chat(self, messages, **kwargs):
        """Chat interface for mock LLM."""
        last_message = messages[-1]["content"] if messages else ""
        return self.generate(last_message)


def main():
    """Run complete multi-agent system example."""
    print("=" * 70)
    print("MULTI-AGENT SYSTEM - COMPLETE WORKFLOW DEMONSTRATION")
    print("=" * 70)

    # Step 1: Initialize Infrastructure
    print("\n--- Step 1: Initialize Infrastructure ---")
    message_bus = MessageBus()
    shared_memory = SharedMemory()
    mock_llm = MockLLM()

    print("✓ MessageBus created")
    print("✓ SharedMemory created")
    print("✓ MockLLM initialized (for demo without API)")

    # Step 2: Create All Specialized Agents
    print("\n--- Step 2: Create Specialized Agents ---")

    coordinator = CoordinatorAgent(llm=mock_llm)
    researcher = ResearcherAgent(llm=mock_llm)
    analyst = AnalystAgent(llm=mock_llm)
    writer = WriterAgent(llm=mock_llm)
    fact_checker = FactCheckerAgent(llm=mock_llm)

    all_agents = [coordinator, researcher, analyst, writer, fact_checker]

    for agent in all_agents:
        print(f"✓ Created {agent.name} Agent (ID: {agent.agent_id[:8]}...)")

    # Step 3: Connect Agents to Infrastructure
    print("\n--- Step 3: Connect Agents to Infrastructure ---")

    for agent in all_agents:
        agent.message_bus = message_bus
        agent.shared_memory = shared_memory
        message_bus.register_agent(agent.agent_id)

    print(f"✓ All {len(all_agents)} agents connected")
    print(f"✓ MessageBus has {message_bus.get_statistics()['registered_agents']} registered agents")

    # Step 4: Register Agents with Coordinator
    print("\n--- Step 4: Register Agents with Coordinator ---")

    coordinator.register_agent(researcher.agent_id, "researcher", researcher.capabilities)
    coordinator.register_agent(analyst.agent_id, "analyst", analyst.capabilities)
    coordinator.register_agent(writer.agent_id, "writer", writer.capabilities)
    coordinator.register_agent(fact_checker.agent_id, "factchecker", fact_checker.capabilities)

    print(f"✓ Coordinator knows about {len(coordinator.available_agents)} agents")

    # Step 5: User Request
    print("\n--- Step 5: Process User Request ---")

    user_request = "Create a comprehensive report on the impact of AI on the job market"
    print(f"\nUser Request: \"{user_request}\"")

    # Simulate the workflow manually (since coordinator.execute_plan requires agent responses)
    print("\n--- Step 6: Execute Multi-Agent Workflow ---")

    # Research Phase
    print("\n[1/4] RESEARCH PHASE")
    print("Researcher Agent gathering information...")

    research_result = researcher.process(user_request)
    shared_memory.write("research_results", research_result, researcher.agent_id)

    print(f"✓ Research completed: {research_result['status']}")
    if research_result['status'] == 'success':
        findings = research_result.get('findings', {})
        print(f"  - Key points: {len(findings.get('key_points', []))}")
        print(f"  - Sources: {len(findings.get('sources', []))}")

    # Analysis Phase
    print("\n[2/4] ANALYSIS PHASE")
    print("Analyst Agent evaluating research...")

    analysis_input = {
        "task": "Analyze research findings",
        "dependencies": {"research": research_result}
    }
    analysis_result = analyst.process(analysis_input)
    shared_memory.write("analysis_results", analysis_result, analyst.agent_id)

    print(f"✓ Analysis completed: {analysis_result['status']}")
    if analysis_result['status'] == 'success':
        analysis_data = analysis_result.get('analysis', {})
        print(f"  - Quality score: {analysis_data.get('quality_score', 0):.2f}")
        print(f"  - Insights: {len(analysis_data.get('insights', []))}")
        print(f"  - Confidence: {analysis_data.get('confidence', 'N/A')}")

    # Fact Checking Phase
    print("\n[3/4] VERIFICATION PHASE")
    print("FactChecker Agent verifying claims...")

    fact_check_input = {
        "task": "Verify research claims",
        "dependencies": {
            "research": research_result,
            "analysis": analysis_result
        }
    }
    fact_check_result = fact_checker.process(fact_check_input)
    shared_memory.write("verification_results", fact_check_result, fact_checker.agent_id)

    print(f"✓ Verification completed: {fact_check_result['status']}")
    if fact_check_result['status'] == 'success':
        verification = fact_check_result.get('verification', {})
        print(f"  - Claims checked: {verification.get('total_claims', 0)}")
        print(f"  - Verified: {verification.get('verified_claims', 0)}")
        print(f"  - Summary: {verification.get('summary', 'N/A')}")

    # Writing Phase
    print("\n[4/4] WRITING PHASE")
    print("Writer Agent creating final report...")

    writer_input = {
        "task": user_request,
        "dependencies": {
            "research": research_result,
            "analysis": analysis_result,
            "verification": fact_check_result
        }
    }
    writer_result = writer.process(writer_input)
    shared_memory.write("final_report", writer_result, writer.agent_id)

    print(f"✓ Report completed: {writer_result['status']}")
    if writer_result['status'] == 'success':
        report = writer_result.get('report', '')
        print(f"  - Report length: {len(report)} characters")
        print(f"  - Word count: {len(report.split())} words")

    # Step 7: Display Results
    print("\n--- Step 7: Final Results ---")

    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    if writer_result['status'] == 'success':
        print("\n" + writer_result['report'])
    else:
        print(f"Error generating report: {writer_result.get('error', 'Unknown error')}")

    # Step 8: System Statistics
    print("\n--- Step 8: System Statistics ---")

    bus_stats = message_bus.get_statistics()
    print("\nMessageBus Statistics:")
    print(f"  - Total messages sent: {bus_stats['messages_sent']}")
    print(f"  - Total messages received: {bus_stats['messages_received']}")
    print(f"  - Registered agents: {bus_stats['registered_agents']}")

    memory_stats = shared_memory.get_statistics()
    print("\nSharedMemory Statistics:")
    print(f"  - Total keys: {memory_stats['total_keys']}")
    print(f"  - Total reads: {memory_stats['reads']}")
    print(f"  - Total writes: {memory_stats['writes']}")
    print(f"  - Keys: {', '.join(shared_memory.keys())}")

    print("\nAgent Performance:")
    for agent in [researcher, analyst, fact_checker, writer]:
        metrics = agent.get_metrics()
        print(f"  - {agent.name}: Completed tasks: {metrics['tasks_completed']}")

    print("\n" + "=" * 70)
    print("✓ MULTI-AGENT WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    print("\n💡 What happened:")
    print("  1. Coordinator planned the workflow")
    print("  2. Researcher gathered information on AI job market impact")
    print("  3. Analyst evaluated data quality and generated insights")
    print("  4. FactChecker verified key claims")
    print("  5. Writer created a professional final report")
    print("  6. All agents collaborated via MessageBus and SharedMemory")

    print("\n🚀 This is a Multi-Agent System in action!")


if __name__ == "__main__":
    main()
