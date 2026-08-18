# Bootstrap scripts

`scripts/package-registry.sh` is the authoritative Bash-only registry. `REGISTRY_UNIT_IDS` is its only enumeration list, and each unit has one self-contained `registry_load_unit` case stanza with explicitly named fields. Canonical IDs are separate from command names, distribution names, and Stow package directories; aliases include `npiperelay.exe` (for `npiperelay`) and `cortex` (for `snowflake`). The registry contains apt, GitHub, Snap, installer, Stow ownership, per-package Stow options, and setup-hook names. Setup phases use `registry_hook_selected` so hook metadata controls package-scoped post-install work instead of serving as a descriptive dead field. The registry intentionally has no jq/yq/Python dependency.

`./bootstrap.sh --package ID` resolves and validates every ID before any setup script runs. Package mode installs only matching tool records and stows only matching packages; full bootstrap selects the complete registry. Stow-only IDs (for example `bash`) are valid, as are installer-plus-Stow IDs such as `ollama`. Unknown IDs fail before mutation. Multiple `--package` options are accepted.

`bootstrap.sh` manages generated and plugin content that cannot be stowed, including TPM and tmux plugins, the fzf clone, Micro plugins, and the Treemux Python environment. Treemux setup runs during a default bootstrap and is omitted when `--package` selects specific package-scoped items. Preview it with `./bootstrap.sh --dry-run`.

Bootstrap scripts source `scripts/lib.sh` (which loads the registry) and call `enable_error_trap`. Use `log` for top-level sections, `sublog` for nested work, and `status` for indented outcomes. `run` makes ordinary commands dry-run aware; use `run_sh` only for pipelines or compound shell commands. Do not print bootstrap actions with ad hoc `printf` or `echo`. `NO_COLOR=1` disables color output.

Use `clone_if_missing` for idempotent clones and `make_temp_dir` for temporary directories so the shared `EXIT` trap cleans them up. Keep expected failures in explicit conditionals and preserve the shared cleanup and error traps.
