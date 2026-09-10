# P2 DeepSeek Profile Introspection and Reference Downgrade v0.1

## Status

The Research Owner supplied a sanitized Worker-profile declaration and confirmed that
`DEEPSEEK_API_KEY` is stored as the `p2-natural-pilot` GitHub Environment Secret. The
secret value is not part of the PR, repository, log, artifact, command line, or configuration
digest.

This increment does **not** authorize a natural-task Worker call.

## Read-only provider evidence

The existing Worker-profile freeze permits a read-only provider/profile introspection that
performs no task generation. The added workflow therefore makes only:

```text
GET https://api.deepseek.com/models
```

It records only sanitized model-list evidence:

- HTTP status;
- returned public model IDs and owner;
- whether `deepseek-v4-pro` is listed;
- hashes of the candidate profile, system prompt, and intended tool catalog.

It does not call Chat Completions, does not create a Worker trajectory, and does not record
the API key, its hash, the Authorization header, account identity, billing data, or response
headers.

A human statement that the returned ID is `deepseek-v4-pro` is preserved as a declaration,
but it is not treated as provider evidence until the controlled `GET /models` record passes.

## Reference-lane downgrade

The Research Owner explicitly reported that a second distinct independent human rater is
unavailable. The already-approved D17 downgrade rule is therefore applied:

```text
semi-open Reference lane =
DEVELOPMENTAL_SINGLE_HUMAN_RATER
```

Consequences:

- `P2-RATER-A` may provide a developmental judgment after the Shadow packet is frozen;
- `P2-RATER-B` is recorded as unavailable, not as a second person;
- no independent inter-rater reliability claim is permitted;
- no Gold-label claim is permitted;
- the declared `P2-ADJUDICATOR` alias is not activated as an independent adjudicator without
  two independent passes;
- Reference packets remain unopened.

## Remaining Gate

After provider introspection succeeds, a smaller Human Gate must freeze the operational
retry policy, context/output caps, per-trajectory token cap, and the authority for a limited
engineering smoke run. The 60-trajectory natural pilot is still not authorized.
