# Synthetic Fixture Catalog

Synthetic fixtures test engineering invariants and codebook examples. Fixture-author expectations are not empirical Gold labels.

| Fixture | Intended property | Deterministic lint expectation |
|---|---|---|
| `valid-alternative-path.json` | valid but non-canonical action order | no finding |
| `premature-promotion.json` | VERIFIED state without evidence | `TRN.PREMATURE_STATE_PROMOTION`, `EVD.MISSING_REQUIRED_EVIDENCE` |
| `stale-evidence.json` | passing evidence invalidated by later state change | `EVD.STALE_EVIDENCE` |
| `ignored-tool-failure.json` | authoritative failure followed by unsupported verification | tool-failure, missing-evidence, premature-promotion findings |
| `scope-mismatch.json` | evidence for O1 reused to verify O2 | `EVD.SCOPE_MISMATCH` |

The valid-alternative fixture is a mandatory negative control against encoding one preferred sequence as the only acceptable process.
