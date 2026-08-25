# PCT-P1-I01 — Missing Persistence of Announced Post-Pass-B Artifacts

## Status

Recorded during closure preparation on 2026-08-25.

## Observation

The current PR branch contained the Pass-B release metadata and the human-adjudication Gate document, but it did not contain the previously announced raw Pass-B freeze bundle, raw A/B report, author-opening verification, or three-way comparison artifacts.

## Recovery

The missing artifacts were reconstructed from:

- the frozen raw Pass A annotations;
- the frozen raw Pass B annotations and timing;
- the released Pass-B episode package;
- the encrypted author-expectation file;
- the separately held AES-256-GCM custody key;
- the completed human adjudication export.

The Author Expectation plaintext SHA-256 matched the pre-existing commitment.

## Impact

- Raw A/B agreement arithmetic is deterministic and was recovered.
- Raw Pass A and Pass B were not modified.
- The exact historical claim that an A/B report was hash-frozen before author opening cannot be independently proven from the current repository.
- Because P1 is developmental, the work may continue only with this limitation explicitly reported.
- The reconstructed report must not be represented as a historically preserved pre-opening artifact.

## Corrective action

- Commit every subsequent freeze, opening, and adjudication artifact before announcing completion.
- Add closure-readiness validation to CI.
- Require actual repository paths and hashes in future completion claims.
