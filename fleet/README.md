# CTOS Fleet

Fleet metadata lives here.

This directory is intentionally light for now. It records roles and inventory shape before any fleet orchestrator is installed.

## Files

- `nodes.json`: current CTOS archipelago inventory and feature track registry.
- `nodes.example.yml`: Ansible-compatible inventory shape for future use.
- `roles.md`: role definitions and intended responsibilities.
- `../bootstrap/manifests/`: first package manifests for role bootstrap.
- `../bootstrap/ctos-apply-role`: first post-install role apply helper.

## Commands

```bash
../scripts/ctos-fleet list
../scripts/ctos-fleet features
../scripts/ctos-fleet status
../scripts/ctos-fleet status --json
```

## Current Policy

- T480 is the mobile admin node.
- Tower is the first `core` node and is now installed as EndeavourOS `ctos-core`.
- Worker nodes are future EndeavourOS machines.
- Inventory files must not contain secrets, private IPs that should not be shared, tokens, or credentials.
- Live status pulls are explicit. Persistent telemetry/heartbeat daemons are deferred until the data and security model is decided.
