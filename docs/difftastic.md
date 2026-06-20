# difftastic

Structural diff tool that understands syntax. Used as the primary git diff driver.

## Install

Installed via snap (managed by `setup-tools.sh`):

```sh
sudo snap install difftastic
```

Binary: `/snap/bin/difftastic`

## Local wrapper (`difft`)

A wrapper script at `~/.local/bin/difft` (managed by the `local-bin` stow package)
calls `difftastic --display inline "$@"`. This ensures `--display inline` is always
active without needing to embed flags in git config (git passes positional args
directly to `diff.external`, so flags can't be added there).

Git config and aliases reference `difft` (the wrapper), not `difftastic` directly.

## Git integration

Configured in the `git` stow package (`~/.gitconfig`).

The recommended integration is `diff.external = difft`, which passes renames and
permission changes to difftastic for richer output. The difftool definition is kept
as a fallback for explicit `git difftool` use.

### Aliases

| Alias | Expands to |
|---|---|
| `git dlog` | `git log -p` with difftastic diffs (inline display) |
| `git dshow` | `git show` (most recent commit) with difftastic (inline display) |
| `git difft` | `git diff` with difftastic (inline display) |

### One-off without aliases

```sh
git -c diff.external=difft diff
git -c diff.external=difft show --ext-diff
git -c diff.external=difft log -p --ext-diff
```

### Opt out for a single command

```sh
git diff --no-ext-diff
```

## Lazygit

`externalDiffCommand: /snap/bin/difftastic --color=always` is present in
`~/.config/lazygit/config.yml` but currently commented out. Uncomment to enable
difftastic diffs inside lazygit.
