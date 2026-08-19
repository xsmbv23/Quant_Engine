# QUANT-N005 — State Authority Projection

Quant Engine is not a second state machine.

Its `state/current_state.json` is a **read-only projection** of Brain authority plus Quant-local operational facts.

## Authority

```text
xsmbv23/Project_Brain_AI/state/current_state.json
```

Current Brain state identity at handoff:

```text
blob = f368e1b448fe34f56897257e318e46709ad268fe
protocol = 1.0
schema = 1.0
```

## Rules

- Quant may observe and execute only capabilities authorized by Brain.
- Quant may not override Brain state.
- Quant may not self-promote a room or layer.
- Historical Quant state remains history, not authority.
- Any conflict with Brain authority is `HARD_DENY`.
- `PASS` is local to a gate and never inherited.
- Unknown is not pass.
- Default deny.

## Current room

```text
ROOM_01_INPUT_ADAPTER = ACTIVE BOUNDARY
ROOM_02 = LOCKED
STAIRCASE = LOCKED
PROMOTION = DENY
```

## Next

`QUANT-N006` — implement a lightweight local projection verifier that consumes Brain authority identity and denies local execution on authority mismatch. It must not create a network dependency or load bulk data.
