"""S1 evidence pipeline: raw -> semantic -> two-source corroboration -> canonical.

This module never fetches data, never invents missing values, and never promotes
state. It consumes already-captured artifacts and emits a canonical candidate
only when every requested business date has two distinct, exactly matching
semantic records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from semantic.xsmb_extract import extract


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("semantic_record_not_object")
    return value


def corroborate_and_canonicalize(
    raw_pairs: list[tuple[str, str, str]],
    *,
    output_path: str | Path,
) -> dict[str, Any]:
    """raw_pairs = [(business_date, source_a_raw, source_b_raw), ...]."""
    if not raw_pairs:
        return {"status": "DENY", "errors": ["empty_date_range"], "promotion": "DENY"}

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_dates: set[str] = set()
    for business_date, source_a, source_b in raw_pairs:
        if business_date in seen_dates:
            errors.append(f"duplicate_date:{business_date}")
            continue
        seen_dates.add(business_date)
        a = extract(source_a, business_date, "SOURCE_A")
        b = extract(source_b, business_date, "SOURCE_B")
        if a.get("status") != "PASS":
            errors.append(f"source_a_semantic_deny:{business_date}")
            continue
        if b.get("status") != "PASS":
            errors.append(f"source_b_semantic_deny:{business_date}")
            continue
        if a.get("source_id") == b.get("source_id"):
            errors.append(f"non_independent_sources:{business_date}")
            continue
        if a.get("full_27") != b.get("full_27"):
            errors.append(f"semantic_conflict:{business_date}")
            continue
        records.append({
            "business_date": business_date,
            "full_27": a["full_27"],
            "source_a_semantic_sha256": a["semantic_sha256"],
            "source_b_semantic_sha256": b["semantic_sha256"],
            "source_a_raw_sha256": a["raw_sha256"],
            "source_b_raw_sha256": b["raw_sha256"],
        })

    dates = sorted(seen_dates)
    if dates:
        from datetime import date, timedelta
        expected = []
        cur = date.fromisoformat(dates[0])
        end = date.fromisoformat(dates[-1])
        while cur <= end:
            expected.append(cur.isoformat())
            cur += timedelta(days=1)
        if dates != expected:
            errors.append("non_consecutive_date_range")
        if len(records) != len(dates):
            errors.append("coverage_incomplete")

    if errors:
        return {"status": "DENY", "promotion": "DENY", "errors": sorted(set(errors))}

    canonical = {
        "schema": "xsmb-canonical/v1",
        "coverage": {"start": dates[0], "end": dates[-1], "days": len(dates)},
        "records": records,
        "conflicts": [],
    }
    raw = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    return {
        **canonical,
        "status": "PASS",
        "promotion": "DENY",
        "canonical_artifact": str(out),
        "canonical_sha256": digest,
    }
