"""Deterministic forensic replay for approved Layer 1 rooms.

Usage:
    python replay.py receipt.json

The replay bundle carries the exact canonical input and expected hashes.
Only explicitly allow-listed room versions may execute.
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import date
from pathlib import Path

from room_receipt import sha256_json
from time_index_contract import DayRecord

ALLOWLIST = {"ROOM_01_SIGNAL_V4": "room_01_signal_v4"}


def load_receipt(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
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

    records = tuple(
        DayRecord(date.fromisoformat(item["date"]), tuple(item["values"]))
        for item in receipt["input"]["records"]
    )
    module = importlib.import_module(module_name)
    features, policy = module.extract_features(
        records,
        missing_day_policy=receipt["input"].get("missing_day_policy", "STRICT"),
        min_feature_density=receipt["input"].get("min_feature_density", 0.10),
        density_action=receipt["input"].get("density_action", "WARNING"),
    )
    output = [x.number for x in module.select_candidates(features, receipt["input"].get("limit", 10))]
    feature_snapshot = [x.__dict__ for x in features]

    observed = {
        "input_hash": sha256_json(receipt["input"]),
        "feature_snapshot_hash": sha256_json(feature_snapshot),
        "policy_hash": sha256_json(policy),
        "output_hash": sha256_json(output),
        "room_version": version,
    }
    observed["input_match"] = observed["input_hash"] == receipt.get("input_hash", observed["input_hash"])
    observed["feature_match"] = observed["feature_snapshot_hash"] == receipt["expected_feature_snapshot_hash"]
    observed["output_match"] = observed["output_hash"] == receipt["expected_output_hash"]
    observed["replay"] = "PASS" if observed["feature_match"] and observed["output_match"] else "DENY"
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
