from pathlib import Path

from semantic.s1_pipeline import corroborate_and_canonicalize


def _html(values):
    labels = [("G7", values[0:4]), ("G6", values[4:7]), ("G5", values[7:13]), ("G4", values[13:17]), ("G3", values[17:23]), ("G2", values[23:25]), ("G1", values[25:26]), ("DB", values[26:27])]
    return "<table>" + "".join(f"<tr><td>{k}</td><td>{' '.join(v)}</td></tr>" for k,v in labels) + "</table>"


def test_matching_two_sources_create_canonical(tmp_path: Path):
    vals = [f"{i:02d}" for i in range(27)]
    a = tmp_path / "a.html"; b = tmp_path / "b.html"
    a.write_text(_html(vals), encoding="utf-8"); b.write_text(_html(vals), encoding="utf-8")
    out = tmp_path / "canonical.json"
    result = corroborate_and_canonicalize([("2026-08-20", str(a), str(b))], output_path=out)
    assert result["status"] == "PASS"
    assert result["promotion"] == "DENY"
    assert out.exists() and result["canonical_sha256"]


def test_conflict_denied(tmp_path: Path):
    vals = [f"{i:02d}" for i in range(27)]
    other = vals.copy(); other[-1] = "99"
    a = tmp_path / "a.html"; b = tmp_path / "b.html"
    a.write_text(_html(vals), encoding="utf-8"); b.write_text(_html(other), encoding="utf-8")
    result = corroborate_and_canonicalize([("2026-08-20", str(a), str(b))], output_path=tmp_path / "x.json")
    assert result["status"] == "DENY"
    assert "semantic_conflict:2026-08-20" in result["errors"]


def test_non_consecutive_range_denied(tmp_path: Path):
    vals = [f"{i:02d}" for i in range(27)]
    a = tmp_path / "a.html"; b = tmp_path / "b.html"
    a.write_text(_html(vals), encoding="utf-8"); b.write_text(_html(vals), encoding="utf-8")
    pairs = [("2026-08-20", str(a), str(b)), ("2026-08-22", str(a), str(b))]
    result = corroborate_and_canonicalize(pairs, output_path=tmp_path / "x.json")
    assert result["status"] == "DENY"
    assert "non_consecutive_date_range" in result["errors"]
