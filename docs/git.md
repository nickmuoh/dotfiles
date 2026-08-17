# Git

The `git` package stows `~/.gitconfig` and `~/.git-attributes`.

Create an untracked `~/.gitconfig.local` on each machine for `[user]` name and email. It can also hold optional SSH commit-signing configuration.

For 1Password signing from WSL, Git uses the Windows `op-ssh-sign-wsl.exe` program and a public key exposed by the active 1Password agent. See [`1password.md`](1password.md) for bridge requirements.

[`difftastic.md`](difftastic.md) is the canonical reference for the configured diff driver and aliases.
