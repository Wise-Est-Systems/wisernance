from __future__ import annotations
from typing import List
from .models import Evaluation, Decision
from .policy import Policy

def _contains_any(text: str, keywords: List[str]) -> List[str]:
    t = (text or "").lower()
    hits = []
    for k in keywords:
        if k.lower() in t:
            hits.append(k)
    return hits

def principle_check(prompt: str, policy: Policy, ev: Evaluation) -> None:
    coercion_hits = _contains_any(prompt, policy.coercion_keywords)
    if coercion_hits:
        ev.add("SOVEREIGNTY_COERCION", f"Potential coercion indicators: {coercion_hits}", "high")
        ev.decision = Decision.HALT

    dignity_hits = _contains_any(prompt, policy.dignity_violation_keywords)
    if dignity_hits:
        ev.add("DIGNITY_VIOLATION", f"Potential dignity violation indicators: {dignity_hits}", "high")
        ev.decision = Decision.HALT

def fabrication_guard(prompt: str, policy: Policy, ev: Evaluation) -> None:
    hits = _contains_any(prompt, policy.fabrication_pressure_keywords)
    if hits:
        ev.add("FABRICATION_PRESSURE", f"User prompt pressures fabrication: {hits}", "high")
        ev.decision = Decision.HALT

def risk_exposure(prompt: str, policy: Policy, ev: Evaluation) -> None:
    for domain, kws in policy.risk_keywords.items():
        hits = _contains_any(prompt, kws)
        if hits:
            if domain not in ev.risk_domains:
                ev.risk_domains.append(domain)
            ev.add("RISK_DOMAIN", f"Risk domain detected: {domain} (hits: {hits})", "medium")

def irreversibility_gate(prompt: str, policy: Policy, ev: Evaluation) -> None:
    hits = _contains_any(prompt, policy.irreversible_keywords)
    if hits:
        if "irreversible" not in ev.risk_domains:
            ev.risk_domains.append("irreversible")
        ev.add("IRREVERSIBLE", f"Irreversibility indicators: {hits}", "high")
        if policy.default_confirmation_on_irreversible:
            ev.requires_confirmation = True
            if ev.decision == Decision.PROCEED:
                ev.decision = Decision.REQUIRE_CONFIRMATION
