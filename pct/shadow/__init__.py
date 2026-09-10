"""P2 non-intervening Shadow foundation and explicit Candidate-Stop sidecar."""
from .adapter import DeepSeekHarnessAdapter
from .auditor import DeterministicShadowAuditor
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .metrics import summarize_bundles
from .replay import run_replay, verify_replay
from .sidecar import CandidateStopSidecar, ReadOnlyCandidateStopObserver
from .snapshot import build_candidate_stop_snapshot

__all__ = [
    "AppendOnlyEventLog",
    "CandidateStopSidecar",
    "DeepSeekHarnessAdapter",
    "DeterministicShadowAuditor",
    "EvidenceLedger",
    "ReadOnlyCandidateStopObserver",
    "build_candidate_stop_snapshot",
    "run_replay",
    "summarize_bundles",
    "verify_replay",
]
