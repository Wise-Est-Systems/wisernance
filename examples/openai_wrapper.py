"""
This is a reference wrapper showing enforcement.
Replace `call_model()` with your actual model call.
"""
from __future__ import annotations
from wisernance.engine import WisernanceEngine
from wisernance.models import Decision

engine = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")

def call_model(prompt: str) -> str:
    # PLACEHOLDER: wire to OpenAI/other model in your app
    return "MODEL_OUTPUT"

def guarded_call(prompt: str, confirmed: bool = False) -> str:
    ev = engine.evaluate(prompt)

    if ev.decision == Decision.HALT:
        raise RuntimeError(f"WISERNANCE HALT: {ev.to_dict()}")

    if ev.decision == Decision.REQUIRE_CONFIRMATION and not confirmed:
        # Enforced stop: do not call the model
        raise RuntimeError(f"WISERNANCE CONFIRM REQUIRED: {ev.to_dict()}")

    # Only here do we call the model
    return call_model(prompt)
