# git

Tracked global git configuration (`~/.gitconfig`), managed via Stow.

## Important files

- `~/.gitconfig` — symlinked from this stow package
- `~/.gitconfig.local` — **not tracked** — holds `[user]` name/email; create manually on each machine

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

## Difftastic integration

See `difftastic.md` in the repo root for full docs.

- `diff.external = difft` is the primary integration (preferred — passes renames and permissions)
- `[difftool "difftastic"]` is kept as a fallback

### Aliases

- `git dl` — `git log -p` with difftastic
- `git ds` — `git show` with difftastic
- `git dft` — `git diff` with difftastic
