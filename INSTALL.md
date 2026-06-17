# Shell setup install guide

Install GNU Stow first, then bootstrap the generated content, then stow the packages.

## Base tools

```sh
sudo apt-get update
sudo apt-get install -y stow bash-completion curl git ctags fzf bat jq yq tmux pandoc starship gh neovim
```

## Shell tools

```sh
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
curl https://getmic.ro | bash
sudo mv micro /usr/bin/micro
mkdir -p ~/.local/bin ~/.local/share/bash-completion/completions
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/keychain.sh -o ~/.local/bin/keychain
curl -fsSL https://raw.githubusercontent.com/danielrobbins/keychain/2b3c181eaa73ca27b0cfa3fd12148d6b69e35311/completions/keychain.bash -o ~/.local/share/bash-completion/completions/keychain
```

## Bootstrap

Run the repo bootstrap script to install generated/plugin content:

```sh
cd /home/nmuoh/.dotfiles
./bootstrap.sh --dry-run
./bootstrap.sh
```

That bootstrap step clones `~/.fzf`, `~/.tmux/plugins/tpm`, and the Micro plugin repos.
If target config files already exist in `$HOME`, use `./bootstrap.sh --adopt` for the first stow pass.

## Stow

Dry run first:

```sh
stow -nv bash micro tmux nvim starship fzf local-bin bash-completions
```

Then deploy:

```sh
stow -v bash micro tmux nvim starship fzf local-bin bash-completions
```

## Notes

- `bat` is invoked as `batcat` on this system.
- `preview` uses the `preview` command in Micro and depends on `pandoc`.
- Package-specific details live in `<package>/README.md`.
