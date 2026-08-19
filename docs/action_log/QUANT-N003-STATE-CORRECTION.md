# QUANT-N003-STATE-CORRECTION

## Purpose

The prior `state/current_state.json` claimed `ROOM_02_EDGE_DETECTOR_V1` was implemented and research-ready. That state is inconsistent with the frozen Layer 1 admission doctrine because canonical real-data admission was not complete.

This event is a **correction, not deletion**.

The historical claim remains preserved in Git history. Its meaning is explicitly superseded for current authority.

## Forensic finding

```text
ROOM_02_IMPLEMENTED = HISTORICAL_CLAIM
ROOM_02_AUTHORITY   = DENY
ROOM_02_REACHABLE   = NO
CANONICAL_REAL_DATA = NOT_ADMITTED
```

The corrected architecture is:

```text
REAL SOURCE A ──┐
                ├─> RAW RECEIPTS ─> SEMANTIC ADMISSION ─> CANONICAL
REAL SOURCE B ──┘

fixture ─────────────> deterministic runtime test only

Room 02 / signals ───> LOCKED until canonical admission
```

## Important rule

Raw-byte hashes from independent websites are **not expected to match**. HTML, advertisements, tracking, timestamps and markup can legitimately differ.

Therefore:

```text
raw_sha256 equality = BYTE_IDENTITY evidence only
raw_sha256 inequality != semantic conflict
```

Canonical quorum requires independently produced semantic hashes for the same business date/domain contract.

## Current correction

- Room 02 edge detector is not reachable for production research.
- Room 01 acquisition remains the active data boundary.
- Source B is being added only as another raw observation source.
- No signal, scoring or edge claim is promoted.
- Fixture is not reality.
- Unknown/unreached is not pass.
