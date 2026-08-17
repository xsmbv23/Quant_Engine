"""Executable, fail-closed contract for ROOM_01_SIGNAL.

This validator governs structure only. It never decides BUY/SELL and never
loads or mutates runtime state. Brain remains the governance authority.
"""
from __future__ import annotations

from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parent / "contracts" / "room_01_signal_v2.json"
REQUIRED_FEATURES = {
    "frequency_30d", "recency", "temporal_echo_t1", "temporal_echo_t2",
    "temporal_echo_t7", "digit_head_imbalance", "digit_tail_imbalance",
}
REQUIRED_HASHES = {
    "input_hash", "feature_snapshot_hash", "policy_hash", "output_hash",
    "execution_signature",
}


def load_contract() -> dict:
    with CONTRACT.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_contract(contract: dict | None = None) -> None:
    c = contract or load_contract()
    if c.get("room_id") != "ROOM_01_SIGNAL":
        raise ValueError("ROOM_01 identity mismatch")
    if c.get("layer") != "LAYER_1":
        raise ValueError("ROOM_01 layer mismatch")
    if c.get("governance_authority") != "PROJECT_BRAIN_AI":
        raise ValueError("ROOM_01 governance authority mismatch")
    if c.get("output", {}).get("decision") is not False:
        raise ValueError("SCORE must never become DECISION")
    if c.get("output", {}).get("probability") is not False:
        raise ValueError("ROOM_01 must not emit probability")
    if c.get("output", {}).get("order_stable") is not True:
        raise ValueError("ROOM_01 output ordering must be stable")
    if c.get("hidden_state") is not False or c.get("global_cache") is not False or c.get("state_between_runs") is not False:
        raise ValueError("ROOM_01 hidden state is forbidden")
    if c.get("implicit_edges") is not False:
        raise ValueError("implicit edges are forbidden")
    features = set(c.get("features", {}).get("required", []))
    if features != REQUIRED_FEATURES:
        raise ValueError("ROOM_01 feature semantic contract mismatch")
    hashes = set(c.get("forensic", {}).get("required_hashes", []))
    if hashes != REQUIRED_HASHES:
        raise ValueError("ROOM_01 forensic hash contract mismatch")
    if c.get("forensic", {}).get("execution_signature_required") is not True:
        raise ValueError("execution signature is mandatory")
