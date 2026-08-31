from __future__ import annotations

import json
import re
from enum import StrEnum

from .adapters import Npx
from .models import (
    Entry,
    InstalledSkill,
    ManagedSkill,
    Operation,
    Report,
    Result,
    Skill,
    Status,
)


class ConfigurationError(ValueError):
    """Raised when a required skillx document is malformed or unusable."""


class SourceState(StrEnum):
    ENUMERATED = "enumerated"


class OwnershipError(ConfigurationError):
    """Raised when installed state cannot be safely attributed to skillx."""

    def __init__(self, refusals: tuple[Entry, ...]) -> None:
        self.refusals = refusals
        super().__init__(
            "ownership is ambiguous: " + "; ".join(r.message for r in refusals)
        )


def parse_lockfile(content: str) -> tuple[Skill, ...]:
    try:
        document = json.loads(content)
    except json.JSONDecodeError as error:
        raise ConfigurationError(f"invalid lockfile JSON: {error.msg}") from error
    if not isinstance(document, dict) or not isinstance(document.get("skills"), dict):
        raise ConfigurationError("lockfile must contain a skills object")

    skills: list[Skill] = []
    for name, value in document["skills"].items():
        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError("every skill needs a non-empty name")
        if not isinstance(value, dict):
            raise ConfigurationError(f"skill {name!r} must be an object")
        source = value.get("source")
        if not isinstance(source, str) or not source.strip():
            raise ConfigurationError(f"skill {name!r} needs a usable source")
        skills.append(Skill(name=name, source=source))
    return tuple(skills)


def _listed_names(output: str) -> set[str] | None:
    try:
        document = json.loads(output)
    except json.JSONDecodeError:
        ansi_escape = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
        names: set[str] = set()
        for raw_line in output.splitlines():
            line = ansi_escape.sub("", raw_line)
            match = re.match(r"^[│|](?: {2}| {4})(\S+)\s*$", line)
            if match:
                names.add(match.group(1).casefold())
        return names if "Available Skills" in output else None
    raw_skills = document.get("skills", []) if isinstance(document, dict) else []
    if not isinstance(raw_skills, list):
        return None
    return {
        item["name"].casefold()
        for item in raw_skills
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def validate(
    lockfile: str,
    content: str,
    npx: Npx,
    operation: Operation = Operation.CHECK,
) -> Report:
    skills = parse_lockfile(content)
    source_states: dict[str, tuple[Status | SourceState, set[str]]] = {}
    source_diagnostics: dict[str, str] = {}
    for source in dict.fromkeys(skill.source for skill in skills):
        command_result = npx.enumerate_source(source)
        diagnostics = f"{command_result.stdout}\n{command_result.stderr}"
        source_diagnostics[source] = diagnostics.strip()
        if command_result.classification == Status.CONFIRMED_MISSING_SOURCE:
            source_states[source] = (Status.CONFIRMED_MISSING_SOURCE, set())
        elif command_result.returncode != 0 and "No valid skills found." in diagnostics:
            source_states[source] = (Status.CONFIRMED_INVALID_SOURCE, set())
        elif command_result.returncode != 0:
            source_states[source] = (Status.INDETERMINATE, set())
        else:
            names = _listed_names(command_result.stdout)
            if names is None:
                source_states[source] = (Status.INDETERMINATE, set())
            elif not names:
                source_states[source] = (
                    Status.CONFIRMED_INVALID_SOURCE,
                    set(),
                )
            else:
                source_states[source] = (SourceState.ENUMERATED, names)

    def entry_for(skill: Skill) -> Entry:
        source_status, names = source_states[skill.source]
        if source_status is Status.CONFIRMED_MISSING_SOURCE:
            return Entry(
                skill.name,
                skill.source,
                source_status,
                "authoritative provider response confirms the source is missing",
                source_diagnostics[skill.source],
            )
        if source_status is Status.CONFIRMED_INVALID_SOURCE:
            return Entry(
                skill.name,
                skill.source,
                source_status,
                "source contains no valid discoverable skills",
                source_diagnostics[skill.source],
            )
        if source_status is Status.INDETERMINATE:
            return Entry(
                skill.name,
                skill.source,
                Status.INDETERMINATE,
                "source could not be validated",
                source_diagnostics[skill.source],
            )
        if skill.name.casefold() in names:
            return Entry(skill.name, skill.source, Status.VALID, "skill is available")
        return Entry(
            skill.name,
            skill.source,
            Status.CONFIRMED_MISSING_SKILL,
            "skill is not available from source",
        )

    entries = tuple(entry_for(skill) for skill in skills)
    result = (
        Result.OK
        if all(entry.status is Status.VALID for entry in entries)
        else Result.BLOCKED
    )
    return Report(operation, result, lockfile, entries)


def check(lockfile: str, content: str, npx: Npx) -> Report:
    return validate(lockfile, content, npx, Operation.CHECK)


def repaired_lockfile(content: str, names: set[str]) -> str:
    document = json.loads(content)
    document["skills"] = {
        name: value for name, value in document["skills"].items() if name not in names
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def parse_inventory(content: str) -> tuple[InstalledSkill, ...]:
    try:
        document = json.loads(content)
    except json.JSONDecodeError as error:
        raise ConfigurationError(f"invalid inventory JSON: {error.msg}") from error
    if not isinstance(document, list):
        raise ConfigurationError("installed inventory must be a JSON array")

    installed: list[InstalledSkill] = []
    for index, item in enumerate(document):
        if not isinstance(item, dict):
            raise ConfigurationError(f"inventory entry {index} must be an object")
        name = item.get("name")
        path = item.get("path")
        scope = item.get("scope")
        agents = item.get("agents")
        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError(f"inventory entry {index} needs a non-empty name")
        if not isinstance(path, str) or not path.startswith("/"):
            raise ConfigurationError(f"inventory entry {index} needs an absolute path")
        if (
            scope != "global"
            or not isinstance(agents, list)
            or not all(isinstance(agent, str) for agent in agents)
        ):
            raise ConfigurationError(f"inventory entry {index} has an invalid shape")
        source = item.get("source")
        source_url = item.get("sourceUrl")
        source_type = item.get("sourceType")
        if source is not None and not isinstance(source, str):
            raise ConfigurationError(f"inventory entry {index} has an invalid source")
        if source_url is not None and not isinstance(source_url, str):
            raise ConfigurationError(
                f"inventory entry {index} has an invalid source URL"
            )
        if source_type is not None and not isinstance(source_type, str):
            raise ConfigurationError(
                f"inventory entry {index} has an invalid source type"
            )
        installed.append(InstalledSkill(name, path, source, source_url))
    return tuple(installed)


def _source_matches(desired: str, installed: InstalledSkill) -> bool:
    if installed.source == desired or installed.source_url == desired:
        return True
    if installed.source is not None or installed.source_url is None:
        return False
    github_url = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?/?",
        installed.source_url,
    )
    github_shorthand = re.fullmatch(r"[^/]+/[^/]+", desired)
    return bool(github_url and github_shorthand and github_url.group(1) == desired)


def adoption_ledger(
    skills: tuple[Skill, ...], inventory: tuple[InstalledSkill, ...]
) -> str:
    records: list[dict[str, str]] = []
    for skill in skills:
        candidates = [
            item for item in inventory if item.name.casefold() == skill.name.casefold()
        ]
        if len(candidates) != 1:
            raise OwnershipError(
                (
                    Entry(
                        skill.name,
                        skill.source,
                        Status.AMBIGUOUS_OWNERSHIP,
                        f"expected one installed path, found {len(candidates)}",
                    ),
                )
            )
        installed = candidates[0]
        if not _source_matches(skill.source, installed):
            raise OwnershipError(
                (
                    Entry(
                        skill.name,
                        skill.source,
                        Status.AMBIGUOUS_OWNERSHIP,
                        "installed source does not match desired source",
                    ),
                )
            )
        records.append(
            {"skill": skill.name, "source": skill.source, "path": installed.path}
        )
    return (
        json.dumps({"schema_version": 1, "managed": records}, indent=2, sort_keys=True)
        + "\n"
    )


def parse_ledger(content: str) -> tuple[ManagedSkill, ...]:
    try:
        document = json.loads(content)
    except json.JSONDecodeError as error:
        raise ConfigurationError(
            f"invalid ownership ledger JSON: {error.msg}"
        ) from error
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ConfigurationError("ownership ledger must use schema_version 1")
    raw_records = document.get("managed")
    if not isinstance(raw_records, list):
        raise ConfigurationError("ownership ledger must contain a managed array")

    records: list[ManagedSkill] = []
    seen_paths: set[str] = set()
    for index, item in enumerate(raw_records):
        if not isinstance(item, dict):
            raise ConfigurationError(f"ledger record {index} must be an object")
        skill = item.get("skill")
        source = item.get("source")
        path = item.get("path")
        if (
            not isinstance(skill, str)
            or not skill.strip()
            or not isinstance(source, str)
            or not source.strip()
            or not isinstance(path, str)
            or not path.strip()
        ):
            raise ConfigurationError(f"ledger record {index} has an invalid shape")
        if not path.startswith("/"):
            raise ConfigurationError(f"ledger record {index} needs an absolute path")
        if path in seen_paths:
            raise ConfigurationError(
                f"ownership ledger contains duplicate path {path!r}"
            )
        seen_paths.add(path)
        records.append(ManagedSkill(skill, source, path))
    return tuple(records)


def prune_candidates(
    desired: tuple[Skill, ...],
    managed: tuple[ManagedSkill, ...],
    inventory: tuple[InstalledSkill, ...],
) -> tuple[ManagedSkill, ...]:
    desired_keys = {(skill.name.casefold(), skill.source) for skill in desired}
    candidates = tuple(
        record
        for record in managed
        if (record.skill.casefold(), record.source) not in desired_keys
    )
    refusals: list[Entry] = []
    for record in candidates:
        name_matches = [
            installed
            for installed in inventory
            if installed.name.casefold() == record.skill.casefold()
        ]
        if len(name_matches) != 1:
            refusals.append(
                Entry(
                    record.skill,
                    record.source,
                    Status.AMBIGUOUS_OWNERSHIP,
                    f"expected one inventory entry named {record.skill}, found {len(name_matches)}",
                )
            )
            continue
        matches = [
            installed for installed in inventory if installed.path == record.path
        ]
        if len(matches) != 1:
            refusals.append(
                Entry(
                    record.skill,
                    record.source,
                    Status.AMBIGUOUS_OWNERSHIP,
                    f"expected one inventory entry at {record.path}, found {len(matches)}",
                )
            )
            continue
        installed = matches[0]
        if installed.name.casefold() != record.skill.casefold():
            refusals.append(
                Entry(
                    record.skill,
                    record.source,
                    Status.AMBIGUOUS_OWNERSHIP,
                    "installed name conflicts with ledger",
                )
            )
        if not _source_matches(record.source, installed):
            refusals.append(
                Entry(
                    record.skill,
                    record.source,
                    Status.AMBIGUOUS_OWNERSHIP,
                    "installed source conflicts with ledger",
                )
            )
    if refusals:
        raise OwnershipError(tuple(refusals))
    return candidates


def ledger_without(
    managed: tuple[ManagedSkill, ...], candidates: tuple[ManagedSkill, ...]
) -> str:
    removed_paths = {record.path for record in candidates}
    records = [
        {"skill": record.skill, "source": record.source, "path": record.path}
        for record in managed
        if record.path not in removed_paths
    ]
    return (
        json.dumps({"schema_version": 1, "managed": records}, indent=2, sort_keys=True)
        + "\n"
    )
