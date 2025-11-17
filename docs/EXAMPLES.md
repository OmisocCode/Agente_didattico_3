# Esempi Pratici - Sistema Multi-Agente

## Indice
- [Quick Start](#quick-start)
- [Esempi Base](#esempi-base)
- [Workflow Avanzati](#workflow-avanzati)
- [Casi d'Uso Reali](#casi-duso-reali)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Installazione e Setup

```bash
# Clone repository
git clone https://github.com/your-org/agente_didattico_3.git
cd agente_didattico_3

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### Configurazione .env

```bash
# LLM Provider (ollama | openai | groq)
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# Groq Configuration (optional)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-70b-versatile

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# System Configuration
LOG_LEVEL=INFO
SYSTEM_NAME=MultiAgentSystem
```

### Primo Programma

```python
from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from agents.researcher_agent import ResearcherAgent

# Setup
config = get_config()
llm = LLMFactory.create_llm(config)

# Create orchestrator
orchestrator = Orchestrator()

# Create and register agent
researcher = ResearcherAgent(llm=llm)
orchestrator.register_agent(researcher)

# Execute simple research
from core.task_queue import TaskPriority

task = orchestrator.add_task(
    agent_type="ResearcherAgent",
    action="research",
    input_data={"topic": "Quantum Computing"},
    priority=TaskPriority.HIGH
)

# Execute
result = orchestrator.execute_all()
print(result)
```

## Esempi Base

### Esempio 1: Single Agent Task

```python
"""
Esempio: Eseguire un singolo task con un agente.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from core.llm import LLMFactory
from core.message_bus import MessageBus
from core.shared_memory import SharedMemory
from agents.researcher_agent import ResearcherAgent

def main():
    # Setup
    config = get_config()
    llm = LLMFactory.create_llm(config)

    # Create infrastructure
    message_bus = MessageBus()
    shared_memory = SharedMemory()

    # Create agent
    researcher = ResearcherAgent(llm=llm)
    researcher.message_bus = message_bus
    researcher.shared_memory = shared_memory

    # Register with message bus
    message_bus.register_agent(researcher.agent_id)

    # Execute research
    print("Starting research...")
    result = researcher.research(
        topic="Artificial Intelligence in Healthcare",
        depth="medium",
        max_sources=5
    )

    # Display results
    print("\n" + "="*70)
    print("RESEARCH RESULTS")
    print("="*70)
    print(f"\nTopic: {result['topic']}")
    print(f"\nContent:\n{result['main_content']}")
    print(f"\nKey Points:")
    for point in result['key_points']:
        print(f"  • {point}")

if __name__ == "__main__":
    main()
```

### Esempio 2: Multi-Agent Collaboration

```python
"""
Esempio: Collaborazione tra multiple agenti.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from core.task_queue import TaskPriority
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent

def main():
    print("="*70)
    print("MULTI-AGENT COLLABORATION EXAMPLE")
    print("="*70)

    # Setup
    config = get_config()
    llm = LLMFactory.create_llm(config)
    orchestrator = Orchestrator()

    # Create and register agents
    researcher = ResearcherAgent(llm=llm)
    analyst = AnalystAgent(llm=llm)
    writer = WriterAgent(llm=llm)

    orchestrator.register_agent(researcher)
    orchestrator.register_agent(analyst)
    orchestrator.register_agent(writer)

    print(f"\n✓ Registered {len(orchestrator.agent_registry.get_all_agents())} agents")

    # Add tasks with dependencies
    print("\nAdding tasks...")

    # Task 1: Research
    task1 = orchestrator.add_task(
        agent_type="ResearcherAgent",
        action="research",
        input_data={
            "topic": "Future of AI",
            "depth": "deep"
        },
        priority=TaskPriority.HIGH
    )
    print(f"  • Research task: {task1.task_id[:8]}")

    # Task 2: Analysis (depends on research)
    task2 = orchestrator.add_task(
        agent_type="AnalystAgent",
        action="analyze",
        input_data={},  # Will use research output
        priority=TaskPriority.MEDIUM,
        dependencies=[task1.task_id]
    )
    print(f"  • Analysis task: {task2.task_id[:8]}")

    # Task 3: Writing (depends on analysis)
    task3 = orchestrator.add_task(
        agent_type="WriterAgent",
        action="write",
        input_data={
            "style": "professional"
        },
        priority=TaskPriority.MEDIUM,
        dependencies=[task2.task_id]
    )
    print(f"  • Writing task: {task3.task_id[:8]}")

    # Show execution plan
    plan = orchestrator.get_execution_plan()
    print(f"\nExecution Plan ({len(plan)} layers):")
    for i, layer in enumerate(plan):
        print(f"  Layer {i+1}: {len(layer)} task(s)")

    # Execute all tasks
    print("\nExecuting tasks...")
    result = orchestrator.execute_all()

    # Display results
    print("\n" + "="*70)
    print("EXECUTION RESULTS")
    print("="*70)
    print(f"  Completed: {len(result['completed'])}")
    print(f"  Failed: {len(result['failed'])}")
    print(f"  Cancelled: {len(result['cancelled'])}")

    # System statistics
    stats = orchestrator.get_system_status()
    print("\n" + "="*70)
    print("SYSTEM STATISTICS")
    print("="*70)
    print(f"  Total agents: {stats['agent_registry']['total_agents']}")
    print(f"  Total tasks: {stats['task_queue']['total_tasks']}")
    print(f"  Success rate: {stats['task_queue']['success_rate']:.1%}")

if __name__ == "__main__":
    main()
```

### Esempio 3: Using Workflow YAML

```python
"""
Esempio: Esecuzione workflow da file YAML.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from core.workflow_engine import WorkflowEngine
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent

def main():
    print("="*70)
    print("WORKFLOW YAML EXAMPLE")
    print("="*70)

    # Setup
    config = get_config()
    llm = LLMFactory.create_llm(config)
    orchestrator = Orchestrator()

    # Register agents
    orchestrator.register_agent(ResearcherAgent(llm=llm))
    orchestrator.register_agent(AnalystAgent(llm=llm))
    orchestrator.register_agent(WriterAgent(llm=llm))

    print(f"\n✓ Registered agents")

    # Create workflow engine
    engine = WorkflowEngine(orchestrator)

    # Load workflow
    workflow_path = Path(__file__).parent.parent / "workflows" / "quick_analysis.yaml"

    if not workflow_path.exists():
        print(f"✗ Workflow not found: {workflow_path}")
        return

    print(f"\nLoading workflow: {workflow_path.name}")
    workflow = engine.load_workflow(workflow_path)

    print(f"✓ Loaded: {workflow['name']}")
    print(f"  Description: {workflow.get('description', 'N/A')}")
    print(f"  Steps: {len(workflow['steps'])}")

    # Get workflow info
    info = engine.get_workflow_info(workflow['name'])
    print(f"\nWorkflow Parameters:")
    for param in info['parameters']:
        print(f"  • {param}")

    # Execute workflow with custom parameters
    print("\nExecuting workflow...")
    result = engine.execute_workflow(
        workflow['name'],
        parameters={
            "topic": "Blockchain Technology",
            "priority_level": "high"
        }
    )

    # Display results
    print("\n" + "="*70)
    print("WORKFLOW RESULTS")
    print("="*70)
    print(f"  Status: {result['status']}")
    print(f"  Execution time: {result['execution_time']:.2f}s")
    print(f"  Steps completed: {len(result['results'])}")

    print("\nStep Results:")
    for step_id, step_result in result['results'].items():
        print(f"  • {step_id}: {step_result['status']}")

    print("\n" + "="*70)
    print("OUTPUT")
    print("="*70)
    print(result['output'])

if __name__ == "__main__":
    main()
```

## Workflow Avanzati

### Esempio 4: Custom Workflow Creation

```python
"""
Esempio: Creazione workflow programmaticamente.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from core.workflow_engine import WorkflowEngine
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent
from agents.fact_checker_agent import FactCheckerAgent

def create_custom_workflow():
    """Create a custom blog post generation workflow."""
    return {
        "name": "Blog Post Generator",
        "description": "Generate SEO-optimized blog post",
        "version": "1.0",

        "parameters": {
            "topic": "Technology Trends",
            "keywords": ["AI", "automation", "innovation"],
            "word_count": 1000,
            "style": "professional"
        },

        "steps": [
            {
                "id": "keyword_research",
                "agent_type": "ResearcherAgent",
                "action": "research",
                "params": {
                    "topic": "{{ parameters.topic }}",
                    "depth": "medium"
                },
                "priority": "high",
                "timeout": 120,
                "description": "Research topic and keywords"
            },
            {
                "id": "content_draft",
                "agent_type": "WriterAgent",
                "action": "write",
                "depends_on": ["keyword_research"],
                "params": {
                    "content": "{{ steps.keyword_research.output }}",
                    "style": "{{ parameters.style }}",
                    "max_length": "{{ parameters.word_count }}"
                },
                "priority": "high",
                "timeout": 180,
                "description": "Write initial draft"
            },
            {
                "id": "fact_check",
                "agent_type": "FactCheckerAgent",
                "action": "verify",
                "depends_on": ["content_draft"],
                "params": {
                    "claims": "{{ steps.content_draft.output }}"
                },
                "priority": "medium",
                "timeout": 120,
                "description": "Verify claims in draft"
            },
            {
                "id": "content_analysis",
                "agent_type": "AnalystAgent",
                "action": "analyze",
                "depends_on": ["content_draft"],
                "params": {
                    "data": "{{ steps.content_draft.output }}"
                },
                "priority": "medium",
                "timeout": 90,
                "description": "Analyze content quality"
            },
            {
                "id": "final_version",
                "agent_type": "WriterAgent",
                "action": "write",
                "depends_on": ["fact_check", "content_analysis"],
                "params": {
                    "content": "{{ steps.content_draft.output }}",
                    "verification": "{{ steps.fact_check.output }}",
                    "analysis": "{{ steps.content_analysis.output }}"
                },
                "priority": "high",
                "timeout": 120,
                "description": "Create final version"
            }
        ],

        "output": {
            "blog_post": "{{ steps.final_version.output }}",
            "quality_score": "{{ steps.content_analysis.output.quality_score }}",
            "fact_check_status": "{{ steps.fact_check.output.overall_credibility }}"
        }
    }

def main():
    print("="*70)
    print("CUSTOM WORKFLOW CREATION EXAMPLE")
    print("="*70)

    # Setup
    config = get_config()
    llm = LLMFactory.create_llm(config)
    orchestrator = Orchestrator()

    # Register all agents
    orchestrator.register_agent(ResearcherAgent(llm=llm))
    orchestrator.register_agent(AnalystAgent(llm=llm))
    orchestrator.register_agent(WriterAgent(llm=llm))
    orchestrator.register_agent(FactCheckerAgent(llm=llm))

    # Create workflow engine
    engine = WorkflowEngine(orchestrator)

    # Create and load custom workflow
    print("\nCreating custom workflow...")
    workflow = create_custom_workflow()

    engine.load_workflow_from_dict(workflow)
    print(f"✓ Loaded: {workflow['name']}")

    # Validate
    try:
        engine._validate_workflow(workflow)
        print("✓ Workflow validation passed")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return

    # Execute
    print("\nExecuting workflow...")
    result = engine.execute_workflow(
        "Blog Post Generator",
        parameters={
            "topic": "Future of Artificial Intelligence",
            "word_count": 1500,
            "style": "technical"
        }
    )

    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Status: {result['status']}")
    print(f"Time: {result['execution_time']:.2f}s")

    print("\nOutput Structure:")
    for key in result['output'].keys():
        print(f"  • {key}")

if __name__ == "__main__":
    main()
```

### Esempio 5: Parallel Execution

```python
"""
Esempio: Esecuzione parallela di task indipendenti.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from core.task_queue import TaskPriority
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
import time

def main():
    print("="*70)
    print("PARALLEL EXECUTION EXAMPLE")
    print("="*70)

    # Setup
    config = get_config()
    llm = LLMFactory.create_llm(config)
    orchestrator = Orchestrator()

    # Register multiple instances of same agent type
    for i in range(3):
        orchestrator.register_agent(ResearcherAgent(llm=llm))

    orchestrator.register_agent(AnalystAgent(llm=llm))

    print(f"\n✓ Registered {len(orchestrator.agent_registry.get_all_agents())} agents")

    # Add parallel research tasks
    print("\nAdding parallel research tasks...")
    research_tasks = []

    topics = [
        "Artificial Intelligence",
        "Quantum Computing",
        "Blockchain Technology"
    ]

    for topic in topics:
        task = orchestrator.add_task(
            agent_type="ResearcherAgent",
            action="research",
            input_data={"topic": topic, "depth": "medium"},
            priority=TaskPriority.HIGH
        )
        research_tasks.append(task)
        print(f"  • Research: {topic} ({task.task_id[:8]})")

    # Add aggregation task (depends on all research)
    aggregation_task = orchestrator.add_task(
        agent_type="AnalystAgent",
        action="analyze",
        input_data={"analysis_type": "aggregation"},
        priority=TaskPriority.MEDIUM,
        dependencies=[task.task_id for task in research_tasks]
    )
    print(f"  • Aggregation ({aggregation_task.task_id[:8]})")

    # Show execution plan
    plan = orchestrator.get_execution_plan()
    print(f"\nExecution Plan:")
    for i, layer in enumerate(plan):
        tasks_in_layer = len(layer)
        print(f"  Layer {i+1}: {tasks_in_layer} task(s)", end="")
        if tasks_in_layer > 1:
            print(" (PARALLEL EXECUTION)")
        else:
            print()

    # Execute
    print("\nExecuting...")
    start = time.time()
    result = orchestrator.execute_all()
    duration = time.time() - start

    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Execution time: {duration:.2f}s")
    print(f"Tasks completed: {len(result['completed'])}")
    print(f"Tasks failed: {len(result['failed'])}")

    # Note: With real parallel execution, should be ~50% faster
    print("\nNote: Parallel tasks in Layer 1 can execute simultaneously,")
    print("reducing total execution time compared to sequential execution.")

if __name__ == "__main__":
    main()
```

## Casi d'Uso Reali

### Caso d'Uso 1: Content Marketing Pipeline

```python
"""
Caso d'uso: Pipeline automatica per content marketing.

Workflow:
1. Keyword research
2. Competitor analysis
3. Content outline
4. Draft creation
5. SEO optimization
6. Fact checking
7. Final editing
"""

def create_content_marketing_workflow():
    return {
        "name": "Content Marketing Pipeline",
        "description": "Automated content creation pipeline",
        "version": "1.0",

        "parameters": {
            "topic": "AI in Business",
            "target_keywords": ["AI", "automation", "business"],
            "competitors": ["competitor1.com", "competitor2.com"],
            "word_count": 2000,
            "tone": "professional"
        },

        "steps": [
            # Phase 1: Research (Parallel)
            {
                "id": "keyword_research",
                "agent_type": "ResearcherAgent",
                "action": "research",
                "params": {
                    "topic": "SEO keywords for {{ parameters.topic }}",
                    "depth": "deep"
                },
                "priority": "high"
            },
            {
                "id": "competitor_analysis",
                "agent_type": "AnalystAgent",
                "action": "analyze",
                "params": {
                    "data": "{{ parameters.competitors }}",
                    "analysis_type": "competitive"
                },
                "priority": "high"
            },
            {
                "id": "trend_research",
                "agent_type": "ResearcherAgent",
                "action": "research",
                "params": {
                    "topic": "Current trends in {{ parameters.topic }}",
                    "depth": "medium"
                },
                "priority": "medium"
            },

            # Phase 2: Planning
            {
                "id": "content_outline",
                "agent_type": "CoordinatorAgent",
                "action": "create_plan",
                "depends_on": [
                    "keyword_research",
                    "competitor_analysis",
                    "trend_research"
                ],
                "params": {
                    "keywords": "{{ steps.keyword_research.output }}",
                    "competitors": "{{ steps.competitor_analysis.output }}",
                    "trends": "{{ steps.trend_research.output }}"
                },
                "priority": "high"
            },

            # Phase 3: Content Creation
            {
                "id": "draft_creation",
                "agent_type": "WriterAgent",
                "action": "write",
                "depends_on": ["content_outline"],
                "params": {
                    "outline": "{{ steps.content_outline.output }}",
                    "word_count": "{{ parameters.word_count }}",
                    "tone": "{{ parameters.tone }}"
                },
                "priority": "high"
            },

            # Phase 4: Quality Assurance (Parallel)
            {
                "id": "fact_verification",
                "agent_type": "FactCheckerAgent",
                "action": "verify",
                "depends_on": ["draft_creation"],
                "params": {
                    "claims": "{{ steps.draft_creation.output }}"
                },
                "priority": "high"
            },
            {
                "id": "content_analysis",
                "agent_type": "AnalystAgent",
                "action": "analyze",
                "depends_on": ["draft_creation"],
                "params": {
                    "data": "{{ steps.draft_creation.output }}",
                    "analysis_type": "quality"
                },
                "priority": "medium"
            },

            # Phase 5: Finalization
            {
                "id": "final_editing",
                "agent_type": "WriterAgent",
                "action": "write",
                "depends_on": ["fact_verification", "content_analysis"],
                "params": {
                    "content": "{{ steps.draft_creation.output }}",
                    "feedback": {
                        "facts": "{{ steps.fact_verification.output }}",
                        "quality": "{{ steps.content_analysis.output }}"
                    }
                },
                "priority": "high"
            }
        ],

        "output": {
            "final_content": "{{ steps.final_editing.output }}",
            "seo_keywords": "{{ steps.keyword_research.output.key_points }}",
            "quality_score": "{{ steps.content_analysis.output.quality_score }}",
            "fact_check_status": "{{ steps.fact_verification.output.overall_credibility }}",
            "metadata": {
                "topic": "{{ parameters.topic }}",
                "word_count": "{{ parameters.word_count }}",
                "execution_time": "{{ execution_time }}"
            }
        }
    }

# Usage
if __name__ == "__main__":
    # Setup (same as previous examples)
    # ...

    workflow = create_content_marketing_workflow()
    engine.load_workflow_from_dict(workflow)

    result = engine.execute_workflow(
        "Content Marketing Pipeline",
        parameters={
            "topic": "AI in Healthcare",
            "word_count": 2500
        }
    )
```

### Caso d'Uso 2: Automated Research Report

```python
"""
Caso d'uso: Report di ricerca automatizzato.

Workflow:
1. Multi-source research
2. Data aggregation
3. Statistical analysis
4. Fact verification
5. Report generation
"""

# Similar structure to above examples
# See workflows/deep_research.yaml for complete example
```

## Troubleshooting

### Problem: LLM Connection Error

```python
# Error
"""
ConnectionError: Failed to connect to Ollama at http://localhost:11434
"""

# Solution
# 1. Check if Ollama is running
import subprocess
subprocess.run(["ollama", "serve"])

# 2. Or use alternative provider
# Edit .env:
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_api_key
```

### Problem: Circular Dependency

```python
# Error
"""
CircularDependencyError: Adding dependency would create a cycle
"""

# Solution
# Check workflow dependencies
from core.workflow_engine import WorkflowEngine

workflow = {
    "steps": [
        {"id": "A", "depends_on": ["B"]},  # A depends on B
        {"id": "B", "depends_on": ["A"]}   # B depends on A - CIRCULAR!
    ]
}

# Fix: Remove circular dependency
workflow = {
    "steps": [
        {"id": "A"},                       # A has no deps
        {"id": "B", "depends_on": ["A"]}   # B depends on A - OK
    ]
}
```

### Problem: Task Timeout

```python
# Error
"""
Task execution failed: Agent did not respond in time
"""

# Solution
# Increase timeout in workflow
workflow = {
    "steps": [
        {
            "id": "long_task",
            "timeout": 600,  # Increase to 10 minutes
            # ...
        }
    ]
}
```

### Problem: Agent Not Found

```python
# Error
"""
No available agent found for task (type: ResearcherAgent)
"""

# Solution
# Make sure agent is registered
orchestrator = Orchestrator()
researcher = ResearcherAgent(llm=llm)
orchestrator.register_agent(researcher)  # Don't forget this!

# Verify registration
agents = orchestrator.agent_registry.get_all_agents()
print(f"Registered: {[a.agent_type for a in agents]}")
```

## See Also

- [System Overview](SYSTEM_OVERVIEW.md)
- [Architecture](ARCHITECTURE.md)
- [Workflow Guide](WORKFLOW_GUIDE.md)
- [API Reference](API_REFERENCE.md)
