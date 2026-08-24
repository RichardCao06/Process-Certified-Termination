# P1 Calibration Data

This directory stores a reviewed, versioned development-data bundle rather than exposing long raw records as ordinary PR text.

## Bundle integrity

- Manifest: `bundle-manifest.json`
- Parts: `bundle-parts/part-00` through `part-04`
- Decoded archive SHA-256: `4baf6d8176b1c2718f28ddea48d1d5e6775cfcd8495bedc41d844eb0e82afed0`
- Materialize locally: `make materialize-calibration`
- Validate without materializing: `python3 scripts/validate_p1_calibration.py`

The bundle preserves Human Pass 1 and Agent Blind Pass 1 as separate immutable inputs and adds derived comparison, adjudication, and regression records. It contains no Fixture Author Expectations, held-out data, sealed data, hidden evaluator output, or post-stop repair outcome.

Original annotations must never be overwritten by adjudication or migration.
