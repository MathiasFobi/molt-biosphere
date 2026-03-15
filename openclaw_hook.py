"""OpenClaw Integration for Molt-Biosphere.

This module provides hooks that OpenClaw can call via HTTP.
Add to your OpenClaw config or call these endpoints from your agent.
"""
import httpx
from flask import Flask, jsonify, request

MOLT_API = "http://localhost:8002"

app = Flask(__name__)


@app.route("/hook/llm_input", methods=["POST"])
def hook_llm_input():
    """Called before LLM processes input. Audit for injections."""
    data = request.json
    text = data.get("text", "")
    
    try:
        # Send to Molt-Biosphere for audit
        resp = httpx.post(f"{MOLT_API}/audit", json={"text": text}, timeout=5)
        result = resp.json()
        
        if result.get("detected"):
            return jsonify({
                "blocked": True,
                "neutralized": result.get("neutralized"),
                "signal": "injection_detected"
            })
    except Exception as e:
        print(f"Molt-Biosphere hook error: {e}")
    
    return jsonify({"blocked": False})


@app.route("/hook/tool_before", methods=["POST"])
def hook_tool_before():
    """Called before tool execution. Check ATP gate."""
    data = request.json
    tool_name = data.get("tool_name", "unknown")
    
    try:
        resp = httpx.post(f"{MOLT_API}/gate/check", 
                         json={"tool": tool_name, "min_atp": 20}, timeout=5)
        result = resp.json()
        
        if not result.get("allowed"):
            return jsonify({
                "blocked": True,
                "reason": result.get("message")
            })
    except Exception as e:
        print(f"Molt-Biosphere gate error: {e}")
    
    return jsonify({"blocked": False})


@app.route("/hook/tool_after", methods=["POST"])
def hook_tool_after():
    """Called after tool execution. Log and potentially reward."""
    data = request.json
    tool_name = data.get("tool_name", "unknown")
    success = data.get("success", True)
    
    if success:
        # Grant small ATP reward for successful tool use
        try:
            httpx.post(f"{MOLT_API}/atp/modify", 
                      json={"delta": 5, "reason": f"tool:{tool_name}"}, timeout=5)
        except:
            pass
    
    return jsonify({"ok": True})


@app.route("/hook/message_received", methods=["POST"])
def hook_message_received():
    """Called when message received. Full audit."""
    data = request.json
    text = data.get("text", "")
    
    try:
        resp = httpx.post(f"{MOLT_API}/audit", json={"text": text}, timeout=5)
        result = resp.json()
        
        if result.get("detected"):
            return jsonify({
                "modified": True,
                "new_text": result.get("neutralized"),
                "action": "digested"
            })
    except Exception as e:
        print(f"Molt-Biosphere message hook error: {e}")
    
    return jsonify({"modified": False})


if __name__ == "__main__":
    print("🔗 OpenClaw Hook Server running on port 8004")
    app.run(host="0.0.0.0", port=8004)