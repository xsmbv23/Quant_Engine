# QUANT-N001 — First Measurable Execution Frame

## Status

IMPLEMENTED — WAITING FOR REAL CANONICAL INPUT

## Scope

N001 creates exactly one minimal execution path:

```text
CANONICAL DATA
    -> INPUT ADAPTER
    -> ROOM 01 / SIGNAL
    -> SCORING
    -> OUTPUT
```

Files:

- `input_adapter.py`
- `room_01_signal.py`
- `scoring.py`
- `app.py`

## Signal

Room 01 implements the deliberately simple baseline requested for N001:

1. flatten the supplied EOD window;
2. count frequency;
3. select the 20 least frequent values;
4. remove values seen in the latest 3 days;
5. emit at most 10 candidates;
6. scoring preserves the signal ordering unchanged.

This is a measurable baseline, not an asserted edge.

## Important anti-self-deception rule

There is **no synthetic fallback** in `app.py`.

The executable form is:

```text
python app.py <canonical-data.json>
```

Missing input is an execution error. The engine must not manufacture demo data to produce a green result.

## Boundary rules

Quant Engine does not recreate Brain's Forensic FSM, corridor security, permission graph, or persistent-memory authority. Brain remains the governance control plane. Quant Engine is execution only.

## Current evidence

Code was created on `main` with the final N001 file commit:

```text
785a91d08329bb3d58f7dd27196df8d5b940bead
```

The repository currently has no verified canonical source fixture available through the GitHub connector, so N001 is **not yet promoted to PASS**. This is intentional.

```text
CODE FRAME            = IMPLEMENTED
REAL INPUT             = NOT AVAILABLE THROUGH CURRENT REPOSITORY SURFACE
RUN -> OUTPUT          = NOT PROVEN
EDGE                   = NOT CLAIMED
PROMOTION              = DENY
N002                   = BLOCKED UNTIL REAL CANONICAL INPUT EXECUTES
```

## Next action

`QUANT-N002` — obtain/consume one real canonical data artifact from the upstream data plane and execute N001 without copying the dataset into Brain or inventing synthetic data. Record the exact input identity/hash, output, runtime, and memory evidence. Only then evaluate whether the baseline has measurable predictive value.
