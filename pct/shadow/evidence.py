"""Replayable Evidence Ledger for the P2 Shadow foundation."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import EvidenceRecord


class EvidenceLedger:
    """Append-only evidence records plus append-only invalidation references."""

    def __init__(self, records: Iterable[EvidenceRecord | Mapping] | None = None) -> None:
        self._records: dict[str, EvidenceRecord] = {}
        self._order: list[str] = []
        self._invalidations: dict[str, list[str]] = {}
        if records is not None:
            for record in records:
                self.add(record)

    @classmethod
    def from_dicts(cls, values: Iterable[Mapping]) -> "EvidenceLedger":
        return cls(EvidenceRecord.from_dict(value) for value in values)

    def add(self, record: EvidenceRecord | Mapping) -> EvidenceRecord:
        item = (
            record
            if isinstance(record, EvidenceRecord)
            else EvidenceRecord.from_dict(record)
        )
        if item.evidence_id in self._records:
            raise ValueError(f"duplicate evidence_id: {item.evidence_id}")
        self._records[item.evidence_id] = item
        self._order.append(item.evidence_id)
        self._invalidations[item.evidence_id] = list(item.invalidated_by_event_ids)
        return item

    def invalidate(self, evidence_id: str, event_id: str) -> None:
        if evidence_id not in self._records:
            raise KeyError(evidence_id)
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be non-empty")
        if event_id not in self._invalidations[evidence_id]:
            self._invalidations[evidence_id].append(event_id)

    def record(self, evidence_id: str) -> EvidenceRecord:
        return self._records[evidence_id]

    def invalidation_event_ids(self, evidence_id: str) -> tuple[str, ...]:
        return tuple(self._invalidations[evidence_id])

    def is_current(
        self,
        evidence_id: str,
        *,
        goal_id: str,
        goal_revision: int,
    ) -> bool:
        record = self.record(evidence_id)
        return (
            record.goal_id == goal_id
            and record.goal_revision == goal_revision
            and not self._invalidations[evidence_id]
        )

    def valid_records_for_obligation(
        self,
        obligation_id: str,
        *,
        goal_id: str,
        goal_revision: int,
    ) -> tuple[EvidenceRecord, ...]:
        return tuple(
            self._records[evidence_id]
            for evidence_id in self._order
            if obligation_id in self._records[evidence_id].obligation_ids
            and self.is_current(
                evidence_id,
                goal_id=goal_id,
                goal_revision=goal_revision,
            )
        )

    def authoritative_failures_for_obligation(
        self,
        obligation_id: str,
        *,
        goal_id: str,
        goal_revision: int,
    ) -> tuple[EvidenceRecord, ...]:
        return tuple(
            record
            for record in self.valid_records_for_obligation(
                obligation_id,
                goal_id=goal_id,
                goal_revision=goal_revision,
            )
            if record.authoritative and record.result == "FAIL"
        )

    def current_evidence_ids(
        self,
        *,
        goal_id: str,
        goal_revision: int,
    ) -> tuple[str, ...]:
        return tuple(
            evidence_id
            for evidence_id in self._order
            if self.is_current(
                evidence_id,
                goal_id=goal_id,
                goal_revision=goal_revision,
            )
        )

    def to_list(self) -> list[dict]:
        values: list[dict] = []
        for evidence_id in self._order:
            value = self._records[evidence_id].to_dict()
            value["invalidated_by_event_ids"] = list(
                self._invalidations[evidence_id]
            )
            values.append(value)
        return values
