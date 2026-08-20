# Cross-Repository Data Admission Contract V1

## Boundary

```text
xsmb-quant
  SOURCE TRUTH
      |
      | canonical immutable envelope
      v
Quant_Engine
  RESEARCH / CALCULATION
      |
      | compact evidence
      v
Project_Brain_AI
  GOVERNANCE / FORENSIC ADMISSION
```

The dependency is directional. Quant Engine must never reconstruct or rewrite source truth and must never reopen Brain governance gates.

## Canonical input requirements

A Layer 1 room may consume only an explicitly frozen canonical input envelope carrying:

- date identity
- exactly 27 integer values in 0..99
- source provenance identifiers
- raw evidence SHA-256 references
- calendar state
- quorum/admission evidence
- canonical payload SHA-256
- immutable version identity

`TAIL_27` is derived only and cannot reconstruct `FULL_27`.

## Temporal rule

T-1/T-2/T-7 are date-aligned. Array position is not temporal truth.

## Research rule

No edge claim may be promoted from synthetic, incomplete, unresolved, leaked, or non-canonical data.

## Memory rule

Use bounded windows, streaming, and sharding. Do not load historical datasets into Brain runtime or create whole-dataset resident structures on Render Free.

## Forensic rule

`IMPLEMENTED != VERIFIED != PROMOTED`.

A correction creates a new immutable input version and hash; it does not mutate an existing frozen input.
