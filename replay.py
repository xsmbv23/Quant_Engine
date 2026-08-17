"""Deterministic forensic replay for approved Layer 1 rooms.

N003 contract:
    FRESH1 == REPLAY1 == REPLAY2 == FRESH2

Replay is reproducible evidence, not correctness proof.
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import date
from pathlib import Path

from forensic_contract import execution_trace_hash, feature_snapshot, sha256_canonical
from replay_guard import assert_replay_module_pure, read_immutable_bytes
from time_index_contract import DayRecord

ALLOWLIST = {"ROOM_01_SIGNAL_V4": "room_01_signal_v4"}


def load_receipt(path: str | Path) -> dict:
    raw = read_immutable_bytes(path)
    payload = json.loads(raw.decode("utf-8"))
    required = {"room_version", "input", "expected_output_hash", "expected_feature_snapshot_hash"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"REPLAY_RECEIPT_MISSING:{','.join(sorted(missing))}")
    return payload


def replay(path: str | Path) -> dict:
    receipt = load_receipt(path)
    version = receipt["room_version"]
    module_name = ALLOWLIST.get(version)
    if not module_name:
        raise ValueError("REPLAY_ROOM_NOT_ALLOWLISTED")

    module_path = Path(importlib.util.find_spec(module_name).origin)
    assert_replay_module_pure(module_path)

    records = tuple(
        DayRecord(date.fromisoformat(item["date"]), tuple(item["values"]))
        for item in receipt["input"]["records"]
    )
    module = importlib.import_module(module_name)
    missing_day_policy = receipt["input"].get("missing_day_policy", "STRICT")
    min_feature_density = receipt["input"].get("min_feature_density", 0.10)
    density_action = receipt["input"].get("density_action", "WARNING")
    limit = receipt["input"].get("limit", 10)

    features, policy = module.extract_features(
        records,
        missing_day_policy=missing_day_policy,
        min_feature_density=min_feature_density,
        density_action=density_action,
    )
    output = [x.number for x in module.select_candidates(features, limit)]
    feature_rows = [x.__dict__ for x in features]
    semantic_features = feature_snapshot(feature_rows)

    empty_reason = None
    if output == []:
        if not features:
            empty_reason = "INSUFFICIENT_DATA"
        elif all(x.recency_excluded for x in features):
            empty_reason = "FILTERED_OUT"
        else:
            empty_reason = "NO_SIGNAL"

    trace = [
        {"step": "LOAD_RECEIPT", "room_version": version},
        {"step": "PURENESS_CHECK", "module": module_name},
        {"step": "PARSE_CANONICAL_RECORDS", "record_count": len(records)},
        {"step": "EXTRACT_FEATURES", "feature_count": len(semantic_features)},
        {"step": "APPLY_POLICY", "missing_day_policy": missing_day_policy, "density_action": density_action},
        {"step": "SELECT_CANDIDATES", "limit": limit, "candidate_count": len(output)},
        {"step": "EMPTY_REASON", "value": empty_reason},
    ]

    input_hash = sha256_canonical(receipt["input"])
    feature_hash = sha256_canonical(semantic_features)
    output_hash = sha256_canonical(output)
    trace_hash = execution_trace_hash(trace)
    expected_trace_hash = receipt.get("expected_execution_trace_hash")

    observed = {
        "input_hash": input_hash,
        "feature_snapshot_hash": feature_hash,
        "policy_hash": sha256_canonical(policy),
        "output_hash": output_hash,
        "execution_trace_hash": trace_hash,
        "empty_reason": empty_reason,
        "room_version": version,
        "reproducibility": "PASS" if (
            input_hash == receipt.get("input_hash", input_hash)
            and feature_hash == receipt["expected_feature_snapshot_hash"]
            and output_hash == receipt["expected_output_hash"]
            and (expected_trace_hash is None or trace_hash == expected_trace_hash)
        ) else "DENY",
        "correctness": "NOT_PROVEN",
    }
    observed["input_match"] = observed["input_hash"] == receipt.get("input_hash", observed["input_hash"])
    observed["feature_match"] = observed["feature_snapshot_hash"] == receipt["expected_feature_snapshot_hash"]
    observed["output_match"] = observed["output_hash"] == receipt["expected_output_hash"]
    observed["trace_match"] = expected_trace_hash is None or observed["execution_trace_hash"] == expected_trace_hash
    observed["replay"] = observed["reproducibility"]
    return observed


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python replay.py receipt.json", file=sys.stderr)
        return 2
    result = replay(argv[1])
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["replay"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
