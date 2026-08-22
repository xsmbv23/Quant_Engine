"""Conservative semantic extraction from already-captured XSMB HTML.

No network access. No inference. A record is emitted only when every prize
class is explicitly represented with its expected number of values.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

PRIZE_COUNTS = {
    "DB": 1, "G1": 1, "G2": 2, "G3": 6, "G4": 4, "G5": 6, "G6": 3, "G7": 4,
}
LABELS = {
    "DB": {"đặc biệt", "g.đb", "gdb", "db"},
    "G1": {"giải nhất", "g1", "g.1"},
    "G2": {"giải nhì", "g2", "g.2"},
    "G3": {"giải ba", "g3", "g.3"},
    "G4": {"giải tư", "g4", "g.4"},
    "G5": {"giải năm", "g5", "g.5"},
    "G6": {"giải sáu", "g6", "g.6"},
    "G7": {"giải bảy", "g7", "g.7"},
}


def _norm(s: str) -> str:
    return " ".join(html.unescape(s).replace("\xa0", " ").split()).strip().lower()


def _digits(s: str) -> list[str]:
    return re.findall(r"(?<!\d)\d{2,6}(?!\d)", s)


class _Tables(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr":
            self._row = []
        elif tag.lower() in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(_norm(" ".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def extract(raw_path: str | Path, business_date: str, source_id: str) -> dict[str, Any]:
    raw = Path(raw_path).read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    parser = _Tables()
    parser.feed(raw.decode("utf-8", errors="strict"))

    found: dict[str, list[str]] = {}
    ambiguities: list[str] = []
    for row in parser.rows:
        if not row:
            continue
        label = row[0]
        matches = [key for key, variants in LABELS.items() if label in variants]
        if len(matches) != 1:
            continue
        key = matches[0]
        values: list[str] = []
        for cell in row[1:]:
            values.extend(_digits(cell))
        expected = PRIZE_COUNTS[key]
        if len(values) != expected:
            ambiguities.append(f"{key}:expected_{expected}:observed_{len(values)}")
            continue
        if key in found and found[key] != values:
            ambiguities.append(f"{key}:duplicate_conflict")
        found[key] = values

    missing = sorted(set(PRIZE_COUNTS) - set(found))
    errors = sorted(set(ambiguities + [f"missing_{x}" for x in missing]))
    if errors:
        return {"schema": "xsmb-semantic/v1", "status": "DENY", "promotion": "DENY", "source_id": source_id, "business_date": business_date, "raw_sha256": raw_sha, "errors": errors}

    flat = [n for key in ["G7", "G6", "G5", "G4", "G3", "G2", "G1", "DB"] for n in found[key]]
    payload = {"schema": "xsmb-semantic/v1", "business_date": business_date, "source_id": source_id, "prizes": found, "full_27": flat}
    semantic_bytes = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**payload, "status": "PASS", "promotion": "DENY", "raw_sha256": raw_sha, "semantic_sha256": hashlib.sha256(semantic_bytes).hexdigest()}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("raw_path")
    p.add_argument("business_date")
    p.add_argument("source_id")
    args = p.parse_args()
    print(json.dumps(extract(args.raw_path, args.business_date, args.source_id), ensure_ascii=False, sort_keys=True))
