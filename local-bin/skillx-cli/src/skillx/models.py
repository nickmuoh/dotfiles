from __future__ import annotations

from dataclasses import dataclass


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
    status: str
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
    operation: str
    result: str
    lockfile: str
    entries: tuple[Entry, ...]
    planned_changes: int = 0

    @property
    def exit_code(self) -> int:
        if self.result == "failed":
            return 2
        if self.result == "blocked":
            return 1
        if self.result == "planned" and self.operation in {"repair", "prune"}:
            return 1
        if self.operation == "repair" and any(
            entry.status == "indeterminate" for entry in self.entries
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
                "valid": sum(entry.status == "valid" for entry in self.entries),
                "planned_changes": self.planned_changes,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }
