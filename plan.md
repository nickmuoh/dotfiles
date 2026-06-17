# GNU Stow Dotfiles Plan — shell_setup

**Repo root:** `/home/nmuoh/.shell_setup`  
**Status:** Active — repo-root-plus-package-docs layout

---

## Layout Philosophy

This repo uses a **repo-root-plus-package-docs** layout:

- **Root docs** (`README.md`, `INSTALL.md`, `AGENTS.md`, `plan.md`) are repo-wide index/reference docs. They are never stowed into `$HOME`.
- **Package docs** live alongside each package's config files and are committed to Git (e.g. `bash/README.md`, `tmux/README.md`). They are excluded from Stow via `.stow-local-ignore`.
- **Stow deploys only config files** — docs, bootstrap scripts, and generated/plugin content are never symlinked into `$HOME`.
- **Bootstrap/plugin/generated content** belongs in `bootstrap.sh` (or equivalent scripts), not in Stow packages.
- **Root `README.md` indexes all package docs** with links to each `<package>/README.md`.

---

## Repository Layout

```
/home/nmuoh/.shell_setup/          ← repo root (stow source dir)
├─ README.md                       ← repo-wide index; links to all package docs
├─ INSTALL.md                      ← repo-wide install instructions
├─ AGENTS.md                       ← repo-wide agent/AI context
├─ plan.md                         ← this file
├─ bootstrap.sh                    ← plugin installs, package manager steps, generated content
├─ .stow-local-ignore              ← global ignore: docs, scripts, bootstrap
├─ .gitignore
│
├─ bash/
│  ├─ README.md                    ← bash package docs (keyed from root README)
│  ├─ .bashrc
│  └─ .bash_aliases
│
├─ tmux/
│  ├─ README.md                    ← tmux package docs
│  └─ .tmux.conf
│     (plugin clones go in bootstrap.sh, not here)
│
├─ micro/
│  ├─ README.md                    ← micro package docs
│  └─ .config/
│     └─ micro/
│        ├─ settings.json
│        ├─ bindings.json
│        └─ palettero.cfg
│        (plug/ clones excluded via micro/.stow-local-ignore)
│
├─ nvim/
│  ├─ README.md                    ← nvim package docs
│  └─ .config/
│     └─ nvim/
│        └─ init.lua               (or init.vim + lua/)
│
├─ starship/
│  ├─ README.md
│  └─ .config/
│     └─ starship.toml
│
├─ fzf/
│  ├─ README.md
│  └─ .fzf/
│
├─ local-bin/
│  └─ .local/
│     └─ bin/
│        └─ keychain
│
└─ bash-completions/
   └─ .local/
      └─ share/
         └─ bash-completion/
            └─ completions/
               └─ keychain
```

**Rule of thumb:** if it's a config file that belongs under `$HOME`, it goes in the package. If it's documentation, a script, or a plugin clone, it does not.

---

## 1. Prerequisites — Install GNU Stow

### Ubuntu / Debian
```bash
sudo apt update && sudo apt install -y stow
```

### macOS (Homebrew)
```bash
brew install stow
```

### Arch / Fedora
```bash
sudo pacman -Syu stow   # Arch
sudo dnf install -y stow  # Fedora
```

---

## 2. Stow Ignore Rules

### Root `.stow-local-ignore` (prevent docs/scripts from reaching `$HOME`)
```
^README\.md$
^INSTALL\.md$
^AGENTS\.md$
^plan\.md$
^bootstrap\.sh$
^\.gitignore$
^scripts/
```

### Per-package ignore — example `micro/.stow-local-ignore`
```
^README\.md$
^docs/
^plug/$
^plug/.*
```

Any package with its own `README.md` or a `docs/` subdirectory should have a `.stow-local-ignore` excluding them.

---

## 3. First-Time Import with `--adopt`

If config files already exist at their `$HOME` paths, use `stow --adopt` to pull them into the package tree before committing:

```bash
cd /home/nmuoh/.shell_setup

# Preview what --adopt would do (dry run)
stow -n --adopt bash

# Actually adopt — moves $HOME files into the package, then symlinks back
stow --adopt bash
stow --adopt micro
stow --adopt tmux
stow --adopt nvim

# Review diffs before committing
git diff
git add -p
git commit -m "chore: adopt existing dotfiles into stow packages"
```

> **Warning:** `--adopt` overwrites package files with whatever is currently at `$HOME`. Always review `git diff` after adopting.

---

## 4. Step-by-Step Setup

### Step 0: Back Up Existing Files
```bash
mkdir -p ~/dotfiles-backups
cp -a ~/.bashrc ~/.bash_aliases ~/.tmux.conf ~/.config/micro ~/.config/nvim ~/dotfiles-backups/ 2>/dev/null || true
```

### Step 1: Create Package Skeletons (if starting fresh)
```bash
cd /home/nmuoh/.shell_setup
mkdir -p bash tmux micro nvim starship fzf local-bin bash-completions
```

### Step 2: Place Config Files in Packages
Move (not copy) to avoid conflicts when Stow creates symlinks:

```bash
# Bash
mv ~/.bashrc ~/.bash_aliases /home/nmuoh/.shell_setup/bash/

# Micro
mkdir -p /home/nmuoh/.shell_setup/micro/.config/micro
mv ~/.config/micro/settings.json ~/.config/micro/bindings.json \
   ~/.config/micro/palettero.cfg \
   /home/nmuoh/.shell_setup/micro/.config/micro/ 2>/dev/null || true

# tmux
mv ~/.tmux.conf /home/nmuoh/.shell_setup/tmux/ 2>/dev/null || true

# Neovim
mkdir -p /home/nmuoh/.shell_setup/nvim/.config
cp -a ~/.config/nvim /home/nmuoh/.shell_setup/nvim/.config/ 2>/dev/null || true

# local bin + completions
mkdir -p /home/nmuoh/.shell_setup/local-bin/.local/bin
mv ~/.local/bin/keychain /home/nmuoh/.shell_setup/local-bin/.local/bin/ 2>/dev/null || true

mkdir -p /home/nmuoh/.shell_setup/bash-completions/.local/share/bash-completion/completions
mv ~/.local/share/bash-completion/completions/keychain \
   /home/nmuoh/.shell_setup/bash-completions/.local/share/bash-completion/completions/ 2>/dev/null || true
```

### Step 3: Run Stow
```bash
cd /home/nmuoh/.shell_setup
stow -v bash micro tmux nvim starship fzf local-bin bash-completions
```

Dry-run first with `-n`:
```bash
stow -nv bash micro tmux nvim
```

**Verify:**
```bash
ls -la ~/.bashrc ~/.tmux.conf ~/.config/micro/settings.json
```

---

## 5. bootstrap.sh — Plugins, Generated Content, Package Installs

Plugin clones, generated files, and system package installs belong here, **not** in Stow packages:

```bash
#!/usr/bin/env bash
# file: /home/nmuoh/.shell_setup/bootstrap.sh
set -euo pipefail

echo "==> Installing micro plugins..."
micro -plugin install gitStatus preview fzfinder || true
git clone https://github.com/terokarvinen/palettero ~/.config/micro/plug/palettero 2>/dev/null || true

echo "==> Installing tmux plugin manager..."
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm 2>/dev/null || true

echo "==> Bootstrap complete. Run: stow -v bash micro tmux nvim"
```

```bash
chmod +x /home/nmuoh/.shell_setup/bootstrap.sh
```

---

## 6. Conflict Resolution

| Situation | Fix |
|-----------|-----|
| File exists at `$HOME` path | `stow --adopt <pkg>`, then `git diff` to review |
| Manual conflict resolution | `mv ~/.bashrc ~/.bashrc.bak && stow bash` |
| Preview changes safely | `stow -nv <pkg>` |
| Remove symlinks | `stow -D <pkg>` |

---

## 7. Package Docs — Indexing from Root README

Each package with notable config (bash, tmux, micro, nvim, starship, fzf) should have a `<package>/README.md` that documents:
- What config files live here
- Key settings, keybindings, or commands
- Plugin list (with URLs) — **actual installs go in bootstrap.sh**
- Dependencies

Root `README.md` should link to each:
```markdown
## Packages
- [bash](bash/README.md) — bashrc, aliases
- [tmux](tmux/README.md) — tmux config, plugins
- [micro](micro/README.md) — settings, keybindings, plugins
- [nvim](nvim/README.md) — neovim config
- [starship](starship/README.md) — prompt config
```

---

## 8. GitHub Workflow

### Push to GitHub
```bash
cd /home/nmuoh/.shell_setup
git add .
git commit -m "chore: initial import of dotfiles (stow layout)"
gh repo create shell_setup --public --source=. --remote=origin --push
```

### Clone and Bootstrap on New Machine
```bash
git clone https://github.com/<username>/shell_setup.git ~/.shell_setup
cd ~/.shell_setup
./bootstrap.sh
stow -v bash micro tmux nvim starship fzf local-bin bash-completions
```

---

## 9. Safety Checklist

- [ ] Back up existing config files before moving (Step 0)
- [ ] Move (not copy) existing files to avoid stow conflicts
- [ ] Test with one package first: `stow -nv bash`
- [ ] Root `.stow-local-ignore` excludes all docs, scripts, plan files
- [ ] Per-package `.stow-local-ignore` excludes `README.md`, `docs/`, `plug/`
- [ ] Plugin clones and generated content are in `bootstrap.sh`, not in packages
- [ ] Package docs exist at `<pkg>/README.md` and are linked from root `README.md`
- [ ] `.gitignore` excludes plugin clones and cache files
- [ ] Commit dotfiles to Git for version control and portability

---

## Notes

- **Repo root:** `/home/nmuoh/.shell_setup`
- **Tools managed:** bash, tmux, micro, nvim, fzf, starship, zoxide, keychain, local bin scripts
- **Backup location:** `~/dotfiles-backups`
- **WSL:** `wsl.conf` documented in `wsl.md`; dotfiles workflow is orthogonal but compatible

---

Updated: 2026-06-16  
Layout: repo-root-plus-package-docs
