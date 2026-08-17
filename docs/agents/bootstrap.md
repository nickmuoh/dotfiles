# Bootstrap scripts

`bootstrap.sh` manages generated and plugin content that cannot be stowed, including TPM and tmux plugins, the fzf clone, Micro plugins, and the Treemux Python environment. Treemux setup runs during a default bootstrap and is omitted when `--package` selects specific package-scoped items. Preview it with `./bootstrap.sh --dry-run`.

Bootstrap scripts source `scripts/lib.sh` and call `enable_error_trap`. Use `log` for top-level sections, `sublog` for nested work, and `status` for indented outcomes. `run` makes ordinary commands dry-run aware; use `run_sh` only for pipelines or compound shell commands. Do not print bootstrap actions with ad hoc `printf` or `echo`. `NO_COLOR=1` disables color output.

Use `clone_if_missing` for idempotent clones and `make_temp_dir` for temporary directories so the shared `EXIT` trap cleans them up. Keep expected failures in explicit conditionals and preserve the shared cleanup and error traps.
