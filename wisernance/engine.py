from __future__ import annotations
from typing import Optional, Dict, Any
from .models import Evaluation, Decision
from .policy import Policy, load_policy
from . import rules

def build_response_contract() -> Dict[str, Any]:
    # This is your enforced output spec the model must follow when PROCEED.
    return {
        "ELOTBC": {
            "truth_only": True,
            "silence_over_invention": True,
            "consent_gate_for_irreversible": True,
            "risk_matrix_required_for_high_stakes": True,
            "source_age_disclosure": True,
        },
        "TRUTHLOCK": {
            "atomic_one_claim_per_line": True,
            "claim_ids_required": True,
            "assumptions_section_required": True,
            "unknown_gate": True,
            "contradiction_scan": True,
            "err_ledger_enabled": True,
        },
        "PILLARS": ["Sovereignty", "Stewardship", "Verifiability", "Dignity"],
        "FORMAT": ["META", "PLAN", "ANSWER", "TAGS"],
        "UNITAG": {
            "required": ["MODE", "DOMAIN", "RISK", "DECISION"],
            "MODE": ["R", "E", "A", "C"],
            "DOMAIN": ["M", "L", "W", "F", "Fl", "X"],
            "RISK": ["LOW", "MED", "HIGH"],
            "DECISION": ["PROCEED", "REQUIRE_CONFIRMATION", "HALT"],
        },
    }

class WisernanceEngine:
    def __init__(self, policy: Policy):
        self.policy = policy

    @classmethod
    def from_file(cls, path: str) -> "WisernanceEngine":
        return cls(load_policy(path))

    def evaluate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Evaluation:
        ev = Evaluation(
            decision=Decision.PROCEED,
            metadata={"context": context or {}},
            response_contract=build_response_contract(),
        )

        # Pre-execution sequence
        rules.principle_check(prompt, self.policy, ev)
        rules.fabrication_guard(prompt, self.policy, ev)
        rules.risk_exposure(prompt, self.policy, ev)
        rules.irreversibility_gate(prompt, self.policy, ev)

        # Decision logic
        high_stakes = {"legal", "financial", "medical"}

        if ev.decision == Decision.HALT:
            ev.decision_reason = "red_flag_or_policy_halt"
            return ev

        if ev.requires_confirmation:
            ev.decision = Decision.REQUIRE_CONFIRMATION
            ev.decision_reason = "irreversibility_gate_requires_consent"
            return ev

        if any(d in high_stakes for d in ev.risk_domains):
            ev.requires_confirmation = True
            ev.decision = Decision.REQUIRE_CONFIRMATION
            ev.add("HIGH_STAKES_CONFIRM", "High-stakes domain detected; require confirmation.", "high")
            ev.decision_reason = "high_stakes_requires_consent"
            return ev

        ev.decision_reason = "no_blockers_detected"
        return ev
