# API Reference - Sistema Multi-Agente

## Indice
- [Core Components](#core-components)
- [Agents](#agents)
- [Workflow Engine](#workflow-engine)
- [Configuration](#configuration)
- [Utilities](#utilities)

## Core Components

### Orchestrator

**Module**: `core.orchestrator`

Coordinatore centrale per il sistema multi-agente.

#### Class: `Orchestrator`

```python
class Orchestrator:
    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        shared_memory: Optional[SharedMemory] = None
    )
```

**Parameters**:
- `message_bus`: MessageBus instance (creates new if None)
- `shared_memory`: SharedMemory instance (creates new if None)

**Attributes**:
- `task_queue`: TaskQueue instance
- `dependency_graph`: DependencyGraph instance
- `agent_registry`: AgentRegistry instance
- `message_bus`: MessageBus instance
- `shared_memory`: SharedMemory instance
- `running`: bool - Orchestrator status

#### Methods

##### register_agent()

```python
def register_agent(self, agent: BaseAgent) -> None
```

Registra un agente con l'orchestrator.

**Parameters**:
- `agent`: BaseAgent - Istanza dell'agente

**Example**:
```python
orchestrator = Orchestrator()
researcher = ResearcherAgent(llm=llm)
orchestrator.register_agent(researcher)
```

##### add_task()

```python
def add_task(
    self,
    agent_type: str,
    action: str,
    input_data: Any = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    dependencies: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Task
```

Aggiunge un task alla coda.

**Parameters**:
- `agent_type`: str - Tipo di agente richiesto
- `action`: str - Azione da eseguire
- `input_data`: Any - Input per il task
- `priority`: TaskPriority - Priorità del task
- `dependencies`: List[str] - Task IDs da cui dipende
- `metadata`: Dict - Metadata aggiuntivi

**Returns**: Task object

**Example**:
```python
task = orchestrator.add_task(
    agent_type="Researcher",
    action="research",
    input_data={"topic": "AI"},
    priority=TaskPriority.HIGH,
    dependencies=[]
)
```

##### execute_task()

```python
def execute_task(self, task: Task) -> bool
```

Esegue un singolo task.

**Parameters**:
- `task`: Task - Task da eseguire

**Returns**: bool - True se eseguito con successo

##### execute_all()

```python
def execute_all(self, max_iterations: int = 100) -> Dict[str, Any]
```

Esegue tutti i task in coda.

**Parameters**:
- `max_iterations`: int - Massimo numero di iterazioni

**Returns**: Dict con risultati esecuzione

**Example**:
```python
result = orchestrator.execute_all()
print(f"Completed: {len(result['completed'])}")
print(f"Failed: {len(result['failed'])}")
```

##### get_execution_plan()

```python
def get_execution_plan(self) -> List[List[str]]
```

Ottiene il piano di esecuzione (task raggruppati per layer).

**Returns**: List of execution layers

**Example**:
```python
plan = orchestrator.get_execution_plan()
for i, layer in enumerate(plan):
    print(f"Layer {i+1}: {len(layer)} tasks (parallel)")
```

##### get_system_status()

```python
def get_system_status(self) -> Dict[str, Any]
```

Ottiene lo stato completo del sistema.

**Returns**: Dict con statistiche sistema

---

### TaskQueue

**Module**: `core.task_queue`

Coda con priorità per la gestione dei task.

#### Class: `TaskQueue`

```python
class TaskQueue:
    def __init__(self)
```

#### Classes

##### TaskPriority (Enum)

```python
class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
```

##### TaskStatus (Enum)

```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

##### Task (Dataclass)

```python
@dataclass
class Task:
    priority: int
    task_id: str
    agent_type: str
    action: str
    input_data: Any
    dependencies: List[str]
    metadata: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Any
    error: Optional[str]
```

**Methods**:
- `start()`: Marca task come iniziato
- `complete(result)`: Marca task come completato
- `fail(error)`: Marca task come fallito
- `cancel()`: Cancella il task
- `get_duration()`: Ottiene durata esecuzione
- `to_dict()`: Converte a dizionario

#### Methods

##### add_task()

```python
def add_task(
    self,
    agent_type: str,
    action: str,
    input_data: Any = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    dependencies: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Task
```

##### get_next_task()

```python
def get_next_task(self, timeout: Optional[int] = None) -> Optional[Task]
```

Ottiene il prossimo task dalla coda (con priorità più alta).

**Parameters**:
- `timeout`: int - Timeout in secondi (None = blocking)

**Returns**: Task or None

##### complete_task()

```python
def complete_task(self, task_id: str, result: Any) -> None
```

##### fail_task()

```python
def fail_task(self, task_id: str, error: str) -> None
```

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

**Returns**:
```python
{
    "total_tasks": int,
    "completed_tasks": int,
    "failed_tasks": int,
    "cancelled_tasks": int,
    "pending_tasks": int,
    "in_progress_tasks": int,
    "queue_size": int,
    "success_rate": float
}
```

---

### DependencyGraph

**Module**: `core.dependency_graph`

DAG per gestione dipendenze tra task.

#### Class: `DependencyGraph`

```python
class DependencyGraph:
    def __init__(self)
```

#### Methods

##### add_node()

```python
def add_node(self, node_id: str) -> None
```

##### add_dependency()

```python
def add_dependency(self, node_id: str, depends_on: str) -> None
```

Aggiunge dipendenza: `node_id` dipende da `depends_on`.

**Raises**: `CircularDependencyError` se crea un ciclo

**Example**:
```python
graph = DependencyGraph()
graph.add_node("task1")
graph.add_node("task2")
graph.add_dependency("task2", "task1")  # task2 depends on task1
```

##### get_ready_nodes()

```python
def get_ready_nodes(self, completed: Set[str]) -> List[str]
```

Ottiene nodi pronti per l'esecuzione.

**Parameters**:
- `completed`: Set[str] - Set di nodi già completati

**Returns**: List di node IDs pronti

##### topological_sort()

```python
def topological_sort(self) -> List[str]
```

Ordine di esecuzione topologico.

**Returns**: List di node IDs in ordine

**Raises**: `CircularDependencyError` se il grafo contiene cicli

##### get_execution_layers()

```python
def get_execution_layers(self) -> List[List[str]]
```

Raggruppa nodi in layer di esecuzione (parallelizzabili).

**Returns**: List of layers

**Example**:
```python
layers = graph.get_execution_layers()
for i, layer in enumerate(layers):
    print(f"Layer {i}: {layer} (can execute in parallel)")
```

---

### AgentRegistry

**Module**: `core.agent_registry`

Registro per discovery e management degli agenti.

#### Class: `AgentRegistry`

```python
class AgentRegistry:
    def __init__(self)
```

#### Classes

##### AgentInfo (Dataclass)

```python
@dataclass
class AgentInfo:
    agent_id: str
    agent_type: str
    name: str
    capabilities: List[str]
    status: str  # "idle", "busy", "offline"
    workload: int
    total_tasks_completed: int
    total_tasks_failed: int
    registered_at: datetime
    last_active: datetime
```

**Methods**:
- `increment_workload()`: Incrementa workload
- `decrement_workload()`: Decrementa workload
- `complete_task()`: Registra task completato
- `fail_task()`: Registra task fallito
- `get_success_rate()`: Ottiene success rate (0-1)

#### Methods

##### register()

```python
def register(
    self,
    agent_id: str,
    agent_type: str,
    name: str,
    capabilities: List[str]
) -> AgentInfo
```

##### find_available_agent()

```python
def find_available_agent(
    self,
    agent_type: Optional[str] = None,
    capability: Optional[str] = None
) -> Optional[AgentInfo]
```

Trova agente disponibile con minor carico.

**Parameters**:
- `agent_type`: str - Tipo richiesto (optional)
- `capability`: str - Capability richiesta (optional)

**Returns**: AgentInfo dell'agente con minor workload

**Example**:
```python
# Find any available researcher
agent = registry.find_available_agent(agent_type="Researcher")

# Find any agent with analysis capability
agent = registry.find_available_agent(capability="analysis")
```

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

**Returns**:
```python
{
    "total_agents": int,
    "idle_agents": int,
    "busy_agents": int,
    "offline_agents": int,
    "total_agent_types": int,
    "total_capabilities": int,
    "total_tasks_processed": int,
    "total_tasks_completed": int,
    "system_success_rate": float
}
```

---

### ResultAggregator

**Module**: `core.result_aggregator`

Aggregazione risultati da multiple agenti.

#### Class: `ResultAggregator`

```python
class ResultAggregator:
    def __init__(self)
```

#### Classes

##### AggregationStrategy (Enum)

```python
class AggregationStrategy(Enum):
    CONSENSUS = "consensus"  # Majority vote
    WEIGHTED = "weighted"    # Weighted by confidence
    ENSEMBLE = "ensemble"    # All results
    BEST = "best"           # Highest confidence
    FIRST = "first"         # First result
    MERGE = "merge"         # Merge structures
```

##### AgentResult (Class)

```python
class AgentResult:
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        value: Any,
        confidence: float = 1.0,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    )
```

#### Methods

##### aggregate()

```python
def aggregate(
    self,
    results: List[AgentResult],
    strategy: AggregationStrategy = AggregationStrategy.CONSENSUS
) -> Any
```

**Example**:
```python
results = [
    AgentResult("agent1", "Researcher", 42, confidence=0.9),
    AgentResult("agent2", "Researcher", 45, confidence=0.6),
    AgentResult("agent3", "Researcher", 42, confidence=0.8),
]

# Consensus (majority vote)
result = aggregator.aggregate(results, AggregationStrategy.CONSENSUS)
# → 42

# Weighted average
result = aggregator.aggregate(results, AggregationStrategy.WEIGHTED)
# → 42.4

# Best (highest confidence)
result = aggregator.aggregate(results, AggregationStrategy.BEST)
# → 42 (from agent1, confidence 0.9)
```

##### analyze_agreement()

```python
def analyze_agreement(self, results: List[AgentResult]) -> Dict[str, Any]
```

**Returns**:
```python
{
    "agreement_level": float,  # 0-1
    "num_unique_values": int,
    "majority_value": Any,
    "majority_count": int,
    "total_results": int,
    "value_distribution": Dict[Any, int]
}
```

---

### WorkflowEngine

**Module**: `core.workflow_engine`

Motore per esecuzione workflow YAML.

#### Class: `WorkflowEngine`

```python
class WorkflowEngine:
    def __init__(self, orchestrator: Orchestrator)
```

#### Methods

##### load_workflow()

```python
def load_workflow(self, workflow_path: Path) -> Dict[str, Any]
```

Carica workflow da file YAML.

**Parameters**:
- `workflow_path`: Path - Path al file YAML

**Returns**: Workflow definition dict

**Raises**: `WorkflowValidationError`

**Example**:
```python
from pathlib import Path

engine = WorkflowEngine(orchestrator)
workflow = engine.load_workflow(Path("workflows/my_workflow.yaml"))
```

##### load_workflow_from_dict()

```python
def load_workflow_from_dict(self, workflow: Dict[str, Any]) -> Dict[str, Any]
```

Carica workflow da dizionario Python.

**Example**:
```python
workflow = {
    "name": "My Workflow",
    "steps": [
        {
            "id": "step1",
            "agent_type": "Researcher",
            "action": "research"
        }
    ]
}

engine.load_workflow_from_dict(workflow)
```

##### execute_workflow()

```python
def execute_workflow(
    self,
    workflow_name: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

Esegue un workflow caricato.

**Parameters**:
- `workflow_name`: str - Nome del workflow
- `parameters`: Dict - Parametri da passare (override defaults)

**Returns**:
```python
{
    "status": str,  # "completed" | "failed"
    "workflow": str,
    "output": Any,
    "results": Dict[str, Any],
    "execution_time": float
}
```

**Example**:
```python
result = engine.execute_workflow(
    "Research Workflow",
    parameters={
        "topic": "Quantum Computing",
        "depth": "deep"
    }
)

print(result['output'])
print(f"Completed in {result['execution_time']:.2f}s")
```

##### list_workflows()

```python
def list_workflows(self) -> List[str]
```

Lista tutti i workflow caricati.

##### get_workflow_info()

```python
def get_workflow_info(self, workflow_name: str) -> Optional[Dict[str, Any]]
```

**Returns**:
```python
{
    "name": str,
    "description": str,
    "version": str,
    "num_steps": int,
    "parameters": List[str]
}
```

---

## Agents

### BaseAgent

**Module**: `agents.base_agent`

Classe base per tutti gli agenti.

#### Class: `BaseAgent` (ABC)

```python
class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None
    )
```

**Attributes**:
- `agent_id`: str - ID univoco
- `name`: str - Nome agente
- `capabilities`: List[str] - Capabilities dell'agente
- `message_bus`: Optional[MessageBus]
- `shared_memory`: Optional[SharedMemory]

#### Abstract Methods

```python
@abstractmethod
def process(self, input_data: Any) -> Any:
    """Processa input e ritorna output"""
    pass
```

---

### ResearcherAgent

**Module**: `agents.researcher_agent`

Agente per ricerca e raccolta informazioni.

#### Class: `ResearcherAgent(BaseAgent)`

```python
class ResearcherAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseLLM,
        agent_id: Optional[str] = None
    )
```

**Capabilities**: `["research", "information_gathering", "source_finding"]`

#### Methods

##### research()

```python
def research(
    self,
    topic: str,
    depth: str = "medium",
    max_sources: int = 5
) -> Dict[str, Any]
```

**Parameters**:
- `topic`: str - Argomento di ricerca
- `depth`: str - "shallow" | "medium" | "deep"
- `max_sources`: int - Massimo numero di fonti

**Returns**:
```python
{
    "topic": str,
    "main_content": str,
    "key_points": List[str],
    "sources": List[Dict],
    "timestamp": str
}
```

##### research_topic()

Alias per `research()`.

---

### AnalystAgent

**Module**: `agents.analyst_agent`

Agente per analisi e generazione insights.

#### Class: `AnalystAgent(BaseAgent)`

```python
class AnalystAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseLLM,
        agent_id: Optional[str] = None
    )
```

**Capabilities**: `["analysis", "data_analysis", "insight_generation"]`

#### Methods

##### analyze()

```python
def analyze(
    self,
    data: Any,
    analysis_type: str = "general",
    focus: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters**:
- `data`: Any - Dati da analizzare
- `analysis_type`: str - Tipo di analisi
- `focus`: List[str] - Aree di focus

**Returns**:
```python
{
    "full_analysis": str,
    "insights": List[str],
    "quality_score": float,
    "confidence": float,
    "timestamp": str
}
```

---

### WriterAgent

**Module**: `agents.writer_agent`

Agente per generazione contenuti.

#### Class: `WriterAgent(BaseAgent)`

```python
class WriterAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseLLM,
        agent_id: Optional[str] = None
    )
```

**Capabilities**: `["writing", "content_generation", "report_creation"]`

#### Methods

##### write()

```python
def write(
    self,
    content: Any,
    style: str = "professional",
    format: str = "markdown",
    max_length: Optional[int] = None
) -> str
```

**Parameters**:
- `content`: Any - Contenuto da formattare
- `style`: str - "professional" | "casual" | "technical" | "brief"
- `format`: str - "markdown" | "html" | "plain"
- `max_length`: int - Lunghezza massima

**Returns**: str - Report formattato

---

### FactCheckerAgent

**Module**: `agents.fact_checker_agent`

Agente per verifica e validazione.

#### Class: `FactCheckerAgent(BaseAgent)`

```python
class FactCheckerAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseLLM,
        agent_id: Optional[str] = None
    )
```

**Capabilities**: `["fact_checking", "verification", "validation"]`

#### Methods

##### verify()

```python
def verify(
    self,
    claims: Union[str, List[str]],
    sources: Optional[List[Dict]] = None,
    verification_level: str = "standard"
) -> Dict[str, Any]
```

**Parameters**:
- `claims`: str | List[str] - Claims da verificare
- `sources`: List[Dict] - Fonti per verifica
- `verification_level`: str - "strict" | "standard" | "lenient"

**Returns**:
```python
{
    "verified_claims": List[Dict],
    "overall_credibility": str,
    "confidence_score": float,
    "verification_summary": str,
    "timestamp": str
}
```

---

### CoordinatorAgent

**Module**: `agents.coordinator_agent`

Agente per coordinamento e planning.

#### Class: `CoordinatorAgent(BaseAgent)`

```python
class CoordinatorAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseLLM,
        agent_id: Optional[str] = None
    )
```

**Capabilities**: `["coordination", "planning", "orchestration"]`

#### Methods

##### create_plan()

```python
def create_plan(self, user_request: str) -> Dict[str, Any]
```

**Returns**:
```python
{
    "goal": str,
    "steps": List[Dict],
    "agents_needed": List[str],
    "estimated_time": int,
    "priority": str
}
```

##### execute_plan()

```python
def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]
```

---

## Configuration

### Config

**Module**: `config`

Sistema di configurazione con Pydantic.

#### Classes

##### LLMConfig

```python
class LLMConfig(BaseModel):
    provider: Literal["ollama", "openai", "groq"]

    # Ollama
    ollama_base_url: str
    ollama_model: str

    # OpenAI
    openai_api_key: Optional[str]
    openai_model: str

    # Groq
    groq_api_key: Optional[str]
    groq_model: str

    # Common
    temperature: float
    max_tokens: int
```

##### Config

```python
class Config(BaseModel):
    llm: LLMConfig
    system_name: str
    log_level: str
```

**Usage**:
```python
from config import get_config

config = get_config()
print(config.llm.provider)  # "ollama"
```

---

## Utilities

### LLM Factory

**Module**: `core.llm`

Factory per creazione istanze LLM.

#### Class: `LLMFactory`

```python
class LLMFactory:
    @staticmethod
    def create_llm(config: Config) -> BaseLLM
```

**Example**:
```python
from core.llm import LLMFactory
from config import get_config

config = get_config()
llm = LLMFactory.create_llm(config)

response = llm.generate("Write a poem about AI")
```

#### Classes

##### BaseLLM (ABC)

```python
class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass
```

##### OllamaLLM

```python
class OllamaLLM(BaseLLM):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:1b",
        temperature: float = 0.7
    )
```

##### GroqLLM

```python
class GroqLLM(BaseLLM):
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7
    )
```

##### OpenAILLM

```python
class OpenAILLM(BaseLLM):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7
    )
```

---

## Error Handling

### Exceptions

```python
# Workflow errors
from core.workflow_engine import WorkflowValidationError, WorkflowExecutionError

# Dependency errors
from core.dependency_graph import CircularDependencyError
```

### Example Error Handling

```python
from core.workflow_engine import WorkflowEngine, WorkflowValidationError
from core.dependency_graph import CircularDependencyError

try:
    workflow = engine.load_workflow("workflow.yaml")
except WorkflowValidationError as e:
    print(f"Invalid workflow: {e}")

try:
    task = orchestrator.add_task(...)
except CircularDependencyError as e:
    print(f"Circular dependency detected: {e}")
```

---

## Complete Example

```python
from pathlib import Path
from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from core.workflow_engine import WorkflowEngine
from agents.researcher_agent import ResearcherAgent
from agents.analyst_agent import AnalystAgent
from agents.writer_agent import WriterAgent

# Setup
config = get_config()
llm = LLMFactory.create_llm(config)

orchestrator = Orchestrator()

# Register agents
researcher = ResearcherAgent(llm=llm)
analyst = AnalystAgent(llm=llm)
writer = WriterAgent(llm=llm)

orchestrator.register_agent(researcher)
orchestrator.register_agent(analyst)
orchestrator.register_agent(writer)

# Create workflow engine
engine = WorkflowEngine(orchestrator)

# Load and execute workflow
engine.load_workflow(Path("workflows/quick_analysis.yaml"))

result = engine.execute_workflow(
    "Quick Analysis",
    parameters={
        "topic": "AI Trends 2025",
        "priority_level": "high"
    }
)

# Access results
print(result['output']['summary'])
print(f"Execution time: {result['execution_time']:.2f}s")

# System statistics
stats = orchestrator.get_system_status()
print(f"Tasks completed: {stats['task_queue']['completed_tasks']}")
print(f"Success rate: {stats['agent_registry']['system_success_rate']:.2%}")
```

---

## See Also

- [System Overview](SYSTEM_OVERVIEW.md)
- [Architecture](ARCHITECTURE.md)
- [Workflow Guide](WORKFLOW_GUIDE.md)
- [Examples](EXAMPLES.md)
