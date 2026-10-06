# CTOS Bootstrap Kit

This directory describes the first USB bootstrap strategy.

## Phase 1

Use the official EndeavourOS installer USB, then use a CTOS kit directory from this repo after the OS is installed.

The kit should contain:

- repo docs and context needed for recovery;
- desktop config;
- scripts;
- fleet role metadata;
- package manifests once decided.

Build a kit directory with:

```bash
./scripts/ctos-build-usb-kit /path/to/empty/ctos-kit
```

For the first tower install, follow:

```bash
less docs/TOWER_CTOS_CORE_INSTALL.md
```

After EndeavourOS first boot on the tower, from the CTOS kit root:

```bash
bootstrap/ctos-apply-role ctos-core plan
sudo bootstrap/ctos-apply-role ctos-core apply
```

The secondary SATA disk is initialized separately and only after an explicit disk check:

```bash
sudo bootstrap/ctos-init-core-storage plan --device /dev/disk/by-id/<samsung-ssd-id>
```

## Phase 2

After the package manifests and bootstrap scripts are proven, use EndeavourOS installer customization:

- `/home/liveuser/user_pkglist.txt`
- `~/user-commands-before.bash`
- `~/user_commands.bash`

Do not use installer automation for destructive disk choices. Partitioning and wipe/dual-boot choices remain manual until a specific machine runbook is written.
