"""Verify source-specific collector contracts without performing network I/O."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("ketqua16", "xsmb")
REQUIRED_SEMANTIC = {
    "target", "domain", "required_values", "value_range", "ads",
    "generic_page_number_regex", "candidate_without_official_panel",
    "ambiguous_multiple_panels", "missing_value", "duplicate_position",
    "semantic_sha256",
}


def load_contract(name: str) -> dict:
    path = ROOT / "contracts" / f"source_{name}_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict:
    results = []
    for name in SOURCES:
        c = load_contract(name)
        sem = c["semantic_layer"]
        prov = c["provenance"]
        assert c["role"] == "REAL_SOURCE_OBSERVATION_ONLY"
        assert c["promotion"] == "FORBIDDEN"
        assert c["transport"]["scheme"] == "https"
        assert c["raw_layer"]["raw_sha256"] == "BYTE_IDENTITY_ONLY"
        assert REQUIRED_SEMANTIC.issubset(sem)
        assert sem["target"] == "OFFICIAL_RESULT_PANEL_ONLY"
        assert sem["required_values"] == 27
        assert sem["ads"] == "NON_TRUTH_CONTENT"
        assert sem["generic_page_number_regex"] == "FORBIDDEN_AS_TRUTH_SOURCE"
        assert all(prov.values())
        results.append({"source": name, "status": "PASS"})
    return {"source_contracts": results, "status": "PASS"}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
