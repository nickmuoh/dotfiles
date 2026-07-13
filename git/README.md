# git

Tracked global git configuration (`~/.gitconfig`), managed via Stow.

## Important files

- `~/.gitconfig` — symlinked from this stow package
- `~/.gitconfig.local` — **not tracked** — holds `[user]` name/email; create manually on each machine
- `%LOCALAPPDATA%/1Password/config/ssh/agent.toml` — optional 1Password SSH agent scope file (WSL path: `/mnt/c/Users/<user>/AppData/Local/1Password/config/ssh/agent.toml`)

## Setup

Before stowing, create `~/.gitconfig.local`:

```sh
cat > ~/.gitconfig.local << 'EOF'
[user]
    name = Your Name
    email = your@email.com
EOF
```

Then stow:

```sh
stow -v git
```

## Optional SSH commit signing

When using a local SSH key loaded into `ssh-agent`/`keychain`, keep the signing config in `~/.gitconfig.local`:

```ini
[user]
    signingkey = ~/.ssh/<public-key>.ed25519.pub

[gpg]
    format = ssh

[commit]
    gpgsign = true
```

Use the public key path for `user.signingkey`; Git signs through the matching private key already loaded in the agent.

When using 1Password from WSL, point Git at the Windows signer binary instead:

```ini
[user]
    signingkey = ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA...

[gpg]
    format = ssh

[gpg "ssh"]
    program = /mnt/c/Users/<user>/AppData/Local/Microsoft/WindowsApps/op-ssh-sign-wsl.exe

[commit]
    gpgsign = true
```

For the 1Password signer to work, the matching private key must exist in 1Password as an `SSH Key` item and be visible through the active `agent.toml` rules. A custom `agent.toml` overrides the default vault scope.

To confirm the key Git should use, run `ssh-add.exe -L` in WSL and copy the public key it returns into `user.signingkey`.

If `agent.toml` exists at `%LOCALAPPDATA%/1Password/config/ssh/agent.toml`, 1Password uses only the keys matched by that file instead of the default Personal/Private/Employee set.

## Difftastic integration

See `difftastic.md` in the repo root for full docs.

- `[diff "difftastic"] command = difft` is the primary integration
- `[difftool "difftastic"]` is kept as a fallback
- `~/.git-attributes` routes `*.ipynb` to `jupyternotebook`

### Aliases

- `git dl` — `git log -p` with difftastic
- `git ds` — `git show` with difftastic
- `git dft` — `git diff` with difftastic
