from __future__ import annotations

import io
import os
import sys
from collections.abc import Sequence
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from .adapters import CommandResult, InstallRequest, Mutation, Runtime, default_runtime
from .cli import ArgumentParser
from .execution import AgentSkillError, execute, usage_failure
from .models import Entry, InstalledSkill, Operation, Report, Result, Status
from .reconcile import (
    OwnershipError,
    adoption_ledger,
    ledger_without,
    parse_inventory,
    parse_ledger,
    parse_lockfile,
    prune_candidates,
    repaired_lockfile,
    validate,
)

DEFAULT_LOCKFILE = os.environ.get(
    "LOCKFILE", str(Path.home() / ".agents" / ".skill-lock.json")
)
DEFAULT_LEDGER = str(Path.home() / ".agents" / ".skillx-managed.json")

cli = ArgumentParser(prog="skillx")
cli.enable_subcommands()


def _common_args(
    *, ledger: bool = False, dry_run: bool = False, yes: bool = False
) -> tuple[object, ...]:
    arguments: list[object] = [
        cli.argument("--lockfile", default=DEFAULT_LOCKFILE),
        cli.argument("--json", action="store_true", dest="json_output"),
        cli.argument("-v", "--verbose", action="count", default=0),
    ]
    if ledger:
        arguments.insert(1, cli.argument("--ledger", default=DEFAULT_LEDGER))
    if dry_run:
        arguments.append(cli.argument("--dry-run", action="store_true"))
    if yes:
        arguments.append(cli.argument("--yes", action="store_true"))
    return tuple(arguments)


def validated_lockfile(
    operation: Operation, lockfile: str, runtime: Runtime
) -> tuple[str, Report]:
    """Read desired state and return its reconciliation report."""
    content = runtime.filesystem.read_text(lockfile)
    return content, validate(lockfile, content, runtime.npx, operation)


def inventory_for(
    operation: Operation, lockfile: str, runtime: Runtime
) -> tuple[InstalledSkill, ...]:
    """Load installed skills or raise one contextual external-command failure."""
    result = runtime.npx.inventory()
    if result.returncode != 0:
        raise AgentSkillError(
            operation,
            lockfile,
            "inventory command failed",
            command_diagnostics(result),
        )
    return parse_inventory(result.stdout)


def command_diagnostics(result: CommandResult) -> str:
    """Select the command output that explains a failed external command."""
    return result.stderr.strip() or result.stdout.strip() or "no diagnostic output"


def require_success(
    mutation: Mutation, operation: Operation, lockfile: str, action: str
) -> None:
    """Restore a failed transaction before raising its contextual failure."""
    if mutation.result.returncode == 0:
        return

    diagnostics = command_diagnostics(mutation.result)
    try:
        mutation.rollback()
    except OSError as error:
        diagnostics = f"{diagnostics}; rollback failed: {error}"
    raise AgentSkillError(operation, lockfile, f"{action} failed", diagnostics)


@cli.command(
    *_common_args(),
    help="validate desired and remote state without mutation",
)
def check(lockfile: str, runtime: Runtime) -> Report:
    """Report source and skill classifications without changing state."""
    _, report = validated_lockfile(Operation.CHECK, lockfile, runtime)
    return report


@cli.command(
    *_common_args(dry_run=True),
    cli.argument("--agent", action="extend", nargs="+", default=[]),
    help="validate and install or update desired skills",
)
def sync(lockfile: str, dry_run: bool, agent: list[str], runtime: Runtime) -> Report:
    """Converge installed skills only after every desired entry validates."""
    _, report = validated_lockfile(Operation.SYNC, lockfile, runtime)
    if report.result is not Result.OK:
        return report

    synced = Report(
        Operation.SYNC,
        Result.PLANNED if dry_run else Result.CHANGED,
        lockfile,
        report.entries,
        planned_changes=len(report.entries),
    )
    if dry_run:
        return synced

    skills_by_source: dict[str, list[str]] = {}
    for entry in report.entries:
        skills_by_source.setdefault(entry.source, []).append(entry.skill)
    requests = tuple(
        InstallRequest(source, tuple(skills), tuple(agent))
        for source, skills in skills_by_source.items()
    )

    mutation = runtime.npx.install_transaction(requests)
    require_success(mutation, Operation.SYNC, lockfile, "install")
    mutation.commit()
    return synced


@cli.command(
    *_common_args(dry_run=True, yes=True),
    help="remove confirmed-invalid desired entries",
)
def repair(lockfile: str, dry_run: bool, yes: bool, runtime: Runtime) -> Report:
    """Back up and repair only entries proven invalid by enumeration."""
    content, report = validated_lockfile(Operation.REPAIR, lockfile, runtime)
    repairable = {
        entry.skill
        for entry in report.entries
        if entry.status
        in {
            Status.CONFIRMED_MISSING_SOURCE,
            Status.CONFIRMED_MISSING_SKILL,
            Status.CONFIRMED_INVALID_SOURCE,
        }
    }
    if not repairable:
        return report

    result = Result.PLANNED
    if yes and not dry_run:
        runtime.filesystem.copy(lockfile, f"{lockfile}.{runtime.now()}.bak")
        runtime.filesystem.write_atomic(
            lockfile, repaired_lockfile(content, repairable)
        )
        result = Result.CHANGED
    return Report(
        Operation.REPAIR,
        result,
        lockfile,
        report.entries,
        planned_changes=len(repairable),
    )


@cli.command(
    cli.argument("--from-lock", action="store_true", required=True),
    *_common_args(ledger=True, dry_run=True, yes=True),
    help="explicitly transfer custody of installed desired skills",
)
def adopt(
    lockfile: str,
    ledger: str,
    dry_run: bool,
    yes: bool,
    runtime: Runtime,
) -> Report:
    """Validate and record exact-path ownership for existing installations."""
    content, report = validated_lockfile(Operation.ADOPT, lockfile, runtime)
    if report.result is not Result.OK:
        return report

    try:
        ledger_content = adoption_ledger(
            parse_lockfile(content), inventory_for(Operation.ADOPT, lockfile, runtime)
        )
    except OwnershipError as error:
        return Report(Operation.ADOPT, Result.BLOCKED, lockfile, error.refusals)

    result = Result.PLANNED
    if yes and not dry_run:
        runtime.filesystem.write_atomic(ledger, ledger_content)
        result = Result.CHANGED
    return Report(
        Operation.ADOPT,
        result,
        lockfile,
        report.entries,
        planned_changes=len(report.entries),
    )


@cli.command(
    *_common_args(ledger=True, dry_run=True, yes=True),
    help="remove unambiguously owned skills absent from desired state",
)
def prune(
    lockfile: str,
    ledger: str,
    dry_run: bool,
    yes: bool,
    runtime: Runtime,
) -> Report:
    """Remove only exact-path ledger entries absent from desired state."""
    desired = parse_lockfile(runtime.filesystem.read_text(lockfile))
    managed = parse_ledger(runtime.filesystem.read_text(ledger))

    try:
        candidates = prune_candidates(
            desired,
            managed,
            inventory_for(Operation.PRUNE, lockfile, runtime),
        )
    except OwnershipError as error:
        return Report(Operation.PRUNE, Result.BLOCKED, lockfile, error.refusals)

    entries = tuple(
        Entry(
            record.skill,
            record.source,
            Status.PRUNABLE,
            f"managed installation at {record.path} is absent from desired state",
        )
        for record in candidates
    )
    if not candidates:
        return Report(Operation.PRUNE, Result.OK, lockfile, entries)
    if dry_run or not yes:
        return Report(
            Operation.PRUNE,
            Result.PLANNED,
            lockfile,
            entries,
            planned_changes=len(candidates),
        )

    mutation = runtime.npx.remove_transaction(
        tuple(record.skill for record in candidates)
    )
    require_success(mutation, Operation.PRUNE, lockfile, "removal")
    try:
        runtime.filesystem.write_atomic(ledger, ledger_without(managed, candidates))
    except OSError as error:
        try:
            mutation.rollback()
        except OSError as rollback_error:
            raise AgentSkillError(
                Operation.PRUNE,
                lockfile,
                "ownership ledger update failed",
                f"{error}; rollback failed: {rollback_error}",
            ) from rollback_error
        raise AgentSkillError(
            Operation.PRUNE,
            lockfile,
            "ownership ledger update failed",
            str(error),
        ) from error
    mutation.commit()
    return Report(
        Operation.PRUNE,
        Result.CHANGED,
        lockfile,
        entries,
        planned_changes=len(candidates),
    )


def main(argv: Sequence[str] | None = None, *, runtime: Runtime | None = None) -> int:
    """Parse arguments and delegate command execution to the CLI-policy module."""
    runtime = default_runtime() if runtime is None else runtime
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser_diagnostics = io.StringIO()

    try:
        with redirect_stdout(runtime.stdout), redirect_stderr(parser_diagnostics):
            args = cli.parse_args(arguments)
    except SystemExit as error:
        exit_code = 0 if error.code is None else int(error.code)
        if exit_code == 0:
            return 0
        return usage_failure(
            arguments,
            parser_diagnostics.getvalue(),
            DEFAULT_LOCKFILE,
            runtime,
            error,
        )

    if args.command is None:
        cli.print_help(file=runtime.stdout)
        return 0

    args.runtime = runtime
    return execute(args.func, args, runtime)


if __name__ == "__main__":
    raise SystemExit(main())
