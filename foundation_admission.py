"""Read-only mirror of the frozen Brain admission semantics.

Quant Engine may observe the admission state but must never promote it,
reinterpret UNKNOWN, or create an alternate security graph.
"""
from __future__ import annotations

from enum import Enum


class GateState(str, Enum):
    UNREACHED = "UNREACHED"
    UNKNOWN = "UNKNOWN"
    PASS = "PASS"
    FAIL = "FAIL"


GATES = (
    "DB_EXISTENCE",
    "DB_BINDING",
    "SECRET_RESOLUTION",
    "DB_TLS_ADMISSION",
    "NETWORK_ORIGIN_PROOF",
    "DB_ROUND_TRIP",
    "PROMOTION",
)


def reachable_gate(states: dict[str, GateState], gate: str) -> bool:
    """Return whether a gate may be evaluated under the frozen prerequisite chain."""
    if gate not in GATES:
        raise ValueError("UNKNOWN_FOUNDATION_GATE")
    index = GATES.index(gate)
    if index == 0:
        return True
    previous = GATES[index - 1]
    return states.get(previous, GateState.UNREACHED) == GateState.PASS


def admissible_for_quant(states: dict[str, GateState]) -> bool:
    """Quant admission is observational only: no promotion authority is granted."""
    for gate in GATES[:-1]:
        if states.get(gate, GateState.UNREACHED) != GateState.PASS:
            return False
    return states.get("PROMOTION", GateState.UNREACHED) == GateState.PASS


def assert_prerequisite_only(states: dict[str, GateState]) -> None:
    """Reject inherited PASS claims: every gate needs its own evidence."""
    for index, gate in enumerate(GATES[1:], start=1):
        if states.get(gate) == GateState.PASS:
            previous = GATES[index - 1]
            if states.get(previous) != GateState.PASS:
                raise ValueError(f"PASS_WITHOUT_LOCAL_PREREQUISITE:{gate}")
