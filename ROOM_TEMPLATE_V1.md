# LAYER 1 ROOM TEMPLATE V1

Every intelligence component MUST instantiate this model before implementation.

```yaml
room_id: L1-ROOM-XXX
room_version: 1.0.0
room_type: SENSOR | MECHANISM | FUNCTION | ALGORITHM | MODEL
layer: L1
door_state: LOCKED

purpose: ""

input_contract: ""
output_contract: ""
dependencies: []
allowed_callers: []
allowed_corridors: []
required_capabilities: []

source_sha256: ""
contract_sha256: ""
test_sha256: ""
evidence_sha256: ""
lineage_root: ""

failure_policy: DENY
evidence_policy: COMPACT_CONTENT_ADDRESSED
promotion_policy: BRAIN_ONLY
```

## Door states

`LOCKED` → no execution.

`OPEN_FOR_TEST` → only bounded verification fixtures.

`OPEN_FOR_VERIFIED_INPUT` → only after contract, corridor, capability, lineage and freshness gates pass.

`QUARANTINED` → evidence or contract conflict.

`DEPRECATED` → retained for forensic history; not callable.

## Absolute rules

1. A Room cannot grant itself capabilities.
2. A Room cannot bypass Brain corridors.
3. A Room cannot rewrite canonical source data.
4. A Room cannot promote its own output.
5. Failed verification cannot become success through metadata edits.
6. Version changes create a new verifiable identity.
7. Every execution must be traceable to input identity and evidence.
