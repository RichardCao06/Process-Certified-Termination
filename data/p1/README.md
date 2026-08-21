# P1 Development Data

## `synthetic/`

Controlled observable trajectories used to test schemas, validators, deterministic candidate lints, and codebook examples. They contain no held-out or sealed evaluator information.

## `annotations/`

Fixture-author expectations used only for engineering smoke tests. They are explicitly marked `FIXTURE_AUTHOR` and must not be reported as human agreement or empirical Gold.

Human pilot annotations should be written to a new versioned development directory after P1 decisions are approved. Original passes must remain immutable through adjudication.
