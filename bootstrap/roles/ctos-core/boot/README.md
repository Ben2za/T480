# ctos-core Boot Contract

Goal: make the tower recoverable after reboot while keeping desktop streaming tunnel-first.

Run locally on `ctos-core`:

```bash
cd /srv/ctos/repo/t480
sudo bootstrap/roles/ctos-core/boot/ctos-core-boot-contract plan
sudo bootstrap/roles/ctos-core/boot/ctos-core-boot-contract apply
```

For unattended DESK after a tower reboot, the tower must also log into an X11 session.
If the tower is physically trusted enough for autologin:

```bash
cd /srv/ctos/repo/t480
sudo bootstrap/roles/ctos-core/boot/ctos-core-boot-contract apply --enable-autologin
```

The rescue SSH service listens on `10.42.0.2:2222` and disables password auth. VNC
still stays localhost-only and is started by the T480 through SSH.
