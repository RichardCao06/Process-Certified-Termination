"""Append-only canonical event log used by the P2 Shadow prototype."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from .canonical import digest_json
from .models import PctEvent


class AppendOnlyEventLog:
    """A strictly ordered event log with no update or delete operation."""

    def __init__(self, events: Iterable[PctEvent | Mapping] | None = None) -> None:
        self._events: list[PctEvent] = []
        self._ids: set[str] = set()
        if events is not None:
            for event in events:
                self.append(event)

    @classmethod
    def from_dicts(cls, values: Iterable[Mapping]) -> "AppendOnlyEventLog":
        return cls(PctEvent.from_dict(value) for value in values)

    def append(self, event: PctEvent | Mapping) -> PctEvent:
        item = event if isinstance(event, PctEvent) else PctEvent.from_dict(event)
        expected = len(self._events) + 1
        if item.sequence != expected:
            raise ValueError(
                f"event sequence must be contiguous: expected {expected}, got {item.sequence}"
            )
        if item.event_id in self._ids:
            raise ValueError(f"duplicate event_id: {item.event_id}")
        self._events.append(item)
        self._ids.add(item.event_id)
        return item

    @property
    def last_sequence(self) -> int:
        return self._events[-1].sequence if self._events else 0

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(tuple(self._events))

    def event_by_id(self, event_id: str) -> PctEvent:
        for event in self._events:
            if event.event_id == event_id:
                return event
        raise KeyError(event_id)

    def to_list(self) -> list[dict]:
        return [event.to_dict() for event in self._events]

    def digest(self) -> str:
        return digest_json(self.to_list())

    def through_sequence(self, sequence: int) -> "AppendOnlyEventLog":
        if sequence < 0 or sequence > self.last_sequence:
            raise ValueError("sequence is outside the event log")
        return AppendOnlyEventLog(self._events[:sequence])

    def validate_goal_identity(self, goal_id: str) -> list[str]:
        return [
            event.event_id
            for event in self._events
            if event.goal_id != goal_id
        ]
