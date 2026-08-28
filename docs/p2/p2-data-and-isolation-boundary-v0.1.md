# P2 Data and Isolation Boundary v0.1

**Status:** FROZEN FOR D01–D12 ENGINEERING  
**Natural-task data:** not yet authorized

Allowed now:

- synthetic fixtures;
- explicitly public, non-sensitive source and event envelopes;
- hashes, schemas, metrics, and non-sensitive reports.

Prohibited now:

- credentials, secrets, tokens, or private keys;
- personal data or private enterprise content;
- production logs or private Harness traces;
- Human labels, Author Intent, Gold, Reference truth, hidden evaluator output, or sealed data in Worker/Shadow runtime input.

Raw authorized traces have a maximum 30-day retention. If prohibited content appears, ingestion stops and the record is quarantined. Shadow output is frozen before any copied-snapshot Reference evaluation. Reference details are never returned to the Worker or runtime Shadow Auditor.
