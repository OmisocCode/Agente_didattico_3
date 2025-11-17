"""
Coordinator Agent for Multi-Agent System.

The Coordinator is responsible for:
- Receiving user requests
- Breaking down complex tasks into subtasks
- Assigning tasks to specialized agents
- Monitoring progress
- Aggregating results
"""

import json
import logging
from typing import Any, Dict, List, Optional
from agents.base_agent import BaseAgent
from core.llm import get_llm

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent that orchestrates the multi-agent system.

    This agent:
    - Analyzes user requests
    - Creates execution plans
    - Delegates tasks to specialized agents
    - Monitors execution
    - Synthesizes final results
    """

    def __init__(self, llm=None):
        """
        Initialize Coordinator Agent.

        Args:
            llm: LLM instance (optional, will use global if not provided)
        """
        super().__init__(
            name="Coordinator",
            capabilities=["orchestration", "planning", "delegation", "synthesis"]
        )
        self.llm = llm
        self.available_agents: Dict[str, str] = {}  # agent_id -> agent_type

    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]):
        """
        Register an agent with the coordinator.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (researcher, analyst, writer, etc.)
            capabilities: List of agent capabilities
        """
        self.available_agents[agent_id] = {
            "type": agent_type,
            "capabilities": capabilities
        }
        logger.info(f"Coordinator registered agent: {agent_type} ({agent_id[:8]}...)")

    def process(self, user_request: str) -> Dict[str, Any]:
        """
        Main processing method for coordinator.

        Args:
            user_request: The user's request/query

        Returns:
            Dictionary with final results
        """
        logger.info(f"Coordinator processing request: {user_request}")

        try:
            # Step 1: Analyze request and create plan
            plan = self.create_plan(user_request)

            # Step 2: Execute plan
            results = self.execute_plan(plan)

            # Step 3: Synthesize final result
            final_result = self.synthesize_results(results, user_request)

            return {
                "status": "success",
                "request": user_request,
                "plan": plan,
                "results": results,
                "final_output": final_result
            }

        except Exception as e:
            logger.error(f"Coordinator error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request": user_request
            }

    def create_plan(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze request and create execution plan.

        Args:
            user_request: User's request

        Returns:
            Execution plan with tasks
        """
        logger.info("Creating execution plan...")

        # Use LLM to analyze request and create plan
        llm = self.llm or get_llm()

        prompt = f"""You are a coordinator agent for a multi-agent research system.

Available agent types:
- Researcher: Searches web, collects information from multiple sources
- Analyst: Analyzes data, identifies patterns, evaluates quality
- Writer: Creates professional reports and documents
- FactChecker: Verifies claims, cross-references sources

User request: {user_request}

Create a step-by-step plan to fulfill this request. For each step, specify:
1. Which agent type to use
2. What the task is
3. Dependencies (which steps must complete first)

Respond in JSON format:
{{
    "steps": [
        {{
            "id": "step_1",
            "agent_type": "researcher",
            "task": "Research topic X",
            "depends_on": []
        }},
        ...
    ]
}}

Keep the plan concise (max 5 steps) and focused on the user's actual needs.
"""

        try:
            response = llm.generate(prompt)

            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            plan = json.loads(json_str)
            logger.info(f"Created plan with {len(plan['steps'])} steps")

            return plan

        except Exception as e:
            logger.warning(f"LLM planning failed: {e}, using fallback plan")
            # Fallback: simple sequential plan
            return {
                "steps": [
                    {
                        "id": "research",
                        "agent_type": "researcher",
                        "task": f"Research: {user_request}",
                        "depends_on": []
                    },
                    {
                        "id": "analyze",
                        "agent_type": "analyst",
                        "task": "Analyze research findings",
                        "depends_on": ["research"]
                    },
                    {
                        "id": "write",
                        "agent_type": "writer",
                        "task": "Write final report",
                        "depends_on": ["research", "analyze"]
                    }
                ]
            }

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plan by delegating to agents.

        Args:
            plan: Execution plan

        Returns:
            Results from each step
        """
        logger.info("Executing plan...")

        results = {}
        completed_steps = set()

        steps = plan.get("steps", [])

        for step in steps:
            step_id = step["id"]
            dependencies = step.get("depends_on", [])

            # Check if dependencies are met
            if not all(dep in completed_steps for dep in dependencies):
                logger.warning(f"Step {step_id} dependencies not met, skipping for now")
                continue

            # Find agent for this step
            agent_type = step["agent_type"]
            agent_id = self._find_agent_by_type(agent_type)

            if not agent_id:
                logger.warning(f"No agent found for type {agent_type}, skipping step {step_id}")
                results[step_id] = {"status": "skipped", "reason": f"No {agent_type} agent available"}
                completed_steps.add(step_id)
                continue

            # Send task to agent
            logger.info(f"Delegating step {step_id} to {agent_type} agent")

            # Gather input data from dependencies
            input_data = {
                "task": step["task"],
                "dependencies": {dep: results.get(dep) for dep in dependencies}
            }

            # Send message to agent
            self.send_message(
                receiver=agent_id,
                msg_type="task",
                content=input_data,
                metadata={"step_id": step_id, "agent_type": agent_type}
            )

            # Wait for response (with timeout)
            response = self.receive_message(timeout=30)

            if response and response.msg_type == "result":
                results[step_id] = response.content
                completed_steps.add(step_id)
                logger.info(f"Step {step_id} completed successfully")
            else:
                results[step_id] = {"status": "timeout", "reason": "Agent did not respond in time"}
                completed_steps.add(step_id)
                logger.warning(f"Step {step_id} timed out")

        return results

    def synthesize_results(self, results: Dict[str, Any], user_request: str) -> str:
        """
        Synthesize final result from all step results.

        Args:
            results: Results from each step
            user_request: Original user request

        Returns:
            Final synthesized output
        """
        logger.info("Synthesizing final results...")

        llm = self.llm or get_llm()

        # Prepare results summary
        results_text = json.dumps(results, indent=2, default=str)

        prompt = f"""You are synthesizing the final output from a multi-agent research system.

Original request: {user_request}

Results from different agents:
{results_text}

Create a coherent, professional final response that:
1. Directly addresses the user's request
2. Integrates information from all agents
3. Is well-structured and easy to read
4. Highlights key findings
5. Notes any limitations or uncertainties

Provide a concise response (max 500 words).
"""

        try:
            final_output = llm.generate(prompt)
            return final_output.strip()
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Results compiled:\n\n{results_text}"

    def _find_agent_by_type(self, agent_type: str) -> Optional[str]:
        """
        Find an agent ID by type.

        Args:
            agent_type: Type of agent to find

        Returns:
            Agent ID or None if not found
        """
        for agent_id, info in self.available_agents.items():
            if info["type"].lower() == agent_type.lower():
                return agent_id
        return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get coordinator status.

        Returns:
            Status information
        """
        return {
            "agent": self.name,
            "state": self.get_state(),
            "registered_agents": len(self.available_agents),
            "agent_types": [info["type"] for info in self.available_agents.values()],
        }
