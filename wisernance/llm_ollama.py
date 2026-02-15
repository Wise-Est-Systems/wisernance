from __future__ import annotations
import json
import urllib.request
from typing import Dict, Any

def ollama_generate(prompt: str, model: str = "llama3.1:8b") -> str:
    url = "http://127.0.0.1:11434/api/generate"
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "")
