from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Operation(StrEnum):
    CHECK = "check"
    SYNC = "sync"
    REPAIR = "repair"
    ADOPT = "adopt"
    PRUNE = "prune"
    UNKNOWN = "unknown"


class Result(StrEnum):
    OK = "ok"
    PLANNED = "planned"
    CHANGED = "changed"
    DRIFT = "drift"
    BLOCKED = "blocked"
    FAILED = "failed"


class FailureState(StrEnum):
    NO_CHANGES = "no-changes"
    ROLLED_BACK = "rolled-back"
    RECOVERY_REQUIRED = "recovery-required"


class Status(StrEnum):
    VALID = "valid"
    INDETERMINATE = "indeterminate"
    CONFIRMED_MISSING_SOURCE = "confirmed-missing-source"
    CONFIRMED_MISSING_SKILL = "confirmed-missing-skill"
    CONFIRMED_INVALID_SOURCE = "confirmed-invalid-source/no-valid-skills"
    AMBIGUOUS_OWNERSHIP = "ambiguous-ownership"
    PRUNABLE = "prunable"


class EventAction(StrEnum):
    AUDIT = "audit"
    BATCH = "batch"
    FETCH = "fetch"
    FILE = "file"
    LINK = "link"
    BLOCKED = "blocked"
    FAILED = "failed"


class EventKind(StrEnum):
    PHASE = "phase"
    PROGRESS = "progress"
    MUTATION = "mutation"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETE = "complete"


@dataclass(frozen=True)
class Skill:
    name: str
    source: str


@dataclass(frozen=True)
class InstalledSkill:
    name: str
    path: str
    source: str | None
    source_url: str | None


@dataclass(frozen=True)
class ManagedSkill:
    skill: str
    source: str
    path: str


@dataclass(frozen=True)
class Entry:
    skill: str
    source: str
    status: Status
    message: str
    diagnostic: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "skill": self.skill,
            "source": self.source,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class ExecutionEvent:
    kind: EventKind
    operation: Operation
    message: str = ""
    current: int | None = None
    total: int | None = None
    skill_id: str | None = None
    report: "Report | None" = None
    diagnostic: str = ""
    debug: str = ""
    action: EventAction | None = None


@dataclass(frozen=True)
class Report:
    operation: Operation
    result: Result
    lockfile: str
    entries: tuple[Entry, ...]
    planned_changes: int = 0
    failure_state: FailureState = FailureState.NO_CHANGES
    dry_run: bool = False
    confirmation_requested: bool = False
    confirmation_command: str = ""

    @property
    def exit_code(self) -> int:
        if self.result is Result.FAILED:
            return 2
        if self.result is Result.BLOCKED:
            return 1
        if self.result is Result.DRIFT:
            return 1
        if self.result is Result.PLANNED and self.operation in {
            Operation.REPAIR,
            Operation.PRUNE,
        }:
            return 1
        if self.operation is Operation.REPAIR and any(
            entry.status is Status.INDETERMINATE for entry in self.entries
        ):
            return 1
        return 0

    def to_dict(self) -> dict[str, object]:
        summary: dict[str, object] = {
            "valid": sum(entry.status is Status.VALID for entry in self.entries),
            "planned_changes": self.planned_changes,
        }
        if self.result is Result.FAILED:
            summary["failure_state"] = self.failure_state
        return {
            "schema_version": 1,
            "operation": self.operation,
            "result": self.result,
            "lockfile": self.lockfile,
            "summary": summary,
            "entries": [entry.to_dict() for entry in self.entries],
        }
