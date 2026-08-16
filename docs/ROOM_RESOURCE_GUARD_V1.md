# QUANT ENGINE — ROOM RESOURCE GUARD V1

Every future Layer 1 room must be resource-bounded before its door can open.

## Room resource contract

```yaml
room_id: required
room_version: required
max_input_rows: required
max_input_bytes: required
max_history_days: required
max_peak_memory_bytes: required
cpu_profile: required
output_max_bytes: required
execution_boundary: required
resume_strategy: required
```

## Door rule

```text
NO RESOURCE CONTRACT
        -> LOCKED

UNKNOWN MEMORY FOOTPRINT
        -> LOCKED

UNBOUNDED INPUT
        -> LOCKED

UNBOUNDED OUTPUT
        -> LOCKED
```

## Execution classes

- `R1`: single bounded object / fixture.
- `R2`: one shard / bounded date range.
- `R3`: multi-shard batch; external worker required.
- `R4`: historical batch / optimization / training; external execution required.

Quant Engine rooms must never assume that the Render Free Brain/UI process is their compute host.

## Evidence

A room returns compact evidence:

```text
room_id
room_version
input_artifact_id
input_sha256
output_artifact_id
output_sha256
resource_class
verification_result
promotion = DENY
```

Raw inputs are referenced, not copied into evidence.
