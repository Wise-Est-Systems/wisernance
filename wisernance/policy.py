from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any
import yaml
from pathlib import Path

@dataclass
class Policy:
    # keyword/pattern lists kept simple + editable
    irreversible_keywords: List[str]
    risk_keywords: Dict[str, List[str]]  # domain -> keywords
    fabrication_pressure_keywords: List[str]
    dignity_violation_keywords: List[str]
    coercion_keywords: List[str]
    default_confirmation_on_irreversible: bool = True

def load_policy(path: str | Path) -> Policy:
    p = Path(path)
    data: Dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    return Policy(
        irreversible_keywords=data.get("irreversible_keywords", []),
        risk_keywords=data.get("risk_keywords", {}),
        fabrication_pressure_keywords=data.get("fabrication_pressure_keywords", []),
        dignity_violation_keywords=data.get("dignity_violation_keywords", []),
        coercion_keywords=data.get("coercion_keywords", []),
        default_confirmation_on_irreversible=bool(
            data.get("default_confirmation_on_irreversible", True)
        ),
    )
