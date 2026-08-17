# QUANT-N001 — Room 01 Signal Foundation

## Status

IMPLEMENTED — WAITING FOR REAL CANONICAL INPUT

## Scope

N001 translates legacy research ideas into a deterministic Layer 1 signal-extraction room without importing legacy Excel/stateful/crawler architecture.

## Signal lineage retained

- frequency/distribution counting;
- recency comparison;
- T-1/T-2/T-7 temporal comparison;
- digit head/tail imbalance;
- missing/continuity awareness.

These are raw measurable hypotheses, not claims of predictive edge.

## Critical correction

A first attempt applied recency exclusion before temporal extraction. That would make T-1/T-2 echoes unobservable because the relevant rows are exactly the rows being removed.

The active implementation therefore uses:

```text
BOUNDED CANONICAL WINDOW
        |
        v
EXTRACT ALL FEATURES
  |      |       |       |
 freq  recency   T-1/T-2/T-7  digit imbalance
        |
        v
SELECTION POLICY
        |
        v
CANDIDATES
```

Recent rows remain available to feature extraction and are excluded only during candidate selection.

## Artifacts

- `room_01_signal.py` — historical baseline preserved.
- `room_01_signal_v2.py` — historical iteration preserved.
- `room_01_signal_v3.py` — current deterministic implementation.
- `tests/test_room_01_signal_v3.py` — active tests.
- `docs/ROOM_01_SIGNAL_DESIGN.md` — lineage and boundary contract.
- Brain handoff: `Project_Brain_AI/docs/architecture/QUANT_ROOM01_SIGNAL_LINEAGE.md`.

## Safety

- maximum working window: 30 days;
- no synthetic data;
- no future reconstruction;
- deterministic explicit ordering;
- feature extraction separated from selection;
- no probability/edge claim;
- Render 512 MB boundary remains active;
- Brain remains governance authority.

## Anti-self-deception rule

No synthetic fallback may be introduced merely to make the room green. Missing canonical input is an execution failure, not an invitation to manufacture data.

## Current evidence

The room implementation is present, but a real canonical source fixture has not yet been proven through the current repository surface.

```text
ROOM_01 CODE              = IMPLEMENTED
FEATURE/SELECTION DESIGN  = IMPLEMENTED
REAL INPUT EXECUTION      = NOT PROVEN
PREDICTIVE EDGE           = NOT CLAIMED
PROMOTION                 = DENY
```

## Next action

`QUANT-N002` — connect the canonical Input Adapter to Room 01 v3 with one real source fixture and emit one compact deterministic receipt:

```text
CANONICAL REAL DATA
    -> INPUT_ADAPTER
    -> ROOM_01_V3
    -> OUTPUT_RECEIPT
```

Only after this path is proven may scoring/prediction work begin.
