# 1Password SSH Agent in WSL

This repo setup forwards SSH agent requests from WSL to the 1Password SSH Agent running on Windows.

What is managed by the repo:
- Created `~/.1password/` and the socket path `~/.1password/agent.sock`.
- Stows `1password/.1password/agent-bridge.sh` into `~/.1password/agent-bridge.sh`.
- Installs `npiperelay.exe` into `~/.local/bin/npiperelay.exe` from the `jstarks/npiperelay` release zip.
- Sources `~/.1password/agent-bridge.sh` from `bash/.bashrc` so the bridge starts when you open a new shell.

Important notes:
- `./bootstrap.sh --reinstall-tools` installs `socat` in WSL and `npiperelay.exe` into `~/.local/bin/`.
- If `npiperelay.exe` is missing, rerun `scripts/setup-tools.sh` or place a copy at `~/.local/bin/npiperelay.exe`.
- 1Password for Windows is required. It must be running with Developer > `Use the SSH agent` enabled, and Windows Hello must be configured for unlocking keys.
- This bridge flow does not use `keychain`; any `keychain` setup in `~/.bashrc` is separate.
- `~/.1password/agent-bridge.sh` restores the caller's shell options before returning, so sourcing it from `~/.bashrc` does not leave interactive shells in `errexit`, `nounset`, or `pipefail` mode.

Manual steps to finish setup in WSL (run inside your WSL distro):
1. Run the repo setup so the helper, `socat`, and relay binary are installed:

   ./bootstrap.sh --reinstall-tools

2. Open a new WSL terminal (or run `source ~/.1password/agent-bridge.sh`) to start the bridge.
3. Test with:

   ssh-add -l

   You should see keys that are stored in 1Password. On first use you may be prompted by Windows Hello to unlock 1Password.

Removing the setup:
- Remove the `source "$HOME/.1password/agent-bridge.sh"` line from `bash/.bashrc` and restow the package.
- Kill any running `socat`/`npiperelay.exe` bridge processes and remove `~/.1password/agent.sock`.
