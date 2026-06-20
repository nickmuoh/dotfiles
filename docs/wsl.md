# WSL configuration (/etc/wsl.conf)

This documents the WSL configuration present in /etc/wsl.conf for this machine and explains each setting.

---

Current file contents:

[boot]
systemd=true

[user]
default=nmuoh

[automount]
options = "metadata"

---

Explanation

- [boot]
  - systemd=true: Enables systemd inside the WSL distro. Requires a Windows/WSL build that supports systemd (Windows 11+ with updated WSL). After changing this, run `wsl --shutdown` from Windows and restart the distro.

- [user]
  - default=nmuoh: Sets the default login user to `nmuoh` for new WSL shells and when launching the distro without an explicit user.

- [automount]
  - options = "metadata": Tells WSL to mount Windows drives (e.g., /mnt/c) with metadata support so POSIX ownership and permission metadata are preserved in extended attributes. This enables more correct Unix-style permissions but can affect mount behavior and performance. Other automount options (like `enabled`, `mountFsTab`) can be added as needed.

Notes & tips

- To apply changes, shut down WSL from Windows: `wsl --shutdown` and then start the distro.
- If systemd fails to start, verify WSL and Windows versions and check `journalctl` inside the distro for errors.
- Keep this doc in sync if /etc/wsl.conf is modified; update the file here to reflect changes.
