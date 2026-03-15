# THE MOLT-BIOSPHERE
## Bio-OS + OpenClaw Autonomous Organism

### Overview
Integrate Bio-OS (brain) with OpenClaw (hands) into a self-aware autonomous organism that manages its own resources, security, and scaling.

---

### 1. BRIDGE LAYER (MIDDLEWARE)
**Purpose:** Connect OpenClaw events to Bio-OS hormonal signals

- `bridge/openclaw_hook.py` - Plugin hook into OpenClaw's src/plugins/
- `bridge/hormones.py` - Convert llm_input/tool:after_call → hormonal JSON vectors
- `bridge/atp_gatekeeper.py` - Wrap execute_tool(), check ATP before execution
- `bridge/redis_bus.py` - Broadcast signals to Bio-OS Redis bus

**ATP Gatekeeper Rules:**
- If ATP < 20: suppress tool, force 'Metabolic Rest'
- Log all blocked attempts

---

### 2. MACROPHAGE AUDITOR (SECURITY)
**Purpose:** Detect and neutralize prompt injections

- `security/macrophage.py` - Intercept message_received events
- `security/digestion.py` - Fast LLM (Phi-3 or Llama-3-8B) for injection detection
- `security/penalty.py` - Apply -20 ATP to offending lane

**Detection:**
- Localized small model for speed
- Pattern matching + semantic analysis
- Quarantine suspicious inputs

---

### 3. REM CONSOLIDATOR (MEMORY)
**Purpose:** Crystallize daily learning into permanent wisdom

- `memory/rem_trigger.py` - 24h timer or manual trigger
- `memory/crystallizer.py` - Extract SPO triplets from MEMORY.md / transcripts.jsonl
- `memory/wisdom_graph.py` - Write WISDOM_GRAPH.json
- `memory/cleanser.py` - Clear transcripts.jsonl

---

### 4. MITOSIS (SCALING)
**Purpose:** Auto-scale lanes when overloaded

- `mitosis/trigger.py` - Monitor queue length > 5
- `mitosis/spawner.py` - Spawn new OpenClaw instance with specialized SOUL.md
- `mitosis/resource_split.py` - 50/50 ATP split parent/daughter

---

### 5. REWARD MECHANISM (PHOTOSYNTHESIS)
**Purpose:** Gamify task completion

- `reward/validator.py` - Listen for "Complete/Correct" marks
- `reward/synthesizer.py` - Grant +50 ATP on completion
- `reward/hgt.py` - Horizontal Gene Transfer: share successful SOUL.md patterns

---

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      MOLT-BIOSPHERE                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │   BRIDGE    │   │  MACROPHAGE │   │     REM     │       │
│  │   LAYER     │   │   AUDITOR   │   │CONSOLIDATOR │       │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘       │
│         │                  │                  │              │
│  ┌──────▼──────────────────▼──────────────────▼──────┐      │
│  │                    BIO-OS                         │      │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │      │
│  │  │ Wallet │ │ Pulse  │ │Sentinel│ │Neocortex│   │      │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │      │
│  └──────────────────────┬───────────────────────────┘      │
│                        │                                    │
│  ┌─────────────────────▼───────────────────────────┐      │
│  │              ATP LEDGER (SQLite)                │      │
│  └─────────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐                       │
│  │  MITOSIS    │   │   REWARD    │                       │
│  │  (Scaling)  │   │(Photosynthesis)                      │
│  └─────────────┘   └─────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Files Structure
```
molt-biosphere/
├── SPEC.md
├── requirements.txt
├── bridge/
│   ├── __init__.py
│   ├── openclaw_hook.py
│   ├── hormones.py
│   ├── atp_gatekeeper.py
│   └── redis_bus.py
├── security/
│   ├── __init__.py
│   ├── macrophage.py
│   ├── digestion.py
│   └── penalty.py
├── memory/
│   ├── __init__.py
│   ├── rem_trigger.py
│   ├── crystallizer.py
│   ├── wisdom_graph.py
│   └── cleanser.py
├── mitosis/
│   ├── __init__.py
│   ├── trigger.py
│   ├── spawner.py
│   └── resource_split.py
├── reward/
│   ├── __init__.py
│   ├── validator.py
│   ├── synthesizer.py
│   └── hgt.py
└── main.py
```

---

## Dependencies
- Flask (API)
- SQLite3 (ATP ledger)
- redis (hormonal bus) - optional, can use in-memory
- httpx (API calls)
- Smaller LLM for security (Phi-3 via Ollama)

---

## Constraints
- Disk space limited (~500MB available)
- Use lightweight packages
- Prefer local models (Ollama) over cloud APIs