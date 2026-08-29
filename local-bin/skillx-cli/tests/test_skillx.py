from __future__ import annotations

import io
import json
import unittest
from pathlib import Path

from skillx.adapters import CommandResult, InstallRequest, Mutation, Runtime
from skillx.main import main


class FakeFilesystem:
    def __init__(self, files: dict[str, str]) -> None:
        self.files = dict(files)
        self.backups: list[tuple[str, str]] = []
        self.fail_writes: set[str] = set()

    def read_text(self, path: str) -> str:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    def write_atomic(self, path: str, content: str) -> None:
        if path in self.fail_writes:
            raise OSError(f"cannot write {path}")
        self.files[path] = content

    def copy(self, source: str, destination: str) -> None:
        self.files[destination] = self.files[source]
        self.backups.append((source, destination))


class FakeNpx:
    def __init__(self) -> None:
        self.inventory_result = CommandResult(0, "[]", "")
        self.source_results: dict[str, CommandResult] = {}
        self.mutations: list[tuple[object, ...]] = []
        self.install_result = CommandResult(0, "", "")
        self.remove_result = CommandResult(0, "", "")
        self.transaction_events: list[str] = []

    def inventory(self) -> CommandResult:
        return self.inventory_result

    def enumerate_source(self, source: str) -> CommandResult:
        return self.source_results[source]

    def install_transaction(self, requests: tuple[InstallRequest, ...]) -> Mutation:
        for request in requests:
            self.mutations.append(
                ("install", request.source, request.skills, request.agents)
            )
        return Mutation(
            self.install_result,
            commit=lambda: self.transaction_events.append("install-commit"),
            rollback=lambda: self.transaction_events.append("install-rollback"),
        )

    def remove_transaction(self, skills: tuple[str, ...]) -> Mutation:
        for skill in skills:
            self.mutations.append(("remove", skill))
        return Mutation(
            self.remove_result,
            commit=lambda: self.transaction_events.append("remove-commit"),
            rollback=lambda: self.transaction_events.append("remove-rollback"),
        )


class SkillxCommandTests(unittest.TestCase):
    def fixture(self, name: str) -> object:
        path = Path(__file__).with_name("fixtures") / name
        return json.loads(path.read_text(encoding="utf-8"))

    def runtime(
        self,
        lockfile: dict[str, object],
    ) -> tuple[Runtime, FakeFilesystem, FakeNpx, io.StringIO, io.StringIO]:
        filesystem = FakeFilesystem({"/config/lock.json": json.dumps(lockfile)})
        npx = FakeNpx()
        stdout = io.StringIO()
        stderr = io.StringIO()
        runtime = Runtime(
            filesystem=filesystem,
            npx=npx,
            now=lambda: "20260822T120000Z",
            stdout=stdout,
            stderr=stderr,
        )
        return runtime, filesystem, npx, stdout, stderr

    def test_check_json_reports_valid_entries_without_mutation(self) -> None:
        runtime, _, npx, stdout, stderr = self.runtime(
            self.fixture("valid-lock.json")  # type: ignore[arg-type]
        )
        npx.source_results["nickmuoh/skills"] = CommandResult(
            0, '{"skills":[{"name":"in-ste"}]}', ""
        )

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json"],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(npx.mutations, [])
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "schema_version": 1,
                "operation": "check",
                "result": "ok",
                "lockfile": "/config/lock.json",
                "summary": {"valid": 1, "planned_changes": 0},
                "entries": [
                    {
                        "skill": "in-ste",
                        "source": "nickmuoh/skills",
                        "status": "valid",
                        "message": "skill is available",
                    }
                ],
            },
        )

    def test_sync_dry_run_reports_plan_without_mutation(self) -> None:
        runtime, _, npx, stdout, stderr = self.runtime(
            {
                "skills": {
                    "one": {"source": "owner/source"},
                    "two": {"source": "owner/source"},
                }
            }
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"one"},{"name":"two"}]}', ""
        )

        exit_code = main(
            ["sync", "--lockfile", "/config/lock.json", "--dry-run", "--json"],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(npx.mutations, [])
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["operation"], "sync")
        self.assertEqual(output["result"], "planned")
        self.assertEqual(output["summary"], {"valid": 2, "planned_changes": 2})

    def test_repair_backs_up_lockfile_and_removes_only_confirmed_missing_skill(
        self,
    ) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime(
            {
                "skills": {
                    "present": {"source": "owner/source"},
                    "removed": {"source": "owner/source"},
                }
            }
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"present"}]}', ""
        )

        exit_code = main(
            ["repair", "--lockfile", "/config/lock.json", "--yes", "--json"],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            filesystem.backups,
            [("/config/lock.json", "/config/lock.json.20260822T120000Z.bak")],
        )
        self.assertEqual(
            json.loads(filesystem.files["/config/lock.json"]),
            {"skills": {"present": {"source": "owner/source"}}},
        )
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["operation"], "repair")
        self.assertEqual(output["result"], "changed")
        self.assertEqual(output["summary"]["planned_changes"], 1)

    def test_adopt_records_valid_installed_skills_by_exact_path(self) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime(
            {"skills": {"one": {"source": "owner/source"}}}
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"one"}]}', ""
        )
        npx.inventory_result = CommandResult(
            0,
            json.dumps(self.fixture("owned-inventory.json")),
            "",
        )

        exit_code = main(
            [
                "adopt",
                "--from-lock",
                "--lockfile",
                "/config/lock.json",
                "--ledger",
                "/config/managed.json",
                "--yes",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(
            json.loads(filesystem.files["/config/managed.json"]),
            {
                "schema_version": 1,
                "managed": [
                    {
                        "skill": "one",
                        "source": "owner/source",
                        "path": "/agents/skills/one",
                    }
                ],
            },
        )
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["operation"], "adopt")
        self.assertEqual(output["result"], "changed")

    def test_prune_removes_only_exact_path_ledger_entry_absent_from_lockfile(
        self,
    ) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime(
            {"skills": {"keep": {"source": "owner/source"}}}
        )
        filesystem.files["/config/managed.json"] = json.dumps(
            {
                "schema_version": 1,
                "managed": [
                    {
                        "skill": "stale",
                        "source": "owner/old",
                        "path": "/agents/skills/stale",
                    }
                ],
            }
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"keep"}]}', ""
        )
        npx.inventory_result = CommandResult(
            0,
            json.dumps(
                [
                    {
                        "name": "stale",
                        "path": "/agents/skills/stale",
                        "scope": "global",
                        "agents": [],
                        "source": "owner/old",
                        "sourceUrl": None,
                        "sourceType": "github",
                    },
                    {
                        "name": "manual",
                        "path": "/agents/skills/manual",
                        "scope": "global",
                        "agents": [],
                        "source": None,
                        "sourceUrl": None,
                        "sourceType": None,
                    },
                ]
            ),
            "",
        )

        exit_code = main(
            [
                "prune",
                "--lockfile",
                "/config/lock.json",
                "--ledger",
                "/config/managed.json",
                "--yes",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(npx.mutations, [("remove", "stale")])
        self.assertEqual(
            json.loads(filesystem.files["/config/managed.json"]),
            {"schema_version": 1, "managed": []},
        )
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["operation"], "prune")
        self.assertEqual(output["result"], "changed")
        self.assertEqual(output["summary"]["planned_changes"], 1)

    def test_sync_reports_all_validation_failures_and_blocks_every_mutation(
        self,
    ) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime(
            {
                "skills": {
                    "missing": {"source": "owner/available"},
                    "private": {"source": "owner/private"},
                }
            }
        )
        original = filesystem.files["/config/lock.json"]
        npx.source_results["owner/available"] = CommandResult(
            0, '{"skills":[{"name":"other"}]}', ""
        )
        npx.source_results["owner/private"] = CommandResult(
            1, "", "Repository not found or authentication required"
        )

        exit_code = main(
            ["sync", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(npx.mutations, [])
        self.assertEqual(filesystem.files["/config/lock.json"], original)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["result"], "blocked")
        self.assertEqual(
            [entry["status"] for entry in output["entries"]],
            ["confirmed-missing-skill", "indeterminate"],
        )

    def test_json_configuration_failure_keeps_stdout_machine_readable(self) -> None:
        runtime, filesystem, _, stdout, stderr = self.runtime({"skills": {}})
        filesystem.files["/config/lock.json"] = "not-json"

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("invalid lockfile JSON", stderr.getvalue())
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "schema_version": 1,
                "operation": "check",
                "result": "failed",
                "lockfile": "/config/lock.json",
                "summary": {"valid": 0, "planned_changes": 0},
                "entries": [],
            },
        )

    def test_check_parses_upstream_list_text_case_insensitively(self) -> None:
        runtime, _, npx, stdout, _ = self.runtime(
            {"skills": {"in-ste": {"source": "owner/source"}}}
        )
        npx.source_results["owner/source"] = CommandResult(
            0,
            "◇  Found 1 skill\n│\n◇  Available Skills\n│  IN-STE\n│    Technical writing\n│\n└  Use --skill <name> to install specific skills\n",
            "",
        )

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["entries"][0]["status"], "valid")

    def test_check_classifies_explicit_no_valid_skills_without_guessing_from_404(
        self,
    ) -> None:
        runtime, _, npx, stdout, _ = self.runtime(
            {
                "skills": {
                    "bad": {"source": "owner/empty"},
                    "private": {"source": "owner/private"},
                }
            }
        )
        npx.source_results["owner/empty"] = CommandResult(
            1,
            "",
            "No valid skills found. Skills require a SKILL.md with name and description.",
        )
        npx.source_results["owner/private"] = CommandResult(
            1, "", "Repository not found"
        )

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            [entry["status"] for entry in json.loads(stdout.getvalue())["entries"]],
            ["confirmed-invalid-source/no-valid-skills", "indeterminate"],
        )

    def test_prune_path_mismatch_reports_ambiguity_and_removes_nothing(self) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime({"skills": {}})
        filesystem.files["/config/managed.json"] = json.dumps(
            {
                "schema_version": 1,
                "managed": [
                    {
                        "skill": "stale",
                        "source": "owner/source",
                        "path": "/agents/skills/stale",
                    }
                ],
            }
        )
        npx.inventory_result = CommandResult(
            0,
            json.dumps(
                [
                    {
                        "name": "stale",
                        "path": "/different/stale",
                        "scope": "global",
                        "agents": [],
                        "source": "owner/source",
                        "sourceUrl": None,
                        "sourceType": "github",
                    }
                ]
            ),
            "",
        )

        exit_code = main(
            [
                "prune",
                "--lockfile",
                "/config/lock.json",
                "--ledger",
                "/config/managed.json",
                "--yes",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("ambiguous", stderr.getvalue())
        self.assertEqual(npx.mutations, [])
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["result"], "blocked")
        self.assertEqual(output["entries"][0]["status"], "ambiguous-ownership")
        self.assertIn("expected one inventory entry", output["entries"][0]["message"])

    def test_sync_groups_source_and_forwards_named_agents(self) -> None:
        runtime, _, npx, stdout, _ = self.runtime(
            {
                "skills": {
                    "one": {"source": "owner/source"},
                    "two": {"source": "owner/source"},
                }
            }
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"one"},{"name":"two"}]}', ""
        )

        exit_code = main(
            [
                "sync",
                "--lockfile",
                "/config/lock.json",
                "--agent",
                "codex",
                "claude-code",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            npx.mutations,
            [("install", "owner/source", ("one", "two"), ("codex", "claude-code"))],
        )
        self.assertEqual(json.loads(stdout.getvalue())["result"], "changed")

    def test_verbose_json_keeps_raw_adapter_diagnostics_on_stderr(self) -> None:
        runtime, _, npx, stdout, stderr = self.runtime(
            {"skills": {"private": {"source": "owner/private"}}}
        )
        npx.source_results["owner/private"] = CommandResult(
            1, "clone output", "authentication required"
        )

        exit_code = main(
            [
                "check",
                "--lockfile",
                "/config/lock.json",
                "--json",
                "--verbose",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(json.loads(stdout.getvalue())["result"], "blocked")
        self.assertIn("clone output", stderr.getvalue())
        self.assertIn("authentication required", stderr.getvalue())
        self.assertNotIn("clone output", stdout.getvalue())

    def test_adopt_refuses_source_mismatch_without_writing_ledger(self) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime(
            {"skills": {"one": {"source": "owner/desired"}}}
        )
        npx.source_results["owner/desired"] = CommandResult(
            0, '{"skills":[{"name":"one"}]}', ""
        )
        npx.inventory_result = CommandResult(
            0,
            json.dumps(
                [
                    {
                        "name": "one",
                        "path": "/agents/skills/one",
                        "scope": "global",
                        "agents": [],
                        "source": "owner/different",
                        "sourceUrl": None,
                        "sourceType": "github",
                    }
                ]
            ),
            "",
        )

        exit_code = main(
            [
                "adopt",
                "--from-lock",
                "--lockfile",
                "/config/lock.json",
                "--ledger",
                "/config/managed.json",
                "--yes",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("does not match", stderr.getvalue())
        self.assertNotIn("/config/managed.json", filesystem.files)
        self.assertEqual(json.loads(stdout.getvalue())["result"], "blocked")

    def test_sync_mutation_failure_returns_machine_readable_exit_two(self) -> None:
        runtime, _, npx, stdout, stderr = self.runtime(
            {"skills": {"one": {"source": "owner/source"}}}
        )
        npx.source_results["owner/source"] = CommandResult(
            0, '{"skills":[{"name":"one"}]}', ""
        )

        npx.install_result = CommandResult(1, "", "disk full")

        exit_code = main(
            ["sync", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("disk full", stderr.getvalue())
        self.assertEqual(json.loads(stdout.getvalue())["result"], "failed")
        self.assertEqual(npx.transaction_events, ["install-rollback"])

    def test_successful_empty_enumeration_is_confirmed_invalid_source(self) -> None:
        runtime, _, npx, stdout, _ = self.runtime(
            {"skills": {"bad": {"source": "owner/empty"}}}
        )
        npx.source_results["owner/empty"] = CommandResult(
            0,
            "◇  Available Skills\n└  Use --skill <name> to install specific skills\n",
            "",
        )

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json"], runtime=runtime
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(stdout.getvalue())["entries"][0]["status"],
            "confirmed-invalid-source/no-valid-skills",
        )

    def test_json_usage_error_still_emits_one_json_document(self) -> None:
        runtime, _, _, stdout, stderr = self.runtime({"skills": {}})

        exit_code = main(
            ["check", "--lockfile", "/config/lock.json", "--json", "--bad-option"],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("unrecognized arguments", stderr.getvalue())
        self.assertEqual(json.loads(stdout.getvalue())["result"], "failed")

    def test_authoritative_missing_source_classification_is_repairable(self) -> None:
        runtime, _, npx, stdout, _ = self.runtime(
            {"skills": {"gone": {"source": "provider/gone"}}}
        )
        npx.source_results["provider/gone"] = CommandResult(
            1, "", "authoritative provider response", "confirmed-missing-source"
        )

        exit_code = main(
            ["repair", "--lockfile", "/config/lock.json", "--dry-run", "--json"],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 1)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["entries"][0]["status"], "confirmed-missing-source")
        self.assertEqual(output["summary"]["planned_changes"], 1)

    def test_prune_rolls_back_removal_when_ledger_commit_fails(self) -> None:
        runtime, filesystem, npx, stdout, stderr = self.runtime({"skills": {}})
        filesystem.files["/config/managed.json"] = json.dumps(
            {
                "schema_version": 1,
                "managed": [
                    {
                        "skill": "stale",
                        "source": "owner/source",
                        "path": "/agents/skills/stale",
                    }
                ],
            }
        )
        filesystem.fail_writes.add("/config/managed.json")
        npx.inventory_result = CommandResult(
            0,
            json.dumps(
                [
                    {
                        "name": "stale",
                        "path": "/agents/skills/stale",
                        "scope": "global",
                        "agents": [],
                        "source": "owner/source",
                        "sourceUrl": None,
                        "sourceType": "github",
                    }
                ]
            ),
            "",
        )

        exit_code = main(
            [
                "prune",
                "--lockfile",
                "/config/lock.json",
                "--ledger",
                "/config/managed.json",
                "--yes",
                "--json",
            ],
            runtime=runtime,
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("cannot write", stderr.getvalue())
        self.assertEqual(json.loads(stdout.getvalue())["result"], "failed")
        self.assertEqual(npx.transaction_events, ["remove-rollback"])


if __name__ == "__main__":
    unittest.main()
