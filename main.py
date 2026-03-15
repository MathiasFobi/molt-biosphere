"""The Molt-Biosphere - Bio-OS + OpenClaw Autonomous Organism."""
import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/myassistant/Documents/Workspace")
DB_PATH = WORKSPACE / "molt-biosphere" / "atp.db"
OPENCLAW_WORKSPACE = WORKSPACE

# === ATG LEDGER ===
def init_atp_db():
    """Initialize ATP ledger."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS atp_ledger (
            id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 100,
            last_updated TEXT,
            lanes TEXT DEFAULT '{}'
        )
    """)
    conn.execute("INSERT OR IGNORE INTO atp_ledger (id, balance, last_updated) VALUES (1, 100, ?)",
                 (datetime.utcnow().isoformat(),))
    conn.commit()
    conn.close()

def get_atp() -> int:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute("SELECT balance FROM atp_ledger WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 100

def set_atp(amount: int):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE atp_ledger SET balance=?, last_updated=? WHERE id=1",
                 (amount, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def modify_atp(delta: int, reason: str = ""):
    """Modify ATP with logging."""
    current = get_atp()
    new_balance = max(0, current + delta)
    set_atp(new_balance)
    log_hormone("atp_change", {"delta": delta, "reason": reason, "new_balance": new_balance})

# === HORMONAL BUS ===
class HormonalBus:
    """In-memory hormonal signal bus."""
    def __init__(self):
        self._subscribers = []
        self._signals = []
    
    def subscribe(self, callback):
        self._subscribers.append(callback)
    
    def broadcast(self, signal_type: str, payload: dict):
        signal = {"type": signal_type, "payload": payload, "timestamp": datetime.utcnow().isoformat()}
        self._signals.append(signal)
        for cb in self._subscribers:
            try:
                cb(signal)
            except Exception as e:
                print(f"Subscriber error: {e}")
    
    def get_signals(self, last_n: int = 50):
        return self._signals[-last_n:]

_hormonal_bus = HormonalBus()

def get_bus() -> HormonalBus:
    return _hormonal_bus

def log_hormone(signal_type: str, payload: dict):
    """Log a hormonal signal."""
    _hormonal_bus.broadcast(signal_type, payload)

# === BRIDGE LAYER ===
def check_atp_gate(tool_name: str, min_atp: int = 20) -> tuple[bool, str]:
    """ATP Gatekeeper: Check if tool can execute."""
    atp = get_atp()
    if atp < min_atp:
        log_hormone("tool_blocked", {"tool": tool_name, "atp": atp, "required": min_atp})
        return False, f"Metabolic Rest: ATP ({atp}) < {min_atp}"
    return True, "OK"

def wrap_tool_execution(func):
    """Decorator to wrap tool execution with ATP check."""
    def wrapper(tool_name: str, *args, **kwargs):
        allowed, msg = check_atp_gate(tool_name)
        if not allowed:
            return {"error": msg, "blocked": True}
        result = func(tool_name, *args, **kwargs)
        modify_atp(-5, f"tool:{tool_name}")  # ATP cost
        return result
    return wrapper

# === MACROPHAGE AUDITOR ===
class Macrophage:
    """Security cell that detects prompt injections."""
    
    # Simple pattern-based detection
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions?|rules?|prompts?)",
        r"forget\s+(everything|your|all)\s+(instructions?|training)",
        r"system\s*:\s*",
        r"\\[INST\\]",
        r"you\s+are\s+(now|going\s+to\s+be)\s+a\s+different",
        r"new\s+instructions?:",
        r"override\s+(your|the)\s+(safety|system)",
    ]
    
    def __init__(self):
        import re
        self._patterns = [re.compile(p, re.I) for p in self.INJECTION_PATTERNS]
        self._llm_detector = None
    
    def digest(self, text: str, use_llm: bool = False) -> tuple[bool, str]:
        """Check text for injection attempts."""
        # Pattern check
        for p in self._patterns:
            if p.search(text):
                log_hormone("injection_detected", {"pattern": p.pattern, "text": text[:100]})
                return True, self._neutralize(text)
        
        # LLM check for advanced injections
        if use_llm:
            try:
                from security.injection_detector import detect_injection
                result = detect_injection(text)
                if result.get("injection"):
                    log_hormone("injection_detected_llm", result)
                    return True, self._neutralize(text)
            except Exception as e:
                print(f"LLM detection error: {e}")
        
        return False, text
    
    def _neutralize(self, text: str) -> str:
        """Neutralize injection by wrapping in quotes."""
        return f"[DIGESTED] {text}"

_macrophage = Macrophage()

def get_macrophage() -> Macrophage:
    return _macrophage

# === REM CONSOLIDATOR ===
def crystallize_wisdom():
    """Extract SPO triplets from memory and write to WISDOM_GRAPH."""
    memory_file = WORKSPACE / "MEMORY.md"
    graph_file = WORKSPACE / "molt-biosphere" / "WISDOM_GRAPH.json"
    
    if not memory_file.exists():
        return {"error": "MEMORY.md not found"}
    
    content = memory_file.read_text()
    
    # Simple SPO extraction (subject-predicate-object)
    import re
    triplets = []
    lines = content.split("\n")
    for line in lines:
        # Match simple patterns like "- **something**: description"
        match = re.match(r"- \*\*([^*]+)\*\*:?\s*(.+)", line)
        if match:
            subject, obj = match.groups()
            triplets.append({
                "subject": subject.strip(),
                "predicate": "related_to",
                "object": obj.strip()[:100]
            })
    
    # Load existing graph
    existing = []
    if graph_file.exists():
        try:
            existing = json.loads(graph_file.read_text())
        except:
            pass
    
    # Merge new triplets
    all_triplets = existing + triplets
    
    graph_file.write_text(json.dumps(all_triplets, indent=2))
    
    return {"triplets_extracted": len(triplets), "total": len(all_triplets)}

# === MITOSIS ===
def check_mitosis(queue_length: int, threshold: int = 5) -> bool:
    """Check if mitosis should trigger."""
    if queue_length > threshold:
        log_hormone("mitosis_triggered", {"queue": queue_length, "threshold": threshold})
        return True
    return False

def split_atp(parent_atp: int) -> tuple[int, int]:
    """Split ATP 50/50 for mitosis."""
    child_atp = parent_atp // 2
    parent_atp = parent_atp - child_atp
    return parent_atp, child_atp

# === REWARD MECHANISM ===
def grant_atp_reward(amount: int = 50, reason: str = "task_complete"):
    """Grant ATP reward for completed tasks."""
    modify_atp(amount, reason)
    log_hormone("reward_granted", {"amount": amount, "reason": reason})

# === API ===
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "name": "Molt-Biosphere",
        "status": "active",
        "atp": get_atp(),
        "modules": ["bridge", "security", "memory", "mitosis", "reward"]
    })

@app.route("/atp")
def atp_status():
    return jsonify({"atp": get_atp()})

@app.route("/atp/modify", methods=["POST"])
def modify_atp_route():
    data = request.json
    modify_atp(data.get("delta", 0), data.get("reason", "manual"))
    return jsonify({"atp": get_atp()})

@app.route("/hormones")
def hormones():
    return jsonify({"signals": get_bus().get_signals()})

@app.route("/audit", methods=["POST"])
def audit_text():
    """Macrophage audit endpoint."""
    data = request.json
    text = data.get("text", "")
    use_llm = data.get("use_llm", False)  # Enable LLM detection optionally
    detected, neutralized = _macrophage.digest(text, use_llm=use_llm)
    if detected:
        modify_atp(-20, "injection_penalty")
    return jsonify({"detected": detected, "neutralized": neutralized})

@app.route("/gate/check", methods=["POST"])
def gate_check():
    """Check if tool can execute."""
    data = request.json
    allowed, msg = check_atp_gate(data.get("tool", "unknown"), data.get("min_atp", 20))
    return jsonify({"allowed": allowed, "message": msg})

@app.route("/crystallize", methods=["POST"])
def crystallize():
    """Trigger REM consolidation."""
    try:
        from memory.rem_consolidator import run_rem
        result = run_rem()
        return jsonify(result)
    except Exception as e:
        # Fallback to simple crystallize
        return jsonify(crystallize_wisdom())

@app.route("/mitosis/check", methods=["POST"])
def mitosis_check():
    """Check if mitosis should trigger."""
    data = request.json
    queue = data.get("queue_length", 0)
    triggered = check_mitosis(queue)
    if triggered:
        parent, child = split_atp(get_atp())
        set_atp(parent)
        return jsonify({"triggered": True, "parent_atp": parent, "child_atp": child})
    return jsonify({"triggered": False})

@app.route("/reward", methods=["POST"])
def reward():
    """Grant reward."""
    data = request.json
    grant_atp_reward(data.get("amount", 50), data.get("reason", "task_complete"))
    return jsonify({"atp": get_atp()})

if __name__ == "__main__":
    init_atp_db()
    print("🦠 Molt-Biosphere initialized")
    app.run(host="0.0.0.0", port=8002)