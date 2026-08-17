# ROOM_01_SIGNAL — Design and Lineage

## Role

Room 01 is a deterministic signal-extraction room in Layer 1. It is not a predictor, not an ML model, and not a portfolio decision engine.

## Accepted raw ideas from legacy V5.8 / V16.0

Legacy research may contribute **ideas**, not executable authority:

- frequency / distribution counting;
- recency comparisons;
- temporal comparison around T-1, T-2, T-7;
- digit head/tail distribution imbalance;
- missing/continuity awareness.

Legacy Excel files, mutable global state, opaque crawler state, and any future-leaking implementation are not imported into Room 01.

## Causal boundary

The supplied EOD window is the only observation universe. T-1, T-2, and T-7 are earlier rows within that already-admitted window. No future row is requested or reconstructed.

A signal is a **raw measurable feature**, not a probability of winning.

## Deterministic ordering

All candidate ordering must use explicit stable tie-breaks. Set/dict iteration order must never determine output order.

## Bounded memory

Maximum working window: 30 days. No whole-history materialization is permitted inside the room.

## Output

Each candidate exposes compact fields:

- number;
- frequency_30d;
- recency exclusion;
- T-1/T-2/T-7 temporal echo flags;
- temporal score;
- digit head/tail imbalance;
- raw score.

The output does not claim that any candidate has a predictive edge.

## Promotion boundary

Room 01 may emit structured signal evidence to the next room only after its contract and deterministic tests pass. It cannot grant itself a corridor, capability, room key, or Brain inner release.
