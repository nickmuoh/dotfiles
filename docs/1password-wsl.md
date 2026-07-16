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
- The Windows `OpenSSH Authentication Agent` service must be stopped and disabled so 1Password can own `\\.\pipe\openssh-ssh-agent`. If that service is running, WSL will reach the Windows agent instead of 1Password.
- This bridge flow does not use `keychain`; any `keychain` setup in `~/.bashrc` is separate.
- `~/.1password/agent-bridge.sh` restores the caller's shell options before returning, so sourcing it from `~/.bashrc` does not leave interactive shells in `errexit`, `nounset`, or `pipefail` mode.
- If `%LOCALAPPDATA%/1Password/config/ssh/agent.toml` exists, 1Password only offers the keys matched by that file. Use the GitHub SSH key item there if you want GitHub auth from WSL.

Manual steps to finish setup in WSL (run inside your WSL distro):
1. On Windows, stop and disable the `OpenSSH Authentication Agent` service:

   ```powershell
   Stop-Service ssh-agent
   Set-Service ssh-agent -StartupType Disabled
   ```

2. In 1Password for Windows, enable Developer > `Use the SSH agent`.
3. If you use a custom `%LOCALAPPDATA%/1Password/config/ssh/agent.toml`, make sure it includes the GitHub SSH key item you want to expose.
4. Run the repo setup so the helper, `socat`, and relay binary are installed:

   ./bootstrap.sh --reinstall-tools

5. Open a new WSL terminal (or run `source ~/.1password/agent-bridge.sh`) to start the bridge.
6. Test the active key fingerprint with:

   ssh-add -L | ssh-keygen -lf -

   The fingerprint should match the GitHub SSH key stored in 1Password.

7. Test with:

   ssh-add -l

   You should see keys that are stored in 1Password. On first use you may be prompted by Windows Hello to unlock 1Password.
8. Verify GitHub SSH with:

   ssh -T git@github.com

Troubleshooting:
- If `ssh-add -L` shows the wrong key, check whether the Windows `ssh-agent` service is still running.
- If `ssh-add -L` shows no keys or the wrong GitHub key, review `%LOCALAPPDATA%/1Password/config/ssh/agent.toml` and the matching 1Password SSH Key items.

Removing the setup:
- Remove the `source "$HOME/.1password/agent-bridge.sh"` line from `bash/.bashrc` and restow the package.
- Kill any running `socat`/`npiperelay.exe` bridge processes and remove `~/.1password/agent.sock`.
