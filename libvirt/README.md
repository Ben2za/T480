# CTOS Libvirt Definitions

This directory contains repo-owned libvirt plans and XML definitions for the host cockpit.

Current status:

- These files are not applied automatically.
- No VM disks, ISOs, snapshots, logs, or secrets belong here.
- CTOS-managed mutation commands are not enabled yet.

Target model:

- CTOS-managed domains use `qemu:///system`.
- `scripts/ctos-vm` remains read-only until lifecycle commands receive an ADR.
- Network and storage definitions live here so the future VM build is reproducible.

Planned files:

- `networks/ctos-nat.xml`: dedicated CTOS NAT network.
- `pools/ctos-images.xml`: dedicated CTOS VM disk pool.
- `pools/ctos-snapshots.xml`: dedicated CTOS snapshot pool.
- `pools/ctos-iso.xml`: dedicated CTOS installer ISO pool.
- `profiles/ctos-vms.json`: planned VM resource/profile metadata.
- `domains/ctos-kali.install.xml`: install-phase Kali domain definition.

Infra command:

```bash
../scripts/ctos-libvirt-infra status
../scripts/ctos-libvirt-infra plan
../scripts/ctos-libvirt-infra apply
```

`apply` defines, starts, and marks only the CTOS network and storage pools for autostart. It refuses to overwrite conflicting live resources.

Kali domain command:

```bash
../scripts/ctos-kali status
../scripts/ctos-kali plan
../scripts/ctos-kali prepare-media
../scripts/ctos-kali define
../scripts/ctos-kali start-install
```

`define` creates the `ctos-kali.qcow2` volume and defines the shutoff domain. It does not start the VM or run the Kali installer.

`prepare-media` imports the Kali installer ISO into the `ctos-iso` pool so QEMU can read it without traversing the operator home directory.

`start-install` starts the existing install-phase domain and opens `virt-viewer`. The Kali installer remains manual and visible.
