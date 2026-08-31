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
    BLOCKED = "blocked"
    FAILED = "failed"


class Status(StrEnum):
    VALID = "valid"
    INDETERMINATE = "indeterminate"
    CONFIRMED_MISSING_SOURCE = "confirmed-missing-source"
    CONFIRMED_MISSING_SKILL = "confirmed-missing-skill"
    CONFIRMED_INVALID_SOURCE = "confirmed-invalid-source/no-valid-skills"
    AMBIGUOUS_OWNERSHIP = "ambiguous-ownership"
    PRUNABLE = "prunable"


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
class Report:
    operation: Operation
    result: Result
    lockfile: str
    entries: tuple[Entry, ...]
    planned_changes: int = 0

    @property
    def exit_code(self) -> int:
        if self.result is Result.FAILED:
            return 2
        if self.result is Result.BLOCKED:
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
        return {
            "schema_version": 1,
            "operation": self.operation,
            "result": self.result,
            "lockfile": self.lockfile,
            "summary": {
                "valid": sum(entry.status is Status.VALID for entry in self.entries),
                "planned_changes": self.planned_changes,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }
