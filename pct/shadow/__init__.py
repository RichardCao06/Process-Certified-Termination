"""P2 non-intervening Shadow foundation.

The package supports observable event normalization, append-only evidence,
deterministic checks, and replay. It does not register runtime hooks and cannot
apply a verdict to a Worker or Harness.
"""
from .adapter import DeepSeekHarnessAdapter
from .auditor import DeterministicShadowAuditor
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .replay import run_replay, verify_replay
from .snapshot import build_candidate_stop_snapshot

__all__ = [
    "AppendOnlyEventLog",
    "DeepSeekHarnessAdapter",
    "DeterministicShadowAuditor",
    "EvidenceLedger",
    "build_candidate_stop_snapshot",
    "run_replay",
    "verify_replay",
]
