# CANONICAL DATASET — Frozen Admission Zone

This directory is the only data boundary that Layer 1 execution may consume.

Promotion is one-way:

```text
DATA_BUFFER
   │
   │ strict admission gate
   ▼
CANONICAL_DATASET
   │
   │ immutable freeze
   ▼
QUANT ENGINE
```

There is no reverse edge.

A canonical artifact requires:

1. real-source provenance
2. raw-byte SHA-256 evidence
3. sufficient consecutive real dates
4. `coverage_ratio == 1.0`
5. no unresolved source conflict
6. explicit admission receipt
7. frozen canonical hash

The canonical dataset must never be silently repaired after freeze. A correction creates a new version with a new hash and a new admission event.
