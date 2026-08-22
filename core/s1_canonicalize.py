"""Fail-closed S1 canonicalizer.

It never invents values from one source. It accepts only explicit semantic
records from two independent sources for the exact same business date, requires
identical normalized payloads, and emits a deterministic canonical artifact.
No state promotion is performed here.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

SOURCE_KEYS = ("source_a", "source_b")
REQUIRED = {"business_date", "source_id", "semantic_sha256", "semantic_payload"}


def canonicalize_day(day: str, source_a: dict[str, Any], source_b: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if source_a.get("source_id") == source_b.get("source_id"):
        errors.append("sources_not_independent")
    for label, rec in (("source_a", source_a), ("source_b", source_b)):
        if not REQUIRED.issubset(rec):
            errors.append(f"{label}_missing_fields")
        if rec.get("business_date") != day:
            errors.append(f"{label}_date_mismatch")
    if not errors:
        if source_a["semantic_payload"] != source_b["semantic_payload"]:
            errors.append("semantic_conflict")
        for label, rec in (("source_a", source_a), ("source_b", source_b)):
            payload_bytes = json.dumps(rec["semantic_payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            if hashlib.sha256(payload_bytes).hexdigest() != rec["semantic_sha256"]:
                errors.append(f"{label}_semantic_sha256_mismatch")
    if errors:
        return {"business_date": day, "status": "DENY", "errors": sorted(set(errors))}
    canonical_payload = {"business_date": day, "result": source_a["semantic_payload"]}
    return {"business_date": day, "status": "PASS", "canonical": canonical_payload}


def build_canonical(days: list[str], records: dict[str, dict[str, dict[str, Any]]]) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    for day in days:
        pair = records.get(day, {})
        result = canonicalize_day(day, pair.get("source_a", {}), pair.get("source_b", {}))
        if result["status"] != "PASS":
            errors.extend([f"{day}:{e}" for e in result["errors"]])
        else:
            rows.append(result["canonical"])
    if errors or len(rows) != len(days):
        return None, sorted(set(errors or ["incomplete_coverage"]))
    artifact = {"schema": "s1-canonical-dataset/v1", "days": rows}
    return artifact, []


def write_if_valid(days: list[str], records: dict[str, dict[str, dict[str, Any]]], output: str | Path) -> dict[str, Any]:
    artifact, errors = build_canonical(days, records)
    if artifact is None:
        return {"status": "DENY", "errors": errors, "promotion": "DENY"}
    data = json.dumps(artifact, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"status": "PASS", "promotion": "DENY", "canonical_artifact": str(path), "frozen_canonical_sha256": hashlib.sha256(data).hexdigest(), "days": days}
