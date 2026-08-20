# QUANT-N007 — Source-specific parser contracts

## Scope

Safe parallel work only. Brain promotion gates remain untouched.

## Completed

Defined independent parser contracts for:

- `ketqua16.net`
- `xsmb.com.vn`

Both contracts enforce:

- raw bytes captured before interpretation
- exact raw SHA-256 remains byte identity only
- semantic SHA-256 is computed only from the validated canonical 27-value domain
- source identity is separate from raw hash
- explicit business date only
- no future dates
- no missing/ambiguous/duplicate values
- no interpolation
- no silent fill
- no synthetic history
- advertisement/non-data HTML must never enter canonical data
- raw artifacts remain immutable
- promotion remains a Brain admission decision

## Important architectural boundary

The two websites must NOT share a parser implementation merely because both represent XSMB. Source-specific DOM/HTML extraction remains isolated. Only the canonical semantic output may converge.

```text
ketqua16 raw HTML ──> ketqua16 parser ──┐
                                       ├──> canonical 27-value domain
xsmb raw HTML ─────> xsmb parser ──────┘
                                             |
                                             v
                                      semantic SHA-256
                                             |
                                      cross-source quorum
```

## CI observation

Do not claim N006 tested from repository structure alone. Exact-current CI observation remains pending unless an independently observable workflow receipt exists.

## Safety

No Brain gate was unlocked. Room 02 remains locked. Staircase remains locked. No database promotion was performed.

## Next

`QUANT-N008` — implement bounded source-specific semantic parsers with fixture-free unit tests using structural HTML snippets only; production admission remains REAL_SOURCE_ONLY and fixture != reality.
