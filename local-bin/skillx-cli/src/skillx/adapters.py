from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Protocol, TextIO


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class Filesystem(Protocol):
    def read_text(self, path: str) -> str: ...

    def write_atomic(self, path: str, content: str) -> None: ...

    def copy(self, source: str, destination: str) -> None: ...


class Npx(Protocol):
    def inventory(self) -> CommandResult: ...

    def enumerate_source(self, source: str) -> CommandResult: ...

    def install(
        self, source: str, skills: tuple[str, ...], agents: tuple[str, ...]
    ) -> CommandResult: ...

    def remove(self, skill: str) -> CommandResult: ...


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

    def install(
        self, source: str, skills: tuple[str, ...], agents: tuple[str, ...]
    ) -> CommandResult:
        arguments = ["npx", "skills", "add", source, "-g", "-y"]
        if agents:
            arguments.extend(["--agent", *agents])
        arguments.extend(["--skill", *skills])
        return self._run(arguments)

    def remove(self, skill: str) -> CommandResult:
        return self._run(["npx", "skills", "remove", skill, "-g", "-y"])


def default_runtime() -> Runtime:
    return Runtime(
        filesystem=LocalFilesystem(),
        npx=SubprocessNpx(),
        now=lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
