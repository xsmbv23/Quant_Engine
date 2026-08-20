"""Verify semantic parser contracts without network I/O or fixture promotion."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "ketqua16": "ketqua16.net",
    "xsmb": "xsmb.com.vn",
}


def load(name: str) -> dict:
    return json.loads((ROOT / "contracts" / f"parser_{name}_v1.json").read_text(encoding="utf-8"))


def verify() -> dict:
    results = []
    for name, source_id in EXPECTED.items():
        c = load(name)
        assert c["source_id"] == source_id
        assert c["room"] == "LAYER_1_ROOM_01"
        assert c["role"] == "SEMANTIC_PARSER_ONLY"
        inp = c["input"]
        assert inp["raw_artifact"] == "EXACT_CAPTURED_RESPONSE_BYTES"
        assert inp["raw_receipt"] == "REQUIRED"
        assert inp["raw_sha256"] == "MUST_MATCH_RECEIPT"
        assert inp["runtime_identity"] == "REQUIRED"
        truth = c["truth_boundary"]
        assert truth["official_result_panel"] == "REQUIRED"
        assert truth["ads"] == "EXCLUDE"
        assert truth["navigation"] == "EXCLUDE"
        assert truth["header_footer_chrome"] == "EXCLUDE"
        assert truth["generic_page_numbers"] == "EXCLUDE"
        assert truth["ambiguous_panel"] == "DENY"
        domain = c["canonical_domain"]
        assert domain["name"] == "XSMB_27_VALUES"
        assert domain["positions"] == 27
        assert domain["each_value"] == "INTEGER_0_TO_99"
        assert domain["missing_position"] == "DENY"
        assert domain["duplicate_position"] == "DENY"
        assert domain["semantic_sha256"] == "SHA256_CANONICAL_27_VALUES"
        assert c["failure"] == "COMPACT_RECEIPT_ONLY;RAW_ARTIFACT_IMMUTABLE"
        assert c["promotion"] == "FORBIDDEN"
        results.append({"source": name, "status": "PASS"})
    return {"parser_contracts": results, "status": "PASS"}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
