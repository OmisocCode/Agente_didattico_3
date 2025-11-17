# Diagrammi di Flusso - Sistema Multi-Agente

Questa documentazione contiene diagrammi di flusso dettagliati per visualizzare i processi principali del sistema.

## Indice
- [Workflow Execution Flow](#workflow-execution-flow)
- [Task Lifecycle](#task-lifecycle)
- [Agent Communication](#agent-communication)
- [Dependency Resolution](#dependency-resolution)
- [Result Aggregation](#result-aggregation)

---

## Workflow Execution Flow

### Flusso Completo di Esecuzione Workflow

```mermaid
flowchart TD
    Start([User Executes Workflow]) --> LoadYAML[Load YAML File]
    LoadYAML --> ParseYAML{Parse YAML}

    ParseYAML -->|Invalid| Error1[Throw ValidationError]
    ParseYAML -->|Valid| ValidateStructure[Validate Structure]

    ValidateStructure --> CheckFields{All Required<br/>Fields Present?}
    CheckFields -->|No| Error2[Throw ValidationError]
    CheckFields -->|Yes| CheckDeps{Valid<br/>Dependencies?}

    CheckDeps -->|No| Error3[Throw ValidationError]
    CheckDeps -->|Yes| MergeParams[Merge Parameters<br/>defaults + user]

    MergeParams --> CreateContext[Create Execution Context]
    CreateContext --> LoopSteps{For Each Step}

    LoopSteps --> SubstParams[Substitute Parameters<br/>{{ parameters.X }}]
    SubstParams --> SubstSteps[Substitute Step Results<br/>{{ steps.Y.output }}]
    SubstSteps --> AddTask[Add Task to Orchestrator]
    AddTask --> StoreMapping[Store step_id → task_id]
    StoreMapping --> MoreSteps{More Steps?}

    MoreSteps -->|Yes| LoopSteps
    MoreSteps -->|No| ExecuteAll[Execute All Tasks<br/>via Orchestrator]

    ExecuteAll --> CheckStatus{All Tasks<br/>Completed?}
    CheckStatus -->|No| ExecuteFailed[Mark as Failed]
    CheckStatus -->|Yes| MapResults[Map task results<br/>to step results]

    MapResults --> BuildOutput[Build Output<br/>using template]
    BuildOutput --> FinalResult[Return Workflow Result]

    ExecuteFailed --> End1([End - Failed])
    FinalResult --> End2([End - Success])
    Error1 --> End3([End - Error])
    Error2 --> End3
    Error3 --> End3

    style Start fill:#90EE90
    style End1 fill:#FF6B6B
    style End2 fill:#90EE90
    style End3 fill:#FF6B6B
    style ExecuteAll fill:#FFD700
```

### Workflow Parameter Substitution

```mermaid
flowchart LR
    subgraph Input
        YAML[YAML Config<br/>with {{ ... }}]
        UserParams[User Parameters]
        StepResults[Previous Step Results]
    end

    subgraph Processing
        Parse[Parse to JSON]
        Regex[Find {{ ... }} patterns]
        Resolve{Pattern Type?}

        Resolve -->|parameters.*| GetParam[Get from parameters]
        Resolve -->|steps.*.output| GetStep[Get from step results]

        GetParam --> Replace[Replace in JSON]
        GetStep --> Replace

        Replace --> More{More Patterns?}
        More -->|Yes| Regex
        More -->|No| Rebuild[Rebuild Config]
    end

    subgraph Output
        Final[Final Configuration]
    end

    YAML --> Parse
    UserParams --> GetParam
    StepResults --> GetStep
    Parse --> Regex
    Rebuild --> Final

    style Parse fill:#FFE4B5
    style Final fill:#90EE90
```

---

## Task Lifecycle

### Complete Task Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: add_task()

    Created --> Pending: Initialize
    Pending --> Queued: Dependencies Met

    Queued --> Assigned: get_next_task()
    Assigned --> InProgress: Agent Starts

    InProgress --> Executing: Agent Processing
    Executing --> Completing: Agent Finishes

    Completing --> Completed: Success
    Completing --> Failed: Error/Timeout

    Pending --> Cancelled: cancel_task()
    Queued --> Cancelled: cancel_task()

    Completed --> [*]
    Failed --> [*]
    Cancelled --> [*]

    note right of Pending
        Waiting for
        dependencies to
        complete
    end note

    note right of Queued
        In priority queue
        ready for execution
    end note

    note right of InProgress
        Agent executing
        workload++
    end note

    note right of Completed
        Result stored
        Dependent tasks
        unblocked
    end note
```

### Task State Transitions Detail

```mermaid
flowchart TD
    A[Task Created] --> B{Has<br/>Dependencies?}

    B -->|No| C[Add to Queue]
    B -->|Yes| D[Mark as Pending]

    C --> E[Wait in Priority Queue]
    D --> F{Dependencies<br/>Completed?}

    F -->|No| D
    F -->|Yes| C

    E --> G[get_next_task called]
    G --> H[Remove from Queue]
    H --> I[Assign to Agent]

    I --> J{Agent<br/>Available?}
    J -->|No| K[Return to Queue]
    J -->|Yes| L[Agent Executes]

    K --> E

    L --> M{Execution<br/>Result?}

    M -->|Success| N[complete_task]
    M -->|Error| O[fail_task]
    M -->|Timeout| O

    N --> P[Store Result]
    O --> Q[Store Error]

    P --> R[Update Statistics]
    Q --> R

    R --> S[Check Dependent Tasks]
    S --> T{Has<br/>Dependents?}

    T -->|Yes| U[Unblock Dependents]
    T -->|No| V[Done]

    U --> V

    style A fill:#90EE90
    style V fill:#90EE90
    style O fill:#FF6B6B
    style L fill:#FFD700
```

---

## Agent Communication

### Message Bus Communication Pattern

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant MB as Message Bus
    participant Q1 as Queue Agent 1
    participant Q2 as Queue Agent 2
    participant A2 as Agent 2

    Note over A1,A2: Setup
    A1->>MB: register_agent(agent1_id)
    A2->>MB: register_agent(agent2_id)
    MB->>Q1: Create queue
    MB->>Q2: Create queue

    Note over A1,A2: Direct Message
    A1->>MB: send(msg: to=agent2)
    MB->>Q2: put(message)
    A2->>MB: receive(agent2_id)
    MB->>Q2: get(timeout=1)
    Q2-->>MB: message
    MB-->>A2: message

    Note over A1,A2: Broadcast
    A1->>MB: subscribe(agent1, "result")
    A2->>MB: subscribe(agent2, "result")

    A1->>MB: broadcast(type="result")
    MB->>Q1: put(message)
    MB->>Q2: put(message)

    A1->>MB: receive()
    MB-->>A1: message
    A2->>MB: receive()
    MB-->>A2: message
```

### Shared Memory Access Pattern

```mermaid
flowchart TD
    subgraph Agent Operations
        A1[Agent 1 Write]
        A2[Agent 2 Read]
        A3[Agent 3 Write]
    end

    subgraph Shared Memory
        Lock[Global RLock]
        KeyLock[Key-Specific Lock]

        Lock --> Access{Operation Type?}
        Access -->|Write| KeyLock
        Access -->|Read| Data[Access Data]

        KeyLock --> Update[Update Entry]
        Update --> Version[Increment Version]
        Version --> Notify[Notify Observers]
        Notify --> Data
    end

    subgraph Observers
        O1[Observer 1]
        O2[Observer 2]
    end

    A1 --> Lock
    A2 --> Lock
    A3 --> Lock

    Notify --> O1
    Notify --> O2

    style Lock fill:#FFE4B5
    style KeyLock fill:#FFD700
    style Notify fill:#90EE90
```

---

## Dependency Resolution

### Topological Sort (Kahn's Algorithm)

```mermaid
flowchart TD
    Start([Start Topological Sort]) --> CalcDegree[Calculate In-Degree<br/>for All Nodes]

    CalcDegree --> InitQueue[Initialize Queue with<br/>Nodes of In-Degree 0]

    InitQueue --> CheckQueue{Queue<br/>Empty?}

    CheckQueue -->|No| Dequeue[Dequeue Node N]
    CheckQueue -->|Yes| CheckResult{All Nodes<br/>in Result?}

    Dequeue --> AddResult[Add N to Result]
    AddResult --> GetDeps[Get Dependents of N]

    GetDeps --> LoopDeps{For Each<br/>Dependent D}

    LoopDeps --> DecrDegree[Decrement<br/>In-Degree of D]
    DecrDegree --> CheckDegree{In-Degree<br/>of D = 0?}

    CheckDegree -->|Yes| Enqueue[Add D to Queue]
    CheckDegree -->|No| NextDep{More<br/>Dependents?}

    Enqueue --> NextDep

    NextDep -->|Yes| LoopDeps
    NextDep -->|No| CheckQueue

    CheckResult -->|Yes| Success([Return Sorted Order])
    CheckResult -->|No| Cycle([Circular Dependency!])

    style Start fill:#90EE90
    style Success fill:#90EE90
    style Cycle fill:#FF6B6B
    style CalcDegree fill:#FFE4B5
```

### Execution Layers Generation

```mermaid
flowchart TD
    Start([Generate Execution Layers]) --> Init[Initialize:<br/>layers = []<br/>completed = {}<br/>remaining = all nodes]

    Init --> Check{Remaining<br/>Nodes?}

    Check -->|No| Return([Return Layers])
    Check -->|Yes| FindReady[Find Ready Nodes<br/>can_execute(node, completed)]

    FindReady --> CheckReady{Found<br/>Ready Nodes?}

    CheckReady -->|No| Error([Circular Dependency!])
    CheckReady -->|Yes| CreateLayer[Create New Layer<br/>with Ready Nodes]

    CreateLayer --> UpdateCompleted[Update completed<br/>with ready nodes]
    UpdateCompleted --> UpdateRemaining[Remove ready nodes<br/>from remaining]

    UpdateRemaining --> Check

    style Start fill:#90EE90
    style Return fill:#90EE90
    style Error fill:#FF6B6B
    style CreateLayer fill:#FFD700

    Note1[Layer 1: A, B<br/>can execute in parallel]
    Note2[Layer 2: C, D<br/>wait for layer 1]

    CreateLayer -.-> Note1
    UpdateCompleted -.-> Note2
```

### Dependency Graph Example

```mermaid
graph TB
    subgraph Layer 1 - Parallel
        A[Task A<br/>Priority: HIGH]
        B[Task B<br/>Priority: CRITICAL]
        C[Task C<br/>Priority: HIGH]
    end

    subgraph Layer 2 - Parallel
        D[Task D<br/>Priority: MEDIUM]
        E[Task E<br/>Priority: HIGH]
    end

    subgraph Layer 3
        F[Task F<br/>Priority: LOW]
    end

    A --> D
    B --> D
    A --> E
    C --> E
    D --> F
    E --> F

    style A fill:#FFA07A
    style B fill:#FF6B6B
    style C fill:#FFA07A
    style D fill:#FFD700
    style E fill:#FFA07A
    style F fill:#90EE90

    Note[Execution Order:<br/>1. A, B, C in parallel<br/>2. D, E in parallel<br/>3. F waits for all]
```

---

## Result Aggregation

### Aggregation Strategy Selection

```mermaid
flowchart TD
    Start([Multiple Agent Results]) --> CheckCount{Number of<br/>Results?}

    CheckCount -->|0| ReturnNone[Return None]
    CheckCount -->|1| ReturnSingle[Return Single Result]
    CheckCount -->|>1| SelectStrategy{Select<br/>Strategy}

    SelectStrategy -->|CONSENSUS| Consensus[Majority Vote]
    SelectStrategy -->|WEIGHTED| Weighted[Weighted Average]
    SelectStrategy -->|ENSEMBLE| Ensemble[Combine All]
    SelectStrategy -->|BEST| Best[Highest Confidence]
    SelectStrategy -->|MERGE| Merge[Merge Structures]

    Consensus --> CounterCheck{All<br/>Simple Types?}
    CounterCheck -->|Yes| UseCounter[Use Counter]
    CounterCheck -->|No| FallbackWeighted[Fallback to Weighted]

    UseCounter --> MostCommon[Return Most Common]

    Weighted --> TypeCheck{All<br/>Numeric?}
    TypeCheck -->|Yes| CalcWeighted[Calculate<br/>Weighted Average]
    TypeCheck -->|No| HighestConf[Return Highest<br/>Confidence]

    Ensemble --> CombineAll[Create List of<br/>All Results]

    Best --> MaxConf[Select Result with<br/>Max Confidence]

    Merge --> StructCheck{Result<br/>Types?}
    StructCheck -->|Dicts| MergeDicts[Merge Dictionaries]
    StructCheck -->|Lists| MergeLists[Combine Lists]
    StructCheck -->|Mixed| FallbackWeighted2[Fallback to Weighted]

    MostCommon --> End([Return Result])
    FallbackWeighted --> CalcWeighted
    CalcWeighted --> End
    HighestConf --> End
    CombineAll --> End
    MaxConf --> End
    MergeDicts --> End
    MergeLists --> End
    FallbackWeighted2 --> HighestConf
    ReturnNone --> End
    ReturnSingle --> End

    style Start fill:#90EE90
    style End fill:#90EE90
    style SelectStrategy fill:#FFD700
```

### Consensus Aggregation Example

```mermaid
flowchart LR
    subgraph Input
        R1[Agent 1: 42<br/>Confidence: 0.9]
        R2[Agent 2: 45<br/>Confidence: 0.6]
        R3[Agent 3: 42<br/>Confidence: 0.8]
        R4[Agent 4: 42<br/>Confidence: 0.7]
    end

    subgraph Processing
        Count[Count Values]
        Count --> C1[42: 3 votes]
        Count --> C2[45: 1 vote]

        C1 --> Select[Select Most Common]
    end

    subgraph Output
        Result[Result: 42<br/>Agreement: 75%]
    end

    R1 --> Count
    R2 --> Count
    R3 --> Count
    R4 --> Count

    Select --> Result

    style Result fill:#90EE90
```

### Weighted Aggregation Example

```mermaid
flowchart TB
    subgraph Input
        R1[Agent 1: 42<br/>Confidence: 0.9]
        R2[Agent 2: 45<br/>Confidence: 0.6]
        R3[Agent 3: 42<br/>Confidence: 0.8]
    end

    subgraph Calculation
        Calc[Weighted Sum /<br/>Total Confidence]

        W1[42 × 0.9 = 37.8]
        W2[45 × 0.6 = 27.0]
        W3[42 × 0.8 = 33.6]

        Sum[Sum = 98.4]
        TotalConf[Total Conf = 2.3]

        Div[98.4 / 2.3 = 42.78]
    end

    subgraph Output
        Result[Result: 42.78<br/>Avg Confidence: 0.77]
    end

    R1 --> W1
    R2 --> W2
    R3 --> W3

    W1 --> Sum
    W2 --> Sum
    W3 --> Sum

    R1 --> TotalConf
    R2 --> TotalConf
    R3 --> TotalConf

    Sum --> Div
    TotalConf --> Div

    Div --> Result

    style Result fill:#90EE90
    style Calc fill:#FFE4B5
```

---

## Agent Load Balancing

### Load Balancing Selection

```mermaid
flowchart TD
    Start([Find Available Agent]) --> GetType{Agent Type<br/>Specified?}

    GetType -->|Yes| FindByType[Get Agents<br/>of Type X]
    GetType -->|No| GetAll[Get All Agents]

    FindByType --> Filter1[Filter by Status<br/>idle or busy]
    GetAll --> Filter1

    Filter1 --> CheckAvail{Any<br/>Available?}

    CheckAvail -->|No| ReturnNone[Return None]
    CheckAvail -->|Yes| SortByWorkload[Sort by<br/>Workload ASC]

    SortByWorkload --> SelectMin[Select Agent<br/>with Min Workload]

    SelectMin --> IncrementWorkload[Increment<br/>Agent Workload]

    IncrementWorkload --> UpdateStatus{Workload >=<br/>Max?}

    UpdateStatus -->|Yes| MarkBusy[Mark as Busy]
    UpdateStatus -->|No| KeepStatus[Keep Current Status]

    MarkBusy --> Return[Return AgentInfo]
    KeepStatus --> Return

    ReturnNone --> End([End])
    Return --> End

    style Start fill:#90EE90
    style Return fill:#90EE90
    style ReturnNone fill:#FF6B6B
    style SelectMin fill:#FFD700
```

### Load Distribution Example

```mermaid
graph TB
    subgraph Orchestrator
        O[Orchestrator]
    end

    subgraph Agent Registry
        R[Registry]
    end

    subgraph Agents
        A1[Researcher 1<br/>Workload: 0<br/>Status: IDLE]
        A2[Researcher 2<br/>Workload: 2<br/>Status: BUSY]
        A3[Researcher 3<br/>Workload: 5<br/>Status: BUSY]
    end

    O -->|Find Researcher| R
    R -->|Check Workload| A1
    R -->|Check Workload| A2
    R -->|Check Workload| A3

    R -.Select Min Workload.-> A1

    A1 -->|Assign Task| Exec[Execute Task]

    style A1 fill:#90EE90
    style A2 fill:#FFD700
    style A3 fill:#FFA07A
    style Exec fill:#90EE90
```

---

## Complete System Flow

### End-to-End Workflow Execution

```mermaid
sequenceDiagram
    actor User
    participant WE as Workflow Engine
    participant O as Orchestrator
    participant TQ as Task Queue
    participant DG as Dep Graph
    participant AR as Agent Registry
    participant MB as Message Bus
    participant A as Agent
    participant SM as Shared Memory

    User->>WE: execute_workflow(name, params)

    rect rgb(220, 240, 255)
        Note over WE: Phase 1: Load & Validate
        WE->>WE: load_workflow_from_dict()
        WE->>WE: _validate_workflow()
        WE->>WE: merge_parameters()
    end

    rect rgb(255, 240, 220)
        Note over WE,DG: Phase 2: Create Tasks
        loop For each step
            WE->>WE: _substitute_params()
            WE->>O: add_task(...)

            O->>TQ: add_task()
            TQ-->>O: Task

            O->>DG: add_node(task_id)
            O->>DG: add_dependency(...)

            O-->>WE: Task created
        end
    end

    rect rgb(240, 255, 240)
        Note over O,SM: Phase 3: Execute Tasks
        WE->>O: execute_all()

        loop Until all tasks complete
            O->>DG: get_ready_nodes()
            DG-->>O: [ready_task_ids]

            O->>TQ: get_next_task()
            TQ-->>O: Task

            O->>AR: find_available_agent()
            AR-->>O: AgentInfo

            O->>MB: send(task_message)
            MB->>A: deliver

            O->>SM: write(task_data)

            A->>A: process(task)

            A->>MB: send(result)
            MB->>O: deliver

            O->>TQ: complete_task()
            O->>AR: record_completion()
            O->>SM: write(result)
        end

        O-->>WE: execution_results
    end

    rect rgb(255, 240, 255)
        Note over WE: Phase 4: Build Output
        WE->>WE: map task_results to step_results
        WE->>WE: _build_output()
        WE-->>User: workflow_result
    end
```

---

## Riferimenti

- [System Overview](SYSTEM_OVERVIEW.md)
- [Architecture](ARCHITECTURE.md)
- [Workflow Guide](WORKFLOW_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Examples](EXAMPLES.md)

---

**Note**: Tutti i diagrammi sono in formato Mermaid e possono essere visualizzati in qualsiasi editor che supporti Mermaid (GitHub, GitLab, VSCode con plugin, ecc.).
