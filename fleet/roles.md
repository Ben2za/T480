# CTOS Fleet Roles

## `godfather`

Mobile admin role for the T480.

- Fleet cockpit and repo control.
- Local coding/Codex workstation.
- SSH/admin origin once the secrets model is decided.
- No heavy always-on workloads by default.

## `core`

Desktop tower role.

- Richer daily desktop.
- Worker host.
- Candidate Git/package/model cache host.
- Candidate AI runtime host.
- First V1 install target is `ctos-core` on EndeavourOS with Xfce, native SSH, CTOS repo copy under `/opt/ctos/repo`, and service/cache roots under `/srv/ctos`.
- Hardware upgrades and heavy services are staged after the OS is recoverable.

## `worker`

General CTOS worker node.

- Runs only selected workers.
- Pulls/apply repo updates by role.
- Must remain independently recoverable.

## `lab`

Isolated guest/lab role.

- Kali and other authorized security environments.
- Offensive tooling remains in this boundary.
