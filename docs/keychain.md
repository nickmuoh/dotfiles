# keychain

SSH agent manager. Keeps one agent per host instead of spawning a new agent per terminal.

## Install

Installed as a Python zipapp (`.pyz`) via `setup-tools.sh` `GITHUB_INSTALLS`:

- Source: `danielrobbins/keychain` GitHub releases
- Version: `3.0.0_beta1`
- Binary: `~/.local/bin/keychain` (placed by bootstrap, **not** stow-tracked)
- Requires: Python 3.9+ (present on Ubuntu 24.04+)

## Important configuration paths

- `~/.bashrc` — shell startup eval block
- `~/.keychain/` — runtime env files written by keychain per hostname
- `~/.local/share/bash-completion/completions/keychain` — bash completion (stow-tracked)

## Current state

Shell startup (`~/.bashrc`) initializes keychain with v3 syntax:

```sh
eval "$(keychain add --quiet --eval "$HOME/.ssh/nick_muoh.trimble-github.ed25519")"
```

- `add` — start or reuse an existing agent and load the key
- `--eval` — emit `SSH_AUTH_SOCK`/`SSH_AGENT_PID` exports for `eval`
- `--quiet` — suppress non-error output; no startup banner (WSL-appropriate)
- Passphrase prompts still appear in the terminal if the key is locked

## Key commands (v3)

```sh
keychain add ~/.ssh/key       # start/reuse agent, load key
keychain inspect              # show current agent state
keychain list                 # list loaded keys
keychain wipe                 # remove all loaded keys
keychain agent stop           # stop the managed agent
keychain man                  # full embedded documentation
```

## Optional config (`~/.keychainrc`)

```ini
[keychain]
quiet = true
lockwait = 5

[agent.ssh]
args = -t 3600          # expire keys after 1 hour
```

## Bash completion

Completion file is from the v2 release (pinned commit), stow-tracked in `bash-completions/`.
May need updating when keychain v3 ships a stable release with its own completion.

## History

- Previously installed as a raw shell script from a pinned GitHub commit (`danielrobbins/keychain` `2b3c181`)
- Switched to Python zipapp (v3 `.pyz`) for the fully maintained and testable rewrite
- v2 used `eval "$(keychain --quiet --eval key)"` syntax; v3 uses `keychain add --eval key`
