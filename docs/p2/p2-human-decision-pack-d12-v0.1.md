# PCT-P2-D12 Decision Record — Candidate-Stop Metadata Source

**Decision:** A — explicit read-only PCT sidecar  
**Approved by:** Research Owner `RichardCao06`  
**PR comment:** `5419844078`  
**Effective:** 2026-08-26T02:43:51Z

The project will not infer stop semantics from assistant prose. A Task or Harness adapter supplies structured Candidate-Stop metadata. Missing metadata remains `UNKNOWN` / `UNDETERMINED`. The Sidecar is replay-bound and cannot steer, block, resume, mutate a Goal, or apply a verdict to runtime.
