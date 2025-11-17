# Architettura del Sistema Multi-Agente

## Indice
- [Panoramica Architetturale](#panoramica-architetturale)
- [Pattern Architetturali](#pattern-architetturali)
- [Componenti Core](#componenti-core)
- [Flussi di Esecuzione](#flussi-di-esecuzione)
- [Integrazione tra Componenti](#integrazione-tra-componenti)

## Panoramica Architetturale

Il sistema è organizzato in 6 layer principali:

```
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI/Scripts  │  │   Examples   │  │   Workflows  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Workflow Engine (YAML)                     │   │
│  │  • Load/Validate  • Execute  • Parameter Subst.     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Orchestrator │  │  Task Queue  │  │   Dep Graph  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │Agent Registry│  │Result Aggreg.│                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  COMMUNICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Message Bus (Pub/Sub)  │  Shared Memory (Blackboard)│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ │
│  │Coordin.│ │Research│ │Analyst │ │ Writer │ │FactCheck │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       LLM LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Ollama (Local)│  │  Groq (Fast) │  │ OpenAI (GPT) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Pattern Architetturali

### 1. Message Bus Pattern (Publish-Subscribe)

```mermaid
graph LR
    A1[Agent 1] -->|publish| MB[Message Bus]
    A2[Agent 2] -->|publish| MB
    A3[Agent 3] -->|publish| MB

    MB -->|subscribe| A1
    MB -->|subscribe| A2
    MB -->|subscribe| A3
    MB -->|subscribe| O[Orchestrator]

    style MB fill:#f9f,stroke:#333,stroke-width:4px
```

**Vantaggi**:
- Disaccoppiamento tra agenti
- Comunicazione asincrona
- Scalabilità
- Flessibilità

**Implementazione**:
```python
class MessageBus:
    def __init__(self):
        self.queues = {}  # agent_id -> Queue
        self.subscriptions = {}  # msg_type -> [agent_ids]

    def send(self, message: Message):
        """Invia messaggio a destinatario specifico"""
        self.queues[message.receiver].put(message)

    def broadcast(self, message: Message):
        """Broadcast a tutti i subscriber"""
        for agent_id in self.subscriptions[message.msg_type]:
            self.send(message)
```

### 2. Blackboard Pattern (Shared Memory)

```mermaid
graph TB
    subgraph Blackboard
        B[Shared Memory<br/>Thread-Safe Storage]
    end

    A1[Agent 1] -->|write| B
    A2[Agent 2] -->|write| B
    A3[Agent 3] -->|write| B

    B -->|read| A1
    B -->|read| A2
    B -->|read| A3

    B -->|notify| O1[Observer 1]
    B -->|notify| O2[Observer 2]

    style B fill:#bbf,stroke:#333,stroke-width:4px
```

**Caratteristiche**:
- Memoria condivisa thread-safe
- Versioning automatico
- Observer notifications
- Lock per-key per concurrency

**Implementazione**:
```python
class SharedMemory:
    def __init__(self):
        self.data = {}
        self.observers = defaultdict(list)
        self._lock = RLock()
        self._key_locks = defaultdict(RLock)

    def write(self, key: str, value: Any, agent_id: str):
        with self._key_locks[key]:
            entry = MemoryEntry(value, agent_id, version)
            self.data[key] = entry
            self._notify_observers(key, entry)
```

### 3. DAG Pattern (Directed Acyclic Graph)

```mermaid
graph TD
    T1[Task 1<br/>Priority: HIGH] --> T3[Task 3<br/>Priority: MEDIUM]
    T2[Task 2<br/>Priority: HIGH] --> T3
    T3 --> T5[Task 5<br/>Priority: LOW]
    T4[Task 4<br/>Priority: CRITICAL] --> T5

    style T1 fill:#faa
    style T2 fill:#faa
    style T3 fill:#ffa
    style T4 fill:#f66
    style T5 fill:#afa
```

**Layer Execution**:
```
Layer 1: [Task 1, Task 2, Task 4]  ← Esecuzione parallela
Layer 2: [Task 3]                   ← Dipende da T1, T2
Layer 3: [Task 5]                   ← Dipende da T3, T4
```

## Componenti Core

### Orchestrator - Flusso Completo

```mermaid
sequenceDiagram
    participant U as User/Workflow
    participant O as Orchestrator
    participant TQ as TaskQueue
    participant DG as DependencyGraph
    participant AR as AgentRegistry
    participant MB as MessageBus
    participant SM as SharedMemory
    participant A as Agent

    U->>O: add_task(type, action, data)

    O->>TQ: add_task(...)
    TQ-->>O: Task object

    O->>DG: add_node(task_id)
    O->>DG: add_dependency(task_id, dep_id)

    Note over O: Task added, waiting for execution

    U->>O: execute_all()

    loop For each task
        O->>DG: get_ready_nodes()
        DG-->>O: [ready_task_ids]

        O->>TQ: get_next_task()
        TQ-->>O: Task

        O->>AR: find_available_agent(task.agent_type)
        AR-->>O: AgentInfo

        O->>AR: increment_workload(agent_id)

        O->>SM: write(task_data)

        O->>MB: send(task_message)
        MB->>A: deliver message

        A->>A: process(task)

        A->>MB: send(result_message)
        MB->>O: deliver result

        O->>TQ: complete_task(task_id, result)
        O->>AR: record_completion(agent_id)
        O->>AR: decrement_workload(agent_id)

        O->>SM: write(result)
    end

    O-->>U: Execution summary
```

### Task Queue - Priorità e Dipendenze

```mermaid
stateDiagram-v2
    [*] --> PENDING: add_task()

    PENDING --> IN_QUEUE: dependencies met
    PENDING --> PENDING: waiting for deps

    IN_QUEUE --> IN_PROGRESS: get_next_task()

    IN_PROGRESS --> COMPLETED: complete_task()
    IN_PROGRESS --> FAILED: fail_task()
    IN_PROGRESS --> CANCELLED: cancel_task()

    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]

    note right of IN_QUEUE
        Priority ordering:
        CRITICAL (0)
        HIGH (1)
        MEDIUM (2)
        LOW (3)
    end note

    note right of COMPLETED
        Triggers check for
        dependent tasks
    end note
```

**Priority Queue Implementation**:
```python
# Task è un @dataclass con order=True
@dataclass(order=True)
class Task:
    priority: int = field(compare=True)  # Solo priority per ordering
    task_id: str = field(compare=False)
    # ... altri campi

# PriorityQueue automaticamente ordina per priority
queue = PriorityQueue()
queue.put(task)  # Auto-sorted
```

### Dependency Graph - Algoritmi

```mermaid
graph TB
    subgraph "Topological Sort - Kahn's Algorithm"
        direction TB
        S1[Start: Calculate in-degree for all nodes]
        S2[Queue = nodes with in-degree 0]
        S3{Queue empty?}
        S4[Dequeue node N]
        S5[Add N to result]
        S6[For each dependent D of N:<br/>Decrement in-degree of D]
        S7{in-degree of D = 0?}
        S8[Add D to queue]
        S9[Return result]
        S10[Circular dependency!]

        S1 --> S2
        S2 --> S3
        S3 -->|No| S4
        S4 --> S5
        S5 --> S6
        S6 --> S7
        S7 -->|Yes| S8
        S8 --> S3
        S7 -->|No| S3
        S3 -->|Yes| S9

        S3 -->|Result incomplete| S10
    end
```

**Execution Layers Algorithm**:
```python
def get_execution_layers(self) -> List[List[str]]:
    layers = []
    completed = set()
    remaining = self.nodes.copy()

    while remaining:
        # Trova nodi eseguibili ora
        ready = [
            node for node in remaining
            if self.can_execute(node, completed)
        ]

        if not ready:
            raise CircularDependencyError()

        layers.append(ready)  # Tutti in ready possono essere paralleli
        completed.update(ready)
        remaining -= set(ready)

    return layers
```

### Agent Registry - Load Balancing

```mermaid
graph TB
    subgraph "Agent Selection Process"
        A1[Request: Find agent of type X]
        A2[Get all agents of type X]
        A3[Filter: status in idle/busy]
        A4{Any available?}
        A5[Select agent with min workload]
        A6[Return None]
        A7[Update workload]
        A8[Return AgentInfo]

        A1 --> A2
        A2 --> A3
        A3 --> A4
        A4 -->|Yes| A5
        A4 -->|No| A6
        A5 --> A7
        A7 --> A8
    end

    subgraph "Agent States"
        I[IDLE<br/>workload = 0]
        B[BUSY<br/>workload > 0]
        O[OFFLINE]

        I -->|task assigned| B
        B -->|task completed| I
        B -->|all tasks done| I
        I -->|unregister| O
        B -->|unregister| O
    end
```

**Workload Tracking**:
```python
@dataclass
class AgentInfo:
    workload: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0

    def get_success_rate(self) -> float:
        total = self.total_tasks_completed + self.total_tasks_failed
        return self.total_tasks_completed / total if total > 0 else 0.0

# Load balancing
def find_available_agent(self, agent_type: str) -> Optional[AgentInfo]:
    candidates = self.find_by_type(agent_type)
    candidates = [a for a in candidates if a.status in ["idle", "busy"]]
    return min(candidates, key=lambda a: a.workload)  # Least loaded
```

### Result Aggregator - Strategie

```mermaid
graph TB
    subgraph "Aggregation Strategies"
        R[Multiple Results] --> S{Strategy?}

        S -->|CONSENSUS| C[Majority Vote]
        S -->|WEIGHTED| W[Weighted by Confidence]
        S -->|ENSEMBLE| E[Combine All]
        S -->|BEST| B[Highest Confidence]
        S -->|MERGE| M[Merge Structures]

        C --> O[Output]
        W --> O
        E --> O
        B --> O
        M --> O
    end

    subgraph "CONSENSUS Example"
        R1[Agent1: 42] --> V{Vote}
        R2[Agent2: 45] --> V
        R3[Agent3: 42] --> V
        V -->|Most common| V1[Result: 42]
    end

    subgraph "WEIGHTED Example"
        RW1[Agent1: 42, conf=0.9] --> WA{Weighted Avg}
        RW2[Agent2: 45, conf=0.6] --> WA
        RW3[Agent3: 42, conf=0.8] --> WA
        WA --> WR[42*0.9 + 45*0.6 + 42*0.8 / 2.3 = 42.4]
    end
```

**Strategy Implementation**:
```python
class AggregationStrategy(Enum):
    CONSENSUS = "consensus"  # Majority vote
    WEIGHTED = "weighted"    # Weighted by confidence
    ENSEMBLE = "ensemble"    # All results
    BEST = "best"           # Highest confidence
    MERGE = "merge"         # Merge dicts/lists

def aggregate(self, results: List[AgentResult], strategy: AggregationStrategy):
    if strategy == AggregationStrategy.CONSENSUS:
        return self._consensus(results)  # Counter for majority
    elif strategy == AggregationStrategy.WEIGHTED:
        return self._weighted(results)   # Weighted average
    # ...
```

### Workflow Engine - Parameter Substitution

```mermaid
graph TB
    subgraph "Workflow Execution Flow"
        W1[Load YAML] --> W2[Validate Structure]
        W2 --> W3[Merge Parameters<br/>defaults + user]
        W3 --> W4{For each step}

        W4 --> W5[Substitute Parameters<br/>{{ parameters.X }}]
        W5 --> W6[Substitute Step Results<br/>{{ steps.Y.output }}]
        W6 --> W7[Add Task to Orchestrator]
        W7 --> W4

        W4 -->|All steps added| W8[Execute via Orchestrator]
        W8 --> W9[Collect Results]
        W9 --> W10[Build Output<br/>apply output template]
        W10 --> W11[Return Result]
    end
```

**Parameter Substitution Process**:
```yaml
# YAML Definition
parameters:
  topic: "AI"
  depth: "deep"

steps:
  - id: research
    params:
      topic: "{{ parameters.topic }}"     # → "AI"
      depth: "{{ parameters.depth }}"     # → "deep"

  - id: analyze
    input: "{{ steps.research.output }}"  # → Result from research step

output:
  report: "{{ steps.analyze.output }}"   # → Result from analyze step
```

**Substitution Algorithm**:
```python
def _substitute_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
    import re, json

    config_str = json.dumps(config)

    def replace_param(match):
        path = match.group(1).strip()

        if path.startswith('parameters.'):
            name = path[len('parameters.'):]
            return str(self.execution_context['parameters'][name])

        elif path.startswith('steps.'):
            parts = path[len('steps.'):].split('.')
            step_id, field = parts[0], '.'.join(parts[1:])
            return str(self.execution_context['steps'][step_id][field])

        return match.group(0)

    # Regex: {{ ... }}
    config_str = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_param, config_str)

    return json.loads(config_str)
```

## Integrazione tra Componenti

### Workflow Engine + Orchestrator Integration

```mermaid
sequenceDiagram
    participant WE as Workflow Engine
    participant O as Orchestrator
    participant TQ as Task Queue
    participant DG as Dependency Graph

    Note over WE: Workflow loaded and validated

    WE->>WE: Merge parameters (defaults + user)

    loop For each step in workflow
        WE->>WE: Substitute parameters in step
        WE->>O: add_task(agent_type, action, params, deps)

        O->>TQ: add_task()
        TQ-->>O: Task

        O->>DG: add_node(task.task_id)

        alt Step has dependencies
            loop For each dependency
                O->>DG: add_dependency(task_id, dep_id)
            end
        end

        O-->>WE: Task object
        WE->>WE: Store step_id → task_id mapping
    end

    WE->>O: execute_all()

    Note over O,DG: Orchestrator executes tasks<br/>respecting dependencies

    O-->>WE: Execution results

    WE->>WE: Map task results to step results
    WE->>WE: Build output using template
    WE-->>WE: Final workflow result
```

### Multi-Agent Collaboration Pattern

```mermaid
sequenceDiagram
    participant C as Coordinator
    participant R as Researcher
    participant A as Analyst
    participant W as Writer
    participant F as FactChecker
    participant SM as Shared Memory
    participant MB as Message Bus

    C->>MB: Broadcast(plan_created)
    MB->>R: Notify
    MB->>A: Notify

    C->>SM: Write(execution_plan)

    R->>SM: Read(execution_plan)
    R->>R: Research topic
    R->>SM: Write(research_results)
    R->>MB: Notify(research_complete)

    MB->>A: Notify
    MB->>F: Notify

    par Parallel Analysis
        A->>SM: Read(research_results)
        A->>A: Analyze data
        A->>SM: Write(analysis)
    and Parallel Fact-Checking
        F->>SM: Read(research_results)
        F->>F: Verify claims
        F->>SM: Write(verification)
    end

    A->>MB: Notify(analysis_complete)
    F->>MB: Notify(verification_complete)

    MB->>W: Notify

    W->>SM: Read(analysis)
    W->>SM: Read(verification)
    W->>W: Generate report
    W->>SM: Write(final_report)
    W->>MB: Notify(report_complete)

    MB->>C: Notify
    C->>SM: Read(final_report)
```

## Performance e Scalabilità

### Thread Safety

Tutti i componenti core sono thread-safe:

```python
# MessageBus - Queue per agent
self.queues[agent_id] = Queue()  # Thread-safe queue

# SharedMemory - RLock
with self._lock:  # Global lock
    with self._key_locks[key]:  # Per-key lock
        self.data[key] = value

# TaskQueue - PriorityQueue
self.queue = PriorityQueue()  # Thread-safe

# AgentRegistry - No shared mutable state issues
# (operazioni atomiche su dict built-in)
```

### Parallelismo

```mermaid
graph TB
    subgraph "Sequential Execution"
        S1[Task 1] --> S2[Task 2] --> S3[Task 3] --> S4[Task 4]
        style S1 fill:#faa
        style S2 fill:#faa
        style S3 fill:#faa
        style S4 fill:#faa
    end

    subgraph "Parallel Execution with DAG"
        P1[Task 1]
        P2[Task 2]
        P3[Task 3]
        P4[Task 4]

        P1 --> P3
        P2 --> P4

        style P1 fill:#afa
        style P2 fill:#afa
        style P3 fill:#afa
        style P4 fill:#afa
    end

    T1[Time] --> T2[2x faster]
```

### Scalabilità Orizzontale

```
┌─────────────────────────────────────┐
│         Load Balancer               │
└─────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┐
    │             │          │
┌───▼───┐    ┌───▼───┐  ┌───▼───┐
│Agent 1│    │Agent 2│  │Agent 3│
│Res.   │    │Res.   │  │Res.   │
│Work=2 │    │Work=0 │  │Work=5 │
└───────┘    └───────┘  └───────┘
                │
        Agent 2 selected (min workload)
```

## Conclusione

L'architettura del sistema è progettata per:
- **Modularità**: Ogni componente ha responsabilità ben definite
- **Scalabilità**: Load balancing e esecuzione parallela
- **Flessibilità**: Pattern configurabili e estensibili
- **Robustezza**: Thread-safety e error handling
- **Osservabilità**: Statistiche e monitoring integrate

Per approfondimenti:
- [System Overview](SYSTEM_OVERVIEW.md)
- [Workflow Guide](WORKFLOW_GUIDE.md)
- [API Reference](API_REFERENCE.md)
