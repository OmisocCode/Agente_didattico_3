# 🤖🤖🤖 Sistema Multi-Agente per Ricerca Avanzata

Un progetto didattico di livello **avanzato** per imparare a costruire sistemi dove più agenti AI specializzati collaborano per risolvere compiti complessi. Questo sistema implementa il pattern di orchestrazione multi-agente con agenti che comunicano, delegano task e sintetizzano risultati.

---

## 💡 Cosa Fa Questa Applicazione?

### Obiettivo Pratico

Questo sistema è un **"Research Assistant Professionale"** che produce **report di ricerca approfonditi e verificati** su qualsiasi argomento complesso.

**Input**: Una query complessa dell'utente  
**Output**: Un report professionale completo con ricerca, analisi, fact-checking e scrittura di qualità

### Esempio Concreto

```
👤 Utente: "Voglio un report professionale sull'impatto dell'AI 
            sul mercato del lavoro nei prossimi 5 anni. Include 
            dati, prospettive diverse, e fonti verificate."

🤖 Sistema Multi-Agente:
   
   ┌─────────────────────────────────────────────────────┐
   │ COORDINATOR: Analizzo la richiesta...               │
   │ Piano: Research → Analysis → Verification → Writing │
   └─────────────────────────────────────────────────────┘
   
   🔍 RESEARCHER AGENT:
      • Cerca 20+ fonti su web (articoli, studi, reports)
      • Estrae dati e statistiche
      • Identifica esperti e loro opinioni
      → Risultato: 50 pagine di materiale grezzo
   
   📊 ANALYST AGENT:
      • Valuta qualità delle fonti
      • Identifica pattern e trend
      • Genera insights chiave
      • Confronta prospettive diverse
      → Risultato: Analisi strutturata con insights
   
   ✓ FACT CHECKER AGENT:
      • Verifica ogni claim importante
      • Cross-reference tra fonti
      • Assegna confidence scores
      • Identifica info contrastanti
      → Risultato: Claims verificati al 95%
   
   ✍️ WRITER AGENT:
      • Scrive report professionale
      • Struttura informazioni chiaramente
      • Cita fonti correttamente
      • Adatta tono e stile
      → Risultato: Report 15 pagine, ben scritto

📄 Output Finale:
   
   ╔═══════════════════════════════════════════════════╗
   ║ AI IMPACT ON JOB MARKET: 2025-2030 ANALYSIS      ║
   ║                                                   ║
   ║ Executive Summary                                 ║
   ║ [Sintesi di 3 paragrafi]                         ║
   ║                                                   ║
   ║ 1. Current State                                  ║
   ║    - Market size: $X billion [✓ Verified]        ║
   ║    - Jobs at risk: Y million [✓ Verified]        ║
   ║                                                   ║
   ║ 2. Optimistic Perspective                        ║
   ║    [Analisi con 5 fonti citate]                  ║
   ║                                                   ║
   ║ 3. Pessimistic Perspective                       ║
   ║    [Analisi con 5 fonti citate]                  ║
   ║                                                   ║
   ║ 4. Data Analysis                                  ║
   ║    [Tabelle, grafici, statistiche verificate]    ║
   ║                                                   ║
   ║ 5. Expert Opinions                                ║
   ║    [Citazioni da 10 esperti]                     ║
   ║                                                   ║
   ║ 6. Conclusions                                    ║
   ║    [Sintesi bilanciata]                          ║
   ║                                                   ║
   ║ Sources: 23 articles, 12 studies, 8 expert       ║
   ║ Verification: 47/52 claims verified (90%)        ║
   ║ Quality: High confidence analysis                ║
   ╚═══════════════════════════════════════════════════╝
```

### Differenze dai Progetti Precedenti

**Progetto 1** (File Agent):
- Analizza **file che hai già**
- Un agente → risponde a domande
- Output: Conversazione Q&A

**Progetto 2** (Web Scraper):
- Cerca **informazioni online**
- Un agente → trova e sintetizza info
- Output: Informazioni aggregate

**Progetto 3** (Multi-Agente):
- **Ricerca approfondita professionale**
- 5+ agenti → collaborano per produrre qualità
- Output: **Report completo verificato e professionale**

### Quando Usare Multi-Agente?

✅ **USA Multi-Agente quando**:
- Servono prospettive multiple (ottimista vs pessimista)
- Qualità è critica (fact-checking essenziale)
- Task complesso con molti subtask
- Ogni fase richiede expertise specifica

❌ **NON usare Multi-Agente quando**:
- Domanda semplice ("Quanto costa Bitcoin?") → Progetto 2
- Analisi singolo file → Progetto 1
- Velocità più importante di qualità
- Risorse limitate (overhead comunicazione agenti)

### Casi d'Uso Ideali

1. **Due Diligence Aziendale**
   - Research: Cerca info su azienda target
   - Analyst: Valuta salute finanziaria
   - Fact Checker: Verifica claims del management
   - Writer: Report decisionale

2. **Analisi Competitiva**
   - Research: Info su 5 competitor
   - Analyst: Confronta features, pricing, market share
   - Fact Checker: Verifica tutti i numeri
   - Writer: Report strategico

3. **Literature Review Accademica**
   - Research: Trova 50+ papers rilevanti
   - Analyst: Identifica trend, gap nella ricerca
   - Fact Checker: Verifica metodologie
   - Writer: Review formale con citazioni

4. **Investigazioni Giornalistiche**
   - Research: Raccoglie fonti multiple
   - Analyst: Identifica pattern sospetti
   - Fact Checker: Verifica ogni fatto
   - Writer: Articolo bilanciato

5. **Decisioni di Investimento**
   - Research: Dati mercato, notizie, reports
   - Analyst: Analisi rischio/rendimento
   - Fact Checker: Verifica metriche finanziarie
   - Writer: Investment memo

### Il Valore Aggiunto del Multi-Agente

**Singolo Agente Generalista**:
```
Query → [Agente LLM] → Report
        ↑
        Fa tutto: cerca, analizza, scrive
        
Problemi:
- Tende a essere superficiale
- Può inventare fatti
- Bias non controllati
- Qualità inconsistente
```

**Sistema Multi-Agente Specializzato**:
```
Query → [Coordinator] → Piano
          ↓
        [Specialist 1] → Ricerca approfondita
          ↓
        [Specialist 2] → Analisi critica
          ↓
        [Specialist 3] → Verifica fatti
          ↓
        [Specialist 4] → Scrittura professionale
          ↓
        Report di alta qualità
        
Vantaggi:
✓ Ogni fase gestita da esperto
✓ Quality control integrato
✓ Prospettive multiple
✓ Fatti verificati
✓ Output professionale
```

---

## 🎯 Obiettivi di Apprendimento

Questo progetto ti insegna concetti di **AI avanzata** e **sistemi distribuiti**:

### 1. **Architettura Multi-Agente**
Come progettare e coordinare più agenti specializzati:
- Definizione ruoli e responsabilità
- Separazione delle competenze
- Comunicazione inter-agente
- Gestione dello stato condiviso

### 2. **Orchestrazione e Delegazione**
Come un agente principale coordina gli altri:
- Task decomposition (scomposizione compiti)
- Assegnazione task agli agenti appropriati
- Gestione dipendenze tra task
- Aggregazione risultati

### 3. **Patterns di Collaborazione**
Diversi modi in cui gli agenti possono lavorare insieme:
- **Hierarchical**: Orchestratore → Worker agents
- **Sequential**: Agent A → Agent B → Agent C
- **Parallel**: Agenti lavorano simultaneamente
- **Debate**: Agenti con prospettive diverse discutono

### 4. **Memoria Condivisa e Messaggistica**
Come gli agenti condividono informazioni:
- Message passing tra agenti
- Shared memory/blackboard
- Event-driven communication
- Sincronizzazione

### 5. **Emergent Intelligence**
Come la collaborazione produce risultati superiori:
- Specializzazione vs generalizzazione
- Collective reasoning
- Self-correction attraverso feedback
- Quality control multi-prospettiva

---

## 🗂️ Struttura del Progetto

```
multi-agent-system/
│
├── 📄 CODICE PRINCIPALE
│   ├── agents/
│   │   ├── base_agent.py           # Classe base per tutti gli agenti
│   │   ├── researcher_agent.py     # Agente ricerca informazioni
│   │   ├── analyst_agent.py        # Agente analisi e valutazione
│   │   ├── writer_agent.py         # Agente scrittura report
│   │   ├── fact_checker_agent.py   # Agente verifica fatti
│   │   └── coordinator_agent.py    # Agente orchestratore
│   │
│   ├── core/
│   │   ├── orchestrator.py         # Sistema di orchestrazione
│   │   ├── message_bus.py          # Sistema messaggistica
│   │   ├── shared_memory.py        # Memoria condivisa
│   │   ├── task_queue.py           # Coda task
│   │   └── workflow_engine.py      # Engine workflow
│   │
│   ├── tools/
│   │   ├── web_tools.py            # Tools web (dal progetto 2)
│   │   ├── data_tools.py           # Tools analisi dati
│   │   ├── text_tools.py           # Tools elaborazione testo
│   │   └── validation_tools.py     # Tools validazione
│   │
│   ├── workflows/
│   │   ├── research_workflow.py    # Workflow ricerca
│   │   ├── analysis_workflow.py    # Workflow analisi
│   │   └── report_workflow.py      # Workflow generazione report
│   │
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configurazione sistema
│   └── requirements.txt             # Dipendenze
│
├── 📚 CONFIGURAZIONE
│   ├── workflows/                   # Definizioni workflow YAML
│   │   ├── deep_research.yaml
│   │   ├── comparative_analysis.yaml
│   │   └── fact_checking.yaml
│   │
│   ├── agents_config.yaml           # Configurazione agenti
│   └── .env.example                 # Template variabili ambiente
│
├── 🧪 TESTING
│   ├── test_agents.py               # Test singoli agenti
│   ├── test_orchestration.py       # Test coordinazione
│   ├── test_workflows.py            # Test workflow completi
│   └── test_integration.py          # Test end-to-end
│
├── 📖 DOCUMENTAZIONE
│   ├── README.md                    # Questa guida
│   ├── ARCHITECTURE.md              # Architettura dettagliata
│   ├── WORKFLOWS.md                 # Guida workflow
│   ├── PATTERNS.md                  # Pattern di collaborazione
│   └── EXAMPLES.md                  # Esempi pratici
│
└── 📁 ESEMPI
    ├── results/                     # Risultati esempio
    └── templates/                   # Template report
```

---

## 🤖 Gli Agenti del Sistema

### 1. **Coordinator Agent** (Orchestratore)
```python
"""
RUOLO: Coordina l'intero sistema multi-agente

RESPONSABILITÀ:
- Riceve richieste dall'utente
- Scompone task complessi in subtask
- Assegna subtask agli agenti specializzati
- Monitora progresso
- Aggrega risultati finali
- Gestisce errori e retry

CAPABILITIES:
- Task decomposition
- Agent selection
- Dependency management
- Result synthesis
"""

class CoordinatorAgent(BaseAgent):
    def process_request(self, user_request: str) -> str:
        # 1. Analizza richiesta
        plan = self.create_plan(user_request)
        
        # 2. Esegue piano coordinando altri agenti
        results = self.execute_plan(plan)
        
        # 3. Sintetizza risultato finale
        return self.synthesize_results(results)
```

### 2. **Researcher Agent** (Ricercatore)
```python
"""
RUOLO: Trova e raccoglie informazioni

RESPONSABILITÀ:
- Ricerca su web (usando tools progetto 2)
- Estrazione informazioni da documenti
- Identificazione fonti affidabili
- Catalogazione risultati

CAPABILITIES:
- Web search
- Document parsing
- Source evaluation
- Information extraction

SPECIALIZZAZIONE: Quantità di informazioni
"""

class ResearcherAgent(BaseAgent):
    def research_topic(self, topic: str, depth: str = "medium") -> Dict:
        # 1. Cerca informazioni multiple fonti
        sources = self.web_search(topic)
        
        # 2. Estrae contenuti
        content = self.extract_content(sources)
        
        # 3. Organizza risultati
        return self.organize_findings(content)
```

### 3. **Analyst Agent** (Analista)
```python
"""
RUOLO: Analizza e valuta informazioni

RESPONSABILITÀ:
- Valuta qualità e affidabilità informazioni
- Identifica pattern e trend
- Esegue analisi comparative
- Genera insights

CAPABILITIES:
- Critical thinking
- Data analysis
- Pattern recognition
- Quality assessment

SPECIALIZZAZIONE: Qualità delle informazioni
"""

class AnalystAgent(BaseAgent):
    def analyze_data(self, data: Dict) -> Dict:
        # 1. Valuta affidabilità
        credibility = self.assess_credibility(data)
        
        # 2. Identifica pattern
        patterns = self.find_patterns(data)
        
        # 3. Genera insights
        return self.generate_insights(patterns, credibility)
```

### 4. **Writer Agent** (Scrittore)
```python
"""
RUOLO: Genera contenuti strutturati

RESPONSABILITÀ:
- Scrive report professionali
- Struttura informazioni in modo chiaro
- Adatta stile e tono al contesto
- Cita fonti correttamente

CAPABILITIES:
- Professional writing
- Content structuring
- Style adaptation
- Citation formatting

SPECIALIZZAZIONE: Comunicazione efficace
"""

class WriterAgent(BaseAgent):
    def write_report(self, research: Dict, analysis: Dict, 
                    style: str = "professional") -> str:
        # 1. Struttura contenuto
        outline = self.create_outline(research, analysis)
        
        # 2. Scrive sezioni
        sections = self.write_sections(outline, style)
        
        # 3. Formatta e rifinisce
        return self.format_report(sections)
```

### 5. **Fact Checker Agent** (Verificatore)
```python
"""
RUOLO: Verifica accuratezza informazioni

RESPONSABILITÀ:
- Cross-reference tra fonti
- Identifica contraddizioni
- Verifica claim fattuali
- Assegna confidence score

CAPABILITIES:
- Fact verification
- Source cross-referencing
- Consistency checking
- Uncertainty quantification

SPECIALIZZAZIONE: Accuratezza e veridicità
"""

class FactCheckerAgent(BaseAgent):
    def verify_claims(self, claims: List[str], sources: List[Dict]) -> Dict:
        # 1. Per ogni claim, cerca conferme/smentite
        verifications = []
        for claim in claims:
            verification = self.check_claim(claim, sources)
            verifications.append(verification)
        
        # 2. Genera report verifiche
        return self.create_verification_report(verifications)
```

---

## 🏗️ Architettura del Sistema

### Pattern Gerarchico (Hierarchical)

```
┌─────────────────────────────────────────────────────────────────┐
│                    UTENTE                                        │
│   "Fai una ricerca approfondita su quantum computing            │
│    e scrivi un report professionale"                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             COORDINATOR AGENT (Orchestratore)                    │
│                                                                  │
│  1. Analizza richiesta                                          │
│  2. Crea piano:                                                 │
│     • Task A: Research quantum computing                        │
│     • Task B: Analyze findings                                  │
│     • Task C: Verify facts                                      │
│     • Task D: Write report                                      │
│  3. Assegna task agli agenti specializzati                     │
└────┬──────────┬──────────┬──────────┬───────────────────────────┘
     │          │          │          │
     │          │          │          │
┌────▼────┐ ┌──▼──────┐ ┌─▼────────┐ ┌▼─────────┐
│RESEARCH │ │ANALYST  │ │FACT      │ │WRITER    │
│AGENT    │ │AGENT    │ │CHECKER   │ │AGENT     │
│         │ │         │ │AGENT     │ │          │
│Cerca    │ │Valuta   │ │Verifica  │ │Scrive    │
│info su  │ │qualità  │ │accuracy  │ │report    │
│web      │ │e genera │ │delle     │ │finale    │
│         │ │insights │ │info      │ │          │
└────┬────┘ └──┬──────┘ └─┬────────┘ └┬─────────┘
     │          │          │          │
     └──────────┴──────────┴──────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             COORDINATOR AGENT                                    │
│  4. Raccoglie tutti i risultati                                 │
│  5. Sintetizza risposta finale                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RISULTATO FINALE                              │
│   Report professionale con:                                      │
│   - Ricerca completa (Researcher)                               │
│   - Analisi critica (Analyst)                                   │
│   - Fatti verificati (Fact Checker)                             │
│   - Scrittura professionale (Writer)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Sistema di Messaggistica

```python
class Message:
    """
    Messaggio tra agenti
    """
    def __init__(self, 
                 sender: str,
                 receiver: str,
                 msg_type: str,
                 content: Any,
                 metadata: Dict = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.msg_type = msg_type  # "task", "result", "question", "notification"
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()


class MessageBus:
    """
    Sistema di messaggistica tra agenti
    """
    def __init__(self):
        self.messages: Dict[str, Queue] = {}
        self.subscribers: Dict[str, List[str]] = {}
    
    def send(self, message: Message):
        """Invia messaggio a un agente specifico"""
        if message.receiver not in self.messages:
            self.messages[message.receiver] = Queue()
        self.messages[message.receiver].put(message)
    
    def broadcast(self, message: Message):
        """Broadcast a tutti gli agenti sottoscritti"""
        for agent_id in self.subscribers.get(message.msg_type, []):
            self.send(Message(
                sender=message.sender,
                receiver=agent_id,
                msg_type=message.msg_type,
                content=message.content
            ))
    
    def receive(self, agent_id: str, timeout: int = None) -> Message:
        """Ricevi prossimo messaggio"""
        return self.messages[agent_id].get(timeout=timeout)
```

### Shared Memory (Blackboard Pattern)

```python
class SharedMemory:
    """
    Memoria condivisa tra agenti (Blackboard Pattern)
    
    Permette agli agenti di:
    - Scrivere informazioni accessibili a tutti
    - Leggere informazioni di altri agenti
    - Notificare cambiamenti
    """
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.locks: Dict[str, Lock] = {}
        self.observers: Dict[str, List[Callable]] = {}
    
    def write(self, key: str, value: Any, agent_id: str):
        """Scrivi nella memoria condivisa"""
        with self.locks.get(key, Lock()):
            self.data[key] = {
                "value": value,
                "author": agent_id,
                "timestamp": datetime.now()
            }
            # Notifica observers
            self._notify_observers(key)
    
    def read(self, key: str) -> Any:
        """Leggi dalla memoria condivisa"""
        return self.data.get(key, {}).get("value")
    
    def subscribe(self, key: str, callback: Callable):
        """Sottoscrivi a cambiamenti di una chiave"""
        if key not in self.observers:
            self.observers[key] = []
        self.observers[key].append(callback)
```

---

## 🔄 Workflow di Esecuzione

### Workflow 1: Deep Research Report

```yaml
# workflows/deep_research.yaml

name: "Deep Research Report"
description: "Ricerca approfondita con analisi e report professionale"

agents:
  - researcher
  - analyst
  - fact_checker
  - writer

steps:
  - id: research_phase
    agent: researcher
    action: research_topic
    params:
      depth: deep
      sources: 10
    output: research_results
  
  - id: analysis_phase
    agent: analyst
    action: analyze_findings
    depends_on: research_phase
    input: research_results
    output: analysis_results
  
  - id: verification_phase
    agent: fact_checker
    action: verify_claims
    depends_on: [research_phase, analysis_phase]
    input: 
      claims: analysis_results.key_claims
      sources: research_results.sources
    output: verification_results
  
  - id: writing_phase
    agent: writer
    action: write_report
    depends_on: [research_phase, analysis_phase, verification_phase]
    input:
      research: research_results
      analysis: analysis_results
      verification: verification_results
    params:
      style: professional
      format: markdown
    output: final_report

output: final_report
```

### Esecuzione del Workflow

```python
from core.workflow_engine import WorkflowEngine

# Carica workflow
workflow = WorkflowEngine.load("workflows/deep_research.yaml")

# Esegui con parametri
result = workflow.execute({
    "topic": "Quantum Computing Applications in Drug Discovery",
    "target_length": "3000 words",
    "technical_level": "intermediate"
})

# Risultato
print(result.final_report)
# "# Quantum Computing Applications in Drug Discovery
#  
#  ## Executive Summary
#  [Written by Writer Agent]
#  
#  ## Research Findings
#  [Gathered by Researcher Agent, 10 sources]
#  
#  ## Analysis
#  [Analyzed by Analyst Agent]
#  
#  ## Fact Verification
#  [Verified by Fact Checker Agent]
#  - Claim 1: ✓ Verified (3 sources)
#  - Claim 2: ⚠️  Partially verified (conflicting sources)
#  
#  ## Conclusion
#  ..."
```

---

## 🎭 Pattern di Collaborazione

### Pattern 1: Sequential Pipeline

```python
"""
Agenti lavorano in sequenza, output di uno = input del prossimo

RESEARCHER → ANALYST → WRITER

Pro: Semplice, prevedibile
Contro: Lento (no parallelismo)
"""

class SequentialPipeline:
    def execute(self, input_data):
        # Step 1
        research = researcher_agent.process(input_data)
        
        # Step 2
        analysis = analyst_agent.process(research)
        
        # Step 3
        report = writer_agent.process(analysis)
        
        return report
```

### Pattern 2: Parallel Processing

```python
"""
Agenti lavorano in parallelo, risultati aggregati

        ┌─→ RESEARCHER A ─┐
INPUT ──┼─→ RESEARCHER B ─┼─→ AGGREGATOR → OUTPUT
        └─→ RESEARCHER C ─┘

Pro: Veloce, copre più ground
Contro: Necessita aggregazione intelligente
"""

import asyncio

class ParallelProcessing:
    async def execute(self, input_data):
        # Esegui in parallelo
        tasks = [
            researcher_a.research(input_data),
            researcher_b.research(input_data),
            researcher_c.research(input_data)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Aggrega risultati
        return aggregator.combine(results)
```

### Pattern 3: Debate & Consensus

```python
"""
Agenti con prospettive diverse discutono fino a consenso

AGENT A (optimistic) ←→ AGENT B (skeptical)
         ↓
    MODERATOR
         ↓
     CONSENSUS

Pro: Quality control, riduce bias
Contro: Lento, può non convergere
"""

class DebatePattern:
    def execute(self, topic, max_rounds=5):
        for round in range(max_rounds):
            # Posizione Agent A
            position_a = optimistic_agent.argue(topic)
            
            # Posizione Agent B
            position_b = skeptical_agent.counter_argue(position_a)
            
            # Moderatore valuta
            if moderator.is_consensus(position_a, position_b):
                return moderator.synthesize(position_a, position_b)
        
        # No consensus: Moderatore decide
        return moderator.resolve(position_a, position_b)
```

### Pattern 4: Hierarchical Delegation

```python
"""
Manager delega a worker, che possono sub-delegare

         COORDINATOR
         /    |    \
    WORKER1 WORKER2 WORKER3
       |              |
   SUB-WORKER1   SUB-WORKER2

Pro: Scalabile, gestisce complessità
Contro: Overhead comunicazione
"""

class HierarchicalDelegation:
    def execute(self, complex_task):
        # Coordinator scompone
        subtasks = coordinator.decompose(complex_task)
        
        results = []
        for subtask in subtasks:
            # Assegna al worker appropriato
            worker = self.select_worker(subtask)
            
            # Worker può sub-delegare
            result = worker.execute(subtask)
            results.append(result)
        
        # Coordinator aggrega
        return coordinator.aggregate(results)
```

---

## 💡 Esempi Pratici

### Esempio 1: Competitive Analysis

```python
# Query
"""
Analizza i top 3 competitor nel mercato degli smartwatch:
Apple Watch, Samsung Galaxy Watch, Garmin.
Confronta features, pricing, recensioni utenti.
"""

# Workflow Generato dal Coordinator
plan = {
    "phase_1_research": {
        "parallel_tasks": [
            {"agent": "researcher_1", "target": "Apple Watch"},
            {"agent": "researcher_2", "target": "Samsung Galaxy Watch"},
            {"agent": "researcher_3", "target": "Garmin"}
        ]
    },
    "phase_2_analysis": {
        "agent": "analyst",
        "input": "all_research_results",
        "tasks": ["compare_features", "analyze_pricing", "sentiment_analysis"]
    },
    "phase_3_verification": {
        "agent": "fact_checker",
        "input": "analysis_results",
        "verify": ["prices", "technical_specs", "market_share"]
    },
    "phase_4_synthesis": {
        "agent": "writer",
        "input": ["research", "analysis", "verification"],
        "output_format": "comparative_report"
    }
}

# Risultato
"""
# COMPETITIVE ANALYSIS: Smartwatch Market Leaders

## Executive Summary
[Synthesized by Writer Agent]
Analysis of Apple Watch Series 9, Samsung Galaxy Watch 6, and Garmin Forerunner 965...

## Product Comparison Matrix
[Researched by 3 Researcher Agents in parallel]

| Feature | Apple Watch | Samsung Watch | Garmin |
|---------|------------|---------------|--------|
| Battery | 18h | 40h | 23 days | ✓ Verified
| Price | $399 | $299 | $599 | ✓ Verified
| Health Features | ECG, Blood O2 | ECG, Body Comp | Advanced Sports | ✓ Verified

## Market Analysis
[Analyzed by Analyst Agent]
- Apple: 34% market share, premium positioning
- Samsung: 18% market share, Android ecosystem
- Garmin: 9% market share, sports/fitness niche

## User Sentiment
[Analyzed from 1,247 reviews]
- Apple: 4.6/5 stars (ease of use praised, battery criticized)
- Samsung: 4.4/5 stars (features praised, UI criticized)
- Garmin: 4.8/5 stars (battery praised, price criticized)

## Fact Verification Status
[Verified by Fact Checker Agent]
✓ All prices verified across 3 sources (last updated: today)
✓ Technical specifications confirmed from official sources
⚠️ Market share data from Q3 2024 (industry estimates vary ±2%)

## Recommendation
Based on use case:
- Best for iPhone users: Apple Watch
- Best battery life: Garmin
- Best value: Samsung
"""
```

### Esempio 2: Controversial Topic Research

```python
# Query
"""
Fai una ricerca bilanciata su 'Impact of AI on job market'.
Presenta sia prospettive ottimistiche che pessimistiche,
citando studi e dati.
"""

# Workflow: Debate Pattern
plan = {
    "phase_1_research": {
        "agent": "researcher",
        "scope": "comprehensive",
        "sources": 20
    },
    "phase_2_debate": {
        "agents": {
            "optimistic_analyst": "Focus on job creation, productivity gains",
            "pessimistic_analyst": "Focus on job displacement, inequality"
        },
        "rounds": 3,
        "moderator": "neutral_analyst"
    },
    "phase_3_fact_check": {
        "agent": "fact_checker",
        "verify_all_claims": True
    },
    "phase_4_synthesis": {
        "agent": "writer",
        "style": "balanced_academic"
    }
}

# Esecuzione Debate
"""
ROUND 1:
Optimistic: "AI will create 97M new jobs by 2025 (WEF report)"
Pessimistic: "But displace 85M jobs, net loss in short term"

ROUND 2:
Optimistic: "Historical precedent: tech always created more jobs"
Pessimistic: "This time different: AI replaces cognitive work, not just manual"

ROUND 3:
Moderator: "Both valid. Evidence suggests transition period with..."
→ Consensus reached on nuanced view
"""

# Risultato
"""
# AI Impact on Job Market: A Balanced Analysis

## Overview
[Synthesized from debate between 2 analyst perspectives]

This report examines both optimistic and pessimistic viewpoints on AI's
impact on employment, based on analysis of 20 studies and 3 rounds of
critical debate.

## Optimistic Perspective
[Argued by Optimistic Analyst Agent]

### Key Arguments:
1. **Job Creation**: WEF estimates 97M new AI-related jobs by 2025
   [✓ Verified: WEF Future of Jobs Report 2020]

2. **Productivity Gains**: AI increases worker productivity by 40%
   [✓ Verified: Stanford & MIT study, 5,000 workers]

3. **Historical Precedent**: Previous tech revolutions created jobs
   [✓ Verified: Multiple economic history sources]

## Pessimistic Perspective
[Argued by Pessimistic Analyst Agent]

### Key Arguments:
1. **Job Displacement**: 85M jobs at risk by 2025 (same WEF report)
   [✓ Verified: WEF Future of Jobs Report 2020]

2. **Inequality**: Benefits concentrated in high-skill workers
   [✓ Verified: McKinsey Global Institute research]

3. **Uniqueness**: AI targets cognitive work, unprecedented
   [⚠️ Partially verified: Debated among economists]

## Consensus View
[Moderated synthesis]

### Areas of Agreement:
- Significant disruption inevitable
- Transition period will be challenging
- Retraining programs essential
- Policy intervention needed

### Remaining Uncertainties:
- Net job creation/loss timeline
- Which sectors most affected
- Effectiveness of policy responses

## Data Summary
- Sources analyzed: 20 academic + industry reports
- Claims verified: 47/52 (90%)
- Confidence level: High on trends, Medium on magnitudes

## Conclusion
Neither pure optimism nor pessimism warranted. Outcome depends heavily
on policy choices and adaptation speed...
"""
```

### Esempio 3: Real-time Multi-Source Monitoring

```python
# Query
"""
Monitora in tempo reale notizie su 'Bitcoin price' da 5 fonti diverse.
Ogni 5 minuti, aggrega e identifica trend.
Allerta se variazione > 5%.
"""

# Workflow: Event-Driven + Parallel
plan = {
    "monitoring_agents": [
        {"agent": "monitor_1", "source": "CoinDesk"},
        {"agent": "monitor_2", "source": "Bloomberg"},
        {"agent": "monitor_3", "source": "Reuters"},
        {"agent": "monitor_4", "source": "Twitter"},
        {"agent": "monitor_5", "source": "Reddit"}
    ],
    "aggregator": "analyst_agent",
    "alerter": "notification_agent",
    "interval": 300  # seconds
}

# Sistema Event-Driven
class MonitoringSystem:
    async def run(self):
        while True:
            # Raccogli dati da tutti i monitor in parallelo
            data = await self.gather_all_sources()
            
            # Aggregatore analizza
            analysis = analyst.analyze_trends(data)
            
            # Check alert conditions
            if analysis.price_change > 0.05:
                await notifier.send_alert(analysis)
            
            # Scrivi su shared memory
            shared_memory.write("latest_btc_analysis", analysis)
            
            # Wait interval
            await asyncio.sleep(300)

# Output esempio (ogni 5 min)
"""
[14:05] Bitcoin Aggregate Analysis
├─ CoinDesk: $43,250 (↑2.1%)
├─ Bloomberg: $43,180 (↑1.9%)
├─ Reuters: $43,300 (↑2.3%)
├─ Twitter sentiment: Bullish (confidence: 72%)
└─ Reddit sentiment: Mixed (confidence: 54%)

Aggregated: $43,243 (↑2.1% vs 5min ago)
Trend: Slight upward momentum
Alert: None (threshold: ±5%)

[14:10] Bitcoin Aggregate Analysis
...
[14:15] 🚨 ALERT: +6.2% spike detected!
All sources confirm sudden increase...
"""
```

---

## 🛠️ Componenti Tecnici Chiave

### 1. Task Queue & Scheduler

```python
class TaskQueue:
    """
    Coda task con priorità e scheduling
    """
    def __init__(self):
        self.queue = PriorityQueue()
        self.in_progress: Set[str] = set()
        self.completed: Set[str] = set()
    
    def add_task(self, task: Task, priority: int = 0):
        """Aggiungi task alla coda"""
        self.queue.put((priority, task))
    
    def get_next_task(self, agent_capabilities: List[str]) -> Task:
        """Ottieni prossimo task per agente con certe capabilities"""
        for priority, task in self.queue:
            if task.required_capability in agent_capabilities:
                self.in_progress.add(task.id)
                return task
        return None
    
    def mark_complete(self, task_id: str, result: Any):
        """Marca task come completato"""
        self.in_progress.remove(task_id)
        self.completed.add(task_id)
```

### 2. Dependency Graph

```python
class DependencyGraph:
    """
    Gestisce dipendenze tra task
    """
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
    
    def add_dependency(self, task_id: str, depends_on: str):
        """Task A dipende da Task B"""
        if task_id not in self.graph:
            self.graph[task_id] = set()
        self.graph[task_id].add(depends_on)
    
    def can_execute(self, task_id: str, completed: Set[str]) -> bool:
        """Verifica se task può essere eseguito"""
        dependencies = self.graph.get(task_id, set())
        return dependencies.issubset(completed)
    
    def get_execution_order(self) -> List[str]:
        """Topological sort per ordine esecuzione"""
        return topological_sort(self.graph)
```

### 3. Agent Registry & Discovery

```python
class AgentRegistry:
    """
    Registro di tutti gli agenti disponibili
    """
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.capabilities: Dict[str, List[str]] = {}
    
    def register(self, agent: BaseAgent):
        """Registra nuovo agente"""
        self.agents[agent.id] = agent
        self.capabilities[agent.id] = agent.capabilities
    
    def find_agent_for_task(self, task: Task) -> BaseAgent:
        """Trova agente migliore per task"""
        candidates = [
            agent_id for agent_id, caps in self.capabilities.items()
            if task.required_capability in caps
        ]
        
        # Scegli agente meno carico
        return min(candidates, key=lambda a: self.agents[a].workload)
```

### 4. Result Aggregator

```python
class ResultAggregator:
    """
    Aggrega risultati da agenti multipli
    """
    def aggregate(self, results: List[AgentResult], 
                 strategy: str = "consensus") -> Any:
        """
        Strategie:
        - consensus: Maggioranza
        - weighted: Media pesata per confidence
        - ensemble: Combina tutti
        - best: Prendi solo il migliore
        """
        if strategy == "consensus":
            return self._consensus(results)
        elif strategy == "weighted":
            return self._weighted_average(results)
        elif strategy == "ensemble":
            return self._ensemble(results)
        else:
            return self._best(results)
    
    def _consensus(self, results: List[AgentResult]) -> Any:
        """Trova consenso tra risultati"""
        from collections import Counter
        values = [r.value for r in results]
        return Counter(values).most_common(1)[0][0]
```

---

## 📋 Requisiti e Installazione

### Prerequisiti

```bash
# Python 3.9+ (per async/await features)
python --version

# Ollama o OpenAI API
ollama --version

# Redis (opzionale, per message queue distribuita)
redis-cli --version
```

### Installazione

```bash
# 1. Setup progetto
cd multi-agent-system

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura
cp .env.example .env
# Edita .env con configurazioni

# 4. Inizializza database (se usi persistence)
python scripts/init_db.py

# 5. Test
python test_system.py

# 6. Avvia sistema
python main.py
```

### Dipendenze

```txt
# Da progetti precedenti
requests
beautifulsoup4
ollama
# ... (vedi progetto 1 e 2)

# Nuove dipendenze multi-agente
celery                    # Task queue distribuita
redis                     # Message broker
pydantic                  # Data validation
networkx                  # Dependency graphs
asyncio                   # Async execution
aiohttp                   # Async HTTP

# Workflow
pyyaml                    # Workflow configs
jsonschema                # Schema validation

# Monitoring
prometheus-client         # Metrics
structlog                 # Structured logging

# Testing
pytest-asyncio            # Async tests
pytest-mock              # Mocking
faker                     # Test data
```

---

## 🎯 Metriche e Monitoring

### Dashboard Esempio

```python
class SystemMetrics:
    """
    Metriche del sistema multi-agente
    """
    def __init__(self):
        self.tasks_completed = Counter()
        self.agent_utilization = {}
        self.avg_response_time = {}
        self.error_rate = {}
    
    def get_dashboard(self) -> Dict:
        return {
            "total_tasks": sum(self.tasks_completed.values()),
            "active_agents": len(self.agent_utilization),
            "avg_response_time": mean(self.avg_response_time.values()),
            "success_rate": 1 - mean(self.error_rate.values()),
            "agent_breakdown": {
                agent_id: {
                    "tasks_completed": self.tasks_completed[agent_id],
                    "utilization": self.agent_utilization[agent_id],
                    "avg_time": self.avg_response_time[agent_id],
                    "error_rate": self.error_rate[agent_id]
                }
                for agent_id in self.agent_utilization
            }
        }
```

Output:
```json
{
  "total_tasks": 1247,
  "active_agents": 5,
  "avg_response_time": 3.2,
  "success_rate": 0.96,
  "agent_breakdown": {
    "researcher_agent": {
      "tasks_completed": 523,
      "utilization": 0.78,
      "avg_time": 4.1,
      "error_rate": 0.02
    },
    "analyst_agent": {
      "tasks_completed": 312,
      "utilization": 0.65,
      "avg_time": 2.8,
      "error_rate": 0.05
    }
  }
}
```

---

## 🚀 Estensioni e Miglioramenti

### Livello Avanzato
- [ ] **Self-improving agents**: Agenti che imparano da feedback
- [ ] **Dynamic agent spawning**: Crea agenti on-demand
- [ ] **Agent marketplace**: Agenti possono offrire/richiedere servizi
- [ ] **Consensus algorithms**: Byzantine fault tolerance

### Livello Produzione
- [ ] **Distributed system**: Multi-machine deployment
- [ ] **Load balancing**: Distribuzione carico tra agenti
- [ ] **Fault tolerance**: Retry, failover, circuit breakers
- [ ] **Observability**: Tracing, logging, monitoring completi

### Livello Ricerca
- [ ] **Emergent behavior**: Studio comportamenti emergenti
- [ ] **Agent evolution**: Selezione naturale di strategie
- [ ] **Game theory**: Agenti con incentivi economici
- [ ] **Swarm intelligence**: Pattern da sistemi biologici

---

## 🤝 Confronto Progetti

| Aspetto | Progetto 1 | Progetto 2 | Progetto 3 |
|---------|-----------|-----------|-----------|
| **Livello** | Base | Intermedio | Avanzato |
| **Agenti** | 1 | 1 | 5+ |
| **Coordinazione** | N/A | N/A | Orchestratore |
| **Comunicazione** | N/A | N/A | Message passing |
| **Tools** | 1 fisso | 5+ dinamici | N tools × M agenti |
| **Planning** | Single-step | Multi-step | Multi-agent planning |
| **Errori** | Semplici | Network | Distributed failures |
| **Scalabilità** | File size | Web scraping | Number of agents |
| **Complessità** | O(1) | O(n) | O(n²) |

---

## 📚 Pattern e Best Practices

### Best Practices

1. **Separazione Responsabilità**
   - Ogni agente un ruolo chiaro e limitato
   - No overlap di responsabilità
   - Interface-based design

2. **Comunicazione Asincrona**
   - Usa message queues
   - Non bloccare agenti in attesa
   - Timeout su tutte le operazioni

3. **Idempotenza**
   - Task ripetibili senza effetti collaterali
   - Gestione duplicati
   - Transazioni atomiche

4. **Monitoring & Observability**
   - Log strutturati
   - Metriche per ogni agente
   - Distributed tracing

5. **Graceful Degradation**
   - Sistema funziona anche se agente fallisce
   - Fallback strategies
   - Partial results meglio di niente

---

## 📖 Risorse Utili

- **Multi-Agent Systems**: Wooldridge - "Introduction to MultiAgent Systems"
- **Distributed Systems**: Kleppmann - "Designing Data-Intensive Applications"
- **AutoGPT**: https://github.com/Significant-Gravitas/Auto-GPT
- **LangGraph**: https://python.langchain.com/docs/langgraph
- **CrewAI**: https://github.com/joaomdmoura/crewAI

---

## 🎓 Cosa Hai Imparato

Completando questo progetto hai imparato:

✅ Progettare sistemi multi-agente complessi  
✅ Orchestrazione e coordinazione distribuita  
✅ Message passing e shared memory patterns  
✅ Workflow automation con agenti  
✅ Collaborative AI problem solving  
✅ Scalabilità e fault tolerance  
✅ Emergent intelligence da cooperazione  

Sei ora pronto per costruire **sistemi AI di livello enterprise**! 🚀

---

**Buon coding con i multi-agenti!**

*Remember: Il vero potere non è nel singolo agente, ma nella loro collaborazione.*
