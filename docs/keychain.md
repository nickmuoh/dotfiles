# keychain

SSH agent manager. Keeps one agent per host instead of spawning a new agent per terminal.

This is separate from the WSL 1Password bridge flow documented in
[`1password.md`](1password.md).

`scripts/setup-tools.sh` installs keychain as a Python zipapp from the
`danielrobbins/keychain` release into `~/.local/bin/keychain`.

## Important configuration paths

- `~/.bashrc` — shell startup eval block
- `~/.keychain/` — runtime env files written by keychain per hostname
- `~/.local/share/bash-completion/completions/keychain` — bash completion (stow-tracked)
- `~/.local/bin/keychain` — must be on `PATH` before Bash reaches the SSH block

## Current state

The tracked `~/.bashrc` currently comments out the `keychain` startup block because SSH auth is expected to come from the 1Password WSL bridge on this machine.

When the block is enabled, shell startup (`~/.bashrc`) initializes keychain with v3 syntax:

```sh
eval "$(keychain add --quiet --eval "$HOME/.ssh/nick_muoh.trimble-github.ed25519")"
```

- `add` — start or reuse an existing agent and load the key
- `--eval` — emit `SSH_AUTH_SOCK`/`SSH_AGENT_PID` exports for `eval`
- `--quiet` — suppress non-error output; no startup banner (WSL-appropriate)
- Passphrase prompts still appear in the terminal if the key is locked
- `~/.local/bin` is exported before this block so Bash can resolve the zipapp during startup

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
