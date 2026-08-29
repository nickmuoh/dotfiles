from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TextIO, cast

from .adapters import InstallRequest, Runtime, default_runtime
from .cli import ArgumentParser
from .models import Entry, Operation, Report, Result
from .reconcile import (
    ConfigurationError,
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
        cli.argument("--verbose", action="store_true"),
    ]
    if ledger:
        arguments.insert(1, cli.argument("--ledger", default=DEFAULT_LEDGER))
    if dry_run:
        arguments.append(cli.argument("--dry-run", action="store_true"))
    if yes:
        arguments.append(cli.argument("--yes", action="store_true"))
    return tuple(arguments)


def _emit_diagnostics(report: Report, stream: TextIO) -> None:
    for entry in report.entries:
        if not entry.diagnostic:
            continue
        stream.write(f"{entry.source} -> {entry.skill}:\n")
        stream.writelines(f"  {line}\n" for line in entry.diagnostic.splitlines())


def _emit_json(report: Report, stream: TextIO) -> None:
    json.dump(report.to_dict(), stream, sort_keys=True)
    stream.write("\n")


def _emit_text(report: Report, stream: TextIO) -> None:
    for entry in report.entries:
        stream.write(f"{entry.status:44} {entry.source} -> {entry.skill}\n")
        if entry.message:
            stream.write(f"  {entry.message}\n")
    stream.write(f"Result: {report.result}; {report.planned_changes} change(s)\n")


def _emit(report: Report, runtime: Runtime, json_output: bool, verbose: bool) -> int:
    if verbose:
        _emit_diagnostics(report, runtime.stderr)
    if json_output:
        _emit_json(report, runtime.stdout)
        return report.exit_code
    stream = (
        runtime.stderr if report.result in {"blocked", "failed"} else runtime.stdout
    )
    _emit_text(report, stream)
    return report.exit_code


def _failure(
    operation: Operation,
    lockfile: str,
    message: str,
    runtime: Runtime,
    json_output: bool,
    verbose: bool,
) -> int:
    runtime.stderr.write(f"skillx: {message}\n")
    return _emit(
        Report(operation, "failed", lockfile, ()), runtime, json_output, verbose
    )


def _validated(
    operation: Operation, lockfile: str, runtime: Runtime
) -> tuple[str, Report] | str:
    try:
        content = runtime.filesystem.read_text(lockfile)
        return content, validate(lockfile, content, runtime.npx, operation)
    except (ConfigurationError, FileNotFoundError, OSError) as error:
        return str(error)


@cli.command(
    *_common_args(),
    help="validate desired and remote state without mutation",
)
def check(
    lockfile: str,
    json_output: bool,
    verbose: bool,
    runtime: Runtime,
    **meta_args,
) -> int:
    """Report source and skill classifications without changing state."""
    del meta_args
    validated = _validated("check", lockfile, runtime)
    if isinstance(validated, str):
        return _failure("check", lockfile, validated, runtime, json_output, verbose)
    _, report = validated
    return _emit(report, runtime, json_output, verbose)


@cli.command(
    *_common_args(dry_run=True),
    cli.argument("--agent", action="extend", nargs="+", default=[]),
    help="validate and install or update desired skills",
)
def sync(
    lockfile: str,
    json_output: bool,
    verbose: bool,
    dry_run: bool,
    agent: list[str],
    runtime: Runtime,
    **meta_args,
) -> int:
    """Converge installed skills only after every desired entry validates."""
    del meta_args
    validated = _validated("sync", lockfile, runtime)
    if isinstance(validated, str):
        return _failure("sync", lockfile, validated, runtime, json_output, verbose)
    _, report = validated
    if report.result != "ok":
        return _emit(report, runtime, json_output, verbose)
    synced = Report(
        "sync",
        "planned" if dry_run else "changed",
        lockfile,
        report.entries,
        planned_changes=len(report.entries),
    )
    if not dry_run:
        skills_by_source: dict[str, list[str]] = {}
        for entry in report.entries:
            skills_by_source.setdefault(entry.source, []).append(entry.skill)
        requests = tuple(
            InstallRequest(source, tuple(skills), tuple(agent))
            for source, skills in skills_by_source.items()
        )
        try:
            mutation = runtime.npx.install_transaction(requests)
        except OSError as error:
            return _failure("sync", lockfile, str(error), runtime, json_output, verbose)
        if mutation.result.returncode != 0:
            diagnostic = (
                mutation.result.stderr.strip() or mutation.result.stdout.strip()
            )
            try:
                mutation.rollback()
            except OSError as rollback_error:
                diagnostic = f"{diagnostic}; {rollback_error}"
            return _failure(
                "sync",
                lockfile,
                f"install failed: {diagnostic}",
                runtime,
                json_output,
                verbose,
            )
        mutation.commit()
    return _emit(synced, runtime, json_output, verbose)


@cli.command(
    *_common_args(dry_run=True, yes=True),
    help="remove confirmed-invalid desired entries",
)
def repair(
    lockfile: str,
    json_output: bool,
    verbose: bool,
    dry_run: bool,
    yes: bool,
    runtime: Runtime,
    **meta_args,
) -> int:
    """Back up and repair only entries proven invalid by enumeration."""
    del meta_args
    validated = _validated("repair", lockfile, runtime)
    if isinstance(validated, str):
        return _failure("repair", lockfile, validated, runtime, json_output, verbose)
    content, report = validated
    repairable = {
        entry.skill
        for entry in report.entries
        if entry.status
        in {
            "confirmed-missing-source",
            "confirmed-missing-skill",
            "confirmed-invalid-source/no-valid-skills",
        }
    }
    if not repairable:
        return _emit(report, runtime, json_output, verbose)
    result: Result = "planned"
    if yes and not dry_run:
        try:
            runtime.filesystem.copy(lockfile, f"{lockfile}.{runtime.now()}.bak")
            runtime.filesystem.write_atomic(
                lockfile, repaired_lockfile(content, repairable)
            )
        except OSError as error:
            return _failure(
                "repair", lockfile, str(error), runtime, json_output, verbose
            )
        result = "changed"
    repaired = Report(
        "repair",
        result,
        lockfile,
        report.entries,
        planned_changes=len(repairable),
    )
    return _emit(repaired, runtime, json_output, verbose)


@cli.command(
    cli.argument("--from-lock", action="store_true", required=True),
    *_common_args(ledger=True, dry_run=True, yes=True),
    help="explicitly transfer custody of installed desired skills",
)
def adopt(
    from_lock: bool,
    lockfile: str,
    ledger: str,
    json_output: bool,
    verbose: bool,
    dry_run: bool,
    yes: bool,
    runtime: Runtime,
    **meta_args,
) -> int:
    """Validate and record exact-path ownership for existing installations."""
    del from_lock, meta_args
    validated = _validated("adopt", lockfile, runtime)

    if isinstance(validated, str):
        return _failure("adopt", lockfile, validated, runtime, json_output, verbose)
    content, report = validated

    if report.result != "ok":
        return _emit(report, runtime, json_output, verbose)
    inventory_result = runtime.npx.inventory()
    if inventory_result.returncode != 0:
        diagnostic = inventory_result.stderr.strip() or inventory_result.stdout.strip()
        return _failure(
            "adopt",
            lockfile,
            f"inventory failed: {diagnostic}",
            runtime,
            json_output,
            verbose,
        )
    try:
        inventory = parse_inventory(inventory_result.stdout)
    except ConfigurationError as error:
        return _failure("adopt", lockfile, str(error), runtime, json_output, verbose)
    try:
        ledger_content = adoption_ledger(parse_lockfile(content), inventory)
    except ConfigurationError as error:
        runtime.stderr.write(f"skillx: {error}\n")
        refusal = Entry("", "", "ambiguous-ownership", str(error))
        return _emit(
            Report("adopt", "blocked", lockfile, (refusal,)),
            runtime,
            json_output,
            verbose,
        )
    result: Result = "planned"
    if yes and not dry_run:
        try:
            runtime.filesystem.write_atomic(ledger, ledger_content)
        except OSError as error:
            return _failure(
                "adopt", lockfile, str(error), runtime, json_output, verbose
            )
        result = "changed"
    adopted = Report(
        "adopt", result, lockfile, report.entries, planned_changes=len(report.entries)
    )
    return _emit(adopted, runtime, json_output, verbose)


@cli.command(
    *_common_args(ledger=True, dry_run=True, yes=True),
    help="remove unambiguously owned skills absent from desired state",
)
def prune(
    lockfile: str,
    ledger: str,
    json_output: bool,
    verbose: bool,
    dry_run: bool,
    yes: bool,
    runtime: Runtime,
    **meta_args,
) -> int:
    """Remove only exact-path ledger entries absent from desired state."""
    del meta_args
    try:
        desired = parse_lockfile(runtime.filesystem.read_text(lockfile))
        managed = parse_ledger(runtime.filesystem.read_text(ledger))
    except (ConfigurationError, FileNotFoundError, OSError) as error:
        return _failure("prune", lockfile, str(error), runtime, json_output, verbose)

    inventory_result = runtime.npx.inventory()
    if inventory_result.returncode != 0:
        diagnostic = inventory_result.stderr.strip() or inventory_result.stdout.strip()
        return _failure(
            "prune",
            lockfile,
            f"inventory failed: {diagnostic}",
            runtime,
            json_output,
            verbose,
        )
    try:
        inventory = parse_inventory(inventory_result.stdout)
        candidates = prune_candidates(desired, managed, inventory)
    except OwnershipError as error:
        runtime.stderr.write(f"skillx: {error}\n")
        return _emit(
            Report("prune", "blocked", lockfile, error.refusals),
            runtime,
            json_output,
            verbose,
        )
    except ConfigurationError as error:
        return _failure("prune", lockfile, str(error), runtime, json_output, verbose)
    entries = tuple(
        Entry(
            record.skill,
            record.source,
            "prunable",
            f"managed installation at {record.path} is absent from desired state",
        )
        for record in candidates
    )
    result: Result = "ok" if not candidates else "planned"
    if candidates and yes and not dry_run:
        try:
            mutation = runtime.npx.remove_transaction(
                tuple(record.skill for record in candidates)
            )
        except OSError as error:
            return _failure(
                "prune", lockfile, str(error), runtime, json_output, verbose
            )
        if mutation.result.returncode != 0:
            diagnostic = (
                mutation.result.stderr.strip() or mutation.result.stdout.strip()
            )
            try:
                mutation.rollback()
            except OSError as rollback_error:
                diagnostic = f"{diagnostic}; {rollback_error}"
            return _failure(
                "prune",
                lockfile,
                f"removal failed: {diagnostic}",
                runtime,
                json_output,
                verbose,
            )
        try:
            runtime.filesystem.write_atomic(ledger, ledger_without(managed, candidates))
        except OSError as error:
            message = str(error)
            try:
                mutation.rollback()
            except OSError as rollback_error:
                message = f"{message}; {rollback_error}"
            return _failure("prune", lockfile, message, runtime, json_output, verbose)
        mutation.commit()
        result = "changed"
    pruned = Report("prune", result, lockfile, entries, planned_changes=len(candidates))
    return _emit(pruned, runtime, json_output, verbose)


def main(argv: Sequence[str] | None = None, *, runtime: Runtime | None = None) -> int:
    runtime = default_runtime() if runtime is None else runtime
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        with redirect_stdout(runtime.stdout), redirect_stderr(runtime.stderr):
            args = cli.parse_args(arguments)
    except SystemExit as error:
        exit_code = 0 if error.code is None else int(error.code)
        if exit_code != 0 and "--json" in arguments:
            operation = (
                arguments[0]
                if arguments
                and arguments[0]
                in {
                    "check",
                    "sync",
                    "repair",
                    "adopt",
                    "prune",
                }
                else "unknown"
            )
            lockfile = DEFAULT_LOCKFILE
            for index, argument in enumerate(arguments):
                if argument == "--lockfile" and index + 1 < len(arguments):
                    lockfile = arguments[index + 1]
                elif argument.startswith("--lockfile="):
                    lockfile = argument.partition("=")[2]
            _emit(
                Report(cast(Operation, operation), "failed", lockfile, ()),
                runtime,
                True,
                "--verbose" in arguments,
            )
        return exit_code
    if args.command is None:
        cli.print_help(file=runtime.stdout)
        return 0
    args.runtime = runtime
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
