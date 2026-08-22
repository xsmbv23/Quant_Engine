import hashlib, json
from pathlib import Path
import pytest
from persistence.s1_evidence_persistence import build_envelope, serialize_envelope


def test_envelope_binds_canonical_and_manifest(tmp_path: Path):
    p = tmp_path / "canonical.json"
    p.write_text('{"schema":"xsmb-canonical/v1","records":[]}', encoding="utf-8")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = {"cycle_id":"C1","canonical_sha256":sha,"business_date_start":"2026-08-20","business_date_end":"2026-08-20"}
    env = build_envelope(cycle_id="C1", canonical_path=p, manifest=manifest)
    assert env["schema"] == "s1-evidence-envelope/v1"
    assert env["canonical_sha256"] == sha
    assert env["evidence_manifest_sha256"] == hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert serialize_envelope(env)


def test_envelope_rejects_mismatched_canonical(tmp_path: Path):
    p = tmp_path / "canonical.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="canonical_hash_mismatch"):
        build_envelope(cycle_id="C1", canonical_path=p, manifest={"canonical_sha256":"0"*64})
