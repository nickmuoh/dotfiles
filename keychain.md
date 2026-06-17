# keychain setup

## Important configuration paths

- `~/.bashrc`
- `~/.local/bin/keychain`
- `~/.local/share/bash-completion/completions/keychain`
- `~/.ssh/nick_muoh.trimble-github.ed25519`

## Installed state

- Installed version: `2.9.8`
- Installed from upstream `keychain.sh` into `~/.local/bin/keychain`
- Bash completion was installed to the user completion directory

## Current state

- Bash now initializes SSH auth through `keychain` instead of starting a raw `ssh-agent`
- The Bash wrapper uses `--quiet` so startup stays clean
- The configured key is `nick_muoh.trimble-github.ed25519`
- `~/.local/bin` is already on `PATH`, so the user-local install is reachable

## History-backed setup notes

- `curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh -o ~/.local/bin/keychain`
- `curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash -o ~/.local/share/bash-completion/completions/keychain`

## Caveats

- This setup caches the SSH key in a shared agent across shells; it still depends on the key passphrase and your normal SSH permissions
