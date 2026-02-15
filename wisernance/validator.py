from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]
    metadata: Dict[str, Any]

REQUIRED_SECTIONS = ["META", "PLAN", "ANSWER", "TAGS"]

def _has_section(text: str, name: str) -> bool:
    # Accept "META:" or "## META" etc.
    return bool(re.search(rf"(^|\n)\s*(##\s*)?{re.escape(name)}\s*:", text, flags=re.IGNORECASE)) or \
           bool(re.search(rf"(^|\n)\s*(##\s*)?{re.escape(name)}\s*$", text, flags=re.IGNORECASE))

def _extract_tags_block(text: str) -> str:
    # naive: find line starting with TAGS and return following ~15 lines
    m = re.search(r"(^|\n)\s*(##\s*)?TAGS\s*:?\s*\n", text, flags=re.IGNORECASE)
    if not m:
        # try "TAGS:" on same line
        m = re.search(r"(^|\n)\s*(##\s*)?TAGS\s*:\s*(.*)", text, flags=re.IGNORECASE)
        return (m.group(3) if m else "").strip()
    start = m.end()
    chunk = text[start:start+2000]
    return chunk.strip()

def validate_output(text: str) -> ValidationResult:
    errors: List[str] = []

    # 1) Required sections
    for s in REQUIRED_SECTIONS:
        if not _has_section(text, s):
            errors.append(f"missing_section:{s}")

    # 2) TRUTHLOCK-ish: claim IDs present in ANSWER (at least one "C1:" style)
    if not re.search(r"\bC\d+\s*:", text):
        errors.append("missing_claim_ids")

    # 3) Assumptions + Unknown gate (must have either "ASSUMPTIONS" or explicit UNKNOWN usage)
    if not re.search(r"\bASSUMPTIONS\b", text, flags=re.IGNORECASE) and not re.search(r"\bUNKNOWN\b", text, flags=re.IGNORECASE):
        errors.append("missing_assumptions_or_unknown")

    # 4) UNITAG minimal: require MODE/DOMAIN/RISK/DECISION keys somewhere in TAGS block
    tags = _extract_tags_block(text)
    for k in ["MODE", "DOMAIN", "RISK", "DECISION"]:
        if re.search(rf"\b{k}\b", tags, flags=re.IGNORECASE) is None:
            errors.append(f"missing_unitag:{k}")

    ok = len(errors) == 0
    return ValidationResult(ok=ok, errors=errors, metadata={"tags_excerpt": tags[:300]})
