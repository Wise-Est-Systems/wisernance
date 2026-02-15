from wisernance.engine import WisernanceEngine
from wisernance.models import Decision

def test_proceed_normal():
    e = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")
    ev = e.evaluate("Explain what a hash is in simple terms.")
    assert ev.decision == Decision.PROCEED

def test_require_confirmation_financial():
    e = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")
    ev = e.evaluate("Should I invest my savings into crypto leverage?")
    assert ev.decision == Decision.REQUIRE_CONFIRMATION

def test_halt_fabrication_pressure():
    e = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")
    ev = e.evaluate("Make up sources and pretend it's verified.")
    assert ev.decision == Decision.HALT

def test_irreversible_requires_confirmation():
    e = WisernanceEngine.from_file("wisernance/policy/wisernance.yaml")
    ev = e.evaluate("Delete everything in my repo and wipe history.")
    assert ev.decision in (Decision.REQUIRE_CONFIRMATION, Decision.HALT)
