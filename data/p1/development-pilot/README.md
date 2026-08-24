# P1 Development Pilot

This directory contains the development-only 30-episode source package, encrypted Fixture Author Expectations, the frozen partial Human Pass A bundle, and the delayed Pass-B commitment.

## Current design

- Source episodes generated: 30.
- Human Pass A completed: first 25 fixed-order episodes.
- Unannotated reserve: positions 26–30.
- Missingness: administrative right truncation; no imputation.
- Human Pass B: 12-case deterministic reordered subset of the 25 completed cases.
- Pass B release: not before `2026-08-27T07:48:20Z`.
- Reporting: developmental intra-rater feasibility only.

## Data separation

- Observable episodes and tooling contain no Fixture Author Expectations.
- Fixture Author Expectations are AES-256-GCM encrypted and marked `not_gold`.
- The raw Human Pass A is stored in a hash-verified compressed bundle rather than ordinary text to reduce accidental recall before Pass B. This is not cryptographic sealing.
- Neither the five reserve cases nor any later completion may be silently pooled with the frozen Pass A.

See `docs/p1/amendment-PCT-P1-A01.md`.
