from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .engine import WisernanceEngine

def main() -> None:
    ap = argparse.ArgumentParser(prog="wisernance", description="Wisernance Pre-Execution Governance Gate")
    ap.add_argument("--policy", default="wisernance/policy/wisernance.yaml", help="Path to policy YAML")
    ap.add_argument("--prompt", help="Prompt string. If omitted, read from stdin.")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = ap.parse_args()

    prompt = args.prompt
    if prompt is None:
        prompt = sys.stdin.read()

    engine = WisernanceEngine.from_file(args.policy)
    ev = engine.evaluate(prompt)

    if args.json:
        print(json.dumps(ev.to_dict(), indent=2))
    else:
        print(f"DECISION: {ev.decision.value}")
        if ev.risk_domains:
            print(f"RISK_DOMAINS: {', '.join(ev.risk_domains)}")
        for s in ev.signals:
            print(f"- [{s.severity}] {s.code}: {s.message}")

    # Exit codes = enforceability for pipelines
    # 0 proceed, 2 require confirmation, 3 halt
    if ev.decision.value == "PROCEED":
        raise SystemExit(0)
    if ev.decision.value == "REQUIRE_CONFIRMATION":
        raise SystemExit(2)
    raise SystemExit(3)
