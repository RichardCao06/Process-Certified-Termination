# P2 Development Data

Only synthetic or explicitly public development inputs are allowed while
`PCT-P2-D02` remains pending.

## Fixtures

- `fixtures/replay-clean-success-v0.1.json` — current authoritative Evidence
  supports a hard deliverable; policy remains pending.
- `fixtures/replay-stale-evidence-v0.1.json` — prior PASS Evidence is
  invalidated by a later state delta, but the obligation is still represented
  as VERIFIED.

These fixtures contain no Human labels, Author Intent, Gold, hidden evaluator,
sealed data, secrets, or private runtime content.

Do not place live Harness traces in this directory until the P2 runtime data
policy is explicitly approved and a separate location, access model, and
retention rule are frozen.
