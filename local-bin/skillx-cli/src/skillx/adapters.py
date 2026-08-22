from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Mapping, Protocol, TextIO


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    classification: Literal["confirmed-missing-source"] | None = None


@dataclass(frozen=True)
class InstallRequest:
    source: str
    skills: tuple[str, ...]
    agents: tuple[str, ...]


class Mutation:
    def __init__(
        self,
        result: CommandResult,
        *,
        commit: Callable[[], None] | None = None,
        rollback: Callable[[], None] | None = None,
    ) -> None:
        self.result = result
        self._commit = commit or (lambda: None)
        self._rollback = rollback or (lambda: None)
        self._finished = False

    def commit(self) -> None:
        if not self._finished:
            self._commit()
            self._finished = True

    def rollback(self) -> None:
        if not self._finished:
            self._rollback()
            self._finished = True


class Filesystem(Protocol):
    def read_text(self, path: str) -> str: ...

    def write_atomic(self, path: str, content: str) -> None: ...

    def copy(self, source: str, destination: str) -> None: ...


class Npx(Protocol):
    def inventory(self) -> CommandResult: ...

    def enumerate_source(self, source: str) -> CommandResult: ...

    def install_transaction(self, requests: tuple[InstallRequest, ...]) -> Mutation: ...

    def remove_transaction(self, skills: tuple[str, ...]) -> Mutation: ...


@dataclass
class Runtime:
    filesystem: Filesystem
    npx: Npx
    now: Callable[[], str]
    stdout: TextIO = field(default_factory=io.StringIO)
    stderr: TextIO = field(default_factory=io.StringIO)


class LocalFilesystem:
    def read_text(self, path: str) -> str:
        return Path(path).expanduser().read_text(encoding="utf-8")

    def write_atomic(self, path: str, content: str) -> None:
        target = Path(path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=target.parent,
                prefix=f".{target.name}.",
                delete=False,
            ) as temporary:
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = temporary.name
            os.replace(temporary_path, target)
            temporary_path = None
        finally:
            if temporary_path is not None:
                Path(temporary_path).unlink(missing_ok=True)

    def copy(self, source: str, destination: str) -> None:
        shutil.copy2(Path(source).expanduser(), Path(destination).expanduser())


class SubprocessNpx:
    def __init__(self, *, environment: Mapping[str, str] | None = None) -> None:
        self.environment = dict(os.environ if environment is None else environment)

    def _run(
        self,
        arguments: list[str],
        *,
        environment: Mapping[str, str] | None = None,
        timeout: int = 120,
    ) -> CommandResult:
        try:
            completed = subprocess.run(
                arguments,
                check=False,
                capture_output=True,
                text=True,
                env=dict(self.environment if environment is None else environment),
                timeout=timeout,
            )
        except FileNotFoundError as error:
            return CommandResult(127, "", str(error))
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout if isinstance(error.stdout, str) else ""
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            return CommandResult(124, stdout, stderr or f"command timed out after {timeout}s")
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)

    def inventory(self) -> CommandResult:
        return self._run(["npx", "skills", "ls", "-g", "--json"])

    def enumerate_source(self, source: str) -> CommandResult:
        with tempfile.TemporaryDirectory(prefix="skillx-validation-") as temporary_home:
            environment = dict(self.environment)
            environment.update(
                {
                    "HOME": temporary_home,
                    "XDG_CONFIG_HOME": f"{temporary_home}/.config",
                    "XDG_CACHE_HOME": f"{temporary_home}/.cache",
                    "npm_config_cache": f"{temporary_home}/.npm",
                    "NO_COLOR": "1",
                    "CI": "1",
                }
            )
            return self._run(
                ["npx", "skills", "add", source, "--list"], environment=environment
            )

    @staticmethod
    def _install_arguments(request: InstallRequest) -> list[str]:
        source, skills, agents = request.source, request.skills, request.agents
        arguments = ["npx", "skills", "add", source, "-g", "-y"]
        if agents:
            arguments.extend(["--agent", *agents])
        arguments.extend(["--skill", *skills])
        return arguments

    @staticmethod
    def _sanitize_name(name: str) -> str:
        sanitized = re.sub(r"[^a-z0-9._]+", "-", name.lower())
        sanitized = re.sub(r"^[.\-]+|[.\-]+$", "", sanitized)
        return sanitized[:255] or "unnamed-skill"

    def _snapshot(self, skills: tuple[str, ...]) -> tuple[tempfile.TemporaryDirectory[str], dict[str, Path | None], Path | None]:
        temporary = tempfile.TemporaryDirectory(prefix="skillx-rollback-")
        snapshot_root = Path(temporary.name)
        home = Path(self.environment.get("HOME", str(Path.home()))).expanduser()
        snapshots: dict[str, Path | None] = {}
        for skill in skills:
            live_path = home / ".agents" / "skills" / self._sanitize_name(skill)
            if not live_path.exists() and not live_path.is_symlink():
                snapshots[skill] = None
                continue
            backup = snapshot_root / "skills" / self._sanitize_name(skill)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if live_path.is_symlink():
                backup.symlink_to(os.readlink(live_path))
            else:
                shutil.copytree(live_path, backup, symlinks=True)
            snapshots[skill] = backup
        live_lock = home / ".agents" / ".skill-lock.json"
        lock_backup: Path | None = None
        if live_lock.exists():
            lock_backup = snapshot_root / ".skill-lock.json"
            shutil.copy2(live_lock, lock_backup)
        return temporary, snapshots, lock_backup

    def _restore(
        self,
        skills: tuple[str, ...],
        snapshots: dict[str, Path | None],
        lock_backup: Path | None,
    ) -> None:
        if skills:
            removed = self._run(["npx", "skills", "remove", *skills, "-g", "-y"])
            if removed.returncode != 0:
                raise OSError(
                    "rollback cleanup failed: "
                    + (removed.stderr.strip() or removed.stdout.strip())
                )
        for skill, backup in snapshots.items():
            if backup is None:
                continue
            restored = self._run(
                ["npx", "skills", "add", str(backup), "-g", "-y", "--skill", skill]
            )
            if restored.returncode != 0:
                raise OSError(
                    f"rollback restore failed for {skill}: "
                    + (restored.stderr.strip() or restored.stdout.strip())
                )
        home = Path(self.environment.get("HOME", str(Path.home()))).expanduser()
        live_lock = home / ".agents" / ".skill-lock.json"
        if lock_backup is None:
            live_lock.unlink(missing_ok=True)
        else:
            live_lock.parent.mkdir(parents=True, exist_ok=True)
            temporary_lock = live_lock.with_name(f".{live_lock.name}.skillx-rollback")
            shutil.copy2(lock_backup, temporary_lock)
            os.replace(temporary_lock, live_lock)

    def install_transaction(self, requests: tuple[InstallRequest, ...]) -> Mutation:
        all_skills = tuple(skill for request in requests for skill in request.skills)
        with tempfile.TemporaryDirectory(prefix="skillx-install-stage-") as staging_root:
            for index, request in enumerate(requests):
                staging_home = Path(staging_root) / str(index)
                staging_home.mkdir()
                environment = dict(self.environment)
                environment.update(
                    {
                        "HOME": str(staging_home),
                        "XDG_CONFIG_HOME": str(staging_home / ".config"),
                        "XDG_CACHE_HOME": str(staging_home / ".cache"),
                        "npm_config_cache": str(staging_home / ".npm"),
                        "NO_COLOR": "1",
                        "CI": "1",
                    }
                )
                staged = self._run(self._install_arguments(request), environment=environment)
                if staged.returncode != 0:
                    return Mutation(staged)

        temporary, snapshots, lock_backup = self._snapshot(all_skills)
        result = CommandResult(0, "", "")
        for request in requests:
            result = self._run(self._install_arguments(request))
            if result.returncode != 0:
                break

        def rollback() -> None:
            self._restore(all_skills, snapshots, lock_backup)
            temporary.cleanup()

        return Mutation(
            result,
            commit=temporary.cleanup,
            rollback=rollback,
        )

    def remove_transaction(self, skills: tuple[str, ...]) -> Mutation:
        temporary, snapshots, lock_backup = self._snapshot(skills)
        result = self._run(["npx", "skills", "remove", *skills, "-g", "-y"])

        def rollback() -> None:
            self._restore(skills, snapshots, lock_backup)
            temporary.cleanup()

        return Mutation(
            result,
            commit=temporary.cleanup,
            rollback=rollback,
        )


def default_runtime() -> Runtime:
    return Runtime(
        filesystem=LocalFilesystem(),
        npx=SubprocessNpx(),
        now=lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
