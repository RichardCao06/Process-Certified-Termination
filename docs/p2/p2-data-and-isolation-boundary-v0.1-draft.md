# P2 Data and Isolation Boundary v0.1 — Draft

## Status

Pending `PCT-P2-D02`, `PCT-P2-D04`, and `PCT-P2-D05`.

Until those decisions are approved, the enforceable default is the most
restrictive one:

- synthetic or explicitly public fixtures only;
- no private runtime traces;
- no semantic Audit Agent calls;
- no reference-label opening;
- no hidden, Gold, sealed, Human-label, or Fixture Author fields in runtime;
- no network dependency in replay;
- no Worker feedback from Shadow findings.

## Separation of lanes

### Worker lane

Receives only the original task, approved tools, and normal Harness state.

### Shadow lane

Receives only approved observable events and read-only snapshots. It cannot
write to Worker state or Goal state.

### Reference lane

Not active in the foundation. A later offline reference evaluator must operate
on copied snapshots after Shadow outputs are frozen.

### Human adjudication lane

P1 human labels and adjudication are development artifacts. They may inform
protocol design but are prohibited runtime inputs.

## Minimum log hygiene

- redact credentials and tokens before persistence;
- preserve a digest and an explicit redaction record;
- distinguish model failure, tool failure, budget exit, infrastructure failure,
  and PCT method failure;
- preserve malformed and adverse traces;
- do not silently delete a record that failed parsing;
- record adapter, schema, policy, and code versions.

## Incident behavior

On detection of prohibited content:

1. stop ingestion of the affected record;
2. preserve a minimal incident hash and source locator;
3. quarantine or delete sensitive bytes according to the approved data policy;
4. mark all derived artifacts affected;
5. create an Incident Record;
6. do not continue the same run using leaked information.
