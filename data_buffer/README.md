# DATA BUFFER — Forensic Accumulation Zone

`data_buffer/` is a **collection zone**, not a truth zone.

## Allowed

- partial real-source acquisition
- multiple source observations for the same business date
- raw response bytes preserved exactly
- raw-byte SHA-256
- retrieval URL, retrieval timestamp, source id, HTTP metadata
- status `UNVERIFIED`, `PARTIAL`, `READY`, `CONFLICT`
- repeated acquisition of the same date/source for evidence

## Forbidden

- Quant Engine execution against buffer data
- synthetic/backfilled/interpolated values
- silent filling of missing dates
- silent source replacement
- rewriting an existing raw artifact
- merging source A + source B into a new truth
- promotion based on collection coverage alone

## Promotion rule

A date may be promoted to `canonical_dataset/` only through the explicit admission gate.

For strict N003 temporal admission:

```text
>= 10 consecutive real-source dates
coverage_ratio = 1.0
raw artifacts hash-frozen
provenance complete
source quorum/conflict policy satisfied
canonical input frozen
```

Preferred acquisition window: 21–30 real dates.

## Source disagreement

Sources are observed independently.

```text
A == B -> quorum evidence may PASS
A != B -> CONFLICT -> DENY
```

The system never merges conflicting sources to manufacture truth.
