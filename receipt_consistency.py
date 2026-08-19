"""Cross-source receipt consistency without confusing bytes with truth.

Raw HTML from independent sites is expected to differ because of markup,
advertising, timestamps, tracking and transport details. Therefore raw-byte
hash equality is evidence of byte identity only; it is NOT a semantic quorum.

Semantic consensus requires an independently produced semantic hash for the
same business date and domain contract. This module never parses source HTML
and never promotes a single observation to canonical truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReceiptEvidence:
    business_date: str
    source_id: str
    raw_sha256: str
    semantic_sha256: str | None = None
    source_family: str | None = None


@dataclass(frozen=True)
class ConsistencyResult:
    status: str
    business_date: str
    source_count: int
    independent_source_count: int
    raw_byte_identity: bool
    semantic_hash_count: int
    semantic_quorum: int
    semantic_consensus: bool
    canonical_admission: str
    reason: str


def compare_receipts(
    receipts: Iterable[ReceiptEvidence], *, semantic_quorum: int = 2
) -> ConsistencyResult:
    rows = list(receipts)
    if semantic_quorum < 2:
        raise ValueError("SEMANTIC_QUORUM_MUST_BE_AT_LEAST_2")
    if not rows:
        return ConsistencyResult(
            status="UNKNOWN",
            business_date="UNKNOWN",
            source_count=0,
            independent_source_count=0,
            raw_byte_identity=False,
            semantic_hash_count=0,
            semantic_quorum=semantic_quorum,
            semantic_consensus=False,
            canonical_admission="DENY",
            reason="NO_RECEIPTS",
        )

    dates = {r.business_date for r in rows}
    if len(dates) != 1:
        return ConsistencyResult(
            status="CONFLICT",
            business_date="MULTIPLE",
            source_count=len(rows),
            independent_source_count=len({r.source_id for r in rows}),
            raw_byte_identity=False,
            semantic_hash_count=0,
            semantic_quorum=semantic_quorum,
            semantic_consensus=False,
            canonical_admission="DENY",
            reason="BUSINESS_DATE_MISMATCH",
        )

    unique_sources = {r.source_id for r in rows}
    families = {r.source_family for r in rows if r.source_family}
    independent = len(unique_sources)
    raw_hashes = {r.raw_sha256 for r in rows}
    semantic_hashes = {r.semantic_sha256 for r in rows if r.semantic_sha256}

    # A source cannot become independent merely by emitting duplicate receipts.
    raw_identity = len(raw_hashes) == 1

    if len(semantic_hashes) >= 1 and independent < semantic_quorum:
        return ConsistencyResult(
            status="INSUFFICIENT_INDEPENDENCE",
            business_date=next(iter(dates)),
            source_count=len(rows),
            independent_source_count=independent,
            raw_byte_identity=raw_identity,
            semantic_hash_count=len(semantic_hashes),
            semantic_quorum=semantic_quorum,
            semantic_consensus=False,
            canonical_admission="DENY",
            reason="INDEPENDENT_SOURCE_QUORUM_NOT_REACHED",
        )

    if len(semantic_hashes) >= 1 and independent >= semantic_quorum:
        semantic_consensus = len(semantic_hashes) == 1
        if semantic_consensus:
            return ConsistencyResult(
                status="SEMANTIC_CONSENSUS",
                business_date=next(iter(dates)),
                source_count=len(rows),
                independent_source_count=independent,
                raw_byte_identity=raw_identity,
                semantic_hash_count=len(semantic_hashes),
                semantic_quorum=semantic_quorum,
                semantic_consensus=True,
                canonical_admission="ADMIT",
                reason="INDEPENDENT_SEMANTIC_QUORUM_MATCH",
            )
        return ConsistencyResult(
            status="CONFLICT",
            business_date=next(iter(dates)),
            source_count=len(rows),
            independent_source_count=independent,
            raw_byte_identity=raw_identity,
            semantic_hash_count=len(semantic_hashes),
            semantic_quorum=semantic_quorum,
            semantic_consensus=False,
            canonical_admission="DENY",
            reason="SEMANTIC_HASH_CONFLICT",
        )

    return ConsistencyResult(
        status="OBSERVED_NO_SEMANTIC_ADMISSION",
        business_date=next(iter(dates)),
        source_count=len(rows),
        independent_source_count=independent,
        raw_byte_identity=raw_identity,
        semantic_hash_count=0,
        semantic_quorum=semantic_quorum,
        semantic_consensus=False,
        canonical_admission="DENY",
        reason="RAW_RECEIPTS_EXIST_BUT_SEMANTIC_CANONICALIZATION_UNREACHED",
    )
