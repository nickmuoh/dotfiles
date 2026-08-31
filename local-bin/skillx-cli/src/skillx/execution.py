from __future__ import annotations

import json
import traceback
from argparse import Namespace
from collections.abc import Callable, Sequence
from typing import TextIO

from .adapters import Runtime
from .models import Operation, Report, Result
from .reconcile import ConfigurationError

CommandHandler = Callable[[Namespace], Report]


class AgentSkillError(RuntimeError):
    """An operational failure enriched with the command that encountered it."""

    def __init__(
        self,
        operation: Operation,
        lockfile: str,
        message: str,
        diagnostics: str = "",
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.lockfile = lockfile
        self.diagnostics = diagnostics


def execute(handler: CommandHandler, args: Namespace, runtime: Runtime) -> int:
    """Run one command and apply the CLI failure and output policy."""
    try:
        report = handler(args)
    except AgentSkillError as error:
        report = Report(error.operation, Result.FAILED, error.lockfile, ())
        _write_error(error, runtime.stderr, args.verbose)
    except (ConfigurationError, OSError) as error:
        contextual = AgentSkillError(
            Operation(args.command), args.lockfile, str(error)
        ).with_traceback(error.__traceback__)
        report = Report(contextual.operation, Result.FAILED, contextual.lockfile, ())
        _write_error(contextual, runtime.stderr, args.verbose)

    return emit(report, runtime, args.json_output, args.verbose)


def usage_failure(
    arguments: Sequence[str],
    diagnostics: str,
    default_lockfile: str,
    runtime: Runtime,
    cause: BaseException | None = None,
) -> int:
    """Render an argument-parsing failure through the normal CLI policy."""
    error = AgentSkillError(
        _operation_from(arguments),
        _option_value(arguments, "--lockfile") or default_lockfile,
        "invalid command usage",
        diagnostics,
    )
    if cause is not None:
        error = error.with_traceback(cause.__traceback__)
    report = Report(error.operation, Result.FAILED, error.lockfile, ())
    verbosity = _verbosity_from(arguments)
    _write_error(error, runtime.stderr, verbosity)
    return emit(report, runtime, "--json" in arguments, verbosity)


def emit(report: Report, runtime: Runtime, json_output: bool, verbosity: int) -> int:
    """Write a report while keeping diagnostics separate from report data."""
    if verbosity:
        _write_report_diagnostics(report, runtime.stderr)
    if json_output:
        json.dump(report.to_dict(), runtime.stdout, sort_keys=True)
        runtime.stdout.write("\n")
    else:
        _write_text_report(report, runtime.stdout)
    return report.exit_code


def _write_error(error: AgentSkillError, stream: TextIO, verbosity: int) -> None:
    if verbosity < 1:
        return
    stream.write(f"skillx: {error}\n")
    if error.diagnostics:
        stream.write(error.diagnostics.rstrip() + "\n")
    if verbosity > 1:
        traceback.print_exception(error, file=stream)


def _write_report_diagnostics(report: Report, stream: TextIO) -> None:
    for entry in report.entries:
        if not entry.diagnostic:
            continue
        stream.write(f"{entry.source} -> {entry.skill}:\n")
        stream.writelines(f"  {line}\n" for line in entry.diagnostic.splitlines())


def _write_text_report(report: Report, stream: TextIO) -> None:
    for entry in report.entries:
        stream.write(f"{entry.status:44} {entry.source} -> {entry.skill}\n")
        if entry.message:
            stream.write(f"  {entry.message}\n")
    stream.write(f"Result: {report.result}; {report.planned_changes} change(s)\n")


def _operation_from(arguments: Sequence[str]) -> Operation:
    try:
        return Operation(arguments[0])
    except (IndexError, ValueError):
        return Operation.UNKNOWN


def _option_value(arguments: Sequence[str], option: str) -> str | None:
    for index, argument in enumerate(arguments):
        if argument == option and index + 1 < len(arguments):
            return arguments[index + 1]
        if argument.startswith(f"{option}="):
            return argument.partition("=")[2]
    return None


def _verbosity_from(arguments: Sequence[str]) -> int:
    return sum(
        1 if argument in {"-v", "--verbose"} else len(argument) - 1
        for argument in arguments
        if argument in {"-v", "--verbose"}
        or (argument.startswith("-") and set(argument[1:]) == {"v"})
    )
