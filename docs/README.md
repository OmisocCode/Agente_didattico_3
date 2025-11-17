# Documentazione Sistema Multi-Agente

Benvenuto nella documentazione completa del Sistema Multi-Agente per orchestrazione di agenti AI specializzati.

## 📚 Documentazione Disponibile

### 1. [System Overview](SYSTEM_OVERVIEW.md)
**Panoramica generale del sistema**
- Introduzione e caratteristiche principali
- Architettura ad alto livello
- Componenti principali
- Fasi di sviluppo completate
- Flusso di esecuzione generale

**Ideale per**: Comprendere il sistema nel suo insieme

---

### 2. [Architecture](ARCHITECTURE.md)
**Architettura dettagliata con diagrammi**
- Pattern architetturali (Message Bus, Blackboard, DAG)
- Componenti core con diagrammi di flusso
- Algoritmi e implementazioni
- Integrazione tra componenti
- Performance e scalabilità

**Ideale per**: Sviluppatori che vogliono comprendere l'implementazione

---

### 3. [Workflow Guide](WORKFLOW_GUIDE.md)
**Guida completa ai workflow YAML**
- Struttura workflow YAML
- Parameter substitution
- Gestione dipendenze
- Template predefiniti
- Best practices

**Ideale per**: Creare e gestire workflow personalizzati

---

### 4. [API Reference](API_REFERENCE.md)
**Riferimento completo delle API**
- Core components (Orchestrator, TaskQueue, ecc.)
- Agents (Researcher, Analyst, Writer, ecc.)
- Workflow Engine
- Configuration
- Esempi d'uso

**Ideale per**: Riferimento rapido durante lo sviluppo

---

### 5. [Examples](EXAMPLES.md)
**Esempi pratici e casi d'uso**
- Quick start
- Esempi base
- Workflow avanzati
- Casi d'uso reali
- Troubleshooting

**Ideale per**: Iniziare rapidamente con esempi funzionanti

---

### 6. [Flow Diagrams](FLOW_DIAGRAMS.md)
**Diagrammi di flusso dettagliati**
- Flussi di esecuzione completi
- Diagrammi per ogni componente
- Visualizzazioni dei pattern
- Sequence diagrams

**Ideale per**: Visualizzare i flussi di esecuzione

---

## 🚀 Quick Start

### 1. Installazione
```bash
git clone https://github.com/your-org/agente_didattico_3.git
cd agente_didattico_3
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configurazione
Modifica `.env` con le tue configurazioni:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

### 3. Primo Esempio
```python
from config import get_config
from core.llm import LLMFactory
from core.orchestrator import Orchestrator
from agents.researcher_agent import ResearcherAgent

config = get_config()
llm = LLMFactory.create_llm(config)
orchestrator = Orchestrator()

researcher = ResearcherAgent(llm=llm)
orchestrator.register_agent(researcher)

# Execute task
from core.task_queue import TaskPriority
task = orchestrator.add_task(
    agent_type="ResearcherAgent",
    action="research",
    input_data={"topic": "AI"},
    priority=TaskPriority.HIGH
)

result = orchestrator.execute_all()
print(result)
```

Vedi [Examples](EXAMPLES.md) per più esempi.

---

## 📖 Percorsi di Lettura Consigliati

### Per Nuovi Utenti
1. [System Overview](SYSTEM_OVERVIEW.md) - Comprendere il sistema
2. [Examples](EXAMPLES.md#quick-start) - Iniziare con esempi
3. [Workflow Guide](WORKFLOW_GUIDE.md) - Creare workflow

### Per Sviluppatori
1. [Architecture](ARCHITECTURE.md) - Comprendere l'architettura
2. [API Reference](API_REFERENCE.md) - Riferimento API
3. [Flow Diagrams](FLOW_DIAGRAMS.md) - Visualizzare i flussi

### Per Utenti Avanzati
1. [Architecture](ARCHITECTURE.md#pattern-architetturali) - Pattern avanzati
2. [Workflow Guide](WORKFLOW_GUIDE.md#workflow-avanzati) - Workflow complessi
3. [Examples](EXAMPLES.md#casi-duso-reali) - Casi d'uso reali

---

## 🏗️ Architettura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                  WORKFLOW YAML FILES                         │
│     quick_analysis  │  deep_research  │  parallel_research  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Workflow  │
                    │   Engine    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │             │
                    │Orchestrator │◄───── Message Bus
                    │             │◄───── Shared Memory
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
   │  Task   │      │Dependency │     │  Agent    │
   │  Queue  │      │   Graph   │     │ Registry  │
   └─────────┘      └───────────┘     └─────┬─────┘
                                             │
                    ┌────────────────────────┼────────────────┐
                    │            │           │       │        │
              ┌─────▼──┐   ┌────▼───┐  ┌───▼────┐ │  ┌────▼──────┐
              │Research│   │Analyst │  │ Writer │ │  │FactChecker│
              │  Agent │   │ Agent  │  │ Agent  │ │  │   Agent    │
              └────────┘   └────────┘  └────────┘ │  └───────────┘
                                                   │
                                            ┌──────▼────────┐
                                            │  Coordinator  │
                                            │     Agent     │
                                            └───────────────┘
```

---

## 🔑 Concetti Chiave

### Multi-Agent System
Sistema in cui multiple agenti AI specializzati collaborano per completare task complessi.

### Orchestrator
Coordinatore centrale che gestisce task, agenti e dipendenze.

### Workflow YAML
File dichiarativi che definiscono sequenze di operazioni multi-agente.

### Task Queue
Coda con priorità per scheduling e gestione task.

### Dependency Graph
DAG (Directed Acyclic Graph) per gestione dipendenze tra task.

### Agent Registry
Registro centralizzato per discovery e load balancing degli agenti.

### Message Bus
Sistema di comunicazione publish-subscribe tra agenti.

### Shared Memory
Blackboard pattern per memoria condivisa thread-safe.

---

## 📊 Statistiche del Progetto

- **Fasi Completate**: 4/4 (100%)
- **Componenti Core**: 8
- **Agenti Specializzati**: 5
- **Workflow Template**: 3
- **Test Coverage**: 100% (tutti i test passano)
- **Linee di Codice**: ~5000+
- **Files Documentazione**: 6

---

## 🔧 Componenti Principali

| Componente | Descrizione | File |
|------------|-------------|------|
| **Orchestrator** | Coordinatore centrale | `core/orchestrator.py` |
| **TaskQueue** | Coda con priorità | `core/task_queue.py` |
| **DependencyGraph** | Gestione dipendenze | `core/dependency_graph.py` |
| **AgentRegistry** | Registry e discovery | `core/agent_registry.py` |
| **WorkflowEngine** | Esecuzione workflow | `core/workflow_engine.py` |
| **MessageBus** | Comunicazione agenti | `core/message_bus.py` |
| **SharedMemory** | Memoria condivisa | `core/shared_memory.py` |
| **ResultAggregator** | Aggregazione risultati | `core/result_aggregator.py` |

---

## 🤖 Agenti Disponibili

| Agente | Responsabilità | Capabilities |
|--------|---------------|--------------|
| **ResearcherAgent** | Ricerca informazioni | research, information_gathering |
| **AnalystAgent** | Analisi e insights | analysis, data_analysis |
| **WriterAgent** | Generazione contenuti | writing, content_generation |
| **FactCheckerAgent** | Verifica e validazione | fact_checking, verification |
| **CoordinatorAgent** | Coordinamento | coordination, planning |

---

## 📝 Workflow Template

| Template | Scopo | Steps | Tempo Medio |
|----------|-------|-------|-------------|
| **quick_analysis.yaml** | Analisi rapida | 3 | < 5 min |
| **deep_research.yaml** | Ricerca approfondita | 4 | 10-15 min |
| **parallel_research.yaml** | Ricerca parallela | 5 | 8-12 min |

---

## 🎯 Roadmap Futura

### Fase 5: Monitoring e Logging
- Sistema di logging avanzato
- Metriche in tempo reale
- Dashboard di monitoring

### Fase 6: Persistenza
- Salvataggio stato
- Database integration
- Workflow history

### Fase 7: API Layer
- REST API
- GraphQL endpoint
- WebSocket support

### Fase 8: UI Dashboard
- Web interface
- Workflow builder
- Real-time monitoring

### Fase 9: Distributed Execution
- Multi-node support
- Load balancing distribuito
- Message queue (RabbitMQ/Kafka)

### Fase 10: Advanced Features
- Machine Learning integration
- Auto-scaling
- Plugin system

---

## 🤝 Contribuire

Per contribuire al progetto:
1. Fork il repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

---

## 📧 Supporto

Per domande o supporto:
- Consulta la documentazione
- Apri un issue su GitHub
- Contatta il team

---

## 📄 Licenza

Vedi file LICENSE per dettagli.

---

## 🙏 Ringraziamenti

- Anthropic per Claude
- Ollama per LLM locali
- Groq per API veloci
- Community open source

---

**Ultima modifica**: 2025-11-17
**Versione**: 1.0
