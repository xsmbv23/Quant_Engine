# QUANT-N003-FIXTURE-ADMISSION — Forensic Proof Attempt

## What was actually executed

A real CI proof path was added and executed against the persisted rehearsal receipt:

```text
actual Room 01 V4 implementation
        +
actual replay.py path
        +
real persisted rehearsal receipt
```

The proof was deliberately run in an isolated workflow so unrelated unit-suite failures could not be mistaken for N003 evidence.

## Result

The proof did **not** reach determinism.

The persisted fixture:

```text
evidence/real_rehearsal/2026-08-12/quant_n002_receipt.json
```

contains 27 values such as:

```text
82326, 31773, 64497, ...
```

The frozen Room 01 V4 domain contract requires:

```text
exactly 27 integers
and each value must be 0..99
```

Therefore the fixture is rejected by the canonical domain gate.

This is not a code bug to be patched by weakening the domain.

## Forensic interpretation

```text
REAL SOURCE RECEIPT = EXISTS
RAW PROVENANCE      = EXISTS
ROOM VERSION        = V4
DOMAIN CONTRACT     = FROZEN
FIXTURE COMPATIBLE  = NO
N003 DETERMINISM    = UNREACHED
CORRECTNESS         = NOT_PROVEN
PROMOTION           = DENY
```

The old receipt is preserved as historical evidence. It must not be overwritten or silently transformed into a different domain.

## Why this is important

A successor Bot must not do any of the following:

- change `0..99` to `0..99999` just to make the test green;
- truncate five-digit values into two digits;
- modulo values into `0..99`;
- fabricate a new fixture;
- overwrite the old receipt;
- label the failed proof as PASS.

Any of those would destroy the Forensic boundary between **source truth** and **engine interpretation**.

## Correct next action

Obtain/admit a new **real-source** fixture that genuinely satisfies the frozen Room 01 V4 canonical domain. Then execute:

```text
FRESH1
  == REPLAY1
  == REPLAY2
  == FRESH2
```

for the complete canonical evidence hash set, plus mutation/anti-cheat rejection.

No promotion until this completes.

## Continuous-evidence rule

This failed attempt is itself valid evidence and remains permanently recorded. The evidence loop must accumulate DENY/UNREACHED history rather than erase failed attempts.

## Foundation relationship

Brain foundation remains frozen and is not reopened. The DB admission chain remains separate from Quant Engine Room 01 proof.

## Successor handoff

`state/next_action.json` now points to `QUANT-N003-FIXTURE-ADMISSION`.
