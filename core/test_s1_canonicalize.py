import hashlib
from core.s1_canonicalize import canonicalize_day, build_canonical


def rec(day, source, payload):
    b = __import__('json').dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return {"business_date": day, "source_id": source, "semantic_sha256": hashlib.sha256(b).hexdigest(), "semantic_payload": payload}


def test_matching_independent_sources_pass():
    day='2026-08-21'; payload={"full_27":["12345"],"special":"42"}
    r=canonicalize_day(day, rec(day,'a',payload), rec(day,'b',payload))
    assert r['status']=='PASS'


def test_conflict_denied():
    day='2026-08-21'
    a=rec(day,'a',{"full_27":["12345"]}); b=rec(day,'b',{"full_27":["54321"]})
    r=canonicalize_day(day,a,b)
    assert r['status']=='DENY' and 'semantic_conflict' in r['errors']


def test_missing_day_denied():
    artifact, errors=build_canonical(['2026-08-20','2026-08-21'], {'2026-08-21': {'source_a':rec('2026-08-21','a',{}),'source_b':rec('2026-08-21','b',{})}})
    assert artifact is None and any('2026-08-20' in e for e in errors)
