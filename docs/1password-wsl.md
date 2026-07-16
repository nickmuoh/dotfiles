# 1Password SSH Agent in WSL

This repo setup forwards SSH agent requests from WSL to the 1Password SSH Agent running on Windows.

What is managed by the repo:
- Created `~/.1password/` and the socket path `~/.1password/agent.sock`.
- Stows `local-bin/.local/bin/1password-ssh-agent` into `~/.local/bin/1password-ssh-agent`.
- Installs `npiperelay.exe` into `~/.local/bin/npiperelay.exe` from the `jstarks/npiperelay` release zip.
- Sources `~/.local/bin/1password-ssh-agent` from `bash/.bashrc` so the bridge starts when you open a new shell.

Important notes:
- `socat` still has to be installed in WSL with `sudo apt install -y socat`.
- If `npiperelay.exe` is missing, rerun `scripts/setup-tools.sh` or place a copy at `~/.local/bin/npiperelay.exe`.
- 1Password for Windows must be running and have Developer > "Use the SSH agent" enabled. Windows Hello must be configured for unlocking keys.

Manual steps to finish setup in WSL (run inside your WSL distro):
1. Install socat (requires sudo):

   sudo apt update && sudo apt install -y socat

2. Run the repo setup so the helper and relay binary are installed:

   ./bootstrap.sh --reinstall-tools

3. Open a new WSL terminal (or run `source ~/.local/bin/1password-ssh-agent`) to start the bridge.
4. Test with:

   ssh-add -l

   You should see keys that are stored in 1Password. On first use you may be prompted by Windows Hello to unlock 1Password.

Removing the setup:
- Remove the `source "$HOME/.local/bin/1password-ssh-agent"` line from `bash/.bashrc` and restow the package.
- Kill any running `socat`/`npiperelay.exe` bridge processes and remove `~/.1password/agent.sock`.
