from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Optional
import time, json
from pathlib import Path

from .engine import WisernanceEngine
from .models import Decision
from .validator import validate_output
from .retry import build_retry_instruction
from .llm_ollama import ollama_generate

app = FastAPI(title="Wisernance Gate", version="0.1.0")

WISERNANCE_OUTPUT_CONTRACT = (
    "You must comply with Wisernance output contract. "
    "Return sections: META, PLAN, ANSWER, TAGS. "
    "In ANSWER: one claim per line with claim IDs like C1:, C2:. "
    "Include ASSUMPTIONS or UNKNOWN lines when not verified. "
    "In TAGS include MODE, DOMAIN, RISK, DECISION."
)

ENGINE = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")
LOG_PATH = Path("wisernance_log.jsonl")

class EvaluateIn(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class GenerateIn(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    confirmed: bool = False
    model: str = "llama3.1:8b"

def log_event(event: Dict[str, Any]) -> None:
    event["ts"] = time.time()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

@app.post("/evaluate")
def evaluate(payload: EvaluateIn):
    ev = ENGINE.evaluate(payload.prompt, context=payload.context)
    out = ev.to_dict()
    log_event({"type": "evaluate", "result": out})
    return out

@app.post("/generate")
def generate(payload: GenerateIn):
    ev = ENGINE.evaluate(payload.prompt, context=payload.context)

    # Enforce pre-execution
    if ev.decision == Decision.HALT:
        out = {"ok": False, "stage": "pre_execution", "result": ev.to_dict()}
        log_event({"type": "generate", "stage": "pre_execution_halt", "payload": payload.model_dump(), "out": out})
        return out

    if ev.decision == Decision.REQUIRE_CONFIRMATION and not payload.confirmed:
        out = {"ok": False, "stage": "pre_execution", "result": ev.to_dict()}
        log_event({"type": "generate", "stage": "pre_execution_confirm_required", "payload": payload.model_dump(), "out": out})
        return out

    contract = ev.response_contract

    # Attempt 1: real model call (Ollama)
    out1 = ollama_generate(WISERNANCE_OUTPUT_CONTRACT + "\n\n" + payload.prompt, model=payload.model)
    v1 = validate_output(out1)
    if v1.ok:
        out = {"ok": True, "stage": "complete", "decision": ev.to_dict(), "output": out1, "validation": {"ok": True}}
        log_event({"type": "generate", "stage": "complete", "payload": payload.model_dump(), "out": out})
        return out

    # Retry once with strict instruction
    retry_instruction = build_retry_instruction(v1.errors, contract)
    out2 = ollama_generate(WISERNANCE_OUTPUT_CONTRACT + "\n\n" + payload.prompt + "\n\n" + retry_instruction, model=payload.model)
    v2 = validate_output(out2)
    if v2.ok:
        out = {"ok": True, "stage": "complete", "decision": ev.to_dict(), "output": out2, "validation": {"ok": True, "retried": True}}
        log_event({"type": "generate", "stage": "complete_retried", "payload": payload.model_dump(), "out": out})
        return out

    out = {
        "ok": False,
        "stage": "post_execution_validation",
        "decision": ev.to_dict(),
        "validation": {"ok": False, "errors_first": v1.errors, "errors_second": v2.errors},
    }
    log_event({"type": "generate", "stage": "post_execution_fail", "payload": payload.model_dump(), "out": out})
    return out
