"""Bounded raw-source collector for real XSMB history.

This collector stores exact response bytes and provenance only. It does not
parse, normalize, fill, merge, or promote data. A caller may point it at a
source URL; the raw response is persisted append-only in data_buffer/raw/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BUFFER = ROOT / "data_buffer" / "raw"
USER_AGENT = "XSMB-Forensic-Collector/1.0"
MAX_BYTES = 2 * 1024 * 1024


def capture(url: str, source_id: str, business_date: str, timeout: int = 20) -> dict[str, object]:
    BUFFER.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"})
    retrieved = datetime.now(timezone.utc).isoformat()
    with urlopen(req, timeout=timeout) as response:
        chunks = []
        remaining = MAX_BYTES
        while remaining > 0:
            chunk = response.read(min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        headers = {k: v for k, v in response.headers.items() if k.lower() not in {"set-cookie", "authorization"}}
        status_code = getattr(response, "status", 200)

    digest = hashlib.sha256(raw).hexdigest()
    safe_source = "".join(c if c.isalnum() or c in "._-" else "_" for c in source_id)
    artifact = BUFFER / f"{business_date}__{safe_source}__{digest}.bin"
    if artifact.exists():
        if artifact.read_bytes() != raw:
            raise RuntimeError("FORENSIC_HASH_COLLISION_OR_MUTATION")
    else:
        artifact.write_bytes(raw)

    manifest = {
        "schema_version": "BUFFER_CAPTURE_V1",
        "business_date": business_date,
        "source_id": source_id,
        "source_url": url,
        "retrieved_at_utc": retrieved,
        "status": "UNVERIFIED",
        "http_status": status_code,
        "content_length": len(raw),
        "raw_bytes_sha256": digest,
        "raw_artifact_path": str(artifact.relative_to(ROOT)),
        "response_headers": headers,
    }
    manifest_path = artifact.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--business-date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    print(json.dumps(capture(args.url, args.source_id, args.business_date), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
