from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TextIO

from .models import EventAction, EventKind, ExecutionEvent, Operation, Report, Result

BLUE_BOLD = "\x1b[1;34m"
DIM = "\x1b[2m"
RESET = "\x1b[0m"
ERASE_LINE = "\x1b[2K"
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
            self._line("Result: FAILED; 0 change(s).")
            return
        if report.result is Result.BLOCKED:
            self._line(f"Result: BLOCKED; {planned} change(s).")
            return
        if report.result is Result.PLANNED:
            self._line(
                f"✨ Dry run complete. {planned} change(s) planned; nothing was changed."
            )
            self._line(f"Result: PLANNED; {planned} change(s).")
            return
        if report.operation is Operation.CHECK and report.result is Result.OK:
            self._line(
                f"✨ All {len(report.entries)} requested skills are valid and up-to-date."
            )
            self._line("Result: OK; 0 change(s) needed.")
            return
        if report.result is Result.OK:
            self._line("✨ No changes needed.")
            self._line("Result: OK; 0 change(s).")
            return

        action = {
            Operation.SYNC: "Reconciled",
            Operation.REPAIR: "Repaired",
            Operation.ADOPT: "Adopted",
            Operation.PRUNE: "Pruned",
        }.get(report.operation, "Completed")
        self._line(f"🎉 {action} {planned} skills. (0 errors)")
        self._line(f"Result: CHANGED; {planned} change(s).")

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
            self.stderr.write(f"{entry.source} -> {entry.skill}:\n")
            self.stderr.writelines(
                f"  {line}\n" for line in entry.diagnostic.splitlines()
            )


def _is_tty(stream: TextIO) -> bool:
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())
