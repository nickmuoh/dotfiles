from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TextIO

from .models import (
    EventAction,
    EventKind,
    Entry,
    ExecutionEvent,
    FailureState,
    Operation,
    Report,
    Result,
    Status,
)

BLUE_BOLD = "\x1b[1;34m"
DIM = "\x1b[2m"
RESET = "\x1b[0m"
ERASE_LINE = "\x1b[2K"
COMPACT_SKILLS_PER_SOURCE = 4
EMOJI = {
    EventAction.AUDIT: "🔍",
    EventAction.BATCH: "📦",
    EventAction.FETCH: "⬇️",
    EventAction.FILE: "📝",
    EventAction.LINK: "🔗",
    EventAction.BLOCKED: "🛑",
    EventAction.FAILED: "❌",
}


def phase(stream: TextIO, message: str, *, interactive: bool) -> None:
    """Render a phase header without making non-TTY logs depend on ANSI."""
    prefix = f"{BLUE_BOLD}==>{RESET}" if interactive else "==>"
    stream.write(f"{prefix} {message}\n")


def progress_line(
    stream: TextIO,
    current: int,
    total: int,
    message: str,
    *,
    interactive: bool,
) -> None:
    """Render one progress position, in place only for an interactive TTY."""
    line = f"[{current}/{total}] {message}"
    if interactive:
        stream.write(f"\r{ERASE_LINE}{DIM}{line}{RESET}")
        stream.flush()
    else:
        stream.write(line + "\n")


def skill_reference(source: str, skill: str) -> str:
    """Render a source-qualified skill without shell-redirection syntax."""
    return f"{source}: {skill}"


class Renderer:
    """Consume execution facts and present either human output or one JSON report."""

    def __init__(self, stdout: TextIO, stderr: TextIO, *, verbosity: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.verbosity = verbosity
        self.interactive = _is_tty(stdout)
        self.progress_open = False

    def render(self, events: Iterable[ExecutionEvent], *, json_output: bool) -> int:
        report: Report | None = None
        for event in events:
            if json_output:
                if event.kind is EventKind.FAILED:
                    self._diagnose_failure(event)
                if event.kind is EventKind.COMPLETE and event.report is not None:
                    report = event.report
                    if self.verbosity:
                        self._diagnose_report(report)
                continue

            self._render_human(event)
            if event.kind is EventKind.COMPLETE:
                report = event.report

        if report is None:
            report = Report(Operation.UNKNOWN, Result.FAILED, "", ())
        if json_output:
            json.dump(report.to_dict(), self.stdout, sort_keys=True)
            self.stdout.write("\n")
        return report.exit_code

    def _render_human(self, event: ExecutionEvent) -> None:
        if event.kind is EventKind.PHASE:
            self._finish_progress()
            phase(self.stdout, self._message(event), interactive=self.interactive)
        elif event.kind is EventKind.PROGRESS:
            progress_line(
                self.stdout,
                event.current or 0,
                event.total or 0,
                self._message(event),
                interactive=self.interactive,
            )
            self.progress_open = self.interactive
        elif event.kind is EventKind.MUTATION or event.kind is EventKind.BLOCKED:
            self._finish_progress()
            self._line(self._message(event))
        elif event.kind is EventKind.FAILED:
            self._finish_progress()
            self._line(self._message(event))
            self._diagnose_failure(event)
        elif event.kind is EventKind.COMPLETE and event.report is not None:
            self._finish_progress()
            self._findings(event.report)
            self._summary(event.report)
            if self.verbosity:
                self._diagnose_report(event.report)

    def _message(self, event: ExecutionEvent) -> str:
        emoji = EMOJI.get(event.action) if event.action is not None else None
        if emoji is None and event.kind is EventKind.FAILED:
            emoji = "❌"
        return f"{emoji} {event.message}" if emoji else event.message

    def _summary(self, report: Report) -> None:
        planned = report.planned_changes
        if report.result is Result.FAILED:
            if report.failure_state is FailureState.ROLLED_BACK:
                self._line("Changes were rolled back safely.")
            elif report.failure_state is FailureState.RECOVERY_REQUIRED:
                self._line(
                    "Rollback failed, so manual recovery may be needed."
                )
            else:
                self._line("No changes were made.")
            return
        if report.result is Result.DRIFT:
            unavailable = sum(
                entry.status is not Status.VALID for entry in report.entries
            )
            noun = "skill is" if unavailable == 1 else "skills are"
            self._line(
                f"⚠ Check completed: {unavailable} requested {noun} unavailable."
            )
            return
        if report.result is Result.BLOCKED:
            return
        if report.result is Result.PLANNED:
            if report.dry_run:
                self._line(
                    f"✨ Dry run complete. {planned} change(s) planned; nothing was changed."
                )
            else:
                self._line(
                    f"✨ Plan ready; {planned} change(s) require confirmation; nothing was changed."
                )
            return
        if report.operation is Operation.CHECK and report.result is Result.OK:
            self._line(
                f"✨ All {len(report.entries)} requested skills are available from their sources."
            )
            return
        if report.operation is Operation.SYNC and report.result is Result.OK:
            self._line("✨ No requested skills; nothing changed.")
            return
        if report.operation is Operation.REPAIR and report.result is Result.OK:
            self._line("✨ No confirmed-invalid lock entries; lockfile unchanged.")
            return
        if report.operation is Operation.ADOPT and report.result is Result.OK:
            self._line("✨ No requested skills to adopt; ownership ledger unchanged.")
            return
        if report.operation is Operation.PRUNE and report.result is Result.OK:
            self._line("✨ No managed skills require pruning; ownership ledger unchanged.")
            return
        if report.result is Result.OK:
            self._line("✨ No changes needed.")
            return

        action = {
            Operation.SYNC: "Reconciled",
            Operation.REPAIR: "Repaired",
            Operation.ADOPT: "Adopted",
            Operation.PRUNE: "Pruned",
        }.get(report.operation, "Completed")
        noun = "skill" if planned == 1 else "skills"
        self._line(f"🎉 {action} {planned} {noun}.")

    def _findings(self, report: Report) -> None:
        """Show actionable drift without turning successful checks into a listing."""
        if report.result in {Result.BLOCKED, Result.DRIFT}:
            findings = tuple(
                entry for entry in report.entries if entry.status is not Status.VALID
            )
        elif report.operation is Operation.REPAIR:
            findings = tuple(
                entry
                for entry in report.entries
                if entry.status
                in {
                    Status.CONFIRMED_MISSING_SOURCE,
                    Status.CONFIRMED_MISSING_SKILL,
                    Status.CONFIRMED_INVALID_SOURCE,
                }
            )
        elif report.operation is Operation.PRUNE:
            findings = tuple(
                entry for entry in report.entries if entry.status is Status.PRUNABLE
            )
        elif report.operation is Operation.ADOPT:
            findings = report.entries
        elif report.operation is Operation.SYNC and report.result is Result.PLANNED:
            findings = report.entries
        else:
            return
        if not findings:
            return

        if report.result is Result.BLOCKED:
            heading = "Unresolved skills:"
        elif report.result is Result.DRIFT:
            heading = "Unavailable skills:"
        elif report.operation is Operation.ADOPT:
            heading = (
                "Ownership records written:"
                if report.result is Result.CHANGED
                else "Planned ownership records:"
            )
        elif report.operation is Operation.SYNC:
            heading = "Planned installations:"
        else:
            heading = (
                "Applied changes:"
                if report.result is Result.CHANGED
                else "Planned changes:"
            )
        self._line(heading)
        if report.operation is Operation.SYNC and report.result is Result.PLANNED:
            self._sync_plan(findings)
        else:
            for entry in findings:
                marker = "✓" if report.operation is Operation.ADOPT else "✗"
                self._line(f"  {marker} {skill_reference(entry.source, entry.skill)}")
                self._line(f"    {entry.message}")

        if report.result in {Result.BLOCKED, Result.DRIFT}:
            self._next_step_for_blocked(findings)
        elif report.operation is Operation.REPAIR and report.result is Result.PLANNED:
            if report.dry_run and report.confirmation_requested:
                self._line(
                    "Next: `--dry-run` overrode `--yes`; rerun without `--dry-run` to apply this plan."
                )
            else:
                self._line(
                    f"Next: run `{report.confirmation_command}` to back up the lockfile and apply this plan."
                )
        elif report.operation is Operation.PRUNE and report.result is Result.PLANNED:
            if report.dry_run and report.confirmation_requested:
                self._line(
                    "Next: `--dry-run` overrode `--yes`; rerun without `--dry-run` to apply this plan."
                )
            else:
                self._line(
                    f"Next: run `{report.confirmation_command}` to apply this plan."
                )
        elif report.operation is Operation.ADOPT and report.result is Result.PLANNED:
            if report.dry_run and report.confirmation_requested:
                self._line(
                    "Next: `--dry-run` overrode `--yes`; rerun without `--dry-run` to write these records."
                )
            else:
                self._line(
                    f"Next: run `{report.confirmation_command}` to write these records."
                )

        if report.operation is Operation.REPAIR and report.result is Result.CHANGED:
            remaining = tuple(
                entry
                for entry in report.entries
                if entry.status is Status.INDETERMINATE
            )
            if remaining:
                self._line("Still unresolved:")
                for entry in remaining:
                    self._line(
                        f"  ✗ {skill_reference(entry.source, entry.skill)}"
                    )
                    self._line(f"    {entry.message}")
                self._line(
                    "Next: retry when source access is available; indeterminate entries are preserved."
                )

    def _sync_plan(self, entries: tuple[Entry, ...]) -> None:
        """Render dry-run installations as compact, source-grouped rows."""
        skills_by_source: dict[str, list[str]] = {}
        for entry in entries:
            skills_by_source.setdefault(entry.source, []).append(entry.skill)

        for source, skills in skills_by_source.items():
            visible = skills if self.verbosity else skills[:COMPACT_SKILLS_PER_SOURCE]
            suffix = ""
            remaining = len(skills) - len(visible)
            if remaining:
                suffix = f" … (+{remaining} more)"
            self._line(f"  📦 {source}: {', '.join(visible)}{suffix}")

    def _next_step_for_blocked(self, findings: tuple[Entry, ...]) -> None:
        statuses = {entry.status for entry in findings}
        indeterminate = Status.INDETERMINATE in statuses
        repairable = bool(
            statuses
            & {
                Status.CONFIRMED_MISSING_SOURCE,
                Status.CONFIRMED_MISSING_SKILL,
                Status.CONFIRMED_INVALID_SOURCE,
            }
        )
        if repairable and indeterminate:
            self._line(
                "Next: `skillx repair` previews removal of confirmed-invalid entries; retry or fix access for the others."
            )
        elif repairable:
            self._line(
                "Next: `skillx repair` previews removal of these confirmed-invalid lock entries."
            )
        elif indeterminate:
            self._line(
                "Next: retry when source access is available; indeterminate entries are preserved."
            )
        elif Status.AMBIGUOUS_OWNERSHIP in statuses:
            self._line(
                "Next: review the ownership ledger and installed skill metadata; nothing was removed."
            )

    def _finish_progress(self) -> None:
        if self.progress_open:
            self.stdout.write("\n")
            self.progress_open = False

    def _line(self, message: str) -> None:
        self.stdout.write(message + "\n")

    def _diagnose_failure(self, event: ExecutionEvent) -> None:
        if self.verbosity < 1:
            return
        self.stderr.write(f"skillx: {event.message}\n")
        if event.diagnostic:
            self.stderr.write(event.diagnostic.rstrip() + "\n")
        if self.verbosity > 1 and event.debug:
            self.stderr.write(event.debug)

    def _diagnose_report(self, report: Report) -> None:
        for entry in report.entries:
            if not entry.diagnostic:
                continue
            self.stderr.write(f"{skill_reference(entry.source, entry.skill)}:\n")
            self.stderr.writelines(
                f"  {line}\n" for line in entry.diagnostic.splitlines()
            )


def _is_tty(stream: TextIO) -> bool:
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())
