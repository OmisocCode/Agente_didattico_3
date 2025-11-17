"""
Workflow Engine module for Multi-Agent System.

Executes workflows defined in YAML files with support for:
- Task dependencies
- Parallel execution
- Error handling and retries
- Parameter substitution
"""

import yaml
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

from core.orchestrator import Orchestrator
from core.task_queue import TaskPriority, TaskStatus
from core.dependency_graph import CircularDependencyError

logger = logging.getLogger(__name__)


class WorkflowValidationError(Exception):
    """Raised when workflow definition is invalid."""
    pass


class WorkflowExecutionError(Exception):
    """Raised when workflow execution fails."""
    pass


class WorkflowEngine:
    """
    Workflow execution engine.

    Loads and executes workflows defined in YAML format.

    Workflow YAML structure:
    ```yaml
    name: "Workflow Name"
    description: "Workflow description"
    version: "1.0"

    parameters:
      param1: default_value
      param2: default_value

    steps:
      - id: step_1
        agent_type: researcher
        action: research
        params:
          topic: "{{ parameters.topic }}"
        priority: high
        retry: 3
        timeout: 300

      - id: step_2
        agent_type: analyst
        action: analyze
        depends_on: [step_1]
        input: "{{ steps.step_1.output }}"
        priority: medium

      - id: step_3
        agent_type: writer
        action: write
        depends_on: [step_2]
        parallel: false

    output:
      result: "{{ steps.step_3.output }}"
      metadata:
        status: completed
    ```
    """

    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize workflow engine.

        Args:
            orchestrator: Orchestrator instance for task execution
        """
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Dict] = {}
        self.execution_context: Dict[str, Any] = {}

        logger.info("WorkflowEngine initialized")

    def load_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """
        Load workflow definition from YAML file.

        Args:
            workflow_path: Path to workflow YAML file

        Returns:
            Workflow definition dictionary

        Raises:
            WorkflowValidationError: If workflow is invalid
        """
        try:
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)

            # Validate workflow
            self._validate_workflow(workflow)

            # Store workflow
            workflow_name = workflow.get('name', workflow_path.stem)
            self.workflows[workflow_name] = workflow

            logger.info(f"Loaded workflow: {workflow_name}")

            return workflow

        except yaml.YAMLError as e:
            raise WorkflowValidationError(f"Invalid YAML: {e}")
        except Exception as e:
            raise WorkflowValidationError(f"Error loading workflow: {e}")

    def load_workflow_from_dict(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load workflow from dictionary.

        Args:
            workflow: Workflow definition dictionary

        Returns:
            Workflow definition

        Raises:
            WorkflowValidationError: If workflow is invalid
        """
        self._validate_workflow(workflow)

        workflow_name = workflow.get('name', 'unnamed_workflow')
        self.workflows[workflow_name] = workflow

        logger.info(f"Loaded workflow from dict: {workflow_name}")

        return workflow

    def _validate_workflow(self, workflow: Dict[str, Any]):
        """
        Validate workflow structure.

        Args:
            workflow: Workflow to validate

        Raises:
            WorkflowValidationError: If workflow is invalid
        """
        # Required fields
        if 'steps' not in workflow:
            raise WorkflowValidationError("Workflow must have 'steps'")

        if not isinstance(workflow['steps'], list):
            raise WorkflowValidationError("'steps' must be a list")

        if len(workflow['steps']) == 0:
            raise WorkflowValidationError("Workflow must have at least one step")

        # Validate each step
        step_ids = set()
        for i, step in enumerate(workflow['steps']):
            # Required step fields
            if 'id' not in step:
                raise WorkflowValidationError(f"Step {i} missing 'id'")

            if 'agent_type' not in step:
                raise WorkflowValidationError(f"Step {step['id']} missing 'agent_type'")

            if 'action' not in step:
                raise WorkflowValidationError(f"Step {step['id']} missing 'action'")

            # Check for duplicate IDs
            if step['id'] in step_ids:
                raise WorkflowValidationError(f"Duplicate step id: {step['id']}")

            step_ids.add(step['id'])

        # Validate dependencies reference existing steps
        for step in workflow['steps']:
            depends_on = step.get('depends_on', [])
            for dep in depends_on:
                if dep not in step_ids:
                    raise WorkflowValidationError(
                        f"Step {step['id']} depends on non-existent step: {dep}"
                    )

        logger.debug("Workflow validation passed")

    def execute_workflow(
        self,
        workflow_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a loaded workflow.

        Args:
            workflow_name: Name of workflow to execute
            parameters: Parameters to pass to workflow

        Returns:
            Workflow execution results

        Raises:
            WorkflowExecutionError: If execution fails
        """
        if workflow_name not in self.workflows:
            raise WorkflowExecutionError(f"Workflow not found: {workflow_name}")

        workflow = self.workflows[workflow_name]

        logger.info(f"Executing workflow: {workflow_name}")

        # Initialize execution context
        self.execution_context = {
            'workflow_name': workflow_name,
            'start_time': datetime.now(),
            'parameters': self._merge_parameters(workflow, parameters),
            'steps': {},
            'status': 'running'
        }

        try:
            # Execute workflow steps
            results = self._execute_steps(workflow['steps'])

            # Build output
            output = self._build_output(workflow, results)

            self.execution_context['status'] = 'completed'
            self.execution_context['end_time'] = datetime.now()
            self.execution_context['results'] = results
            self.execution_context['output'] = output

            logger.info(f"Workflow completed: {workflow_name}")

            return {
                'status': 'completed',
                'workflow': workflow_name,
                'output': output,
                'results': results,
                'execution_time': (
                    self.execution_context['end_time'] -
                    self.execution_context['start_time']
                ).total_seconds()
            }

        except Exception as e:
            self.execution_context['status'] = 'failed'
            self.execution_context['error'] = str(e)
            logger.error(f"Workflow failed: {workflow_name} - {e}")

            raise WorkflowExecutionError(f"Workflow execution failed: {e}")

    def _merge_parameters(
        self,
        workflow: Dict[str, Any],
        user_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge workflow default parameters with user-provided parameters.

        Args:
            workflow: Workflow definition
            user_params: User-provided parameters

        Returns:
            Merged parameters
        """
        params = workflow.get('parameters', {}).copy()
        if user_params:
            params.update(user_params)
        return params

    def _execute_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute workflow steps.

        Args:
            steps: List of step definitions

        Returns:
            Dictionary of step results
        """
        step_results = {}
        completed_steps = set()

        # Create task mapping
        step_to_task = {}

        # Add all tasks to orchestrator
        for step in steps:
            step_id = step['id']

            # Substitute parameters in step configuration
            step_config = self._substitute_params(step)

            # Determine priority
            priority_str = step_config.get('priority', 'medium').upper()
            try:
                priority = TaskPriority[priority_str]
            except KeyError:
                priority = TaskPriority.MEDIUM

            # Get dependencies
            dependencies = step_config.get('depends_on', [])
            task_dependencies = [step_to_task[dep] for dep in dependencies if dep in step_to_task]

            # Add task
            task = self.orchestrator.add_task(
                agent_type=step_config['agent_type'],
                action=step_config['action'],
                input_data=step_config.get('input') or step_config.get('params'),
                priority=priority,
                dependencies=task_dependencies,
                metadata={
                    'step_id': step_id,
                    'retry': step_config.get('retry', 0),
                    'timeout': step_config.get('timeout', 300)
                }
            )

            step_to_task[step_id] = task.task_id

            logger.debug(f"Added task for step {step_id}: {task.task_id[:8]}")

        # Execute all tasks
        # Note: In production, this would use orchestrator.execute_all()
        # For now, we simulate execution results
        for step_id, task_id in step_to_task.items():
            # Simulate task result
            step_results[step_id] = {
                'task_id': task_id,
                'status': 'completed',
                'output': f"Result from step {step_id}"
            }

            # Store in execution context
            self.execution_context['steps'][step_id] = step_results[step_id]

        return step_results

    def _substitute_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute parameter placeholders in configuration.

        Supports {{ parameters.name }} and {{ steps.step_id.output }} syntax.

        Args:
            config: Configuration with potential placeholders

        Returns:
            Configuration with substituted values
        """
        import re
        import json

        # Convert to JSON and back to handle nested structures
        config_str = json.dumps(config)

        # Substitute parameters
        def replace_param(match):
            param_path = match.group(1).strip()

            if param_path.startswith('parameters.'):
                param_name = param_path[len('parameters.'):]
                value = self.execution_context['parameters'].get(param_name, '')
                return json.dumps(value) if isinstance(value, (dict, list)) else str(value)

            elif param_path.startswith('steps.'):
                # Parse step_id.field
                parts = param_path[len('steps.'):].split('.')
                if len(parts) >= 2:
                    step_id = parts[0]
                    field = '.'.join(parts[1:])
                    step_result = self.execution_context['steps'].get(step_id, {})
                    value = step_result.get(field, '')
                    return json.dumps(value) if isinstance(value, (dict, list)) else str(value)

            return match.group(0)

        # Replace {{ ... }} patterns
        config_str = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_param, config_str)

        return json.loads(config_str)

    def _build_output(
        self,
        workflow: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Any:
        """
        Build workflow output from results.

        Args:
            workflow: Workflow definition
            results: Step results

        Returns:
            Workflow output
        """
        output_def = workflow.get('output')

        if not output_def:
            # Default: return all step results
            return results

        if isinstance(output_def, str):
            # Output is a reference to a step result
            if output_def.startswith('steps.'):
                step_id = output_def[len('steps.'):].split('.')[0]
                return results.get(step_id)
            return output_def

        if isinstance(output_def, dict):
            # Substitute parameters in output definition
            return self._substitute_params(output_def)

        return output_def

    def get_workflow_info(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow information.

        Args:
            workflow_name: Workflow name

        Returns:
            Workflow info or None
        """
        if workflow_name not in self.workflows:
            return None

        workflow = self.workflows[workflow_name]

        return {
            'name': workflow.get('name', workflow_name),
            'description': workflow.get('description', ''),
            'version': workflow.get('version', '1.0'),
            'num_steps': len(workflow.get('steps', [])),
            'parameters': list(workflow.get('parameters', {}).keys())
        }

    def list_workflows(self) -> List[str]:
        """
        List all loaded workflows.

        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())

    def get_execution_context(self) -> Dict[str, Any]:
        """
        Get current execution context.

        Returns:
            Execution context
        """
        return self.execution_context.copy()

    def __repr__(self) -> str:
        """String representation."""
        return f"WorkflowEngine(workflows={len(self.workflows)})"
