from __future__ import annotations
from typing import Dict, Any, List

def build_retry_instruction(errors: List[str], contract: Dict[str, Any]) -> str:
    # This is the strict "do it again" instruction used once if output fails validation.
    # It is enforceable because we refuse the output otherwise.
    req_sections = contract.get("FORMAT", ["META","PLAN","ANSWER","TAGS"])
    unitag = contract.get("UNITAG", {}).get("required", ["MODE","DOMAIN","RISK","DECISION"])

    return (
        "Your previous output failed Wisernance validation.\n"
        f"Fix ONLY the issues listed: {errors}\n\n"
        "Hard requirements:\n"
        f"- Include sections exactly: {req_sections}\n"
        "- In ANSWER, use atomic claims with Claim IDs like 'C1: ...' one claim per line.\n"
        "- Include an ASSUMPTIONS section or explicit UNKNOWN lines where facts are not verified.\n"
        f"- In TAGS, include keys: {unitag}\n"
        "Return the corrected full response. No extra commentary."
    )
