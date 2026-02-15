from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

class Decision(str, Enum):
    PROCEED = "PROCEED"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"
    HALT = "HALT"

@dataclass
class Signal:
    code: str
    message: str
    severity: str  # low | medium | high

@dataclass
class Evaluation:
    decision: Decision
    signals: List[Signal] = field(default_factory=list)
    risk_domains: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    decision_reason: str = ""
    response_contract: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add(self, code: str, message: str, severity: str = "medium"):
        self.signals.append(Signal(code=code, message=message, severity=severity))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "requires_confirmation": self.requires_confirmation,
            "decision_reason": self.decision_reason,
            "risk_domains": list(self.risk_domains),
            "signals": [s.__dict__ for s in self.signals],
            "response_contract": self.response_contract,
            "metadata": self.metadata,
        }
