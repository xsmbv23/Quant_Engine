"""N003 proof runner: fresh vs replay determinism + mutation resistance.

The runner uses the real Room 01 V4 implementation and the persisted real-source
receipt. It never promotes the room and emits only compact hashes/results.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from forensic_contract import execution_trace_hash, feature_snapshot, sha256_canonical, sha256_raw_bytes
from replay_guard import read_immutable_bytes
from room_01_signal_v4 import extract_features, select_candidates
from time_index_contract import DayRecord

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "evidence" / "real_rehearsal" / "2026-08-12" / "quant_n002_receipt.json"


def fresh_execute(receipt: dict) -> dict:
    records = tuple(DayRecord(date.fromisoformat(x["date"]), tuple(x["values"])) for x in receipt["input"]["records"])
    features, policy = extract_features(
        records,
        missing_day_policy=receipt["input"].get("missing_day_policy", "STRICT"),
        min_feature_density=receipt["input"].get("min_feature_density", 0.10),
        density_action=receipt["input"].get("density_action", "WARNING"),
    )
    output = [x.number for x in select_candidates(features, receipt["input"].get("limit", 10))]
    semantic = feature_snapshot([x.__dict__ for x in features])
    trace = [
        {"step": "LOAD_RECEIPT", "room_version": receipt["room_version"]},
        {"step": "PURENESS_CHECK", "module": "room_01_signal_v4"},
        {"step": "PARSE_CANONICAL_RECORDS", "record_count": len(records)},
        {"step": "EXTRACT_FEATURES", "feature_count": len(semantic)},
        {"step": "APPLY_POLICY", "missing_day_policy": receipt["input"].get("missing_day_policy", "STRICT"), "density_action": receipt["input"].get("density_action", "WARNING")},
        {"step": "SELECT_CANDIDATES", "limit": receipt["input"].get("limit", 10), "candidate_count": len(output)},
    ]
    return {
        "input_hash": sha256_canonical(receipt["input"]),
        "feature_snapshot_hash": sha256_canonical(semantic),
        "policy_hash": sha256_canonical(policy),
        "output_hash": sha256_canonical(output),
        "execution_trace_hash": execution_trace_hash(trace),
        "output": output,
    }


def replay_execute() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "replay.py"), str(RECEIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"REPLAY_DENY:{proc.stdout[-2000:]}:{proc.stderr[-1000:]}")
    return json.loads(proc.stdout)


def main() -> int:
    raw = read_immutable_bytes(RECEIPT)
    receipt = json.loads(raw.decode("utf-8"))

    fresh1 = fresh_execute(copy.deepcopy(receipt))
    replay1 = replay_execute()
    replay2 = replay_execute()
    fresh2 = fresh_execute(copy.deepcopy(receipt))

    checks = {
        "fresh1_replay1": all(fresh1[k] == replay1[k] for k in ("input_hash", "feature_snapshot_hash", "output_hash")),
        "replay1_replay2": all(replay1[k] == replay2[k] for k in ("input_hash", "feature_snapshot_hash", "output_hash", "execution_trace_hash")),
        "fresh1_fresh2": all(fresh1[k] == fresh2[k] for k in ("input_hash", "feature_snapshot_hash", "output_hash", "execution_trace_hash")),
        "trace_equivalence": fresh1["execution_trace_hash"] == replay1["execution_trace_hash"],
        "raw_hash_stable": sha256_raw_bytes(raw) == sha256_raw_bytes(bytes(raw)),
    }

    mutated = copy.deepcopy(receipt)
    mutated["input"]["records"][0]["values"][0] += 1
    mutation_hash = sha256_canonical(mutated["input"])
    checks["mutation_changes_input_hash"] = mutation_hash != fresh1["input_hash"]
    checks["expected_hash_rejects_mutation"] = mutation_hash != receipt["input_hash"]

    result = {
        "action_id": "QUANT-N003-PROOF",
        "room_version": receipt["room_version"],
        "fixture_id": receipt.get("fixture_id"),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "DENY",
        "correctness": "NOT_PROVEN",
        "promotion": "DENY",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
