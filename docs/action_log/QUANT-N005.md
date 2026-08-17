# QUANT-N005 — Forensic Readiness Visibility Wiring

## Objective

Wire compact readiness visibility into the active Layer 1 / Room 01 acquisition boundary without allowing the accumulation buffer to become canonical truth.

## Implemented

Added:

- `data_buffer/readiness_status.py`
- `tests/test_readiness_status.py`

The new status adapter exposes only compact metadata:

- observed days
- contiguous days
- coverage ratio
- quorum-ok days
- conflict days
- readiness score
- minimum/preferred history targets
- early-freeze rehearsal status
- strict-admission status
- promotion state
- canonical truth boundary

## Important architectural decision

The readiness adapter is **not** imported into Room 01 signal calculation and is **not** allowed to promote the buffer.

This is deliberate:

```text
DATA BUFFER
   |
   +--> READINESS VISIBILITY
   |        |
   |        +--> status only
   |        +--> no promotion authority
   |
   +--> STRICT ADMISSION
            |
            +--> CANONICAL DATASET
                    |
                    +--> ROOM 01
```

This prevents the readiness layer from becoming an implicit second admission engine.

## State semantics

```text
ACCUMULATING
    = not enough evidence for strict admission

EARLY_FREEZE_CANDIDATE_REHEARSAL_ONLY
    = useful for rehearsal/visibility, never truth

STRICT_ADMISSION_READY
    = the strict temporal/quorum/conflict conditions are satisfied
```

Even `STRICT_ADMISSION_READY` remains a **readiness signal**. Canonical promotion must still execute through the authoritative admission path and produce its own evidence.

## Tests added

1. Partial accumulation remains visible but `promotion=DENY`.
2. Full 10-day contiguous quorum with no conflicts becomes `STRICT_ADMISSION_READY`.
3. Any conflict blocks promotion even with full coverage.

Existing `data_buffer/forensic_readiness.py` remains authoritative for the underlying readiness mathematics.

## Preserved invariants

- REAL_SOURCE_ONLY
- NO_SYNTHETIC_HISTORY
- NO_BACKFILL
- NO_INTERPOLATION
- NO_SILENT_FILL
- NO_RAW_EVIDENCE_DELETION
- NO_PARTIAL_TEMPORAL_CLAIM
- UNKNOWN_IS_NOT_PASS
- UNREACHED_IS_NOT_PASS
- DEFAULT_DENY
- PASS_AT_GATE_IS_PREREQUISITE_ONLY
- ONE_FORENSIC_DATABASE_FSM
- BUFFER != ENGINE INPUT
- PARTIAL != TRUTH
- COLLECTION != ADMISSION
- FAIL_HISTORY_IS_IMMUTABLE
- CANONICAL_PROMOTION_IS_ONE_WAY
- RENDER_FREE_512MB_HARD_BOUNDARY
- 320 MiB conservative guard

## N003 remains unresolved

This action does **not** solve the existing N003 fixture mismatch or prove four-run determinism. The incompatible 2026-08-12 five-digit receipt remains historical evidence and must not be rewritten.

Therefore:

```text
N003 DETERMINISM       = UNREACHED
N003 TEMPORAL PROOF    = UNREACHED
CANONICAL PROMOTION    = DENY
```

## Successor instruction

The next action must first inspect the real-source acquisition implementation and determine whether the readiness status is already connected to the collector/status path. If it is not, connect it only at the metadata/status boundary. Never connect readiness directly to Room 01 execution as an admission shortcut.
