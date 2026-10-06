# VM Lifecycle Model

Date: 2026-06-02

Scope: CTOS-managed libvirt domains on the T480 host. This model defines the target before any VM creation, start/stop automation, or snapshot automation.

## Decision Summary

- CTOS-managed domains use `qemu:///system`.
- `qemu:///session` remains observable by `scripts/ctos-vm`, but is not the CTOS control-plane target.
- CTOS-managed storage uses dedicated system pools, not the generic `default` pool:
  - `ctos-images`: `/var/lib/libvirt/ctos/images`
  - `ctos-snapshots`: `/var/lib/libvirt/ctos/snapshots`
  - `ctos-iso`: `/var/lib/libvirt/ctos/iso`
- Installer ISOs remain outside Git and must live in a libvirt-accessible pool before VM start.
- CTOS-managed guests use a dedicated NAT network:
  - network: `ctos-nat`
  - bridge: `virbr-ctos`
  - subnet: `192.168.130.0/24`
- No CTOS domain autostarts by default.
- No host shared folders by default.
- No inbound port forwarding by default.
- Snapshot automation starts with shutoff/offline disk snapshots only. Live snapshots are deferred until a guest-agent/filesystem-freeze policy exists.

## Why `qemu:///system`

The host is a cockpit/control plane, not a disposable user-session VM playground. CTOS needs persistent virtual networks, bridge/NAT management, future optional autostart control, and consistent virt-manager/virsh behavior.

`qemu:///system` is the right default for that. It gives libvirt the privileges needed for proper virtual networking and host-level VM lifecycle management. `qemu:///session` is useful for unprivileged experiments but has networking limitations and would create a split-brain risk for the cockpit.

## Domain Naming

Planned names:

- `ctos-kali`: Kali guest for authorized security work.
- `ctos-dev`: isolated CTOS/dev workstation guest.

Reserved:

- `ctos-ai`: only if AI workers later need a guest boundary.
- `ctos-game`: rejected for now; game mode should be a host performance mode unless a later GPU/VM decision changes this.

## Resource Policy

T480 visible capacity:

- 8 logical CPUs.
- about 16 GiB RAM.

Initial planned ceilings:

- `ctos-kali`: 2 vCPU, 6144 MiB RAM, 40 GiB qcow2 disk.
- `ctos-dev`: 2 vCPU, 6144 MiB RAM, 60 GiB qcow2 disk.

Mode rule:

- Kali and Dev may run separately.
- Kali + Dev + AI workers should not be treated as a normal steady state on 16 GiB RAM.
- Game mode stops CTOS VMs and AI workers before launching Minecraft.

## Storage Policy

Git contains only definitions, docs, and scripts. It must never contain:

- VM disks.
- ISOs.
- snapshots.
- generated domain XML from live libvirt if it contains environment-specific identifiers.
- logs, loot, reports, browser state, private keys, or tokens.

Future disk/media names:

- `/var/lib/libvirt/ctos/images/ctos-kali.qcow2`
- `/var/lib/libvirt/ctos/images/ctos-dev.qcow2`
- `/var/lib/libvirt/ctos/iso/kali-linux-2025.4-installer-amd64.iso`

The existing `/var/lib/libvirt/images/kali.qcow2` is not a CTOS-managed VM disk. It is currently only a sparse qcow2 stub and should be left untouched until a cleanup/import decision is made.

## Network Policy

Initial network:

- `ctos-nat` on `192.168.130.0/24`.
- host bridge address: `192.168.130.1`.
- DHCP range: `192.168.130.100` through `192.168.130.254`.
- NAT outbound allowed by libvirt network config.
- No inbound port forwards.

This is separate from the existing libvirt `default` network, which uses `192.168.122.0/24` on `virbr0`.

The dedicated CTOS network gives the cockpit a stable boundary to display and control without modifying generic/default libvirt state.

## Snapshot Policy

First implementation target:

- only snapshot shutoff domains.
- disk-only snapshots.
- no RAM snapshots.
- no live snapshots.
- explicit name required.
- explicit retention policy required before automatic cleanup.

Rationale:

Libvirt documents that running-guest disk snapshots may be crash-consistent rather than clean. A shutoff snapshot avoids that class of failure while the repo does not yet define guest-agent and filesystem-freeze behavior.

Deferred:

- live snapshots.
- memory/full-system snapshots.
- automatic retention pruning.
- block-commit/rebase automation.

## Lifecycle Commands Target

Future `scripts/ctos-vm` mutating commands may be added only after their behavior is documented:

- `define`: define repo-owned pools/network/domain XML.
- `start <name>`: start an existing CTOS domain.
- `shutdown <name>`: graceful shutdown only.
- `destroy <name> --force`: explicit hard stop, never an implicit fallback.
- `snapshot <name> <label>`: shutoff disk snapshot only in the first implementation.

No command should silently switch between `system` and `session`. CTOS-managed mutations target `qemu:///system`.

## Current Non-Goals

- No VM creation in this step.
- No deletion or migration of the existing `kali.qcow2` stub.
- No firewall/VPN/killswitch decision.
- No Kali install automation yet.
- No Dev VM OS selection yet.
- No AI worker placement decision yet.

## Verification

Checked on 2026-06-02:

- `virsh -c qemu:///system --readonly net-dumpxml default`
- `ip route`
- `ip addr show virbr0`
- `python -m json.tool libvirt/profiles/ctos-vms.json`
- `xmllint --noout libvirt/networks/ctos-nat.xml libvirt/pools/ctos-images.xml libvirt/pools/ctos-snapshots.xml`
- `virt-xml-validate libvirt/networks/ctos-nat.xml network`
- `virt-xml-validate libvirt/pools/ctos-images.xml storagepool`
- `virt-xml-validate libvirt/pools/ctos-snapshots.xml storagepool`

Relevant observed state:

- host LAN: `192.168.1.0/24`
- libvirt default network: `192.168.122.0/24`
- proposed CTOS network: `192.168.130.0/24`

## Applied State

The network and pool definitions from this model were applied on 2026-06-03 with `scripts/ctos-libvirt-infra apply`.

Live post-apply state is recorded in `context/12_libvirt_infra_state.md`.

The first Kali start attempt proved that installer ISOs under `/home/operator` are not usable by QEMU because `/home/operator` is not traversable by the QEMU/libvirt process. The Kali installer ISO was imported into `ctos-iso` on 2026-06-03.
