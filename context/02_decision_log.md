# Decision Log

All significant choices must be documented here before implementation.

Format:

```text
ID:
Date:
Status: proposed | accepted | rejected | blocked | superseded
Decision:
Context:
Options considered:
Sources:
Rationale:
Verification:
Consequences:
```

## ADR-0001: Use AGENTS.md plus context folder for Codex project knowledge

Date: 2026-05-04
Status: accepted

Decision:

Use a short repository-root `AGENTS.md` for durable Codex instructions and keep detailed knowledge in `context/`.

Context:

The user explicitly requested a local context folder and better agent configuration. OpenAI Codex documentation describes `AGENTS.md` as the project instruction file. The same documentation states Codex has a default project-doc size limit, so detailed memory should not be packed into one large instruction file.

Options considered:

- Put everything in `AGENTS.md`.
- Put only durable rules in `AGENTS.md` and detailed memory in `context/`.
- Use an undocumented filename such as `Setup.md` as the main instruction source.

Sources:

- OpenAI Codex AGENTS.md documentation, accessed 2026-05-04: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex config basics, accessed 2026-05-04: https://developers.openai.com/codex/config-basic
- OpenAI Codex skills documentation, accessed 2026-05-04: https://developers.openai.com/codex/skills
- OpenAI `agents.md` open format repository, accessed 2026-05-04: https://github.com/openai/agents.md

Rationale:

This gives Codex stable repo-local rules while keeping detailed project knowledge organized, editable, and less likely to be silently truncated.

Verification:

Files created in repo root and `context/`; final verification pending.

Consequences:

Future detailed context updates should go into `context/`, not into a growing `AGENTS.md`.

## ADR-0002: Install official VS Code binary and OpenAI Codex on T480

Date: 2026-05-24
Status: accepted

Decision:

Install Microsoft Visual Studio Code through AUR package `visual-studio-code-bin`, install Node.js/npm from Arch repositories, install Codex CLI with `npm install -g @openai/codex`, and install the official Codex VS Code extension `OpenAI.chatgpt`.

Context:

The T480 is EndeavourOS/Arch-like, reachable via `ssh operator@192.168.1.21`, with temporary passwordless sudo enabled for bootstrap. Git and yay are already installed; `code`, `node`, `npm`, and `codex` are not installed.

Options considered:

- `visual-studio-code-bin` from AUR: official Microsoft binary distribution, provides `code`/`vscode`, conflicts with `code`.
- `code` from Arch repositories: open-source Code - OSS build, but not the same Microsoft binary distribution.
- Manual tarball/RPM/deb: worse integration with Arch package management.
- Snap: not native to current EndeavourOS setup and unnecessary.

Sources:

- Microsoft VS Code Linux setup, accessed 2026-05-24: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code download page, accessed 2026-05-24: https://code.visualstudio.com/download
- AUR `visual-studio-code-bin`, accessed 2026-05-24: https://aur.archlinux.org/packages/visual-studio-code-bin
- ArchWiki Visual Studio Code, accessed 2026-05-24: https://wiki.archlinux.org/title/Visual_Studio_Code
- OpenAI Codex GitHub README, accessed 2026-05-24: https://github.com/openai/codex
- npm `@openai/codex`, accessed 2026-05-24: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI Codex extension, accessed 2026-05-24: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt

Rationale:

The user asked for VS Code and Codex on the ThinkPad itself. The official VS Code binary is the closest match to "VS Code" and has the expected Microsoft Marketplace behavior. OpenAI documents Codex CLI installation through npm, and the Marketplace extension ID is `OpenAI.chatgpt`.

Verification:

Completed on 2026-05-24 over SSH to `operator@192.168.1.21`:

- `code --version`: `1.121.0`, commit `f6cfa2ea2403534de03f069bdf160d06451ed282`, `x64`.
- `node --version`: `v26.2.0`.
- `npm --version`: `11.14.1`.
- `codex --version`: `codex-cli 0.133.0`.
- `code --list-extensions --show-versions`: `openai.chatgpt@26.519.32039`.
- Pacman packages: `linux 7.0.10.arch1-1`, `linux-lts 6.18.33-1`, `nodejs 26.2.0-1`, `npm 11.14.1-1`, `visual-studio-code-bin 1.121.0-1`.

Consequences:

This accepts Microsoft VS Code proprietary licensing and npm global installation. A reboot is recommended because the running kernel is still `6.18.26-2-lts` while installed LTS is `6.18.33-1`. The temporary sudoers rule must be removed after bootstrap.

## ADR-0003: Use grim and slurp for basic Hyprland screenshots

Date: 2026-05-26
Status: accepted

Decision:

Use the already-installed `grim` and `slurp` packages for basic Wayland screenshots on Hyprland. Add Hyprland keybinds that save full-screen and region screenshots under `~/Pictures/Screenshots`.

Context:

The user needs to capture the screen to show transient UI problems, such as a top-screen message hiding Waybar battery/Wi-Fi information. The T480 already has `grim 1.5.0-2` and `slurp 1.5.0-2` installed, while `wl-clipboard`, `swappy`, `hyprshot`, and `satty` are not installed. The immediate need is saving screenshot files, not annotation or clipboard workflow.

Options considered:

- `grim` only: works for full-screen screenshots but no region selection.
- `grim` + `slurp`: small, already installed, current Hyprland-documented Wayland workflow for region capture.
- `grim` + `slurp` + `wl-clipboard`: useful for clipboard copy, but would require a new package.
- `swappy`, `satty`, `hyprshot`, or HyprCapture: richer workflows, but unnecessary for the immediate capture need and would require additional package decisions.

Sources:

- Hyprland Wiki Screenshots & Recording, accessed 2026-05-26: https://wiki.hypr.land/Useful-Utilities/Screenshots-and-Recording/
- Arch Linux package `grim`, accessed 2026-05-26: https://archlinux.org/packages/extra/x86_64/grim/
- Arch Linux package `slurp`, accessed 2026-05-26: https://archlinux.org/packages/extra/x86_64/slurp/

Rationale:

This gives the smallest reliable screenshot workflow with no new installation and no extra desktop dependencies. It also stays compatible with the current Hyprland/Wayland setup.

Verification:

Local checks on 2026-05-26:

- `pacman -Q grim slurp`: `grim 1.5.0-2`, `slurp 1.5.0-2`.
- `which grim slurp hyprctl swaybg notify-send`: commands present.
- `grim -h`, `slurp -h`, and `swaybg --help` show the required options.

Consequences:

Screenshots are saved to disk under `~/Pictures/Screenshots`. Clipboard copy and annotation are intentionally deferred until `wl-clipboard`, `swappy`, `satty`, or another tool is researched and accepted.

## ADR-0004: Rename host workspaces around control and VM orchestration

Date: 2026-05-26
Status: accepted

Decision:

Replace the host Waybar workspace labels `RECON`, `EXPLOIT`, `REVERSE`, `DEV`, `AI`, `LOGS`, `VAULT`, `COMMS`, and `LAB` with host-control labels. As of 2026-06-16, the visible host strip is `CTRL`, `DESK`, `STATION`, `VMS`, `AI`, `VAULT`, `COMMS`, and `GAME`. Keep Hyprland workspace IDs numeric for stable native switching.

Context:

The previous workspace names were cyber-lab oriented and should move into the future Kali VM. The host should act as the clean control plane for VM orchestration, system status, local AI, personal work, and a later Minecraft/performance mode. This keeps the host boundary aligned with the project principle that offensive workflows belong in isolated lab VMs.

Options considered:

- Keep cyber labels on the host: rejected because it mixes Kali/lab mental model with the host control-plane role.
- Use one generic desktop set only: rejected because VM/AI/game modes need explicit places in the UI.
- Use a host cockpit model with short labels: accepted because it keeps Waybar readable and maps directly to planned repo layers.

Sources:

- Project brief and host/lab boundary in `context/00_project_brief.md`.
- Working agreements in `context/01_working_agreements.md`.
- Hyprland workspace/dispatcher documentation, accessed 2026-05-26: https://wiki.hypr.land/Configuring/Basics/Dispatchers/
- Waybar Hyprland workspace module documentation, accessed 2026-05-26: https://github.com/Alexays/Waybar/wiki/Module%3A-Hyprland
- Hyprland Workspace Rules documentation, accessed 2026-06-16: https://wiki.hypr.land/Configuring/Workspace-Rules/

Rationale:

The host UI should communicate what the host is responsible for: control, normal use, repo/config work, AI, VM control, secrets, communications, and game mode. Kali-specific names will be recreated inside the Kali guest where they match the task boundary.

Verification:

Completed on 2026-05-26:

- Updated `~/.config/waybar/config` labels.
- Fixed Waybar workspace CSS selector from `#workspace` to `#workspaces`.
- Kept Hyprland native workspace dispatchers for `SUPER+1..9`.
- Reloaded Hyprland.
- Restarted Waybar.
- `hyprctl configerrors` returned no errors.
- `hyprctl binds` confirmed native workspace dispatchers for keys `1` through `9`.

Updated on 2026-06-16:

- Removed visible `CODE`.
- Renamed `WORK` to `STATION`.
- Moved `VMS` to workspace 4, left of `AI`.
- Moved `GAME` to workspace 8.
- Added a workspace-specific DESK rule with no gaps, no border, and no rounding so the remote desktop frame fills the useful screen area under Waybar.

Consequences:

Future Kali desktop configuration should define the cyber workspaces. Future host dashboard work should build around `CTRL` and `VMS`, while `GAME` should become a host performance mode unless a later GPU/VM decision justifies gaming inside a guest. `STATION` is the general local work surface, including code/config work, until the host needs another visible workspace again. Internal Hyprland workspace names should stay numeric unless a future tested config proves named workspaces do not break native switching behavior.

## ADR-0005: Start control space with a stdlib local dashboard

Date: 2026-05-26
Status: accepted

Decision:

Create a first host control-space implementation under `control/` using Python standard library only:

- `control/tui.py` for an immediate terminal cockpit in `kitty`.
- `control/server.py` for a localhost HTTP dashboard on `127.0.0.1:8765`.
- `control/static/` for a browser-ready visual shell with a canvas globe.
- `scripts/ctos-control` as the launcher.
- `SUPER+C` as the Hyprland shortcut for the terminal cockpit.

Context:

The user asked to begin the control workspace after moving VS Code to `DESK`. The host currently has Python and Kitty but no installed browser package such as Firefox or Chromium. The dashboard should not pull in a frontend framework, browser, or service stack before the repo has package manifests and researched desktop/dashboard decisions.

Options considered:

- Install a browser and build a full web dashboard now: rejected for this step because it creates a package decision and larger dependency surface too early.
- Build only a terminal dashboard: useful immediately, but does not prepare the future visual cockpit.
- Build a stdlib terminal cockpit plus localhost web shell: accepted because it is usable now, auditable, and dependency-light.

Sources:

- Python `http.server` documentation, accessed 2026-05-26: https://docs.python.org/3/library/http.server.html
- Python `subprocess` documentation, accessed 2026-05-26: https://docs.python.org/3/library/subprocess.html
- MDN Canvas API documentation, accessed 2026-05-26: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

Rationale:

This establishes `CTRL` as a real control surface without installing new packages. Binding the HTTP server to localhost limits exposure, and the TUI gives an immediate cockpit even without a browser. The web shell preserves the visual direction for the later dashboard.

Verification:

Completed on 2026-05-26:

- `python -m py_compile control/status.py control/tui.py control/server.py`.
- `bash -n scripts/ctos-control`.
- `timeout 3 scripts/ctos-control tui` rendered host status.
- `scripts/ctos-control serve` started the localhost server.
- Local HTTP test returned JSON from `/api/status` when run outside the Codex network sandbox.
- `hyprctl clients` showed `CTOS_CONTROL` on workspace 1 and VS Code on workspace 2.
- `hyprctl binds` showed `SUPER+C`.

Updated on 2026-05-27:

- Expanded `/api/status` with CPU counters, thermal data, service state, parsed VM list, and planned modes.
- Reworked `control/static/` into the first cockpit view.
- `python -m py_compile control/status.py control/tui.py control/server.py`.
- `node --check control/static/app.js`.
- Restarted `scripts/ctos-control serve`.
- HTTP checks returned `200` for `/` and valid JSON for `/api/status`.

Consequences:

The dashboard reports unavailable libvirt or AI state instead of silently hiding it. Browser/front-end runtime selection remains open for a later researched decision. The current HTTP server is for localhost operator use only, not production or LAN exposure.

## ADR-0006: Add wl-clipboard for screenshot paste workflow

Date: 2026-05-26
Status: accepted

Decision:

Install Arch package `wl-clipboard` and route Hyprland screenshot binds through `scripts/ctos-screenshot`, saving screenshots under `~/Pictures/Screenshots` and copying the PNG image to the Wayland clipboard for immediate paste with `Ctrl+V`.

Context:

The user needs to paste screenshots directly into Codex/chat with `Ctrl+V`. Existing `grim` and `slurp` can create screenshots but do not set the Wayland clipboard. The package `wl-clipboard` provides `wl-copy` and `wl-paste`, which are the standard command-line utilities for Wayland clipboard operations.

Options considered:

- Keep file-only screenshots: rejected because it forces manual file attachment.
- Use `grim ... - | wl-copy`: accepted as the core mechanism, wrapped in a repo script for maintainability.
- Add screenshot annotation/history tools now: rejected for this step; clipboard paste is the immediate need.

Sources:

- Arch Linux package `wl-clipboard`, accessed 2026-05-26: https://archlinux.org/packages/extra/x86_64/wl-clipboard/
- Upstream `wl-clipboard`, accessed 2026-05-26: https://github.com/bugaevc/wl-clipboard
- ArchWiki Clipboard, accessed 2026-05-26: https://wiki.archlinux.org/title/Clipboard

Rationale:

`wl-clipboard` is small, packaged in Arch `extra`, and directly matches the Wayland/Hyprland clipboard requirement. A repo-owned wrapper script keeps Hyprland config simple and auditable.

Verification:

Completed on 2026-05-27:

- Added `scripts/ctos-screenshot`.
- Updated Hyprland screenshot binds to call the wrapper.
- Added French AZERTY top-row workspace binds.
- Reloaded Hyprland.
- `hyprctl configerrors` returned no errors.
- `hyprctl binds` showed `ampersand`, `eacute`, `quotedbl`, `apostrophe`, `parenleft`, `minus`, `egrave`, `underscore`, and `ccedilla` workspace binds.
- User installed `wl-clipboard 1:2.3.0-1` with sudo.
- `which wl-copy wl-paste`: `/usr/bin/wl-copy`, `/usr/bin/wl-paste`.
- Removed screenshot notifications from `scripts/ctos-screenshot`; screenshots now save and copy silently.

Consequences:

Screenshots become short-lived clipboard content as well as durable files. Clipboard history/persistence remains out of scope until explicitly researched. The screenshot workflow is intentionally silent: no desktop notification is emitted after capture.

## ADR-0007: Track host cockpit Hyprland and Waybar config in the repo

Date: 2026-05-27
Status: accepted

Decision:

Create repo-owned desktop config paths:

- `hyprland/hyprland.conf`
- `waybar/config`
- `waybar/style.css`
- `scripts/ctos-install-desktop`

The install script copies repo config into `~/.config/hypr/` and `~/.config/waybar/`, preserving timestamped backups when destination files differ.

Context:

The cockpit workspace, AZERTY binds, silent screenshot workflow, background, and Waybar labels were first applied directly to the live host config. The next project step is to make that state reproducible before adding VM controls, richer dashboard work, or mode scripts.

Options considered:

- Leave configs only under `~/.config`: rejected because it is not reproducible.
- Symlink directly from the repo: deferred because the repo layout and future dotfile manager are not decided yet.
- Copy with backup through a repo script: accepted as a simple and auditable first step.

Sources:

- Local repo blueprint: `context/07_repo_blueprint.md`
- Local project brief: `context/00_project_brief.md`
- Existing live configs under `~/.config/hypr/` and `~/.config/waybar/`

Rationale:

Copy-with-backup avoids hidden destructive changes while making the current desktop recoverable from Git. It also keeps the door open for a future researched dotfile manager decision.

Verification:

Completed on 2026-05-27:

- Repo `hyprland/hyprland.conf` matches live `~/.config/hypr/hyprland.conf`.
- Repo `waybar/config` matches live `~/.config/waybar/config`.
- Repo `waybar/style.css` matches live `~/.config/waybar/style.css`.
- `bash -n scripts/ctos-install-desktop`.
- `./scripts/ctos-install-desktop --dry-run`.

Consequences:

Future desktop changes should be made in the repo first, then installed to the live config. The dotfile-manager question remains open and should be researched before replacing the copy-with-backup script with symlinks or a manager such as Stow, chezmoi, or yadm.

## ADR-0008: Start VM automation with a read-only libvirt inventory CLI

Date: 2026-06-02
Status: accepted

Decision:

Add `scripts/ctos-vm` as a read-only libvirt helper with `list`, `status`, and `inspect` commands. The helper always calls `virsh` with `--readonly` and checks both `qemu:///system` and `qemu:///session` by default. Do not add start, shutdown, destroy, define, or snapshot mutation commands in this step.

Context:

The cockpit roadmap needs VM visibility before VM control. The current host has libvirt/QEMU installed, a default NAT network, storage pools, a Kali ISO, and a tiny `kali.qcow2` allocation stub, but no defined domains. The user wants the host to become the control plane for Kali, Dev, AI, and Game modes, while cyber-specific workflows move into isolated guests.

Options considered:

- Use `virt-manager` manually: useful for inspection, but not reproducible enough for the cockpit/repo workflow.
- Add full `ctos-vm start/stop/snapshot` immediately: rejected because there are no domains yet and snapshot/storage policy is not documented.
- Add read-only `ctos-vm list/status/inspect` first: accepted because it creates a safe observation layer and avoids silent assumptions.

Sources:

- libvirt `virsh` manpage, accessed 2026-06-02: https://www.libvirt.org/manpages/virsh.html
- libvirt connection URI documentation, accessed 2026-06-02: https://libvirt.org/uri.html
- libvirt VM lifecycle documentation, accessed 2026-06-02: https://wiki.libvirt.org/VM_lifecycle.html
- Local inventory: `context/10_libvirt_inventory.md`

Rationale:

`virsh --readonly` matches the current need: observe domains, networks, pools, volumes, and per-domain metadata without mutating libvirt state. Checking both system and session connections avoids hiding state behind the wrong URI. Keeping control actions out of scope prevents accidental VM lifecycle decisions before domain XML, storage ownership, networking, and snapshot policy are documented.

Verification:

Completed on 2026-06-02:

- `python -m py_compile scripts/ctos-vm control/status.py control/tui.py control/server.py`
- `node --check control/static/app.js`
- `scripts/ctos-vm list`
- `scripts/ctos-vm status`
- `scripts/ctos-vm --json status`
- `scripts/ctos-vm inspect kali` returned the expected "domain not found" error because no Kali domain is defined yet.

Consequences:

The dashboard and CLI now distinguish "no VM defined" from "libvirt unavailable". Kali remains a planned VM until a repo-owned domain definition exists. Future lifecycle commands require a new or updated ADR before implementation.

## ADR-0009: Use qemu system mode and dedicated CTOS pools/network for managed VMs

Date: 2026-06-02
Status: accepted

Decision:

CTOS-managed libvirt domains will use `qemu:///system`, not `qemu:///session`. The repo will carry non-applied XML definitions for a dedicated CTOS NAT network and storage pools:

- `libvirt/networks/ctos-nat.xml`
- `libvirt/pools/ctos-images.xml`
- `libvirt/pools/ctos-snapshots.xml`

Planned CTOS-managed domain names are `ctos-kali` and `ctos-dev`. CTOS domains will not autostart by default. Initial snapshot automation will support only shutoff disk snapshots; live and memory snapshots are deferred.

Context:

The T480 host is the cockpit/control plane. It needs predictable VM visibility, networking, and later lifecycle controls. Current inventory shows no defined domains, a generic `default` libvirt NAT network on `192.168.122.0/24`, and a Kali qcow2 stub that is not an installed VM. The host LAN is `192.168.1.0/24`, so `192.168.130.0/24` is available in the current observed routing table for a dedicated CTOS NAT network.

Options considered:

- Use `qemu:///session`: rejected because it has weaker/default networking behavior and would be a poor fit for host-level cockpit orchestration.
- Use the existing `default` network and `default` pool: rejected as the long-term model because CTOS-managed state should be explicit and separable from generic virt-manager/libvirt state.
- Use `qemu:///system` with dedicated CTOS network and pools: accepted because it is more predictable for lifecycle, networking, and future dashboard control.
- Enable live snapshots from the start: rejected until guest-agent/filesystem-freeze behavior is defined.

Sources:

- libvirt connection URI documentation, accessed 2026-06-02: https://libvirt.org/uri.html
- libvirt FAQ on `qemu:///system` vs `qemu:///session`, accessed 2026-06-02: https://wiki.libvirt.org/FAQ.html
- ArchWiki libvirt, accessed 2026-06-02: https://wiki.archlinux.org/title/Libvirt
- libvirt network XML documentation, accessed 2026-06-02: https://libvirt.org/formatnetwork.html
- libvirt storage management documentation, accessed 2026-06-02: https://libvirt.org/storage.html
- libvirt storage pool/volume XML documentation, accessed 2026-06-02: https://www.libvirt.org/formatstorage.html
- libvirt snapshot XML documentation, accessed 2026-06-02: https://libvirt.org/formatsnapshot.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`

Rationale:

System-mode libvirt is the better fit for a persistent host control plane with managed NAT networking and future lifecycle operations. Dedicated CTOS network and storage definitions make the boundary explicit, keep the generic `default` resources untouched, and give the dashboard stable names to report. Deferring live snapshots avoids crash-consistency and filesystem-freeze ambiguity while the guests are not yet configured.

Verification:

Completed on 2026-06-02:

- `virsh -c qemu:///system --readonly net-dumpxml default`
- `ip route`
- `ip addr show virbr0`
- JSON profile validated with Python `json.tool`.
- `xmllint --noout libvirt/networks/ctos-nat.xml libvirt/pools/ctos-images.xml libvirt/pools/ctos-snapshots.xml`
- `virt-xml-validate libvirt/networks/ctos-nat.xml network`
- `virt-xml-validate libvirt/pools/ctos-images.xml storagepool`
- `virt-xml-validate libvirt/pools/ctos-snapshots.xml storagepool`

Consequences:

The next implementation step should create/apply CTOS pools and network before defining domains. Future `ctos-vm define/start/shutdown/snapshot` commands must target `qemu:///system` explicitly and must not silently fall back to `qemu:///session`. The existing Kali qcow2 stub remains untouched until a cleanup or import decision is made.

## ADR-0010: Apply only CTOS libvirt infrastructure before defining domains

Date: 2026-06-03
Status: accepted

Decision:

Add `scripts/ctos-libvirt-infra` as a focused idempotent command for CTOS libvirt infrastructure. It supports `status`, `plan`, and `apply`, and only converges these resources on `qemu:///system`:

- network `ctos-nat`
- storage pool `ctos-images`
- storage pool `ctos-snapshots`
- storage pool `ctos-iso`

It must not define VM domains, create VM disks, modify the generic `default` network/pool, or delete existing resources. If a CTOS-named resource already exists but differs from the repo XML signature, the command fails instead of overwriting it.

Context:

The lifecycle model is accepted, but no CTOS live libvirt infrastructure exists yet. Applying the network and pools is the smallest useful mutation before building `ctos-kali`: it creates the stable libvirt boundary the cockpit will later target without installing an OS, creating a VM disk, or changing existing libvirt domains.

Options considered:

- Apply network, pools, and Kali domain in one step: rejected because it increases blast radius and mixes infrastructure convergence with guest definition.
- Extend `scripts/ctos-vm` directly: rejected for this step because `ctos-vm` currently means read-only VM inventory, and keeping mutation separate is easier to audit.
- Add a dedicated `ctos-libvirt-infra` command: accepted because it cleanly scopes the first live libvirt mutation to named infrastructure resources.

Sources:

- libvirt `virsh` manpage, accessed 2026-06-03: https://www.libvirt.org/manpages/virsh.html
- libvirt network XML documentation, accessed 2026-06-03: https://libvirt.org/formatnetwork.html
- libvirt storage management documentation, accessed 2026-06-03: https://libvirt.org/storage.html
- libvirt storage pool/volume XML documentation, accessed 2026-06-03: https://www.libvirt.org/formatstorage.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`

Rationale:

The script gives a reversible mental model even though the live operations are persistent: validate, inspect, plan, then apply. It avoids silent fallback by blocking on conflicts and partial read errors. It also keeps the host cockpit ready for future domain definitions while preserving the existing `default` libvirt setup untouched.

Verification:

Completed on 2026-06-03:

- `python -m py_compile scripts/ctos-libvirt-infra scripts/ctos-vm control/status.py control/tui.py control/server.py`
- `xmllint --noout libvirt/networks/ctos-nat.xml libvirt/pools/ctos-images.xml libvirt/pools/ctos-snapshots.xml`
- `virt-xml-validate libvirt/networks/ctos-nat.xml network`
- `virt-xml-validate libvirt/pools/ctos-images.xml storagepool`
- `virt-xml-validate libvirt/pools/ctos-snapshots.xml storagepool`
- `scripts/ctos-libvirt-infra plan`
- `scripts/ctos-libvirt-infra apply`
- `scripts/ctos-libvirt-infra apply` again returned `no changes needed`.
- Later on 2026-06-03, `ctos-iso` was added and `scripts/ctos-libvirt-infra apply` converged it without changing existing CTOS resources.
- `scripts/ctos-libvirt-infra --json status`
- `scripts/ctos-vm status`
- `virsh -c qemu:///system --readonly list --all` showed no domains.
- `virsh -c qemu:///system --readonly net-list --all` showed `ctos-nat` active/autostart/persistent.
- `virsh -c qemu:///system --readonly pool-list --all` showed `ctos-images` and `ctos-snapshots` active/autostart.
- `ip addr show virbr-ctos` showed `192.168.130.1/24`.
- Local cockpit API returned JSON with `vms.infra.ok: true`.

Consequences:

Future `ctos-kali` domain work can target stable names: `ctos-nat`, `ctos-images`, `ctos-snapshots`, and `ctos-iso`. Cleanup/removal commands remain out of scope and require a separate explicit decision.

## ADR-0011: Define ctos-kali as a shutoff install-phase domain

Date: 2026-06-03
Status: accepted

Decision:

Add `libvirt/domains/ctos-kali.install.xml` and `scripts/ctos-kali`. The command supports `status`, `plan`, and `define`. `define` creates only the `ctos-images/ctos-kali.qcow2` volume and defines the `ctos-kali` domain on `qemu:///system`; it does not start the VM or run the Kali installer.

The install-phase profile is:

- name: `ctos-kali`
- machine: q35
- firmware: BIOS/SeaBIOS, not OVMF
- OS metadata: `debian13` because local osinfo has no Kali entry
- memory: 6144 MiB
- vCPU: 2
- disk: 40 GiB qcow2, virtio
- CDROM: `/home/operator/iso/kali-linux-2025.4-installer-amd64.iso`
- network: `ctos-nat`, virtio
- graphics: SPICE
- autostart: no

Context:

The CTOS libvirt network and pools now exist. The next narrow step is to create a defined but shutoff Kali domain that is ready for a manual installer boot. This preserves the host boundary and avoids starting or installing a security-lab guest before the user is ready.

Options considered:

- Use virt-manager manually: rejected for reproducibility.
- Use `virt-install` to create and immediately boot the installer: rejected because it starts installation behavior too early.
- Generate a virt-install dry-run XML, remove generated UUID/MAC state, commit repo XML, and define with `virsh define`: accepted.
- Use UEFI/OVMF: rejected for this first profile because BIOS boot is sufficient for Kali and simpler for install-phase recovery.

Sources:

- Kali installation requirements, accessed 2026-06-03: https://www.kali.org/docs/installation/hard-disk-install/
- virt-install upstream manpage, accessed 2026-06-03: https://github.com/virt-manager/virt-manager/blob/main/man/virt-install.rst
- libvirt domain XML documentation, accessed 2026-06-03: https://www.libvirt.org/formatdomain.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`
- Local infra state: `context/12_libvirt_infra_state.md`

Rationale:

Kali's own documentation states that the default Xfce and `kali-linux-default` target should have at least 2 GiB RAM and 20 GiB disk; the CTOS profile's 6 GiB RAM and 40 GiB disk leave room for security tooling while respecting the T480's 16 GiB host limit. A shutoff domain lets the cockpit see and manage Kali before first boot without creating hidden install state.

Verification:

Completed on 2026-06-03:

- `virt-install --connect qemu:///system ... --dry-run --print-xml 1`
- `virt-xml-validate libvirt/domains/ctos-kali.install.xml domain`
- `xmllint --noout libvirt/domains/ctos-kali.install.xml libvirt/networks/ctos-nat.xml libvirt/pools/ctos-images.xml libvirt/pools/ctos-snapshots.xml`
- `python -m json.tool libvirt/profiles/ctos-vms.json`
- `python -m py_compile scripts/ctos-kali scripts/ctos-libvirt-infra scripts/ctos-vm control/status.py control/tui.py control/server.py`
- `scripts/ctos-kali plan`
- `scripts/ctos-kali define`
- `scripts/ctos-kali define` again returned `no changes needed`.
- `scripts/ctos-kali status`
- `scripts/ctos-kali --json status`
- `scripts/ctos-vm status`
- `virsh -c qemu:///system --readonly dominfo ctos-kali`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`
- `virsh -c qemu:///system --readonly domiflist ctos-kali`
- local cockpit API returned HTTP `200` and included `ctos-kali` as `shut off`.

Implementation note:

The first `scripts/ctos-kali define` created the volume and domain successfully, but the post-check initially returned non-zero because `qemu-img info` could not read the libvirt-created disk file as the operator user. The script was corrected to validate volume format and capacity through libvirt `vol-dumpxml`, which is the appropriate API for this permission model.

Consequences:

The next step after definition is a deliberate installer start, likely through virt-manager or a future `ctos-kali start-install` command. After installation, a follow-up domain profile should detach the ISO or change boot order so the installed disk is primary.

## ADR-0012: Start Kali installation only through an explicit visible command

Date: 2026-06-03
Status: accepted

Decision:

Add `scripts/ctos-kali start-install`. The command checks the existing install-phase domain, refuses incompatible state, starts `ctos-kali` only if it is shut off, and opens a visible graphical console unless `--no-viewer` is passed.

On Hyprland, the console launch path is:

- `hyprctl dispatch exec "virt-manager -c qemu:///system --show-domain-console ctos-kali"`

Fallback outside Hyprland is `virt-viewer --connect qemu:///system --wait ctos-kali`.

It does not:

- create or redefine the domain.
- create or resize the disk.
- automate the Kali installer.
- detach the ISO.
- create snapshots.

Context:

`ctos-kali` is already defined as a shutoff install-phase domain with Kali installer ISO attached. The next step should be visible to the user because the installer is interactive and creates guest state. The user asked to proceed, and the host has `virt-viewer`, `remote-viewer`, `virt-manager`, and Hyprland available.

Options considered:

- Start the VM manually with virt-manager: acceptable but not reproducible enough for the cockpit flow.
- Add a fully automated unattended Kali install: rejected; too much guest state and credential/config policy is undecided.
- Add explicit `start-install`: accepted because it starts the visible manual installer while keeping the command auditable.

Sources:

- libvirt `virsh start` help, checked locally on 2026-06-03.
- `virt-viewer --help`, checked locally on 2026-06-03.
- `virt-manager --help`, checked locally on 2026-06-03.
- `hyprctl clients`, checked locally on 2026-06-03.
- virt-viewer upstream project, accessed 2026-06-03: https://gitlab.com/virt-viewer/virt-viewer
- libvirt `virsh` manpage, accessed 2026-06-03: https://www.libvirt.org/manpages/virsh.html
- Local Kali domain state: `context/13_kali_domain_state.md`
- Local Kali install start state: `context/14_kali_install_start.md`

Rationale:

Starting the VM is a visible lifecycle transition. Keeping it behind a named command avoids hidden boot/install side effects while still making the cockpit workflow practical. In this Hyprland session, `virt-manager` launched through `hyprctl dispatch exec` stayed visible while direct detached `virt-viewer` did not.

Verification:

Completed on 2026-06-03:

- Initial `scripts/ctos-kali start-install` failed before boot because QEMU could not traverse `/home/operator` to read the installer ISO.
- Added `ctos-iso` pool under `/var/lib/libvirt/ctos/iso`.
- Imported the Kali ISO into `ctos-iso` with `scripts/ctos-kali prepare-media`.
- Redefined `ctos-kali` to use `/var/lib/libvirt/ctos/iso/kali-linux-2025.4-installer-amd64.iso`.
- `scripts/ctos-kali start-install` started the domain.
- `hyprctl dispatch exec "virt-manager -c qemu:///system --show-domain-console ctos-kali"` opened a visible console window.
- `virsh -c qemu:///system --readonly domstate ctos-kali`: `running`.
- `scripts/ctos-vm inspect ctos-kali` showed disk, ISO CDROM, `ctos-nat`, and no snapshots.
- `scripts/ctos-kali start-install --no-viewer` recognized the domain was already running and made no viewer change.

Consequences:

After Kali installation completes, CTOS needs a post-install transition: shut down, detach ISO or adjust boot profile, then create a baseline snapshot.

## ADR-0013: Split Kali install and installed boot profiles

Date: 2026-06-03
Status: accepted

Decision:

Keep the Kali installer domain profile as `libvirt/domains/ctos-kali.install.xml` and add an installed-system profile at `libvirt/domains/ctos-kali.xml`.

Add `scripts/ctos-kali finalize-install` to stop an installer VM when explicitly requested, preserve the existing domain UUID, redefine the persistent domain with the installed profile, optionally start the guest, and open the visible console.

The installed profile:

- boots from `hd` only.
- removes the installer ISO/CDROM from the domain.
- keeps `ctos-nat`, virtio disk/network, SPICE graphics, 6 GiB RAM, and 2 vCPU.
- sets `<on_reboot>restart</on_reboot>` for normal installed guest behavior.

Context:

The manual Kali installer reached completion, but the domain remained `paused (user)`. The install-phase domain still had the Kali ISO attached and booted from `cdrom` first, so simply restarting would risk returning to the installer. There was no active libvirt domain job.

Options considered:

- Resume the paused installer VM only: rejected because the persistent domain would still boot from the installer ISO first.
- Edit the live domain only through virt-manager: rejected because the repo would lose the VM lifecycle state.
- Replace the install profile with the installed profile: rejected because reinstall/recovery should remain explicit and reproducible.
- Keep separate install and installed profiles with an explicit finalize command: accepted.

Sources:

- libvirt domain XML documentation, already consulted 2026-06-03: https://www.libvirt.org/formatdomain.html
- libvirt `virsh` manpage, already consulted 2026-06-03: https://www.libvirt.org/manpages/virsh.html
- Local Kali install start state: `context/14_kali_install_start.md`
- Local Kali post-install state: `context/15_kali_post_install_boot.md`

Rationale:

Separate profiles make the lifecycle explicit: installer boot is a one-time/manual phase, installed boot is the normal operational phase. Removing the CDROM avoids accidental installer re-entry, and `on_reboot=restart` makes guest reboots behave like a normal VM.

Verification:

Completed on 2026-06-03:

- `python -m py_compile scripts/ctos-kali`
- `virt-xml-validate libvirt/domains/ctos-kali.xml domain`
- `xmllint --noout libvirt/domains/ctos-kali.xml libvirt/domains/ctos-kali.install.xml`
- `virsh -c qemu:///system --readonly domstate ctos-kali --reason`: `paused (user)`
- `virsh -c qemu:///system --readonly domjobinfo ctos-kali`: no active job
- `scripts/ctos-kali finalize-install --force-stop --start`
- `virsh -c qemu:///system --readonly domstate ctos-kali`: `running`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`: only `vda` attached
- `virsh -c qemu:///system --readonly dumpxml --inactive ctos-kali`: `boot dev='hd'`, no CDROM, `on_reboot=restart`
- `hyprctl clients`: visible `ctos-kali on QEMU/KVM` virt-manager console

Consequences:

Future Kali VM operations should use the installed profile by default. Reinstalling Kali requires deliberately redefining from the install profile and reattaching installer media. A baseline snapshot should be created only after the installed guest is logged into, networking is verified, and the guest is shut down cleanly.

## ADR-0014: Allow CTOS VM egress with a dedicated firewalld policy

Date: 2026-06-04
Status: blocked

Decision:

Use a dedicated firewalld policy named `ctos-vm-egress` to allow egress from the `libvirt` zone to the host's external `public` zone with IPv4 masquerade.

Proposed runtime/permanent policy:

- ingress zone: `libvirt`
- egress zone: `public`
- target: `ACCEPT`
- masquerade: enabled

Context:

The installed Kali guest is reachable from the host at `192.168.130.50` and can ping the host bridge gateway `192.168.130.1`. The host can reach the internet. The guest has a correct default route via `192.168.130.1` but cannot ping `1.1.1.1`, and DNS resolution fails. `ctos-nat` is active and `virbr-ctos` is assigned to firewalld zone `libvirt`; `wlan0` is in the default `public` zone. Root-only nftables/iptables inspection is unavailable without sudo.

Options considered:

- Change the Kali guest network again: rejected because the guest route and gateway reachability are correct.
- Add ad hoc nftables NAT rules: rejected for now because firewalld is the active firewall manager and unmanaged rules would be harder to audit.
- Disable firewalld temporarily: rejected because it weakens host policy and does not create a reproducible control.
- Create a firewalld policy for VM egress: proposed because it matches firewalld's zone/policy model and keeps the change auditable.

Sources:

- libvirt firewall documentation, accessed 2026-06-04: https://libvirt.org/firewall
- firewalld concepts, accessed 2026-06-04: https://firewalld.org/documentation/concepts.html
- firewall-cmd manual, accessed 2026-06-04: https://firewalld.org/documentation/man-pages/firewall-cmd.html

Rationale:

Firewalld's current model denies inter-zone forwarding by default unless a policy allows it. The host currently has the VM bridge in `libvirt` and Wi-Fi egress in `public`, so the narrowest durable fix is a named policy that permits only that zone path and enables masquerade for VM internet access.

Verification:

Blocked on 2026-06-04:

- `ctos-vm-egress` appears in active firewalld policies with ingress `libvirt` and egress `public`.
- Kali still cannot ping `1.1.1.1`.
- Kali can ping `192.168.130.1`, so guest route/gateway are correct.
- Host can ping `1.1.1.1`, so host internet egress is correct.
- Root-only firewalld/nftables inspection requires sudo and cannot be completed by Codex without operator password.

Next diagnostic is a temporary, named nftables NAT/forward table to prove whether host forwarding/NAT is the only remaining fault.

After applying any replacement fix, verify from Kali:

- `ping -c 2 1.1.1.1`
- `ping -c 2 deb.debian.org`

Consequences:

All interfaces in the `libvirt` zone can egress through `public` while this policy is active. If future CTOS VM networks need stricter separation, create a dedicated `ctos-vm` firewalld zone for `virbr-ctos` instead of sharing the generic `libvirt` zone.

## ADR-0015: Use a temporary nftables table to isolate Kali NAT failure

Date: 2026-06-04
Status: accepted

Decision:

Use a temporary nftables table named `ctos_vm_egress_test` to add only:

- forward allow from `virbr-ctos` to `wlan0`
- return allow from `wlan0` to `virbr-ctos` for established/related traffic
- IPv4 masquerade for `192.168.130.0/24` out `wlan0`

Context:

The firewalld policy approach is active but did not restore Kali egress. The guest reaches the host bridge and the host reaches the internet, so a runtime nftables test can prove whether an explicit host NAT/forward path fixes the failure.

Options considered:

- Continue changing Kali networking: rejected because route and gateway are already correct.
- Disable firewalld: rejected because it is too broad.
- Add a permanent unmanaged nftables rule immediately: rejected until runtime behavior is proven.
- Add a temporary named nftables table: proposed as the smallest reversible diagnostic.

Sources:

- nftables wiki NAT documentation, accessed 2026-06-04: https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)
- nftables wiki quick reference, accessed 2026-06-04: https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes
- Local Kali egress failure state in `context/05_task_board.md`

Rationale:

The test is narrowly scoped to the CTOS subnet and bridge, avoids changing the guest again, and can be removed with a single `nft delete table ip ctos_vm_egress_test` command.

Verification:

Pending:

- `ping -c 2 1.1.1.1` from Kali.
- `ping -c 2 deb.debian.org` from Kali.

Consequences:

If this runtime test works, the durable implementation should be converted into a documented firewalld/nftables host rule instead of leaving an unmanaged ad hoc state.

## ADR-0017: Add runtime CTOS egress allow rules to the standalone nftables forward chain

Date: 2026-06-04
Status: accepted

Decision:

Add a root-only helper, `scripts/ctos-firewall-fix-vm-egress`, that inserts two runtime rules into the existing standalone nftables chain `inet filter forward`:

- allow new/forwarded packets from `virbr-ctos` to `wlan0`
- allow established/related return packets from `wlan0` to `virbr-ctos`

Context:

The root firewall report showed that firewalld/libvirt rules are present and matching, but a separate `/etc/nftables.conf`-owned table exists:

- table: `inet filter`
- chain: `forward`
- hook: `forward`
- policy: `drop`
- rules: none

Because forwarded packets traverse all relevant base chains, this standalone default-drop forward chain blocks VM egress even though firewalld and libvirt allow it. Libvirt NAT rules exist for `192.168.130.0/24`, and firewalld policy `ctos-vm-egress` is active.

Options considered:

- Disable `nftables.service` and delete table `inet filter`: rejected for now because it changes firewall authority too broadly.
- Change `/etc/nftables.conf` permanently immediately: deferred until runtime behavior is verified.
- Add runtime accept rules only to the blocking chain: proposed as the smallest reversible test.

Sources:

- nftables wiki quick reference, accessed 2026-06-04: https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes
- libvirt firewall documentation, accessed 2026-06-04: https://libvirt.org/firewall
- Local firewall report: `/tmp/ctos-firewall-report.txt`

Rationale:

The existing host firewall already has default-drop input behavior from the standalone nftables table. Adding narrow forward exceptions preserves that posture while allowing only the CTOS VM bridge to egress via the current Wi-Fi uplink.

Verification:

Completed on 2026-06-04:

- run `sudo scripts/ctos-firewall-fix-vm-egress`
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 192.168.130.1`: 0% packet loss
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 1.1.1.1`: 0% packet loss
- `scripts/ctos-kali-agent run /usr/bin/getent hosts deb.debian.org`: returned Fastly/Debian host records

Consequences:

The helper changes runtime nftables state only. Because it fixed egress, the equivalent rules should be persisted in `/etc/nftables.conf` before taking a baseline VM snapshot.

## ADR-0018: Persist CTOS VM egress rules in `/etc/nftables.conf`

Date: 2026-06-04
Status: proposed

Decision:

Add `scripts/ctos-install-host-firewall`, a root-only installer that backs up `/etc/nftables.conf`, inserts the CTOS VM egress allow rules into the standalone `inet filter forward` chain, validates the file with `nft -c -f`, installs it, and reloads nftables.

Context:

The runtime rules added by `scripts/ctos-firewall-fix-vm-egress` fixed Kali egress. Without persistence, a reboot or nftables reload would reintroduce the default-drop forwarding bug.

Options considered:

- Leave runtime rules only: rejected because reboot would break Kali internet again.
- Disable `/etc/nftables.conf`: rejected because it also contains the current default-drop input policy.
- Persist narrow CTOS VM forward exceptions in `/etc/nftables.conf`: proposed.

Sources:

- Local `/etc/nftables.conf`
- nftables wiki quick reference, accessed 2026-06-04: https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes
- Local verification of ADR-0017

Rationale:

The standalone nftables table is currently part of host firewall posture. Adding narrow forward exceptions preserves default-drop behavior while making CTOS VM NAT reproducible.

Verification:

Completed on 2026-06-04:

- `bash -n scripts/ctos-install-host-firewall`
- `sudo scripts/ctos-install-host-firewall`
- `/etc/nftables.conf` contains CTOS VM egress rules in `inet filter forward`
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 1.1.1.1`: 0% packet loss
- `scripts/ctos-kali-agent run /usr/bin/getent hosts deb.debian.org`: returned Debian/Fastly records

Consequences:

This persists a Wi-Fi-specific uplink assumption: `wlan0`. If the host egress interface changes, the firewall model should be generalized or regenerated from current route state.

## ADR-0016: Use qemu-guest-agent for controlled Kali guest operations

Date: 2026-06-04
Status: accepted

Decision:

Use qemu-guest-agent as the first controlled host-to-Kali command channel and add `scripts/ctos-kali-agent` as a repo helper for `guest-ping` and `guest-exec`.

Context:

SSH was not yet available in the guest, but libvirt `qemu-agent-command ctos-kali '{"execute":"guest-ping"}'` returned successfully. The user asked for a way for Codex to interact with Kali directly because screenshot-by-screenshot workflow was too slow.

Options considered:

- Keep interacting only through screenshots and manual typing: rejected as too slow for diagnosis.
- Enable SSH immediately: deferred because it requires guest service/user policy decisions.
- Use qemu-guest-agent: accepted because the domain already has the guest-agent channel and the guest agent is responding.

Sources:

- libvirt `virsh qemu-agent-command` manual, accessed 2026-06-04: https://www.libvirt.org/manpages/virsh.html
- Local Kali post-install state: `context/15_kali_post_install_boot.md`

Rationale:

qemu-guest-agent gives a narrow, auditable control path for owned guest diagnostics without storing the user's Kali password and without opening a network service in the guest.

Verification:

Completed on 2026-06-04:

- `scripts/ctos-kali-agent ping`
- `scripts/ctos-kali-agent run /usr/bin/ip route`
- `scripts/ctos-kali-agent run /usr/bin/ip -br addr`
- `scripts/ctos-kali-agent run /usr/bin/pgrep -af 'orca|speech|voice|dictation'`

Consequences:

Guest-agent access runs commands with elevated guest privileges. Use it only for owned guest administration, diagnostics, and explicit user-approved changes. SSH can still be added later as a normal operator workflow once guest hardening decisions are made.

## ADR-0019: Create a shutoff external disk baseline snapshot for `ctos-kali`

Date: 2026-06-05
Status: accepted

Decision:

Add `scripts/ctos-kali snapshot-baseline <label>` and use it to create `ctos-kali-post-install-20260604` as a disk-only snapshot while the guest is shut off.

The command:

- refuses labels outside a small safe character set;
- verifies `ctos-snapshots` is running;
- verifies the active disk is the expected baseline source before the first baseline snapshot;
- optionally shuts down the guest through qemu-guest-agent;
- creates an external disk-only snapshot with `virsh snapshot-create-as --disk-only --atomic`;
- verifies the active disk switches to the overlay.

Context:

The VM lifecycle model requires first snapshot automation to use shutoff/offline disk snapshots only. Kali had been installed, booted, and verified for network/DNS. The user asked to proceed after confirming the VM was usable.

Options considered:

- Live snapshot: rejected because the repo has not defined a filesystem-freeze policy.
- Manual `virsh snapshot-create-as`: rejected because it is easy to mistype the disk path and creates undocumented state.
- Repo-owned shutoff external snapshot command: accepted.

Sources:

- Local VM lifecycle model: `context/11_vm_lifecycle_model.md`
- Local `virsh help snapshot-create-as`, checked 2026-06-04/05
- Local libvirt storage profile: `libvirt/profiles/ctos-vms.json`

Rationale:

An external disk snapshot keeps the original installed qcow2 as the baseline and moves future writes into a visible overlay under `ctos-snapshots`. This makes the restore point explicit without copying the entire VM disk into Git or into an unmanaged path.

Verification:

Completed:

- `scripts/ctos-kali snapshot-baseline post-install-20260604 --shutdown --timeout 180`
- `virsh -c qemu:///system --readonly snapshot-list ctos-kali --tree`: `ctos-kali-post-install-20260604`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`: `vda` points to `/var/lib/libvirt/ctos/snapshots/ctos-kali-post-install-20260604.overlay.qcow2`
- After host battery power-off and reboot, the snapshot metadata and overlay disk chain were still present.
- `ctos-kali` restarted successfully from the overlay.

Consequences:

The baseline snapshot represents the installed VM state before later LightDM/Orca remediation. The active overlay now carries those later fixes. A second snapshot should be created after the user confirms the post-login state is clean.

## ADR-0020: Disable Kali greeter screen reader with LightDM controls and an Orca diversion

Date: 2026-06-05
Status: accepted

Decision:

Disable the unwanted Kali voice/screen-reader behavior at the greeter and binary-launch levels:

- set the screen-reader GSettings key to `false` for `lightdm` and `ctos`;
- add exact-name `orca-autostart.desktop` XDG autostart overrides for `lightdm` and `ctos`;
- force LightDM greeter reader/a11y settings off;
- remove `~a11y` from the LightDM greeter indicators list;
- use `dpkg-divert --local --rename --add /usr/bin/orca`;
- replace `/usr/bin/orca` with a root-owned wrapper that exits immediately.

Context:

After rebooting the VM from the baseline overlay, `orca` and `speech-dispatcher` were again active. Process inspection showed `orca` was launched by `lightdm-gtk-greeter` as user `lightdm`, before the `ctos` user session. User-session autostart overrides were therefore insufficient.

Options considered:

- Only kill the processes: rejected because LightDM relaunched them.
- Only set user-session GSettings: rejected because `orca` was launched by the greeter.
- Purge `orca` and `speech-dispatcher`: deferred because package removal is broader than needed.
- Use LightDM config plus `dpkg-divert`: accepted because it is durable, reversible, and does not remove the Kali package.

Sources:

- Local process tree from Kali guest: `lightdm-gtk-greeter -> orca`
- Local `/etc/lightdm/lightdm-gtk-greeter.conf.original` accessibility option comments
- Local `dpkg-divert --list /usr/bin/orca`

Rationale:

The greeter ignored or bypassed the narrower controls and continued launching `orca`. A local diversion preserves package ownership metadata while ensuring any remaining call to `/usr/bin/orca` becomes inert.

Verification:

Completed:

- `runuser -u lightdm -- dbus-run-session gsettings get org.gnome.desktop.a11y.applications screen-reader-enabled`: `false`
- `runuser -u ctos -- dbus-run-session gsettings get org.gnome.desktop.a11y.applications screen-reader-enabled`: `false`
- `/etc/lightdm/lightdm-gtk-greeter.conf` contains:
  - `a11y-states = -contrast;-font;-keyboard;-reader`
  - `reader = /bin/false`
  - no `~a11y` indicator
- `dpkg-divert --list /usr/bin/orca`: local diversion to `/usr/bin/orca.distrib`
- Active process check found no non-zombie `orca`, `speech-dispatcher`, `sd_espeak-ng`, or `sd_dummy` processes.

Consequences:

This intentionally disables screen-reader functionality in the Kali VM. To revert, remove the wrapper and diversion, then restore the greeter config from `/etc/lightdm/lightdm-gtk-greeter.conf.ctos-before-a11y-disable`.

## ADR-0021: Add checkpoint snapshots for existing Kali overlay chains

Date: 2026-06-05
Status: accepted

Decision:

Add `scripts/ctos-kali snapshot-checkpoint <label>` for shutoff disk-only snapshots when `ctos-kali` already runs from a CTOS-managed overlay chain.

The command:

- requires an explicit safe label;
- verifies `ctos-snapshots` is running;
- verifies the active disk is either the original CTOS image or an overlay under `ctos-snapshots`;
- optionally shuts the guest down through qemu-guest-agent;
- creates a new external disk-only snapshot with `virsh snapshot-create-as --disk-only --atomic`;
- verifies `vda` switches to the new overlay.

Context:

`ctos-kali-post-install-20260604` was the first baseline snapshot. The LightDM/Orca fixes were applied after that snapshot and therefore lived in the active overlay. The user confirmed that Kali was clean after login, so the fixed state needed its own checkpoint before more work.

Options considered:

- Reuse `snapshot-baseline`: rejected because it intentionally refuses to snapshot when the active disk is no longer the original baseline image.
- Manually create a second `virsh` snapshot: rejected because it would be easy to create undocumented or misnamed libvirt state.
- Add a separate checkpoint command: accepted because it keeps baseline creation strict while allowing explicit later restore points.

Sources:

- Local VM lifecycle model: `context/11_vm_lifecycle_model.md`
- Local `virsh help snapshot-create-as`, checked 2026-06-05
- Live snapshot tree and disk state from `virsh --readonly`

Rationale:

The first baseline and later checkpoints have different invariants. A dedicated checkpoint command makes that distinction visible and avoids weakening the original baseline guard.

Verification:

Completed:

- `python -m py_compile scripts/ctos-kali scripts/ctos-kali-agent`
- `scripts/ctos-kali snapshot-checkpoint --help`
- `scripts/ctos-kali snapshot-checkpoint voice-fixed-20260605 --description ... --shutdown --timeout 180`
- `virsh -c qemu:///system --readonly snapshot-list ctos-kali --tree`: `ctos-kali-post-install-20260604 -> ctos-kali-voice-fixed-20260605`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`: `vda` points to `/var/lib/libvirt/ctos/snapshots/ctos-kali-voice-fixed-20260605.overlay.qcow2`
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 1.1.1.1`: 0% packet loss
- `scripts/ctos-kali-agent run /usr/bin/getent hosts deb.debian.org`: returned Debian/Fastly records
- Active voice process check returned no non-zombie voice/speech processes

Consequences:

The active Kali state is now the `voice-fixed` overlay. Future package/tool installation should happen after this checkpoint, and another checkpoint should be created before any high-risk Kali customization.

## ADR-0022: Expose only allowlisted `ctos-kali` actions in the local cockpit

Date: 2026-06-08
Status: accepted

Decision:

Extend the localhost CTOS dashboard with:

- detailed `ctos-kali` status in `/api/status`;
- a localhost-only POST endpoint, `/api/vm/action`;
- strict allowlisting for domain `ctos-kali` only;
- strict action allowlisting: `start`, `shutdown`, `console`, `checkpoint`;
- frontend buttons that disable impossible actions based on current VM state.

Context:

The Kali VM is installed, network-verified, voice-fixed, and protected by baseline/checkpoint snapshots. The next cockpit step is operational control from `CTRL`, without turning the dashboard into a generic remote shell.

Options considered:

- Keep the dashboard read-only: rejected because the cockpit needs basic VM lifecycle control.
- Expose arbitrary commands or arbitrary libvirt domains: rejected because it expands the control plane too far.
- Add a small allowlisted action endpoint for `ctos-kali`: accepted.

Sources:

- Local VM lifecycle model: `context/11_vm_lifecycle_model.md`
- Local Kali snapshot state: `context/16_kali_baseline_snapshot.md`
- Local `virsh` behavior verified with `domstate`, `domblklist`, `snapshot-list`, `start`, and `shutdown --mode agent`

Rationale:

The host cockpit should control owned lab VMs, but the first version should stay narrow. Limiting the endpoint to one known domain and four fixed actions keeps the behavior auditable and avoids accepting user-provided shell commands.

Verification:

Completed:

- `python -m py_compile control/status.py control/server.py scripts/ctos-kali scripts/ctos-kali-agent`
- `python -m py_compile control/tui.py control/status.py control/server.py`
- direct `control.tui.render(0)` check showed `KALI CONTROL`, snapshot chain, disk role, and health summary
- direct `control.status.snapshot()` check returned:
  - `kali_state`: `shut off`
  - `kali_snapshot`: `ctos-kali-voice-fixed-20260605`
- temporary server on `127.0.0.1:8766`
- `GET /api/status`: returned VM and host status JSON
- `POST /api/vm/action` with `{"domain":"ctos-kali","action":"shutdown"}`: returned no-op success while shut off
- `POST /api/vm/action` with `{"domain":"ctos-dev","action":"start"}`: returned allowlist rejection

Consequences:

The cockpit can now start, gracefully shut down, open console, and checkpoint `ctos-kali`. `checkpoint` remains offline-only; users must shut down the VM first.

## ADR-0023: Model the recovered tower as `ctos-core` in an EndeavourOS archipelago

Date: 2026-06-09
Status: accepted

Decision:

Create a secondary CTOS fleet mission:

- keep the T480 as the mobile admin and daily work machine;
- convert the recovered Windows tower into `ctos-core` only after hardware inventory, data backup, and an explicit install decision;
- keep EndeavourOS as the target OS for the tower and future worker nodes;
- start with an official EndeavourOS installer plus a separate CTOS bootstrap kit directory;
- defer custom/all-in-one EndeavourOS installer automation until package manifests and role bootstrap scripts are proven;
- keep initial fleet metadata Ansible-compatible, but do not install or require Ansible yet.

Context:

The user wants a future fleet where the tower becomes the central heavy node for workers, local AI capacity, visual desktop work, and update distribution. The T480 should remain the admin/godfather machine while still being comfortable for regular coding and Codex work.

Options considered:

- Turn the T480 into the central server: rejected because it must stay portable and usable as a laptop.
- Keep the recovered tower on Windows and build around that: rejected as the long-term CTOS target because the user wants EndeavourOS consistency.
- Build a custom all-in-one installer immediately: rejected because package manifests, disk policy, and role bootstrap are not proven yet.
- Use official EndeavourOS install first plus a CTOS kit: accepted as the lowest-risk path.

Sources:

- EndeavourOS installation and customization docs, accessed 2026-06-09: https://discovery.endeavouros.com/installation/customizing-the-endeavouros-install-process/
- EndeavourOS latest release/install context, accessed 2026-06-09: https://endeavouros.com/latest-release/
- Ansible inventory docs, accessed 2026-06-09: https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html
- Local repo blueprint: `context/07_repo_blueprint.md`
- Local cockpit roadmap: `context/09_cockpit_roadmap.md`

Rationale:

The first fleet step should be recoverable and auditable. A separate CTOS kit directory can carry scripts, docs, role metadata, and later package manifests without modifying installer internals or risking destructive disk automation. Once the role scripts are proven, EndeavourOS installer customization files can reduce friction.

Verification:

Completed:

- Added `context/17_archipelago_fleet_model.md`.
- Added `docs/ARCHIPELAGO.md`.
- Added `fleet/` role and inventory scaffolding.
- Added `bootstrap/README.md`.
- Added `scripts/ctos-build-usb-kit`.

Consequences:

The next real-world step is tower inventory and backup decision, not OS installation. Fleet package manifests, secrets policy, SSH trust, package/model caches, and Ansible adoption remain separate decisions.

## ADR-0024: Use a temporary foreground OpenSSH bridge for tower diagnostics

Date: 2026-06-12
Status: accepted

Decision:

Use a temporary USB-delivered PowerShell pack to:

- install the T480 public SSH key into `C:\ProgramData\ssh\administrators_authorized_keys`;
- start Windows `sshd.exe` in foreground mode with `-D -e`;
- keep the PowerShell window open only while the T480 connects.

Do not treat this as the final SSH service configuration for `ctos-core`.

Context:

The recovered tower is currently on Windows 10 Home. The built-in OpenSSH server capability is installed, the firewall rule exists, `sshd -t` passes, and manual debug mode successfully listens on TCP/22. However, `Start-Service sshd` fails with service exit code `1067` and no useful OpenSSH event log.

Options considered:

- Continue trying to fix the Windows service before any remote access: rejected for now because manual foreground `sshd` works and the tower is intended to be reinstalled later.
- Install WSL first: rejected as the first bridge because Windows hardware/service inventory is better accessed from PowerShell.
- Use a temporary foreground `sshd` bridge with key auth: accepted for short-lived local diagnostics.

Sources:

- Local tower diagnostic pack output under `ctos_tower_diag_output`, read 2026-06-12.
- Microsoft OpenSSH Windows installation/service docs previously consulted for ADR-0023.

Rationale:

This creates a narrow local admin bridge without exposing passwords in chat and without spending more time repairing a Windows service on a machine that is expected to become EndeavourOS. The key is public, and the PowerShell window acts as an explicit on/off switch.

Verification:

Completed:

- Diagnostic output confirmed `OpenSSH.Server` installed.
- `sshd -t` returned `LASTEXITCODE=0`.
- Foreground debug run showed `Server listening on :: port 22` and `Server listening on 0.0.0.0 port 22`.
- USB pack `ctos_tower_ssh_link/` was staged with key install and foreground launch scripts.
- T480 reached TCP/22 on `192.168.1.18`.
- Public-key login succeeded as `desktop-lalfaj9\admin`.
- Added and verified `scripts/ctos-tower test` and `scripts/ctos-tower inventory`.

Consequences:

Use the bridge only for inventory/bootstrap preparation while the tower remains on Windows, then prefer EndeavourOS-native SSH after install.

## ADR-0025: Install the tower as a simple EndeavourOS `ctos-core` V1

Date: 2026-06-12
Status: accepted

Decision:

Wipe Windows from the recovered tower and install EndeavourOS bare metal as `ctos-core`.

For the first same-day install:

- use the official EndeavourOS installer rather than a custom ISO;
- install the OS on the 1 TB WDC NVMe;
- use Xfce as the V1 desktop baseline;
- apply CTOS packages and service scaffolding after first boot with `bootstrap/ctos-apply-role`;
- initialize the 500 GB Samsung SATA SSD separately as `/srv/ctos` with `bootstrap/ctos-init-core-storage`;
- keep AUR packages, secrets distribution, AI services, package caches, and model caches out of the V1 bootstrap.

Context:

The user explicitly wants no Windows on the tower and wants EndeavourOS as the common fleet base. Current tower hardware is usable but not yet final: ASUS ROG STRIX B550-F GAMING, Ryzen 5 2400G, 8 GiB RAM, GTX 1650, 1 TB NVMe, and 500 GB SATA SSD. Future RX 6600 and Ryzen 7 5700X upgrades are planned, but PSU, BIOS, cooler, and RAM upgrades are not confirmed yet.

Options considered:

- Build a custom EndeavourOS ISO now: rejected because package manifests and post-install scripts were not proven and destructive disk automation would be premature.
- Install a heavy/polished desktop now: rejected for V1 because the tower currently has 8 GiB RAM and the immediate goal is a recoverable central node.
- Keep Windows or dual boot temporarily: rejected because the user explicitly chose a wipe path.
- Use official EndeavourOS install plus a CTOS post-install kit: accepted as the fastest auditable path.

Sources:

- EndeavourOS installer/customization documentation, accessed 2026-06-12: https://discovery.endeavouros.com/installation/customizing-the-endeavouros-install-process/
- EndeavourOS latest release/install context, accessed 2026-06-12: https://endeavouros.com/latest-release/
- Btrfs subvolume/filesystem documentation, accessed 2026-06-12: https://btrfs.readthedocs.io/en/latest/Subvolumes.html
- Arch Linux Xfce package group index, accessed 2026-06-12: https://archlinux.org/groups/x86_64/xfce4/
- Local tower diagnostic state: `context/18_tower_diagnostic_state.md`
- Local package availability checks with `pacman -Si` and `pacman -Sgq`, 2026-06-12.

Rationale:

The first `ctos-core` should come online quickly, be easy to recover, and avoid hiding destructive disk choices in scripts. Xfce gives a stable graphical desktop on the current 8 GiB RAM state. The NVMe carries the OS and active work; the SATA SSD becomes a service/cache/storage root only after the installed system is verified. This preserves the future architecture while keeping today's install practical.

Verification:

Completed before staging the USB kit:

- Added `docs/TOWER_CTOS_CORE_INSTALL.md`.
- Added package manifests under `bootstrap/manifests/`.
- Added `bootstrap/ctos-apply-role`.
- Added `bootstrap/ctos-init-core-storage`.
- `bash -n bootstrap/ctos-apply-role`
- `bash -n bootstrap/ctos-init-core-storage`
- `bootstrap/ctos-apply-role ctos-core plan`
- non-group pacman package names resolve with local `pacman -Si`.
- `xfce4` and `xfce4-goodies` resolve with local `pacman -Sgq`.
- `scripts/ctos-build-usb-kit /tmp/ctos-core-kit-clean3-2`
- physical USB copy attempted but blocked by stale `/tmp/ctos-usb` I/O errors after `/dev/sdb` disappeared.

Consequences:

The tower can be installed today with a documented, low-magic path. Heavy services, local AI runtime, LAN caches, RAM/GPU/CPU tuning, and AUR/VS Code installation remain separate follow-up decisions after `ctos-core` boots cleanly and is reachable from the T480.

## ADR-0026: Use a USB round-trip helper for first tower network recovery

Date: 2026-06-12
Status: accepted

Decision:

Add `bootstrap/roles/ctos-core/network-usb/ctos-core-netfix` and copy it to the CTOS USB as `/ctos-core-netfix/ctos-core-netfix`.

The helper supports:

- `diag`: collect a tower-side network report into `outputs/`;
- `wifi`: recreate a NetworkManager Wi-Fi profile with explicit `wifi-sec.key-mgmt`;
- `iphone`: attempt iPhone USB tethering through available kernel modules, NetworkManager, and `usbmuxd`/`libimobiledevice` if installed;
- `auto`: try iPhone tethering and then collect diagnostics.

Context:

After the offline EndeavourOS install, the tower can scan Wi-Fi networks but connection attempts fail with `802-11-wireless-security.key-mgmt: property is missing`. The tower has no working Ethernet path, no SSH link yet, and the user has an iPhone 12 Pro Max connected by USB tethering.

Options considered:

- Continue debugging only through screenshots: too slow and error-prone.
- Require Internet first to install packages: circular dependency.
- Use a USB round-trip script: accepted because the T480 can prepare the script and the tower can return reports on the same key.

Sources:

- NetworkManager `nmcli` reference, accessed 2026-06-12: https://networkmanager.dev/docs/api/latest/nmcli.html
- NetworkManager 802.11 wireless security settings, accessed 2026-06-12: https://networkmanager.dev/docs/api/latest/settings-802-11-wireless-security.html
- Local `pacman -Si` package checks for `networkmanager`, `usbmuxd`, `libimobiledevice`, and `ifuse`.

Rationale:

The first recovery path should work without LAN, SSH, or GUI tools. NetworkManager is already the EndeavourOS networking baseline, and the reported error maps directly to a missing Wi-Fi security property. The script asks for the Wi-Fi password interactively and does not write it to logs.

Verification:

Completed on the T480:

- `bash -n bootstrap/roles/ctos-core/network-usb/ctos-core-netfix`
- `bootstrap/roles/ctos-core/network-usb/ctos-core-netfix --help`
- copied to `/tmp/ctos-usb/ctos-core-netfix/ctos-core-netfix`
- `bash -n /tmp/ctos-usb/ctos-core-netfix/ctos-core-netfix`
- `/tmp/ctos-usb/ctos-core-netfix/ctos-core-netfix --help`
- `sync`

Consequences:

Until SSH works, diagnostics move by USB. The script may enable/start NetworkManager and, if present, `usbmuxd`. It does not install packages, expose remote services, or store secrets.

## ADR-0027: Use T480 Ethernet shared mode as tower rescue network

Date: 2026-06-14
Status: accepted

Decision:

Configure the T480 Ethernet profile `Wired connection 1` on interface `enp0s31f6` with NetworkManager `ipv4.method shared` and `ipv6.method ignore`.

Context:

The freshly installed tower has no reliable Wi-Fi/USB tethering path yet, but it detects a wired Ethernet connection to the T480. The T480 has working Internet over Wi-Fi (`Livebox-8F18`) and can act as the temporary rescue router.

Options considered:

- Keep using USB round-trips only: accepted as fallback, but slow.
- Direct static-only Ethernet link: useful for SSH, but does not give the tower Internet by itself.
- NetworkManager shared mode on the T480: accepted because it provides a local Ethernet subnet and NAT/DHCP from T480 Wi-Fi.

Sources:

- NetworkManager IPv4 `shared` method documentation, accessed 2026-06-14: https://networkmanager.dev/docs/api/latest/settings-ipv4.html
- Local T480 checks: `nmcli dev status`, `ip -brief addr`, `ip route`.

Rationale:

This is the smallest reversible way to make the T480 a rescue uplink for the tower without introducing a permanent router/service stack. NetworkManager owns the DHCP/NAT behavior and can be reverted by changing the profile back to `ipv4.method auto` or disconnecting the cable.

Verification:

Completed:

- `enp0s31f6` shows `UP,LOWER_UP`.
- `nmcli con modify "Wired connection 1" ipv4.method shared ipv6.method ignore connection.autoconnect yes`.
- `nmcli con up "Wired connection 1"`.
- `enp0s31f6` has `10.42.0.1/24`.
- default route remains Wi-Fi via `192.168.1.1` on `wlan0`.
- no tower ARP entry was visible immediately after activation.
- added `bootstrap/roles/ctos-core/ethernet-rescue/ctos-ethernet-rescue`.
- `bash -n bootstrap/roles/ctos-core/ethernet-rescue/ctos-ethernet-rescue`.
- copied the rescue pack to `/tmp/ctos-usb/ctos-ethernet-rescue/`.
- `bash -n /tmp/ctos-usb/ctos-ethernet-rescue/ctos-ethernet-rescue`.

Consequences:

The tower should use DHCP on its wired profile, or static fallback `10.42.0.2/24` gateway `10.42.0.1` DNS `10.42.0.1` or `1.1.1.1`. Once the tower network is repaired, this rescue profile can remain as an emergency path or be reverted.

## ADR-0028: Preserve the tower's existing display manager during bootstrap

Date: 2026-06-14
Status: accepted

Decision:

`bootstrap/ctos-apply-role` enables `lightdm.service` only when no `/etc/systemd/system/display-manager.service` is already configured.

Context:

The freshly installed tower already reaches a usable graphical session. The first `ctos-core` bootstrap should make the machine reproducible and remotely manageable without silently replacing the current greeter/session stack.

Sources:

- Local script review of `bootstrap/ctos-apply-role`.
- systemd display manager convention: `/etc/systemd/system/display-manager.service` is the active display-manager alias.

Rationale:

Changing the display manager is user-visible and can make recovery harder if the current desktop is already working. Installing Xfce/lightdm remains allowed by the package manifests, but activation is conservative until the desktop baseline is explicitly chosen.

Verification:

Pending tower apply. The script plan now states that `lightdm` is enabled only if no display manager is already configured.

Consequences:

The bootstrap may install desktop packages without forcing a login-manager switch. A later desktop cleanup step can deliberately choose Xfce/lightdm, SDDM/KDE, or another baseline after we inspect the live tower state.

## ADR-0029: Use explicit package names in bootstrap manifests

Date: 2026-06-15
Status: accepted

Decision:

Replace pacman group names in `bootstrap/manifests/desktop-xfce.pacman` with explicit Xfce package names, and add `crun` explicitly as the OCI runtime provider for container tooling.

Context:

The first `ctos-core` apply reached pacman's dependency resolution but stopped before the transaction. The transcript shows interactive prompts for `xfce4`, `xfce4-goodies`, replacement packages, and the `oci-runtime` provider. No `/etc/ctos-role` marker, `/opt/ctos/repo`, or `/srv/ctos` directories were created afterward, and major role packages remained missing.

Sources:

- Attached bootstrap transcript from 2026-06-15.
- Tower checks over SSH: `/etc/ctos-role` missing, no pacman lock, no pacman process, major role packages absent.
- Local `pacman -Si` verification for the explicit Xfce packages and `crun`.

Rationale:

Role manifests should be deterministic and scriptable. Pacman group names are convenient by hand but create broad interactive selections during automated bootstrap. Explicit packages keep the desktop baseline auditable and reduce install size and prompt count.

Verification:

Completed on the T480:

- `bash -n bootstrap/ctos-apply-role`
- `bootstrap/ctos-apply-role ctos-core plan`
- `pacman -Si` for each newly explicit Xfce package and `crun`

Consequences:

The next apply may still need normal pacman upgrade confirmation, but it should no longer ask the operator to select all members of `xfce4` and `xfce4-goodies`, nor ask which OCI runtime provider to use.

## ADR-0030: Refresh package keyrings before ctos-core full upgrade

Date: 2026-06-15
Status: accepted

Decision:

`bootstrap/ctos-apply-role` now runs `pacman -Sy --needed archlinux-keyring endeavouros-keyring` before the full role package upgrade/install, then repopulates the local pacman keyrings.

Context:

The second apply attempt reached package signature verification and failed before transaction commit because key `9B7A287D9A2EC608` was missing from the tower's local keyring. The log ended with `required key missing from keyring` and `Errors occurred, no packages were upgraded`.

Sources:

- Live apply output from 2026-06-15.
- Arch packaging practice: update `archlinux-keyring` before large upgrades when local package databases reference packages signed by newer maintainer keys.
- Local script verification with `bash -n bootstrap/ctos-apply-role`.

Rationale:

Refreshing keyring packages preserves pacman's signature verification model. Disabling signature checks or lowering `SigLevel` is rejected because it would weaken the package trust boundary for the new `ctos-core` node.

Verification:

Completed on 2026-06-15:

- `bootstrap/ctos-apply-role ctos-core apply --yes` updated `archlinux-keyring` and `endeavouros-keyring` before the full role transaction.
- The following full package install/upgrade completed and wrote `/etc/ctos-role`.
- Tower verification over SSH confirmed active `NetworkManager`, `sshd`, and `avahi-daemon`, preserved SDDM as the active display manager, installed the expected role packages, and retained working DNS through the T480 link.

Consequences:

The bootstrap performs one package database sync for keyrings, then immediately performs the full `pacman -Syu --needed` role install. This avoids a long-lived partial-upgrade state.

## ADR-0031: Use and remove a narrow temporary sudo rule for tower bootstrap

Date: 2026-06-15
Status: accepted

Decision:

Use a temporary `/etc/sudoers.d/ctos-bootstrap` rule only for `/home/ctos/T480/bootstrap/ctos-apply-role`, then remove it immediately after the role apply and verification.

Context:

The tower bootstrap needed repeated privileged package/service operations over SSH. Full interactive sudo through the remote command path was brittle, and a broad passwordless sudo rule would leave an unnecessary persistent privilege path on the new `ctos-core` node.

Sources:

- Local helper `bootstrap/ctos-enable-bootstrap-sudo`.
- Local cleanup mode `bootstrap/ctos-apply-role ctos-core cleanup-sudo`.
- SSH verification output from 2026-06-15.

Rationale:

The rule is narrower than granting full passwordless sudo, and it is short-lived. It still trusts a user-writable path during bootstrap, so it must not persist beyond the initial controlled apply. The cleanup mode resyncs the repo copy and removes the rule as the last privileged bootstrap action.

Verification:

Completed on 2026-06-15:

- `/etc/sudoers.d/ctos-bootstrap` parsed successfully before apply.
- `ctos-core` role apply completed through the temporary rule.
- `bootstrap/ctos-apply-role ctos-core cleanup-sudo` reported `temporary CTOS bootstrap sudo rule removed`.
- Follow-up `sudo -n` over SSH returned `sudo: a password is required`, confirming the passwordless bootstrap path is no longer active.

Consequences:

Future privileged maintenance on `ctos-core` requires normal sudo authentication or a newly documented, scoped helper. The temporary bootstrap mechanism should not be treated as a standing administration interface.

## ADR-0032: Make T480-to-ctos-core cockpit integration status-only

Date: 2026-06-15
Status: accepted

Decision:

Add `scripts/ctos-core` as a T480-side SSH helper for `ctos@10.42.0.2`, and expose its JSON status in the local CTOS cockpit. Keep the first integration read-only/status-only.

Context:

The tower is now installed as `ctos-core`, reachable from the T480 over the Ethernet rescue link, and has `/srv/ctos` on the SATA SSD. The next useful step is making the T480 cockpit aware of the tower without turning the dashboard into an unchecked remote administration surface.

Sources:

- Local verified SSH access to `ctos@10.42.0.2`.
- Live `ctos-core` checks from `scripts/ctos-core status`.
- Existing cockpit boundary in `control/server.py`, `control/status.py`, and `control/README.md`.

Rationale:

Read-only SSH status gives the T480 immediate fleet visibility while preserving the safety boundary after the temporary bootstrap sudo rule was removed. Mutating actions such as package upgrades, service changes, reboot, disk formatting, or worker deployment should be added later as explicit, narrow commands with their own documentation and verification.

Verification:

Completed on 2026-06-15:

- `scripts/ctos-core status` reports `ctos-core`, kernel `7.0.12-arch1-1`, `/srv/ctos` on `/dev/sda1`, working T480/DNS checks, active core services, and passwordless sudo closed.
- `scripts/ctos-core status --json` emits parseable JSON.
- `control.status.snapshot()` includes `core.available=true`, `core.hostname=ctos-core`, `core.storage.srv.source=/dev/sda1`, and `core.storage.srv.writable=true`.
- Terminal TUI renders a `CTOS CORE` section.
- Local dashboard `/api/status` includes the `core` object after starting `scripts/ctos-control serve`.

Consequences:

The cockpit can now display the tower as part of the archipelago. Remote changes on `ctos-core` still require an explicit command path and normal sudo authentication.

## ADR-0033: Start ctos-core services with a non-daemon /srv/ctos layout

Date: 2026-06-15
Status: accepted

Decision:

Create the first `ctos-core` service foundation as user-writable directories under `/srv/ctos`, plus a T480-to-core repo subset sync. Do not enable package cache daemons, worker daemons, HTTP services, or LAN ports in this step.

Context:

`ctos-core` now has a dedicated SATA-backed `/srv/ctos` and is visible from the T480 cockpit. The next useful step is to give package/cache/model/worker concepts real paths without committing to a network service stack before the fleet security model and package-cache implementation are chosen.

Sources:

- Live `/srv/ctos` state on `ctos-core`.
- Local `scripts/ctos-core plan-services`, `apply-layout`, and `sync-repo`.
- Existing CTOS fleet model in `context/17_archipelago_fleet_model.md`.

Rationale:

A directory layout is reversible, auditable, and low-risk. It gives later package cache, Git mirror, model cache, and worker scheduler tasks stable mount-backed locations while avoiding premature daemon exposure. Copying a safe repo subset to `/srv/ctos/repo/t480` gives the tower a local copy for inspection and recovery without copying `.git`, Codex state, VM disks, ISOs, raw images, or logs.

Verification:

Completed on 2026-06-15:

- `scripts/ctos-core plan-services` renders the non-daemon layout plan.
- `scripts/ctos-core apply-layout` created 14 directories under `/srv/ctos`.
- `/srv/ctos/state/layout-v1.json` exists.
- `scripts/ctos-core sync-repo` copied the safe repo subset to `/srv/ctos/repo/t480`.
- `scripts/ctos-core status --json` reports `layout.complete=true` and `layout.marker_exists=true`.
- The local dashboard `/api/status` reports `core.layout.complete=true`.

Consequences:

`ctos-core` now has stable storage paths for future services. The next service decision must separately choose whether to expose a LAN Git mirror, Arch/EndeavourOS package cache, model cache, or worker queue, including port binding, firewall, authentication, update cadence, and rollback behavior.

## ADR-0034: Start fleet inventory as declarative metadata plus explicit live pulls

Date: 2026-06-15
Status: accepted

Decision:

Create `fleet/nodes.json` as the first CTOS archipelago inventory library and add `scripts/ctos-fleet` to render node/feature status. Live data is collected by explicit pulls only: local T480 reads and SSH reads through `scripts/ctos-core` for the tower.

Context:

The archipelago roadmap now includes remote tower control from the T480, a machine inventory library, later node constants/heartbeats toward `ctos-core`, and future multi-SSD server expansion. The fleet needs a stable node registry before adding background telemetry or services.

Sources:

- User-requested feature tracks from 2026-06-15.
- Existing `fleet/` scaffolding.
- Verified `scripts/ctos-core status --json` output.

Rationale:

A declarative JSON inventory is simple, auditable, and does not introduce external dependencies. Explicit live pulls avoid a premature monitoring daemon, port exposure, authentication model, retention policy, or background write path. This gives the T480 and cockpit a global view today while leaving `ctos-core` telemetry ingestion as a later documented service decision.

Verification:

Completed on 2026-06-15:

- `python -m json.tool fleet/nodes.json`.
- `python -m py_compile scripts/ctos-fleet`.
- `scripts/ctos-fleet list`.
- `scripts/ctos-fleet features`.
- `scripts/ctos-fleet status` shows `ctos-t480` and `ctos-core` online and `ctos-worker-01` planned.
- Dashboard `/api/status` includes `fleet.available=true` and the expected node/feature records.

Consequences:

Future telemetry/constants, remote control, and storage expansion work can reference stable node IDs and feature tracks. Any always-on telemetry receiver on `ctos-core` remains deferred until data model, security, and retention decisions are made.

## ADR-0035: Start tower remote control as tunnel-first inventory and command generation

Date: 2026-06-15
Status: accepted

Decision:

Add `scripts/ctos-remote` as a non-mutating T480-side helper for the `ctos-core` remote-control track. It inventories local viewer packages, tower server packages, graphical sessions, relevant unit files, and common RDP/VNC listeners. It can print SSH tunnel commands but does not install packages, start services, open firewall rules, or create a persistent tunnel.

Context:

The user wants a VM/desktop remote-control path from the T480 to the tower while keeping the T480 usable as the main work/admin machine. The tower is installed as EndeavourOS `ctos-core`, reachable at `ctos@10.42.0.2`, and currently uses SDDM with a graphical desktop. A premature remote desktop service would increase the attack surface and make debugging harder.

Sources:

- Local `ctos-core` SSH probe on 2026-06-15.
- Local package database check on 2026-06-15: `pacman -Si krdp krfb freerdp remmina tigervnc waypipe wayvnc moonlight-qt`.
- Local package file inspection on 2026-06-15: `krdp` provides `usr/bin/krdpserver`, `app-org.kde.krdpserver.service`, and `kcm_krdpserver`; `freerdp` provides `wlfreerdp3` and `xfreerdp3`.
- KDE KRdp source inspection on 2026-06-15: `server/main.cpp` documents `--address`, `--port`, PAM auth, and username/password options; `krdpserversettings.kcfg` documents `ListenPort`, `Users`, `SystemUserEnabled`, and `Autostart`.
- KDE KRFB Desktop Sharing app page: https://apps.kde.org/krfb/
- FreeRDP project: https://www.freerdp.com/
- TigerVNC project: https://www.tigervnc.org/
- Waypipe project: https://gitlab.freedesktop.org/mstoeckl/waypipe

Rationale:

SSH is already verified, auditable, and recoverable. A tunnel-first RDP/VNC path lets the tower desktop be tested without opening a permanent LAN listener. `krdp`/`krfb` are the closest official-repo candidates for a KDE current-session desktop, while `freerdp`/`remmina` are the likely T480 viewers. `xrdp` is deferred because it was not visible in the official pacman repo check on this host; adding AUR dependencies needs an explicit later decision.

Verification:

Completed on 2026-06-15:

- `python -m py_compile scripts/ctos-remote`.
- `scripts/ctos-remote plan`.
- `scripts/ctos-remote tunnel-command --protocol rdp`.
- `scripts/ctos-remote install-commands`.
- `scripts/ctos-remote krdp-localhost --start --json`.
- `scripts/ctos-remote client-command --protocol rdp`.
- `scripts/ctos-remote service-command status`.
- `scripts/ctos-remote status --json` confirmed SSH reachability and no installed desktop-control server on `ctos-core`.
- After package install, `scripts/ctos-remote status` confirmed `krdp 6.6.5-1`, `freerdp 3.26.0-1`, active `app-org.kde.krdpserver.service`, localhost-only override, `SystemUserEnabled=true`, and listener `127.0.0.1:3389`.
- A temporary SSH tunnel from T480 `127.0.0.1:3390` to tower `127.0.0.1:3389` passed a local TCP connection test, then was closed.
- The first visual FreeRDP attempt reached KRDP authentication but produced a blank client window while logging VAAPI/libavcodec initialization failures. Local `xfreerdp3 /help` confirmed `/gdi: sw|hw`, `/bpp`, `/network`, fixed geometry, and `/cert:ignore`; `scripts/ctos-remote client-command` now defaults to an `xfreerdp3` software-rendering profile.
- A later KRDP journal check showed the software-only `xfreerdp3` profile was rejected with `Client does not support graphics pipeline which is required`.
- A subsequent RDPGFX/no-AVC attempt was rejected by KRDP with `Client does not support H.264 in YUV420 mode!`. The V1 client profile now uses `xfreerdp3` with `/gfx:AVC420:on,AVC444:on`, fixed geometry, and tunnel-only certificate ignore.
- The RDPGFX/AVC attempt reached authentication, loaded `rdpgfx`, and KRDP selected `RDPGFX_CAPVERSION_107`, but the visible client stayed blank until cancelled and KRDP logged `ERRINFO_LOGOFF_BY_USER`. Treat KRDP as not visually validated for V1 and move the next test to VNC/KRFB fallback.
- Local Remmina has a VNC plugin file, but it failed to load because `libvncclient.so.1` was missing; VNC fallback requires `libvncserver` on the T480 and `krfb` on `ctos-core`.
- VNC fallback packages were installed on 2026-06-16: T480 `remmina` plus `libvncserver`, and tower `krfb`.
- Launching `krfb` in the active KDE session showed it listening on `0.0.0.0:5900` and `[::]:5900`, not localhost-only.
- The user added runtime firewalld rich reject rules for TCP `5900` on the tower public zone; direct T480 access to `10.42.0.2:5900` returned `Connection refused`.
- An SSH tunnel `127.0.0.1:5901 -> ctos-core:127.0.0.1:5900` was opened and TCP-tested successfully.
- The first Remmina VNC launch blocked on a desktop keyring unlock prompt before showing the VNC session, so the VNC test client was changed to TigerVNC `vncviewer` while keeping Remmina as an optional fallback.
- TigerVNC authenticated against KRFB and displayed a desktop frame, but the frame did not refresh and keyboard/mouse input did not work. Setting `[Security] allowDesktopControl=true`, restarting KRFB, and disabling TigerVNC remote resize did not fix it.
- `scripts/ctos-remote` now generates commands for TigerVNC attached-screen fallback: `w0vncserver` for the current Wayland session, and `x0vncserver` for Plasma X11 if Wayland remains unreliable.
- `tigervnc 1.16.2-4` was installed on `ctos-core` after a forced pacman database refresh resolved mirror 404s for the previous `1.16.2-3` package entry.
- `w0vncserver` was launched as a transient user service with `-localhost -rfbport 5902 -SecurityTypes None -AlwaysShared`; it listened only on localhost and accepted a tunnelled TigerVNC client, but sent zero framebuffer updates and produced no visible T480 viewer window. Reject `w0vncserver` on the current Plasma Wayland session for V1.

Consequences:

The next request can focus on completing an attached-screen TigerVNC test through SSH. The tower has a current-session RDP service, but it is localhost-only and reachable from the T480 only through an explicit SSH tunnel. KRDP remains disabled for autostart until the workflow is proven. KRFB is rejected for V1 because it connected but did not produce a live interactive session. Do not keep KRFB running as a service. `w0vncserver` on the current Plasma Wayland session is also rejected for V1. Switch the tower login session to Plasma X11 and use `x0vncserver -localhost`. Keep these tests tunnel-only and avoid permanent LAN listeners until a backend is proven.

## ADR-0036: Use a repo-owned Hyprland boot cockpit session

Date: 2026-06-16
Status: accepted

Decision:

Add a repo-owned Hyprland startup orchestrator for the T480 cockpit. `scripts/ctos-session boot` restores the wallpaper, starts the localhost web cockpit, opens the terminal cockpit on `CTRL`, attempts the tunnel-only `ctos-core` X11 VNC desktop on `DESK`, and opens an interactive Kali VM control panel on `VMS`. Kali is not started automatically at login; the VMS panel exposes explicit user actions for start, console, shutdown, refresh, and checkpoint.

Context:

The user wants the T480 to boot into a usable operator layout: `CTRL` for host cockpit, `DESK` for desktop/remote desktop control, and `VMS` for VM operations with Kali launch possible. The desktop must prioritize function and recoverability over decoration. The tower remote-control backend that actually works is Plasma X11 plus `x0vncserver` behind an SSH tunnel.

Sources:

- Local Hyprland config in `hyprland/hyprland.conf`.
- Hyprland Window Rules wiki, accessed 2026-06-16: https://wiki.hypr.land/Configuring/Window-Rules/
- Local TigerVNC `vncviewer(1)` manpage, checked 2026-06-16.
- TigerVNC `DesktopWindow.cxx` source, inspected 2026-06-16: https://github.com/TigerVNC/tigervnc/blob/master/vncviewer/DesktopWindow.cxx
- Local TigerVNC `vncviewer --help`, checked 2026-06-16.
- Repo control scripts: `scripts/ctos-control`, `scripts/ctos-kali`, and `control/server.py`.
- Runtime verification on 2026-06-16: `x0vncserver` on `ctos-core` listened only on localhost, detected XTest 2.2, and produced a visible TigerVNC window on the T480.
- Repo asset `Assets/BackGround/4.webp`.

Rationale:

A single startup script is easier to audit than many independent `exec-once` commands. Keeping all behavior in repo scripts makes the desktop reproducible and keeps failures visible in terminal windows. The remote desktop path remains tunnel-first and localhost-only, so no VNC port is opened on the LAN. Kali remains operator-triggered because automatically starting a VM at login would consume RAM/CPU and blur the host/VM boundary.

Verification:

Completed on 2026-06-16:

- Shell syntax checks passed for `scripts/ctos-wallpaper`, `scripts/ctos-session`, `scripts/ctos-desk-remote`, and `scripts/ctos-vms-panel`.
- Python compile checks passed for the existing cockpit modules touched by the startup path.
- `scripts/ctos-install-desktop` copied the repo Hyprland config into `~/.config/hypr/hyprland.conf` with an automatic backup.
- `hyprctl reload` succeeded.
- The initial `windowrulev2` placement rules produced live Hyprland deprecation errors; they were replaced with current anonymous `windowrule = match:...` syntax from the Hyprland Window Rules documentation.
- `hyprctl configerrors` returned no errors after the syntax correction.
- `scripts/ctos-session status` showed the localhost cockpit server running, `swaybg` using `Assets/BackGround/4.webp`, and the expected `CTOS_CONTROL`, `Vncviewer`, and `CTOS_VMS` windows.
- `hyprctl clients` confirmed `CTOS_CONTROL` on `CTRL`, the TigerVNC remote desktop on `DESK`, `CTOS_VMS` on `VMS`, and VS Code on the local work surface.
- `vncviewer(1)` documents mouse-edge scrolling in full-screen mode when the remote screen is larger than the local screen; `scripts/ctos-desk-remote` now uses this for the DESK panorama profile.
- TigerVNC source inspection confirmed fullscreen edge scrolling is also called for drag events, but local `vncviewer --help` exposes no edge-scroll speed or threshold option. `scripts/ctos-desk-remote` therefore keeps TigerVNC as the V1 DESK viewer and lowers `PointerEventInterval` to reduce drag latency.
- Remmina scaled VNC was tested as a possible full-panorama fallback but reopened the desktop keyring prompt and did not provide a clean unattended DESK session, so it is rejected for V1.
- The user rejected the full global/scaled DESK view on UX grounds. Do not continue optimizing that direction unless explicitly requested again.

Pending:

- Validate the full startup sequence after a real logout/login or reboot.

Consequences:

Hyprland startup now depends on the repo path `/home/operator/T480`. If the tower is offline or not in Plasma X11, the `DESK` terminal reports the blocker instead of silently failing. `VMS` actions are intentionally explicit and local to the T480 session; no persistent VM daemon is introduced.

## ADR-0037: Make the T480/tower cockpit restart-safe with tunnel-only desktop sharing

Date: 2026-06-17
Status: accepted

Decision:

Keep the T480 boot path repo-owned through `scripts/ctos-session boot`, and make `scripts/ctos-desk-remote` automatically try normal SSH `22` first, then the documented rescue SSH `2222` path while tower SSH is being repaired. Add `bootstrap/roles/ctos-core/boot/ctos-core-boot-contract` as the tower-side root script for restart safety: enable normal `sshd.service`, install a restricted `ctos-sshd-rescue.service` on `10.42.0.2:2222`, keep VNC localhost-only, and optionally configure SDDM autologin into Plasma X11 only when the operator explicitly passes `--enable-autologin`.

Context:

The user wants `CTRL`, `DESK`, and `VMS` available after restarting the T480 and/or the tower. During Wi-Fi testing, normal TCP/22 on `ctos-core` accepted connections but intermittently timed out during SSH banner exchange. A foreground `sshd` on port `2222` restored access, but that manual process would not survive a tower reboot. The working desktop sharing backend remains `x0vncserver` attached to an active Plasma X11 session and bound to localhost.

Sources:

- OpenSSH `sshd(8)`, accessed 2026-06-17: https://man.openbsd.org/sshd.8
- Local `sshd.service` and runtime checks on `ctos-core`, 2026-06-17: `systemctl status sshd`, `journalctl -u sshd`, `ss -lntp`, and `ps -ef`.
- Local SDDM session inventory on `ctos-core`, 2026-06-17: `/usr/share/xsessions/plasmax11.desktop`, `/usr/share/wayland-sessions/plasma.desktop`, and existing `/etc/sddm.conf`.
- Hyprland startup/window placement already decided in ADR-0036.
- TigerVNC localhost/tunnel-only desktop sharing already decided in ADR-0035 and ADR-0036.

Rationale:

The safe restart model is to keep SSH as the only network control channel and keep VNC private behind SSH. A persistent rescue SSH service is acceptable only because it is restricted to the T480 Ethernet address, disables password authentication, and exists to recover the cockpit path when normal SSH/22 misbehaves. Autologin is not silently enabled because it changes the physical-console security posture; it is available as an explicit flag when unattended DESK after a tower reboot matters more than lock-screen protection.

Verification:

Completed on 2026-06-17:

- `scripts/ctos-desk-remote` now supports `CTOS_CORE_SSH_PORTS` and tries `22 2222` by default unless `CTOS_CORE_SSH_PORT` is explicitly set.
- `scripts/ctos-vms-panel` now passes `--readonly` to `virsh` correctly and surfaces libvirt errors instead of collapsing them to plain `unavailable`.
- `bootstrap/roles/ctos-core/boot/ctos-core-boot-contract plan` renders the intended tower boot contract locally and from `/srv/ctos/repo/t480` on `ctos-core`.
- `./scripts/ctos-core sync-repo` copied the new boot contract to `ctos-core`.
- `virsh -c qemu:///system --readonly domstate ctos-kali` outside the sandbox reports `shut off`; the Kali domain exists.
- `ssh -F /dev/null ctos@10.42.0.2` now succeeds again on normal port `22`.
- `scripts/ctos-desk-remote tiger` successfully selected SSH/22, restarted localhost-only `x0vncserver`, opened/kept the SSH tunnel, and confirmed DESK ready.
- `hyprctl configerrors` returns no errors.
- `scripts/ctos-session status` shows `CTOS_CONTROL`, `ctos@ctos-core - TigerVNC`, and `CTOS_VMS`.

Pending:

- The tower-side boot contract still needs to be applied with sudo on `ctos-core`.
- A real two-machine reboot test remains pending.

Consequences:

After the tower-side script is applied, the T480 should recover the DESK stream through port `22` or the restricted rescue port `2222` without manual editing. If unattended DESK is required immediately after a tower reboot, the operator must explicitly enable SDDM autologin into Plasma X11; otherwise DESK becomes available after the user logs into the tower.

## ADR-0038: Keep DESK self-healing inside the Hyprland user session

Date: 2026-06-17
Status: accepted

Decision:

Add `scripts/ctos-desk-guard` and start it from `scripts/ctos-session boot`. The guard runs as the T480 desktop user, checks every 20 seconds whether `ctos-core` is reachable over SSH, whether the tower has an active Plasma X11 session, whether remote `x0vncserver` is listening on `127.0.0.1:5902`, whether the local SSH tunnel exists, and whether the local TigerVNC viewer is running. If the remote desktop is reachable but the local viewer or tunnel path is missing, the guard launches `scripts/ctos-desk-remote` in non-interactive mode to repair the stream.

Context:

The user closed the DESK viewer on the T480 and asked for the remote desktop to reopen automatically when the tower desktop is reachable. A root service is not required for this behavior because all required actions already happen inside the logged-in Hyprland session: SSH to `ctos-core`, localhost tunnel management, and opening TigerVNC on workspace `DESK`.

Sources:

- Local `scripts/ctos-session`, 2026-06-17.
- Local `scripts/ctos-desk-remote`, 2026-06-17.
- Runtime checks on 2026-06-17: `hyprctl clients`, `ctos-desk-guard status`, `pgrep`, and SSH inspection of `kwin_x11`/`x0vncserver` on `ctos-core`.
- Prior tunnel-only desktop sharing decisions in ADR-0035, ADR-0036, and ADR-0037.

Rationale:

A user-session watchdog is the smallest reliable mechanism for this phase. It avoids a privileged daemon, avoids adding a systemd user unit before the flow has settled, and keeps the behavior tied to the visible desktop session where TigerVNC can actually open. The guard does not expose VNC on the network; it only repairs the existing SSH-localhost path.

Verification:

Completed on 2026-06-17:

- `bash -n` passed for `scripts/ctos-desk-guard`, `scripts/ctos-desk-remote`, and `scripts/ctos-session`.
- After the DESK viewer had been closed, `scripts/ctos-desk-guard once` detected `viewer=0 tunnel=1 remote_vnc=1` and relaunched TigerVNC through SSH/22.
- `scripts/ctos-session boot` started the persistent guard.
- `ctos-desk-guard status` reported SSH ready on port `22`, viewer running, local tunnel listening on `127.0.0.1:5902`, remote X11 ready, and remote VNC listening on `127.0.0.1:5902`.
- `hyprctl clients` showed `ctos@ctos-core - TigerVNC` fullscreen on workspace `DESK`.

Consequences:

Closing TigerVNC is now treated as a recoverable failure, so it will reopen while the guard is running and the tower is reachable. To intentionally keep DESK closed for a longer period, the operator should stop the guard first or temporarily change the session startup behavior.

## ADR-0039: Install VS Code and Codex on `ctos-core` as user-local workstation tools

Date: 2026-06-17
Status: accepted

Decision:

Install the tower workstation tools for user `ctos` without sudo: official VS Code stable Linux x64 tarball under `~/.local/opt/vscode`, `code` symlink under `~/.local/bin`, Codex CLI through `npm install -g --prefix ~/.local @openai/codex@latest`, and the official VS Code extension `OpenAI.chatgpt`.

Context:

The user wants to work directly on the tower. `ctos-core` already has `nodejs`, `npm`, `git`, `base-devel`, and `yay`, but `sudo -n true` fails with `sudo: a password is required`, so the preferred AUR package path would block unattended execution. The T480 already uses official VS Code and Codex; the tower should match the user-facing tooling while avoiding a root prompt in this phase.

Sources:

- Microsoft VS Code Linux setup, accessed 2026-06-17: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code download/update endpoint checked from `ctos-core`, 2026-06-17: `https://update.code.visualstudio.com/latest/linux-x64/stable`
- AUR `visual-studio-code-bin`, already tracked from ADR-0002: https://aur.archlinux.org/packages/visual-studio-code-bin
- npm `@openai/codex`, checked from `ctos-core` with `npm view @openai/codex version`, 2026-06-17: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI extension, accessed 2026-06-17: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt

Rationale:

The AUR package remains the cleaner system-level Arch option, but it requires sudo. The official tarball is the smallest reversible path that gives the same Microsoft VS Code binary and Marketplace-compatible extension behavior without weakening sudo policy or asking the user to type a password into an SSH session. Installing Codex under the npm user prefix avoids global root-owned npm state.

Verification:

Completed on 2026-06-17:

- Added `scripts/ctos-core-install-workstation` with `plan`, `apply`, `path`, and `status` modes.
- Synced the repo to `/srv/ctos/repo/t480` on `ctos-core`.
- `ctos-core-install-workstation apply` downloaded VS Code stable, installed the OpenAI extension, and installed Codex CLI.
- `ctos-core-install-workstation status` reports VS Code `1.125.0`, commit `93cfdd489c3b228840d0f86ec77c3636277c93ea`, `x64`, Codex CLI `0.140.0`, and extension `openai.chatgpt`.
- `bash -lc 'command -v code; command -v codex; code --version; codex --version'` on `ctos-core` finds `/home/ctos/.local/bin/code` and `/home/ctos/.local/bin/codex`.
- `~/.local/share/applications/code.desktop` exists for the tower desktop launcher.

Consequences:

This installation is user-local and will not be upgraded by `pacman -Syu`. Updating it should be done through the repo script or by replacing it later with `visual-studio-code-bin` once an intentional sudo/package-management step is scheduled. Codex auth is not copied from the T480; the user must log in on the tower separately.

## ADR-0040: Build CTOS AI as a tool-governed assistant, not a generic Jarvis fork

Date: 2026-06-17
Status: accepted

Decision:

Start `ctos-ai` as a repo-owned, tool-governed assistant layer. V0 will define the local tool contract and agenda/memory surface before adding a model runtime. Open-source agent projects may be used as references or later dependencies, but CTOS will not adopt a broad "Jarvis" stack wholesale. The first implementation target is deterministic and dependency-light: `ctos-agenda`, `ctos-ai`, context search, cockpit status, and explicit permission tiers.

Context:

The user wants a Jarvis-like assistant that can converse, help organize time, code, and eventually perform real operations on owned machines. The CTOS environment already has a T480 cockpit, a `ctos-core` tower, a Kali VM boundary, SSH/VNC control paths, and repo-owned scripts. Giving an LLM unrestricted shell or desktop control would conflict with the existing safety and reproducibility model.

Sources:

- OpenHands GitHub, accessed 2026-06-17: https://github.com/All-Hands-AI/OpenHands
- Open Interpreter docs, accessed 2026-06-17: https://docs.openinterpreter.com/getting-started/introduction
- LangGraph documentation, accessed 2026-06-17: https://langchain-ai.github.io/langgraph/
- Model Context Protocol introduction, accessed 2026-06-17: https://modelcontextprotocol.io/docs/getting-started/intro
- Model Context Protocol security best practices, accessed 2026-06-17: https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices
- OpenAI Agents SDK guide, accessed 2026-06-17: https://developers.openai.com/api/docs/guides/agents-sdk
- OpenAI computer-use tool guide, accessed 2026-06-17: https://platform.openai.com/docs/guides/tools-computer-use
- Ollama GitHub, accessed 2026-06-17: https://github.com/ollama/ollama
- openWakeWord GitHub, accessed 2026-06-17: https://github.com/dscripka/openWakeWord
- whisper.cpp GitHub, accessed 2026-06-17: https://github.com/ggerganov/whisper.cpp
- Piper project note, accessed 2026-06-17: https://github.com/rhasspy/piper

Rationale:

OpenHands, Open Interpreter, LangGraph, MCP, OpenAI Agents, and voice projects all offer useful pieces, but none matches the current CTOS boundary as-is. CTOS needs a smaller core: named tools, permission tiers, local agenda/memory, clear approval gates, and no persistent AI service until the security model is documented. This lets the assistant grow toward voice, computer use, workers, and model orchestration without making the host or tower fragile.

Verification:

Completed on 2026-06-17:

- Added `context/20_ctos_ai_v0_model.md` with inspiration scan, permission tiers, V0 shape, storage boundaries, and roadmap.
- Updated `context/05_task_board.md` with the CTOS AI V0 track.
- Updated `context/README.md` so the AI model document is discoverable.
- Added executable `scripts/ctos-agenda` and `scripts/ctos-ai`.
- `python -m py_compile scripts/ctos-agenda scripts/ctos-ai` passed.
- Verified `ctos-agenda` with `CTOS_AI_DB=/tmp/ctos-ai-v0-verify-20260617.sqlite3`: `init`, `add`, `list`, `list --json`, and `plan-day`.
- Verified `ctos-ai capabilities`, `ctos-ai search-context`, `ctos-ai agenda list`, and print-only `open-desk`/`open-vms`.
- `ctos-ai status --json` returns structured status; in the Codex sandbox, SSH and default agenda storage are reported as unavailable due sandbox restrictions rather than producing an uncaught traceback.
- Added read-only CTOS AI status to `control/status.py`: model runtime state, tool availability, agenda DB metadata, task counts, and permission tier hints.
- Updated `control/tui.py` to render a `CTOS AI` block.
- Updated `control/static/app.js` so the web dashboard AI panel renders the tool contract, agenda, deferred model runtime, Ollama, and planned workers.
- `python -m py_compile control/status.py control/tui.py control/server.py scripts/ctos-agenda scripts/ctos-ai` passed.
- `node --check control/static/app.js` passed.
- With `CTOS_AI_DB=/tmp/ctos-ai-v0-verify-20260617.sqlite3`, `control.status.snapshot()["ai"]` reported both tools available and agenda counts `open=1`, `due_today=1`, `total=1`.
- `timeout 3 python control/tui.py` rendered the `CTOS AI` cockpit block successfully with the temporary DB.
- Restarted `scripts/ctos-control serve` outside the sandbox and verified it listens on `127.0.0.1:8765`.
- Initialized the real user agenda DB with `scripts/ctos-agenda init`; it lives outside Git at `/home/operator/.local/share/ctos-ai/agenda.sqlite3`.
- Live `/api/status` check on 2026-06-18 shows `ai.agenda.db_exists=true`, `state_root_writable=true`, both CTOS AI tools available, and model runtime deferred.
- Added `scripts/ctos-ai brief` on 2026-06-18 as a deterministic operator brief command.
- Verified `scripts/ctos-ai brief` with a temporary agenda DB and a live outside-sandbox run. The live brief reported `ctos-core` available, Kali `shut off`, agenda open count `0`, and a next recommendation to add one concrete agenda task.
- Added `scripts/ctos-install-user-bin` and installed user-local shims under `~/.local/bin`, with a guarded `~/.bashrc` PATH block. Verified from a fresh interactive shell in `~` that `ctos-ai brief` works without entering the repo directory.

Consequences:

The next implementation should create an explicit approval surface before exposing mutable Tier 2 tools to any model. Model/provider integration, MCP exposure, always-on voice, external calendar connectors, and computer-use automation remain separate decisions.

## ADR-0041: Defer GLM-5.2 and AirLLM runtime adoption until CTOS approval boundaries exist

Date: 2026-06-19
Status: accepted

Decision:

Do not install or select GLM-5.2 or AirLLM as the first CTOS AI runtime. Keep GLM-5.2 as a future external/frontier model candidate and AirLLM as an experimental low-VRAM/offload reference. The next CTOS AI implementation step is an approval surface for Tier 2 actions plus a provider/runtime profile abstraction, not a model install.

Context:

The user asked whether GLM-5.2 and AirLLM should inform the next Jarvis-like CTOS AI step. CTOS currently has deterministic tools, agenda state, cockpit status, and user-local commands. It does not yet have a human approval surface for mutable model actions.

Sources:

- Z.ai GLM-5 GitHub README, accessed 2026-06-19: https://github.com/zai-org/GLM-5
- AirLLM GitHub README, accessed 2026-06-19: https://github.com/lyogavin/airllm
- AirLLM PyPI package page, accessed 2026-06-19: https://pypi.org/project/airllm/

Rationale:

GLM-5.2 is relevant as a powerful future model candidate, but its public footprint is not realistic as a local runtime for the current T480 and `ctos-core` hardware. AirLLM is interesting for disk/layer-offload experiments, but it is not a strong default for an always-available assistant surface. The meaningful blocker is not model capability; it is safe authority. A strong model without a scoped approval path would increase risk before it increases reliability.

Consequences:

`ctos-ai` remains model-agnostic for now. The next implementation should add an approval queue or approval command that can show exact action, target, risk, and rollback notes before any Tier 2 tool runs. Runtime/provider profiles can then be added without committing CTOS to a specific model backend.

## ADR-0042: Gate first CTOS AI mutable actions through a local allowlist approval queue

Date: 2026-06-19
Status: accepted

Decision:

Add a local approval queue to `ctos-ai` before exposing mutable actions to any model. The first surface is CLI-only and model-agnostic:

- `ctos-ai actions`
- `ctos-ai propose <action>`
- `ctos-ai approvals`
- `ctos-ai show <id>`
- `ctos-ai approve <id>`
- `ctos-ai reject <id>`

The queue is allowlist-only. It stores records outside Git at `~/.local/share/ctos-ai/approvals.sqlite3` by default. The first allowlisted actions are limited to CTOS-owned operations: Kali VM start/shutdown/console/checkpoint and `ctos-core` repo/layout sync.

Context:

CTOS AI V0 already has deterministic read-only and Tier 1 convenience tools. The next risk boundary is allowing a model or operator shortcut to request mutable VM or core-node actions. The project rules require explicit, auditable, reproducible mechanisms and no unrestricted shell authority.

Sources:

- CTOS AI V0 model: `context/20_ctos_ai_v0_model.md`
- CTOS VM lifecycle model: `context/11_vm_lifecycle_model.md`
- ctos-core service layout model: `context/17_archipelago_fleet_model.md`
- Existing local scripts: `scripts/ctos-ai`, `scripts/ctos-kali`, and `scripts/ctos-core`

Rationale:

The approval queue gives a model-safe shape without adding a daemon or dependency. A proposed action must come from a static registry with target, tier, exact command, risk, and rollback text. Approval execution recomputes the command from the current allowlist and rejects records whose stored command no longer matches. This is not a secrets boundary against local user tampering, but it prevents `ctos-ai` from becoming an arbitrary command launcher.

Verification:

Completed on 2026-06-19:

- `python -m py_compile scripts/ctos-ai`
- With `CTOS_AI_APPROVAL_DB=/tmp/ctos-ai-approvals-test.sqlite3`, `ctos-ai actions` listed the allowlist.
- `ctos-ai propose core-sync-repo --note test-approval-surface` created pending approval `#1`.
- `ctos-ai approvals`, `ctos-ai show 1`, and `ctos-ai approve 1 --dry-run` rendered the queued command without execution.
- `ctos-ai propose arbitrary-shell` was rejected as an unknown action.
- `ctos-ai propose kali-checkpoint --label bad/label` was rejected by label validation.
- `ctos-ai propose kali-checkpoint --label ai-test-20260619` created a valid pending checkpoint proposal.
- `ctos-ai reject 1 --reason verification-complete` moved the test approval to `rejected`.
- `ctos-ai capabilities --json` now reports the approval DB path and allowlisted actions.
- `control/status.py` reads the approval DB in SQLite read-only mode and exposes `ai.approvals` without creating state.
- The terminal `CTRL` cockpit renders pending/failed/total approval counts and recent pending IDs.
- The web dashboard AI panel and event feed render pending approvals without adding an execute/approve button.
- With `CTOS_AI_APPROVAL_DB=/tmp/ctos-ai-ctrl-approvals-20260619.sqlite3`, two pending approvals were created and surfaced through `control.status.snapshot()["ai"]["approvals"]` and `control.tui.render(...)`.
- `python -m py_compile control/status.py control/tui.py control/server.py scripts/ctos-ai` passed.
- `node --check control/static/app.js` passed.

Consequences:

Future model integrations may propose Tier 2 actions but should not directly execute them. Pending approvals are now visible in `CTRL`; the next step is to add provider/runtime profiles. Tier 3 actions remain manual until a stronger approval and rollback UX exists.

## ADR-0043: Describe CTOS AI model backends as inert runtime profiles before activation

Date: 2026-06-19
Status: accepted

Decision:

Add repo-owned runtime/provider profiles under `ai/runtime_profiles.json` and expose them through `ctos-ai runtimes`, `ctos-ai runtime <id>`, and `ctos-ai runtime-recommend`. Keep `active_profile` unset. Do not install packages, download models, launch daemons, or route personal context as part of this step.

The initial profiles are:

- `openai-responses-api`: first external/frontier candidate after secrets and privacy policy.
- `ollama-core-local`: first local candidate for `ctos-core` after hardware/storage inventory.
- `llama-cpp-core-server`: tunable local candidate for later GGUF/offload work.
- `glm-5-2-external`: future external/frontier candidate, not a current local target.
- `airllm-core-experiment`: lab/offload experiment, not the interactive Jarvis surface.

Context:

CTOS now has deterministic AI tools, an agenda, a read-only cockpit integration, and a local allowlist approval queue for mutable actions. The next risk is choosing a model/runtime too early and mixing package installs, secrets, model cache, and authority decisions. The user also asked to factor GLM-5.2 and AirLLM into the direction without blindly adopting them.

Sources:

- OpenAI Responses API reference, accessed 2026-06-19: https://platform.openai.com/docs/api-reference/responses
- Ollama API documentation, accessed 2026-06-19: https://docs.ollama.com/api
- Ollama OpenAI compatibility documentation, accessed 2026-06-19: https://docs.ollama.com/openai
- llama.cpp server documentation, accessed 2026-06-19: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
- Z.ai GLM-5 GitHub README, accessed 2026-06-19: https://github.com/zai-org/GLM-5
- AirLLM GitHub README, accessed 2026-06-19: https://github.com/lyogavin/airllm
- AirLLM PyPI package page, accessed 2026-06-19: https://pypi.org/project/airllm/

Rationale:

The runtime profile file gives CTOS a stable vocabulary for model choices without committing the system to any backend. A local-first route likely starts with Ollama on `ctos-core` because it is operationally simple. llama.cpp remains valuable when CTOS needs lower-level model/offload control. OpenAI Responses API is the clean external frontier path once secrets, privacy, and cost decisions exist. GLM-5.2 and AirLLM stay visible but deferred so they can inform architecture without becoming premature dependencies.

Verification:

Completed on 2026-06-19:

- Added `ai/README.md` and `ai/runtime_profiles.json`.
- `python -m json.tool ai/runtime_profiles.json` passed.
- Added `ctos-ai runtimes`, `ctos-ai runtime <id>`, and `ctos-ai runtime-recommend`.
- `ctos-ai runtimes` listed all five initial profiles.
- `ctos-ai runtime ollama-core-local` rendered the first local candidate with fit, constraints, and sources.
- `ctos-ai runtime-recommend` kept `active_profile` unset and recommended dry-run adapters before backend selection.
- `ctos-ai brief` now reports runtime profile count and active profile.
- `control/status.py` exposes `ai.runtime_profiles` in the read-only status snapshot.
- The terminal cockpit renders runtime profile count and top candidates in the `CTOS AI` block.
- The web dashboard AI panel and event feed render runtime profile state.
- `python -m py_compile scripts/ctos-ai control/status.py control/tui.py control/server.py` passed.
- `node --check control/static/app.js` passed.
- The live localhost dashboard was restarted and `/api/status` exposed `ai.runtime_profiles.count=5` with `active_profile=null`.

Consequences:

The next implementation should add a dry-run adapter contract, not a model daemon. A dry-run can validate endpoint configuration, env variables, and candidate routing while refusing to send private context. Any external provider activation still requires a secrets/privacy decision. Any local runtime activation still requires a package/model-cache/storage decision and a small benchmark.

## ADR-0044: Add a no-network-by-default dry-run adapter for AI runtime profiles

Date: 2026-06-19
Status: accepted

Decision:

Add `ctos-ai runtime-check <id>` as the first model-runtime adapter contract. The command validates a runtime profile before any runtime is activated:

- required profile fields;
- known interface type;
- endpoint shape when declared;
- declared secret environment variable names and present/missing state;
- readiness blockers;
- optional owned-node probe with `--target-probe`.

The default path must not contact an external endpoint, must not contact a model runtime, and must not print secret values. `--target-probe` is limited to owned CTOS targets such as `ctos-core` and checks reachability plus service-storage readiness.

Context:

CTOS now has deterministic AI commands, agenda state, a Tier 2 approval queue, and inert runtime profiles. The next risk is accidentally turning a profile into an implicit provider call or model daemon before secrets, privacy, storage, and benchmark decisions exist.

Sources:

- CTOS runtime profiles: `ai/runtime_profiles.json`
- CTOS AI V0 model: `context/20_ctos_ai_v0_model.md`
- Provider/runtime source registry entry: `context/06_source_registry.md`
- Previous runtime ADR: ADR-0043 in this file.

Rationale:

The dry-run adapter gives CTOS a reusable handshake for future providers without giving an LLM new authority. External providers stay blocked by explicit secret/privacy policy. Local runtimes stay blocked by package, service, model-cache, and benchmark decisions. Optional `ctos-core` probing is useful because it verifies owned infrastructure readiness without sending prompts or personal context.

Verification:

Completed on 2026-06-19:

- `python -m py_compile scripts/ctos-ai control/status.py control/tui.py control/server.py` passed.
- `node --check control/static/app.js` passed.
- `ctos-ai capabilities` lists `runtime-check <id>`.
- `ctos-ai runtime-check ollama-core-local` returned `metadata_ok True`, did not contact network/model runtime, and remained blocked only by readiness `not_installed_or_model_unselected`.
- `ctos-ai runtime-check openai-responses-api` returned `metadata_ok True`, did not contact network/model runtime, and remained blocked by missing `OPENAI_API_KEY` plus secrets policy.
- `ctos-ai runtime-check airllm-core-experiment --json` returned structured dry-run output without contacting a runtime.
- In the default sandbox, `ctos-ai runtime-check ollama-core-local --target-probe` failed with `socket: Operation not permitted`, confirming the probe is real network/SSH work rather than a fake local check.
- With approved host access, `ctos-ai runtime-check ollama-core-local --target-probe` confirmed `ctos-core` reachable, `/srv/ctos` mounted and writable, and `/srv/ctos/models/ollama` ready.
- `control.status.snapshot()["ai"]["runtime_profiles"]["adapter_contract"]` exposes command `ctos-ai runtime-check <id>`, `network_default=false`, `model_contact_default=false`, and `target_probe_optional=true`.
- The live localhost dashboard was restarted and `/api/status` exposed the same adapter contract.

Consequences:

The next CTOS AI step should choose the V1 interaction surface or a local-runtime benchmark plan, not activate a provider yet. Runtime activation still requires separate ADR coverage for secrets/privacy, model storage, package/service lifecycle, and rollback.

## ADR-0045: Prepare a localhost-only Ollama benchmark on ctos-core before runtime activation

Date: 2026-06-20
Status: accepted

Decision:

Prepare, but do not automatically execute, the first local model benchmark for `ollama-core-local`.

The benchmark plan is stored at `ai/benchmarks/ollama_core_local_v0.json` and is operated from the T480 through `ctos-ollama-bench`.

Accepted constraints:

- package candidate: Arch `ollama`;
- service unit: `ollama.service`;
- bind address: `127.0.0.1:11434` on `ctos-core`;
- LAN exposure: none;
- model cache: `/srv/ctos/models/ollama`;
- first model path: `qwen2.5-coder:0.5b` for smoke, then `qwen2.5-coder:1.5b` for a first coding benchmark;
- GPU-specific packages are deferred until the RX6600/driver path is decided.

`ctos-ollama-bench install`, `pull`, and `bench` all require explicit `--yes`. The script uses non-interactive sudo for install so it fails closed when a password is required. It does not expose Ollama on the LAN.

Context:

CTOS has runtime profiles and a no-network dry-run adapter, but no activated model backend. `ctos-core` is the intended local runtime host, yet its current hardware state still differs from the future RX6600/Ryzen plan. A small CPU-safe benchmark gives useful data without turning Ollama into the assistant runtime yet.

Sources:

- Arch Linux `ollama` package, accessed 2026-06-20: https://archlinux.org/packages/extra/x86_64/ollama/
- Ollama Linux documentation, accessed 2026-06-20: https://docs.ollama.com/linux
- Ollama API introduction, accessed 2026-06-20: https://docs.ollama.com/api/introduction
- Ollama pull API, accessed 2026-06-20: https://docs.ollama.com/api/pull
- Ollama generate API, accessed 2026-06-20: https://docs.ollama.com/api/generate
- Ollama running models API, accessed 2026-06-20: https://docs.ollama.com/api/ps
- Ollama Qwen2.5-Coder 0.5B model card, accessed 2026-06-20: https://ollama.com/library/qwen2.5-coder:0.5b
- Ollama Qwen2.5-Coder 1.5B model card, accessed 2026-06-20: https://ollama.com/library/qwen2.5-coder:1.5b

Rationale:

Ollama is the simplest local runtime candidate because it provides a local HTTP API and packaged service path. Binding it to localhost keeps the service as a local/tunneled component instead of a network service. Starting with small Qwen2.5-Coder models respects the current low-RAM `ctos-core` state while still testing the coding-assistant direction. Deferring Vulkan/ROCm avoids tying the benchmark to unfinished GPU hardware work.

Verification:

Completed on 2026-06-20:

- `python -m json.tool ai/benchmarks/ollama_core_local_v0.json` passed.
- `python -m py_compile scripts/ctos-ollama-bench scripts/ctos-ai scripts/ctos-core` passed.
- `ctos-ollama-bench plan` rendered the benchmark plan.
- `ctos-ai capabilities` lists `ctos-ollama-bench plan` in runtime commands.
- `ctos-install-user-bin` linked `/home/operator/.local/bin/ctos-ollama-bench`.
- Sandbox `ctos-ollama-bench preflight` failed with `socket: Operation not permitted`, confirming SSH is real network work.
- Approved host preflight against `ctos-core` found: kernel `7.0.12-arch1-1`, 3.12 GiB RAM available, NVIDIA GTX 1650 plus AMD Raven/Vega detected, `ollama` not installed, `ollama.service` inactive/not-found, no `11434` listener, localhost API offline, `/srv/ctos/models/ollama` exists and is writable, sudo password required.
- `ctos-ollama-bench status` confirmed `/api/version`, `/api/tags`, and `/api/ps` are offline before install.

Live execution update:

Completed on 2026-06-21:

- The operator ran `scripts/ctos-ollama-bench install-interactive --yes` and entered the local `ctos-core` sudo password.
- `ollama 0.30.8-1` installed from Arch `extra`.
- `ollama.service` is enabled and active.
- Service drop-in `/etc/systemd/system/ollama.service.d/ctos.conf` binds Ollama to `127.0.0.1:11434` and stores models under `/srv/ctos/models/ollama`.
- `/api/version` returns `{"version":"0.30.8"}`.
- `qwen2.5-coder:0.5b` was pulled through the local Ollama API. `/api/tags` reports size `397821516`, parameter size `494.03M`, quantization `Q4_K_M`, and capabilities `completion`, `tools`, `insert`.
- `ctos-ollama-bench bench --model qwen2.5-coder:0.5b --yes` completed all three synthetic prompts successfully.
- Benchmark output was written on `ctos-core` to `/srv/ctos/state/ai/benchmarks/ollama-qwen2.5-coder-0.5b-20260621-020230.json`.
- Observed post-load generation speed was about `35` tokens/s on the small coding and ops prompts; the initial sanity prompt included model load time and returned `CTOS_OK`.

Consequences:

Ollama is now a working local runtime candidate on `ctos-core`, but it is still not the active CTOS assistant backend. The next live step should be either a bounded `ctos-ai ask-local` command using the 0.5B model, or a second benchmark with `qwen2.5-coder:1.5b` before any active profile selection or chat UI.

## ADR-0046: Add a bounded local model ask command before any agent authority

Date: 2026-06-21
Status: accepted

Decision:

Add `ctos-ai ask-local` as the first model-backed CTOS command.

Constraints:

- Uses only the local Ollama runtime on `ctos-core` through SSH.
- Default model is `qwen2.5-coder:0.5b`.
- Sends only the prompt provided to the command, plus an optional per-call system instruction.
- Does not read repo context, files, screenshots, agenda, approvals, shell history, browser state, or secrets automatically.
- Does not expose any CTOS action/tool execution to the model.
- Does not store conversation history or memory.
- Keeps `ai/runtime_profiles.json.active_profile` unset until the V1 interaction surface is decided.

Context:

Ollama is now installed and smoke-benchmarked on `ctos-core`, and the runtime profile is ready. The user wants a Jarvis-like assistant, but the project boundary requires safe action authority before attaching a model to tools. The smallest useful next step is therefore a single-turn local prompt command, not an autonomous agent.

Sources:

- Local runtime decision and benchmark record: ADR-0045 in this file.
- CTOS AI permission-tier model: `context/20_ctos_ai_v0_model.md`.
- Runtime profile registry: `ai/runtime_profiles.json`.

Rationale:

This gives the operator a real local model loop while preserving CTOS safety boundaries. It proves the path from T480 CLI to tower-local model without broadening authority. Future chat, memory, and tool-calling can build on this only after the approval and privacy boundaries are explicit.

Verification:

Completed on 2026-06-21:

- `python -m py_compile scripts/ctos-ai` passed.
- `ctos-ai ask-local --help` renders the new command and limits.
- `ctos-ai capabilities` lists `ask-local` under Tier 0 read-only and runtime commands.
- Live model call through `ctos-ai ask-local "Réponds exactement CTOS_LOCAL_OK si tu me lis." --max-tokens 16 --stats` returned `CTOS_LOCAL_OK` from `qwen2.5-coder:0.5b` at about `44.86` tokens/s for the tiny response.

Consequences:

The next AI step should not be unrestricted tool use. Choose between benchmarking `qwen2.5-coder:1.5b`, designing a V1 chat/CLI surface, or adding a strictly read-only context retrieval command whose input is explicit and inspectable.

## ADR-0047: Keep 0.5B as the fast local default after benchmarking Qwen2.5-Coder 1.5B

Date: 2026-06-22
Status: accepted

Decision:

Pull and benchmark `qwen2.5-coder:1.5b` on `ctos-core`, but do not make it the default `ctos-ai ask-local` model yet. Keep `qwen2.5-coder:0.5b` as the fast default for smoke and quick operator checks. Expose `qwen2.5-coder:1.5b` through the existing `--model` option for deliberate coding prompts.

Context:

The 0.5B smoke model proved the local runtime path and gave about `35` tokens/s on non-trivial benchmark prompts. Before designing the V1 assistant surface, CTOS needs to know whether the 1.5B model is still interactive enough on the current `ctos-core` hardware.

Sources:

- Prior local runtime benchmark plan and sources: ADR-0045.
- Bounded local ask boundary: ADR-0046.
- Local benchmark output on `ctos-core`: `/srv/ctos/state/ai/benchmarks/ollama-qwen2.5-coder-1.5b-20260622-021732.json`.

Rationale:

The 1.5B model works and is useful to keep available, but its measured speed is roughly half the 0.5B model on the same prompts. The V1 surface should feel responsive by default, so CTOS should keep the smaller model as the default until a routing policy exists.

Verification:

Completed on 2026-06-22:

- `ctos-ollama-bench preflight` confirmed `ollama 0.30.8-1`, active/enabled `ollama.service`, and localhost-only listener `127.0.0.1:11434`.
- `ctos-ollama-bench pull --model qwen2.5-coder:1.5b --yes` returned `{"status":"success"}`.
- `/api/tags` reports `qwen2.5-coder:1.5b`, size `986062089`, parameter size `1.5B`, quantization `Q4_K_M`, and capabilities `completion`, `tools`, `insert`.
- `ctos-ollama-bench bench --model qwen2.5-coder:1.5b --yes` completed all benchmark prompts successfully.
- Observed non-trivial prompt speeds were about `16.52` and `16.22` tokens/s.
- `ctos-ai ask-local "Réponds exactement CTOS_15B_OK si le modèle 1.5B répond." --model qwen2.5-coder:1.5b --max-tokens 16 --stats` returned `CTOS_15B_OK`.

Consequences:

The next AI step is no longer runtime proof. It is V1 surface design and routing policy: fast 0.5B for quick/local checks, 1.5B for deliberate coding/ops reasoning, and no autonomous tool use until the approval model is wired into the interaction layer.

## ADR-0048: Build CTOS AI as durable loops with a default local identity contract

Date: 2026-06-23
Status: accepted

Decision:

Build the Jarvis/CTOS assistant through explicit implementation loops rather than increasingly long injected prompts. Add a default CTOS identity contract to local model calls and expose a small localhost API before adding richer UI or voice surfaces.

Context:

The local Ollama runtime works, but a direct `qwen2.5-coder:1.5b` prompt claimed an incorrect cloud/GPT identity. The user wants a more ambitious assistant that can eventually help operate owned machines, but the current safety boundary allows only bounded prompt answers and read-only/local helper commands.

Constraints:

- The model must not claim cloud identity, persistent memory, file access, desktop access, or tool authority.
- API calls must remain localhost-only on the T480 side and tunnel to the localhost-only Ollama service on `ctos-core`.
- Voice V1 must not enable always-on microphone or speech-to-text until the backend and privacy tradeoffs are documented.
- No new package/service decision is made in this ADR; the implementation uses Python stdlib plus already-installed `ssh`, `curl`, and local TTS commands.

Sources:

- Existing local runtime decisions: ADR-0045 through ADR-0047 in this file.
- CTOS AI model: `context/20_ctos_ai_v0_model.md`.
- Runtime profile registry: `ai/runtime_profiles.json`.
- Implementation files: `ai/ctos_prompt.py`, `ai/local_api.py`, `scripts/ctos-ai`, `scripts/ctos-ai-api`, `scripts/ctos-ai-tunnel`, `scripts/ctos-voice`.

Rationale:

Durable loops make the assistant auditable: each capability is observable, bounded, implemented in the repo, verified, and logged. A default identity contract is necessary because small local models can otherwise hallucinate provider identity and authority. A local API gives future UI/voice layers a stable surface without granting additional permissions.

Verification:

Completed on 2026-06-23:

- `python -m py_compile scripts/ctos-ai ai/ctos_prompt.py ai/local_api.py scripts/ctos-voice` passed.
- `bash -n scripts/ctos-ai-api scripts/ctos-ai-tunnel scripts/ctos-install-user-bin` passed.
- `ctos-ai ask-local --model qwen2.5-coder:1.5b` answered as a local CTOS assistant instead of claiming a cloud identity.
- `ctos-ai-tunnel ensure` opened a detached tunnel and `ctos-ai-api health` reported Ollama `0.30.8` plus the cached `qwen2.5-coder:0.5b` and `qwen2.5-coder:1.5b` models.
- `ctos-ai-api ask` returned `CTOS_API_OK` through the localhost tunnel.
- `ctos-ai-api serve --port 8767` answered `GET /health` during a short start/curl/stop test.
- `ctos-ai-api-server start/status` kept the local API available at `http://127.0.0.1:8767`.
- `ctos-ai-chat --model qwen2.5-coder:1.5b ...` returned `CTOS_CHAT_OK` through the `/chat` API path.
- `ctos-voice probe` found `espeak-ng`, `espeak`, `pw-record`, `parec`, `arecord`, and `ffmpeg`, with no verified speech-to-text backend.
- `ctos-voice ask --no-speak --model qwen2.5-coder:1.5b` returned `CTOS_VOICE_OK`.
- `ctos-voice chat --no-speak --model qwen2.5-coder:1.5b` returned `CTOS_VOICE_CHAT_OK`.
- `ctos-voice command --no-speak brief` displayed a read-only CTOS brief.
- `ctos-voice listen-once` refused clearly because no STT backend is selected.
- After adding a deterministic identity guard, the original regression prompt `tu fonctionnes?` returned `Je fonctionne bien.` through both `ctos-ai-api ask --model qwen2.5-coder:1.5b` and `ctos-ai ask-local --model qwen2.5-coder:1.5b`; no GPT/OpenAI identity claim was emitted.

Consequences:

The local identity loop is now guarded by prompt plus deterministic response filtering. The model still has no direct tool access; process/file/system mutations must continue through deterministic CTOS commands and the approval queue.

## ADR-0049: Use Vosk small French for CTOS voice input V1

Date: 2026-06-23
Status: accepted

Decision:

Use Vosk with `vosk-model-small-fr-0.22` as the first local speech-to-text backend for CTOS voice input. Bind it only to push-to-talk style commands in `ctos-voice`; do not add an always-on microphone listener or wake-word daemon.

Context:

CTOS now has a local model API, chat loop, and voice output. The missing piece for first voice discussions is speech-to-text. The T480 control plane and current `ctos-core` hardware favor a small offline STT path over a heavier Whisper path for the first iteration.

Constraints:

- Offline/local only; no cloud STT for V1.
- No persistent microphone service.
- No long-lived voice recordings by default.
- Store downloaded STT models under `~/.local/share/ctos-ai/stt/`, outside Git.
- Keep voice commands read-only until the Tier 2 approval UX is wired.

Sources:

- Vosk official models page, accessed 2026-06-23: https://alphacephei.com/vosk/models
- Vosk official French small model URL, accessed 2026-06-23: https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
- Local Arch package database on 2026-06-23: `python-vosk 0.3.50-7`, `vosk-api 0.3.50-7`, upstream URL `https://alphacephei.com/vosk/`.

Rationale:

Vosk is light enough for short French command phrases, available as Arch packages, and works offline once the small French model is downloaded. Whisper remains a better candidate for higher-quality long-form dictation later, but it is heavier and not required for the first Jarvis-style loop.

Implementation:

- `ctos-voice probe` now reports Python Vosk import readiness, recorder readiness, model path, and model readiness.
- `ctos-voice setup-vosk --yes` installs missing Arch packages, then downloads/extracts the model outside the repo with Python stdlib zip handling.
- `ctos-voice setup-vosk --venv --yes` installs Python Vosk into `~/.local/share/ctos-ai/venvs/vosk` when system packages are blocked by sudo.
- `ctos-voice record-once` records a short mono WAV.
- `ctos-voice transcribe-file` transcribes a WAV through Vosk.
- `ctos-voice listen-once` records, transcribes, sends the text to CTOS Local, speaks the answer, and deletes the temporary recording by default.
- `ctos-voice voice-command` maps one spoken phrase only to the read-only `brief/status/agenda` intents.

Verification:

Completed on 2026-06-23 before package install:

- `python3 -m py_compile scripts/ctos-voice` passed.
- `ctos-voice probe --json` showed TTS and recorder readiness, with `python_modules.vosk=false` and `vosk.model_ready=false`.
- `ctos-voice setup-vosk --print-commands` rendered the exact package/model install path.
- `setup-vosk` was later made idempotent: it skips `pacman` when Python can already import `vosk`, skips the model download when the target model is already present, and no longer depends on the external `unzip` package.
- A sandboxed official-model-page check was blocked by DNS; an approved `curl -fsSL https://alphacephei.com/vosk/models` check confirmed `vosk-model-small-fr-0.22.zip` is listed in the French section.
- `ctos-voice setup-vosk --model-only --yes` downloaded and extracted the 40.27 MiB official French small model under `~/.local/share/ctos-ai/stt/vosk-model-small-fr-0.22`; `ctos-voice probe` reports `vosk.model_ready=true`.
- `sudo -n pacman -S --needed python-vosk vosk-api` failed with `sudo: a password is required`, confirming that only the package install step still requires operator input.
- `ctos-voice setup-vosk --venv --yes` installed PyPI `vosk 0.3.45` plus dependencies in the local venv `~/.local/share/ctos-ai/venvs/vosk`; `ctos-voice probe` now reports `python_modules.vosk=true`, `vosk.venv_ready=true`, and `voice_input_ready=true`.
- A synthetic French WAV generated with `espeak-ng` and converted with `ffmpeg` was transcribed by `ctos-voice transcribe-file`.
- `ctos-voice listen-once --from-wav /tmp/ctos-vosk-synth.wav --no-speak` completed the STT-to-model loop.
- `ctos-voice record-once --seconds 1 --out /tmp/ctos-mic-smoke.wav --json` produced a valid mono 16 kHz microphone WAV through PipeWire.
- `ctos-voice listen-once --seconds 1 --no-speak` handled silence safely with `Je n'ai pas compris. Retente avec une phrase courte.`
- `ctos-voice voice-command --from-wav /tmp/ctos-vosk-status.wav --no-speak` mapped Vosk transcript `santé` to the read-only `ctos-ai brief` command. Outside the sandbox, the brief reached `ctos-core` and Kali state.

Remaining operator-facing check:

The plumbing is verified. The remaining subjective check is a real spoken phrase by the operator with `ctos-voice listen-once --seconds 4`; no sudo is required.

Consequences:

Voice input is now usable without sudo through the local venv. The system still cannot mutate CTOS state by voice; it can answer prompts and trigger only the read-only voice command intents.

## ADR-0050: Keep ctos-core behind the T480 bastion and expose only push-to-talk voice commands

Date: 2026-07-07
Status: accepted

Decision:

Keep `ctos-core` dependent on the T480 Ethernet-sharing path for Internet access for now. The T480 remains the bastion, mobile control plane, and choke point for `ctos-core` egress. Resume Jarvis-style operation through explicit push-to-talk voice commands only; no always-on microphone listener and no voice-triggered mutable CTOS action without the existing approval surface.

Context:

The tower Wi-Fi dongle is not currently a reliable kernel/NetworkManager device, while the T480-to-tower Ethernet path is verified. The user wants remote/control capability and real voice interaction, but the CTOS assistant is still in the early bounded-tool phase.

Constraints:

- Do not make `ctos-core` a second independent Internet perimeter until the Wi-Fi/uplink story is reliable and documented.
- Do not add always-on microphone capture.
- Do not keep voice recordings by default.
- Keep voice commands in Tier 0/Tier 1 unless a separate approval UX is used.
- Do not expose arbitrary shell or root actions to a spoken phrase.

Sources:

- Local diagnostic recorded in `context/05_task_board.md` on 2026-07-07: T480 Wi-Fi healthy, Ethernet sharing active on `10.42.0.1/24`, `ctos-core` reachable at `10.42.0.2`, `ctos-core` Wi-Fi hardware missing, tower egress restored by `scripts/ctos-firewall-fix-tower-egress`.
- Existing ADR-0049 Vosk voice input decision in this file.
- Existing CTOS AI permission tiers in `context/20_ctos_ai_v0_model.md`.

Rationale:

The T480 bastion design is simpler to reason about than a partially working tower Wi-Fi uplink. Push-to-talk voice gives the operator a real Jarvis-style interaction loop without introducing privacy risk, false wake triggers, or unreviewed state changes. The safe first command set should launch or display existing CTOS surfaces, not invent new authority.

Implementation:

- `ctos-voice` maps spoken/read phrases to safe intents: brief/status, agenda/day plan, DESK repair/open, VMS panel open, approvals list, capabilities, and help.
- `scripts/ctos-voice-ptt` provides a visible terminal push-to-talk launcher.
- Hyprland binds `SUPER+SHIFT+V` to the voice launcher and routes the `CTOS_VOICE` window to workspace `AI`.

Verification:

Planned focused checks:

- `ctos-voice probe --json`
- `ctos-voice command --no-speak aide`
- `ctos-voice command --no-speak "ouvre vms"`
- `ctos-voice command --no-speak "approbations"`
- `python3 -m py_compile scripts/ctos-voice scripts/ctos-ai`
- `hyprctl configerrors` after applying the desktop config live.

Consequences:

The tower remains operationally dependent on the T480 for egress. Voice can now open/read CTOS surfaces, but starting/stopping VMs, syncing repo state, package installs, and privileged changes remain outside direct voice execution.

## ADR-0051: Evaluate Home Assistant/Wyoming-style voice backend instead of expanding Vosk matching

Date: 2026-07-07
Status: accepted

Decision:

Keep the current Vosk push-to-talk path as the Voice V1 fallback, but start Voice Backend V2 as a backend spike around a mature local voice stack. The selected direction is Home Assistant Assist/Wyoming as the ecosystem target, Speech-to-Phrase-style fixed command recognition for CTOS intents, and Piper-quality local TTS after command recognition is reliable. OpenVoiceOS and Leon remain inspiration/sandbox candidates, not the primary install path.

Context:

The operator tested real push-to-talk voice and found that most commands work, but `agenda` was not reliably recognized. This is an expected limitation of the current Vosk-small-French plus substring routing approach. The desired Jarvis UX needs better command recognition and clearer voice output without giving voice phrases direct mutable authority over CTOS.

Constraints:

- Keep microphone use push-to-talk first.
- Do not add always-on wake word yet.
- Do not use cloud STT by default.
- Do not keep recordings/transcripts in the repo.
- Do not allow spoken phrases to directly execute Tier 2/Tier 3 actions.
- Keep `ctos-core` behind the T480 bastion for now.
- No new daemon or package install is accepted by this ADR.

Sources:

- Home Assistant local voice assistant docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant voice control docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant custom sentences docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences/
- Speech-to-Phrase repo, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Speech-to-Phrase README/packaging scan, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming Piper repo, accessed 2026-07-07: https://github.com/rhasspy/wyoming-piper
- OpenVoiceOS repo, accessed 2026-07-07: https://github.com/OpenVoiceOS/OpenVoiceOS
- Leon repo, accessed 2026-07-07: https://github.com/leon-ai/leon
- Current CTOS Voice V1 state: `scripts/ctos-voice`, `scripts/ctos-voice-ptt`, `context/20_ctos_ai_v0_model.md`.

Rationale:

Fixed CTOS commands are not the same problem as open dictation. A phrase/intent backend is more appropriate for `brief`, `agenda`, `ouvre desk`, `ouvre vms`, and similar commands than a free transcription model plus ad hoc fuzzy matching. Home Assistant Assist/Wyoming is a mature ecosystem to study and potentially reuse, while CTOS keeps its own action and approval boundary.

Implementation:

- Added `ai/voice_backends.json` as an inert backend registry.
- Added `ai/voice_intents_fr.json` as the CTOS-owned French intent catalog.
- Added `ai/voice_intents.py` as the shared deterministic matcher for helper and runtime use.
- Added `docs/VOICE_BACKEND_V2.md` as the operator runbook.
- Added `context/21_ctos_voice_backend_v2.md` as durable context.
- Added `scripts/ctos-voice-v2` for plan/status/backends/intents/match/sample-plan/regression/export-phrases/next-command handoff.
- Added `ctos-voice-v2` to the user-bin installer list.
- Updated `scripts/ctos-voice` so the real push-to-talk command path consumes `ai/voice_intents_fr.json` first and keeps the previous V1 matcher as fallback.
- Added agenda phrase variants for likely Vosk misrecognitions: `l agenda`, `a jenda`, and `ajenda`.
- Added Home Assistant/Speech-to-Phrase custom-sentence export from the CTOS intent catalog.
- Added a CTOS sidecar backend-intent map so backend recognition stays separate from CTOS command authority.
- Added backend bundle validation and non-mutating backend handoff command output.
- Added backend preflight output that reports bundle readiness, local tool readiness, Python runtime imports, optional `ctos-core` readiness, and Home Assistant websocket/token-file readiness.
- Updated Speech-to-Phrase handoff commands to make the first step a venv import/help smoke test, not a persistent daemon.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`
- `python3 -m json.tool ai/voice_backends.json`
- `python3 -m json.tool ai/voice_intents_fr.json`
- `ctos-voice-v2 plan`
- `ctos-voice-v2 status`
- `ctos-voice-v2 intents`
- `ctos-voice-v2 match agenda`
- `ctos-voice-v2 export-phrases --format jsonl`
- `ctos-voice-v2 next-commands`
- `scripts/ctos-install-user-bin --dry-run` showed only the new `ctos-voice-v2` symlink was missing.
- `scripts/ctos-install-user-bin` installed `/home/operator/.local/bin/ctos-voice-v2`.
- `command -v ctos-voice-v2` resolves to the new user-local command.
- `ctos-ai capabilities --json` includes `ctos-voice-v2 plan/status`.
- `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`
- `ctos-voice-v2 match "a jenda"` matched `ctos_agenda -> ctos-ai plan-day`.
- `ctos-voice command --no-speak agenda` matched the shared catalog and opened the day plan.
- `ctos-voice command --no-speak "a jenda"` matched the shared catalog and opened the day plan.
- `ctos-voice command --no-speak capacites` matched the shared catalog and opened the capabilities list.
- `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples-test --write-manifest` generated temporary sample commands and manifest rows outside Git.
- `ctos-voice-v2 regression --manifest /tmp/ctos-voice-regression.jsonl` passed transcript fixtures for `ctos_agenda`, `ctos_open_vms`, and `ctos_capabilities`.
- `ctos-voice-v2 export-phrases --format ha-sentences` emitted Home Assistant custom-sentence YAML.
- `ctos-voice-v2 export-phrases --format ha-map` emitted the CTOS sidecar intent map.
- `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend-test` wrote an inert backend bundle.
- `python3 -m json.tool /tmp/ctos-voice-backend-test/ctos_intent_map.json` validated the generated map.
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test` verified 6 backend intents and all CTOS phrases/commands/tiers.
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test --json` emitted machine-readable validation.
- `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend-test` printed the next non-mutating handoff commands.
- `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test` verified the exported bundle and reported missing runtime/Home Assistant context explicitly.

Consequences:

CTOS now has a concrete bridge toward a mature local voice ecosystem without installing a daemon. Speech-to-Phrase is treated as a serious backend candidate, but not as a magic standalone recognizer: a full test needs a temporary Home Assistant/Wyoming context and a token file outside Git. The next loop should test the exported custom sentences against a real backend and recorded French samples. Persistent Home Assistant/Wyoming/Piper services stay blocked until CTOS chooses an install path and service boundary.

## ADR-0052: Use a disposable Speech-to-Phrase venv smoke test before any persistent install

Date: 2026-07-07
Status: accepted

Decision:

Run the first Speech-to-Phrase runtime check in a disposable virtual environment under `/tmp`. The smoke test may install Python dependencies into that temporary venv and verify import/help behavior, but it must not create a durable user-local venv, install system packages, start a daemon, expose a port, or configure Home Assistant secrets.

Context:

Voice Backend V2 now exports and validates CTOS custom sentences, but the preflight correctly reports that `speech_to_phrase` and `wyoming` are not importable locally. Before choosing a persistent service layout, CTOS needs to know whether the upstream package installs and exposes a usable runtime/help surface on the current EndeavourOS/Python environment.

Constraints:

- Use `/tmp` for the smoke venv.
- No permanent package-manager install.
- No systemd service.
- No open listener.
- No token pasted into shell history.
- No recordings or transcripts committed to Git.
- Keep CTOS action authority separate from backend recognition labels.

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Speech-to-Phrase package metadata, accessed 2026-07-07: https://pypi.org/project/speech-to-phrase/
- Home Assistant custom sentences docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences/
- Home Assistant custom sentence YAML docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences_yaml/
- CTOS preflight result on 2026-07-07: `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`

Rationale:

A transient venv answers the narrow runtime question without locking CTOS into a service boundary. If install/import/help fails, the failure is cheap and local. If it succeeds, CTOS can decide whether the real backend belongs on the T480, `ctos-core`, or inside a future container.

Implementation:

- Create `/tmp/ctos-speech-to-phrase-smoke-venv`.
- Install Speech-to-Phrase in that venv only.
- Prefer `PIP_NO_CACHE_DIR=1` for future smoke commands so package caches are not written durably.
- Run Python import checks for `speech_to_phrase` and `wyoming`.
- Inspect available console/module help without starting a server.
- Re-run `ctos-voice-v2 backend-preflight` using the normal system Python to confirm that the durable environment remains unchanged.
- Re-run `ctos-voice-v2 backend-preflight --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python` to confirm the disposable runtime is recognized.

Verification:

Completed on 2026-07-07:

- `python3 -m venv /tmp/ctos-speech-to-phrase-smoke-venv`
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m pip install speech-to-phrase` failed because PyPI had no matching distribution for the current environment.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m pip index versions speech-to-phrase -v` found no matching distribution.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m pip index versions speech_to_phrase -v` found no matching distribution.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m pip install git+https://github.com/OHF-Voice/speech-to-phrase.git` succeeded from commit `b4ecef9519e84fefd5dc35c0384c50efa13a0bad`.
- Import check reported `speech_to_phrase 1.4.3` and `wyoming 1.5.4`.
- Console-script inspection found no dedicated `speech-to-phrase` executable.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase --help` succeeded and listed the required runtime arguments.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase --version` reported `1.4.3`.
- `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python` reported `backend_runtime_ready True` and `full_recognition_ready False`.
- `hassil.Intents.from_files([.../custom_sentences/fr/ctos.yaml])` inside the temporary venv parsed the generated CTOS custom sentences and found all six backend intent labels.
- `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase.train --help` succeeded, confirming a no-Home-Assistant training entry point.
- The same preflight now reports `offline_training_context_ready False` because `/srv/ctos/models/speech-to-phrase` and `/srv/ctos/cache/speech-to-phrase/tools` do not yet contain the `fr_FR-rhasspy` model and Kaldi/OpenFST/OpenGRM/Phonetisaurus tools.

Note:

During the first escalated install, `pip` wrote a wheel cache entry under the user's pip cache despite the venv being under `/tmp`. Future generated commands include `PIP_NO_CACHE_DIR=1`; no cache cleanup was performed automatically.

Consequence:

The next Speech-to-Phrase step is not more fuzzy phrase matching. It is a cache/storage decision for the French model and speech tools, probably on `ctos-core` under `/srv/ctos`, followed by an explicit offline training run. A full live recognizer still also needs a temporary Home Assistant websocket URI and token file outside Git.

## ADR-0053: Put Speech-to-Phrase model/tool caches on ctos-core

Date: 2026-07-07
Status: accepted

Decision:

Use `ctos-core` as the preferred owner for Speech-to-Phrase model, training, and speech-tool caches:

- model cache: `/srv/ctos/models/speech-to-phrase`
- training cache: `/srv/ctos/cache/speech-to-phrase/train`
- tools cache: `/srv/ctos/cache/speech-to-phrase/tools`

Add a read-only helper path through `ctos-voice-v2 stp-cache` so CTOS can inspect cache readiness locally and over SSH before running downloads, training, or services.

Context:

The T480 is the control/bastion machine and should stay light. The heavier Jarvis backend path needs a French `fr_FR-rhasspy` Kaldi model plus Kaldi/OpenFST/OpenGRM/Phonetisaurus tooling. This belongs with the service/model storage on `ctos-core`, not in transient T480 user state.

Constraints:

- No automatic model/tool download in this decision.
- No Home Assistant token in shell history.
- No daemon/service creation.
- No recordings or transcripts in Git.
- Keep the CTOS intent catalog and action tiers as the source of command authority.

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Local Speech-to-Phrase installed source inspected on 2026-07-07: `speech_to_phrase/train.py`, `train_kaldi.py`, `models.py`, and `speech_tools.py`
- Home Assistant Wyoming integration docs, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- CTOS core storage convention from `context/17_archipelago_fleet_model.md` and `context/20_ctos_ai_v0_model.md`

Rationale:

Keeping model/tool caches on `ctos-core` aligns the eventual voice backend with the existing AI/runtime placement model. The T480 remains the operator microphone, UI, and bastion; `ctos-core` carries heavier model artifacts and later services.

Verification:

Completed on 2026-07-07:

- `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python` identified `fr_FR-rhasspy`, rendered the model URL, and reported missing local model/tool cache paths.
- `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --json` emitted machine-readable cache status.
- `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --target-probe` reached `ctos-core` over SSH outside the sandbox and confirmed all required model/tool cache paths are currently missing.

Consequence:

The next implementation step is a controlled cache/bootstrap command for `ctos-core`, not a broader assistant install. Once the model/tools cache exists, CTOS can run the commented `speech_to_phrase.train` command against the generated CTOS custom-sentence YAML and evaluate real command recognition.

## ADR-0054: Prefer the official Speech-to-Phrase Wyoming container for the first live voice backend

Date: 2026-07-07
Status: accepted

Decision:

For the first live Speech-to-Phrase backend test, prefer the official `docker.io/rhasspy/wyoming-speech-to-phrase` container on `ctos-core` instead of building or assembling a local Kaldi/OpenFST/OpenGRM/Phonetisaurus toolchain directly on EndeavourOS.

Keep CTOS-generated custom sentences and intent mapping outside the container under:

- `/srv/ctos/voice/backend/speech-to-phrase/custom_sentences`
- `/srv/ctos/voice/backend/speech-to-phrase/ctos_intent_map.json`

Run any first container test localhost-only on `ctos-core`, for example `tcp://127.0.0.1:10300`, and tunnel it from the T480 when needed. Do not create a persistent service until a manual `--help` inspection and one recognition loop have passed.

Context:

The user wants a more sophisticated local Jarvis path now, not months of ad hoc Vosk phrase tuning. The local Python package spike proved that Speech-to-Phrase imports and parses CTOS custom sentences, but its no-Home-Assistant trainer expects Kaldi/OpenFST/OpenGRM/Phonetisaurus tool paths to already exist. A containerized Wyoming backend is the smaller live test because it keeps backend dependencies isolated while CTOS preserves action authority.

Constraints:

- No always-on microphone.
- No cloud STT by default.
- No Home Assistant token in Git or shell history; use a token file and environment variable.
- No direct voice execution of Tier 2/Tier 3 CTOS actions.
- No persistent daemon until a manual live loop is verified.
- `ctos-core` remains behind the T480 bastion.

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Speech-to-Phrase Docker Hub image page, accessed 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-speech-to-phrase
- Local Speech-to-Phrase installed source inspected on 2026-07-07: `speech_to_phrase/__main__.py`, `train.py`, `train_kaldi.py`, `models.py`, and `speech_tools.py`
- Home Assistant Wyoming integration docs, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/

Rationale:

This keeps the first mature voice backend test reversible and isolated. It avoids turning the host into a hand-built speech-toolchain machine before CTOS has proven the live recognition loop. It also matches the existing architecture: the T480 remains the operator/bastion node, and `ctos-core` carries heavier runtime/model artifacts.

Verification:

Completed on 2026-07-07:

- `ctos-voice-v2 stp-container-plan` rendered the container-first plan without starting a container.
- `ctos-voice-v2 stp-container-plan --target-probe` reached `ctos-core`, found `/usr/bin/podman`, and confirmed `/srv/ctos/voice/backend/speech-to-phrase/custom_sentences` is present.
- `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend` generated the inert CTOS backend bundle.
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend` verified 6 Tier 0/1 intents.
- The validated bundle was copied to `ctos-core` with `tar` over SSH.
- Local and remote `sha256sum` values matched for the bundle files.
- The first unqualified image probe failed because Podman refused short-name resolution for `rhasspy/wyoming-speech-to-phrase`; CTOS now uses the fully qualified `docker.io/rhasspy/wyoming-speech-to-phrase` image reference.
- `ctos-voice-v2 stp-container-inspect` pulled the fully qualified image on `ctos-core`, verified `--help`, and recorded digest `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`.
- Remote image inspection found `ENTRYPOINT=["bash","/run.sh"]`; `/run.sh` runs from `/usr/src` and passes image-internal `--tools-dir ./tools`, so CTOS must not mount or override `/tools` for the first live container test.
- `/srv/ctos/cache/speech-to-phrase/train` and `/srv/ctos/models/speech-to-phrase` were created on `ctos-core` as `ctos:ctos` with setgid directory permissions.
- The generated live test command now mounts the Home Assistant token file read-only into the temporary container at `/run/secrets/ctos-ha-token` and reads it inside the container entrypoint. This avoids printing the token or passing it as a host shell token argument.
- `ctos-voice-v2 stp-container-plan --target-probe` still verifies `ctos-core` readiness after this command-shape change: `/usr/bin/podman` is present, and `backend_dir`, `custom_sentences`, `train_dir`, and `models_dir` all exist.
- `ctos-voice-v2 stp-container status|start|stop|logs` now manages the temporary container without a persistent service. `start` runs the Home Assistant token/API gate before any `podman run`; with the current missing token, it expected-fails with `blocked_before_container_start`, leaving the container absent and port `10300` free.

Consequence:

The next implementation step is not a local Kaldi build and not another container inspection. It is choosing the smallest temporary Home Assistant/Wyoming websocket/token-file context, then running one localhost-only manual recognition loop through the inspected container before any persistent service is created.

## ADR-0055: Use a temporary localhost-only Home Assistant container for the first Speech-to-Phrase loop

Date: 2026-07-07
Status: accepted

Decision:

Use a temporary Home Assistant Container instance on `ctos-core` only to provide the websocket/API context and long-lived token expected by Speech-to-Phrase. The first test shape is:

- image: `ghcr.io/home-assistant/home-assistant:stable`
- runtime: rootless `podman`
- config: `/srv/ctos/voice/home-assistant-test/config`
- bind: `127.0.0.1:8123:8123`
- token file: `/run/user/$UID/ctos-ha-token`
- lifecycle: manual `podman run --rm`, no systemd unit

Do not use Home Assistant OS/Supervisor and do not expose the UI/API on LAN for the first test. Do not mount privileged host devices, DBus, or hardware integrations. The first purpose is a no-device recognition loop, not home automation.

Context:

The user correctly identified that manually tuning Vosk phrase drift will not scale into a useful Jarvis. Speech-to-Phrase is the stronger fixed-command recognizer, but the live backend expects Home Assistant websocket/token context. A full Home Assistant install would add persistent services and broad state before CTOS has verified one command loop.

Constraints:

- Keep CTOS as the action and approval boundary.
- No always-on microphone.
- No cloud STT by default.
- No Home Assistant token in Git or shell history.
- No persistent service until a manual recognition loop passes.
- `ctos-core` remains behind the T480 bastion.

Sources:

- Home Assistant Linux/Container installation docs, accessed 2026-07-07: https://www.home-assistant.io/installation/linux
- Home Assistant WebSocket API docs, accessed 2026-07-07: https://developers.home-assistant.io/docs/api/websocket/
- Home Assistant local voice assistant docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Speech-to-Phrase repo/README and local container inspection from ADR-0054, accessed/checked 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase

Rationale:

This gives CTOS a mature local assistant context quickly without adopting a full home-automation platform as the authority layer. Home Assistant supplies the websocket/token surface and future Assist/Wyoming compatibility; CTOS supplies permissions, agenda actions, VM actions, and approval policy.

Verification:

Completed on 2026-07-07:

- `ctos-voice-v2 hass-context-plan` rendered the temporary Home Assistant container, tunnel, onboarding, token, and Speech-to-Phrase follow-up commands without starting a service.
- `ctos-voice-v2 hass-context-plan --json` emitted the same plan as machine-readable JSON.
- `ctos-voice-v2 hass-context start` pulled `ghcr.io/home-assistant/home-assistant:stable`, started `ctos-ha-test`, and kept the API/UI bound to `127.0.0.1:8123`.
- `ctos-voice-v2 hass-context status --json` verified image present, container running, port busy, and HTTP `302`.
- Home Assistant image inspection on `ctos-core` recorded image id `ceb81d836a0b125a4ec14a754231a5dd1cc5f2feb2594107320c3cea345dd9d1`, digest `sha256:21e0d1bae299819d8cf4ef8aa197593205a5fae51c69031c13bfd1eac8c56204`, and size `2486193643`.
- `ctos-voice-v2 hass-context logs --logs-tail 20` showed first startup. The rootless container reports a DHCP watcher permission warning, which is acceptable for the current websocket/token-only test because no LAN device discovery is required.
- `ctos-voice-v2 hass-context token-status|readiness|tunnel-command|token-command` now provides a safe preflight for the manual onboarding boundary. The token checks print only file metadata and HTTP/API readiness, never token content. `token-status` and `readiness` exit non-zero until `state=ready`, so the commands can safely gate the Speech-to-Phrase run.
- `ctos-voice-v2 hass-context readiness` verified that `ctos-ha-test` is running on `ctos-core`, the Home Assistant image is present, localhost port `8123` is busy, and HTTP returns `302`; the remaining blocker is the missing `/run/user/1000/ctos-ha-token` file.
- Expected-fail verification confirmed both `ctos-voice-v2 hass-context readiness` and `ctos-voice-v2 hass-context token-status` return non-zero while reporting `state=missing_token`.

Pending:

- Complete onboarding through an SSH tunnel, create the token file, and run one localhost-only Speech-to-Phrase recognition loop.

Update 2026-07-07:

Because the T480 currently has no classic browser available for the tunneled Home Assistant UI, CTOS now provides `ctos-voice-v2 hass-context onboard-api` as a browserless first-onboarding helper. This helper is limited to the temporary localhost-only Home Assistant context and was implemented only after inspecting the running container's server-side schemas:

- `/api/onboarding/users` requires `name`, `username`, `password`, `client_id`, and `language`.
- `/auth/token` accepts the returned authorization code.
- `/api/onboarding/core_config`, `/api/onboarding/analytics`, and `/api/onboarding/integration` are called with the short-lived access token.
- `auth/long_lived_access_token` is created through the authenticated Home Assistant websocket with `lifespan` and `client_name`.

The helper prompts for secrets, never prints the password/auth code/access token/refresh token/long-lived token, and stores only the generated long-lived token through the existing `/run/user/$UID/ctos-ha-token` path on `ctos-core`.

Update 2026-07-07:

`scripts/ctos-voice-setup` is the guided operator entry point for this temporary stack. It does not introduce a service or a new trust boundary; it sequences the already documented checks: `ctos-core` probe, Home Assistant status/start, token readiness, browserless onboarding when needed, Speech-to-Phrase start, and open-STT path probe. It supports `--plan` so the operator can audit the steps without touching SSH, containers, or secrets.

Consequence:

The next Jarvis step is not more Vosk synonym tuning. It is a controlled, temporary Home Assistant context plus Speech-to-Phrase recognition test. If that loop passes, CTOS can decide whether to keep Home Assistant as a voice bus, replace it later with a custom local service, or use it only as an adapter while local models mature on `ctos-core`.

## ADR-0056: Use a mature hybrid voice stack instead of building Jarvis voice from scratch

Date: 2026-07-07
Status: accepted

Decision:

Stop treating every missed French keyword as a phrase-matching problem. For the next usable Jarvis milestone, CTOS should use a mature local voice stack for audio I/O and language understanding adapters, while keeping CTOS as the action, permission, audit, and approval boundary.

The target shape is hybrid:

- Home Assistant Assist + Wyoming as the local voice bus and adapter layer.
- Speech-to-Phrase for deterministic, safety-sensitive fixed commands.
- A local open-ended STT path, likely Whisper-compatible through Wyoming, for natural dictation and conversational requests.
- Piper or an equivalent local TTS backend for audible responses.
- `ctos-ai`, `ctos-agenda`, VM controls, desktop controls, and future worker orchestration as CTOS-owned tools exposed through a narrow command/approval API.

Do not adopt a full third-party assistant as the root authority for the machine. OpenVoiceOS and Open Interpreter/01 remain inspiration and possible sandboxed research targets, but they should not receive direct unattended control over CTOS hosts. AirLLM and GLM-family model research belong to the later model-runtime layer, not the first voice-bus decision.

Context:

The live push-to-talk test mostly worked, but the word `agenda` was missed. That is expected for a narrow phrase recognizer and should not drive an endless synonym-tuning loop. The user wants a Jarvis that can converse, organize time, and perform real machine operations. That needs both deterministic commands and flexible natural language input.

Constraints:

- Keep the T480 as the operator/bastion node and `ctos-core` as the heavier runtime host.
- Keep all microphones push-to-talk or explicitly session-scoped until a permission model exists.
- No cloud STT/TTS by default.
- No raw voice-to-shell execution.
- Tier 2/Tier 3 actions still require explicit confirmation or a CTOS approval gate.
- Do not store tokens, audio transcripts, or private schedules in Git.

Sources:

- Home Assistant voice control documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant Wyoming integration documentation, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Speech-to-Phrase repository, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- OpenVoiceOS core repository, accessed 2026-07-07: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter documentation, accessed 2026-07-07: https://docs.openinterpreter.com/
- Open Interpreter 01 repository, accessed 2026-07-07: https://github.com/OpenInterpreter/01
- AirLLM repository lookup, accessed 2026-07-07: https://github.com/lyogavin/airllm
- GLM model-family lookup, accessed 2026-07-07: https://github.com/zai-org/GLM-4.5

Rationale:

Home Assistant/Wyoming gives CTOS a local, modular voice ecosystem now, instead of forcing CTOS to become an audio platform before it becomes useful. Speech-to-Phrase stays valuable for commands that must be exact. A Whisper-like STT path handles the user’s real need: saying “ajoute un rendez-vous demain” or “organise ma journée” without pre-enumerating every possible phrase. CTOS remains the safety layer that translates recognized intent into owned-system actions.

Verification:

Completed on 2026-07-07:

- Current CTOS phrase matching already handles the deterministic `agenda` text path.
- The live voice test proved the current narrow recognizer can miss short French command words.
- The temporary Home Assistant + Speech-to-Phrase path is already implemented up to the onboarding/token blocker.
- `ctos-voice-v2 open-stt-plan` now renders the open-ended STT rail plan and policy without installing packages or starting services.
- `ctos-voice-v2 open-stt-plan --target-prepare --target-probe` created and verified the planned `ctos-core` directories: `/srv/ctos/models/open-stt`, `/srv/ctos/cache/open-stt`, and `/srv/ctos/voice/backend/open-stt`.

Consequence:

The next Jarvis implementation should complete one Speech-to-Phrase loop only as the fixed-command rail, then add a local open-ended STT rail before more phrase-tuning work. The first useful assistant interface should accept typed text and push-to-talk speech into the same CTOS intent/action planner so the product improves without being blocked by voice recognition accuracy.

## ADR-0057: Route typed and spoken Jarvis requests through one CTOS action planner

Date: 2026-07-07
Status: accepted

Decision:

Create a shared CTOS action planner for both typed text and voice/STT transcripts. The planner lives in `ai/action_planner.py` and is exposed through `ctos-ai route-text`. The live `ctos-voice command` deterministic catalog path now uses the same planner before executing anything.

The planner may directly execute only Tier 0/Tier 1 commands owned by `ctos-ai`, and only when `--execute-safe` is explicitly passed. By default, it prints a plan and performs no action. Unmatched natural-language requests stay as transcript text with a category such as `agenda_candidate`, `vm_candidate`, or `assistant_candidate`; they are not converted into shell commands or mutable system actions.

Context:

The user correctly pushed against spending months tuning one narrow phrase recognizer. A mature stack such as Home Assistant Assist/Wyoming can provide audio I/O, Speech-to-Phrase, Whisper-class STT, and Piper TTS, but CTOS still needs one local boundary that decides what recognized text is allowed to do.

Constraints:

- Voice recognition quality must not determine the safety boundary.
- Speech-to-Phrase and open-ended STT must both feed the same CTOS policy.
- No raw voice-to-shell execution.
- VM lifecycle, package installs, firewall/network edits, and agenda mutations beyond read/plan remain outside direct voice execution until a parser plus approval loop exists.
- Do not persist private transcripts by default.

Sources:

- ADR-0056 sources and rationale in this decision log.
- Existing CTOS AI approval queue decision in ADR-0042.
- Existing Vosk push-to-talk boundary in ADR-0050.
- Local implementation files: `ai/voice_intents.py`, `ai/voice_intents_fr.json`, `scripts/ctos-ai`, and `scripts/ctos-voice`.

Rationale:

The mature voice stack should be treated as an input layer, not as the root authority for the machine. A shared planner lets CTOS accept text from Vosk today, Speech-to-Phrase tomorrow, and Whisper later without re-implementing action policy in every adapter. It also provides a typed debug path, so voice recognition bugs can be isolated from intent/action bugs.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile ai/action_planner.py ai/voice_intents.py scripts/ctos-ai scripts/ctos-voice scripts/ctos-voice-v2`
- `python3 -m json.tool ai/voice_intents_fr.json`
- `ctos-ai route-text agenda --json` matched `ctos_agenda` with `safe_to_execute=true`.
- `ctos-ai route-text --source voice --execute-safe agenda` executed `ctos-ai plan-day` and printed the current agenda plan.
- `ctos-ai route-text "ajoute un rendez-vous demain" --json` classified the request as `agenda_candidate` without execution.
- `ctos-ai route-text --execute-safe "ajoute un rendez-vous demain" --json` refused execution with rc `2`.
- `ctos-voice command --no-speak agenda` used the shared planner and executed `ctos-ai plan-day`.
- `ctos-ai capabilities --json` includes `route-text`.
- targeted `git diff --check` over the changed files passed.

Consequence:

The next useful Jarvis slice is the first permissioned agenda action loop: parse a natural request into a proposed agenda change, show the exact mutation, require confirmation, and only then write to `ctos-agenda`. Piper can be added after the recognition/action boundary is stable.

## ADR-0058: Add a permissioned natural-language agenda proposal loop

Date: 2026-07-07
Status: accepted

Decision:

Add a deterministic local agenda parser in `ai/agenda_parser.py` and expose it through `ctos-ai agenda-propose`. The command parses simple French requests such as `ajoute acheter du lait demain 30 min priorité 4` into a proposed `ctos-agenda add ...` command. It writes nothing by default. A real agenda mutation requires both `--commit` and `--yes`.

`ctos-ai route-text` may attach an `agenda_proposal` for unmatched agenda-like text, but it still does not execute the mutation. The existing `ctos-agenda` store remains the only writer.

Context:

The user wants a practical Jarvis path, not months of hand-tuning voice phrases. The shared action planner can already route fixed commands such as `agenda`, but natural requests need a bounded parser before they can safely become local actions.

Constraints:

- No raw voice-to-shell execution.
- No agenda write from voice or STT without a reviewed proposal and explicit confirmation.
- No new package, daemon, cloud service, or model runtime for this slice.
- No private agenda test data in Git; tests use `CTOS_AI_DB=/tmp/...`.
- Keep the parser intentionally narrow and expand only from real missed French forms.

Sources:

- ADR-0056 mature hybrid voice stack decision.
- ADR-0057 shared CTOS action planner decision.
- Existing local agenda tool: `scripts/ctos-agenda`.
- Existing local implementation files: `ai/action_planner.py`, `scripts/ctos-ai`, and `scripts/ctos-voice`.

Rationale:

This creates the first useful "natural language to action" bridge while preserving CTOS as the permission boundary. The parser can serve typed input, Vosk transcripts, Speech-to-Phrase transcripts, and a future Whisper-compatible rail without giving any STT backend direct system authority.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile ai/agenda_parser.py ai/action_planner.py ai/voice_intents.py scripts/ctos-ai scripts/ctos-voice scripts/ctos-voice-v2 scripts/ctos-agenda`
- `python3 -m json.tool ai/voice_intents_fr.json`
- `ctos-ai route-text "ajoute acheter du lait demain 30 min priorité 4" --json`
- `ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --json`
- `CTOS_AI_DB=/tmp/ctos-agenda-propose-final.sqlite3 ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --commit --yes --json`
- `CTOS_AI_DB=/tmp/ctos-agenda-propose-final.sqlite3 scripts/ctos-agenda list --json`
- `CTOS_AI_DB=/tmp/ctos-agenda-propose-refuse.sqlite3 ctos-ai agenda-propose "ajoute acheter du pain demain" --commit` refused with rc `2` because `--yes` was absent.
- `ctos-ai capabilities --json`
- targeted `git diff --check` over the changed files passed.

Consequence:

The next implementation step can wire open-ended STT transcripts into `ctos-ai route-text` and then into `agenda-propose` for operator review. Parser expansion should be driven by real failed phrases, not speculative grammar work.

## ADR-0059: Route push-to-talk transcripts through the CTOS planner before mutation

Date: 2026-07-07
Status: accepted

Decision:

Add `ctos-voice route` and `ctos-voice route-once` as the voice-facing natural-language routing path. `route` accepts typed transcript text for debugging. `route-once` records or reads one WAV, transcribes it with the current Vosk backend, and sends the transcript into the shared CTOS planner.

This path prints deterministic matches and agenda proposals, but it does not write agenda tasks by default. `--execute-safe` is still limited to Tier 0/Tier 1 commands already considered safe by the planner. Agenda writes remain behind `ctos-ai agenda-propose ... --commit --yes`.

Context:

The fixed `ctos-voice voice-command` path is useful for short commands such as `agenda`, but it is a poor fit for natural requests like `ajoute acheter du lait demain`. The user wants a practical Jarvis interface, so the microphone path must start feeding the same planner used by typed text and future STT backends.

Constraints:

- Keep microphone use push-to-talk.
- Do not persist audio by default.
- Do not execute raw transcripts as shell commands.
- Do not write agenda state from natural speech without explicit reviewed confirmation.
- Keep `voice-command` available as the deterministic fixed-command rail.

Sources:

- ADR-0056 mature hybrid voice stack decision.
- ADR-0057 shared CTOS action planner decision.
- ADR-0058 permissioned natural-language agenda proposal loop.
- Local implementation files: `scripts/ctos-voice`, `ai/action_planner.py`, and `scripts/ctos-ai`.

Rationale:

This gives the current Vosk push-to-talk setup a useful Jarvis-shaped behavior immediately, without waiting for Home Assistant, Speech-to-Phrase, Whisper, or Piper. It also ensures future mature STT backends can replace the transcription layer without changing the action safety boundary.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile scripts/ctos-voice ai/action_planner.py ai/agenda_parser.py scripts/ctos-ai`
- `ctos-voice route "ajoute acheter du lait demain 30 min priorité 4" --no-speak`
- `ctos-voice route "ajoute acheter du lait demain 30 min priorité 4" --execute-safe --no-speak --json` refused with rc `2`.
- `ctos-voice route agenda --execute-safe --no-speak` executed only the safe agenda day plan.

Consequence:

The next live test can use `ctos-voice route-once --seconds 4 --no-speak` and speak a natural agenda phrase. If the transcript is poor, the fix belongs in STT/backend quality or recorded regression samples, not in the action permission layer.

## ADR-0060: Store voice agenda proposals before confirmed agenda writes

Date: 2026-07-07
Status: accepted

Decision:

Add a pending agenda-proposal queue inside the CTOS approval DB. `ctos-ai agenda-propose ... --save --source voice` stores a reviewed proposal without mutating agenda state. `ctos-ai agenda-proposals`, `ctos-ai agenda-show latest`, `ctos-ai agenda-confirm latest --yes`, and `ctos-ai agenda-reject latest` expose the review loop. `ctos-voice route ... --save-agenda` and `ctos-voice route-once ... --save-agenda` may store recognized agenda proposals, but direct natural-language agenda writes still require explicit confirmation.

Context:

The user tested push-to-talk voice and found that the simple command path mostly works but can miss words such as `agenda`. Continuing to tune a single keyword would not scale. The useful Jarvis behavior is to understand agenda-like requests from their structure, stage them safely, and let the operator confirm them later.

Constraints:

- Keep voice push-to-talk only.
- Do not persist audio by default.
- Do not write the real agenda from a raw voice transcript.
- Keep proposal state out of Git; it lives in the local CTOS state DB.
- Refuse ambiguous mixed modes such as `--save-agenda --execute-safe`.

Sources:

- ADR-0056 mature hybrid voice stack decision.
- ADR-0057 shared CTOS action planner decision.
- ADR-0058 natural-language agenda proposal loop.
- ADR-0059 push-to-talk planner route.
- Local implementation files: `scripts/ctos-ai`, `scripts/ctos-voice`, and `ai/agenda_parser.py`.

Rationale:

This is the smallest practical step between "voice understood something" and "Jarvis changed my system." The operator gets an actual workflow from speech to pending action, while CTOS preserves reviewability and avoids training the system to execute noisy STT output. Future Home Assistant/Wyoming, Speech-to-Phrase, Whisper-compatible STT, or Piper components can feed the same proposal queue without changing the action boundary.

Verification:

Completed on 2026-07-07 with temporary `/tmp` state databases:

- `CTOS_AI_APPROVAL_DB=/tmp/ctos-agenda-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-agenda-tasks.sqlite3 scripts/ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --save --source voice --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-agenda-proposals.sqlite3 scripts/ctos-ai agenda-proposals --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-agenda-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-agenda-tasks.sqlite3 scripts/ctos-ai agenda-confirm latest` refused with rc `2` because `--yes` was absent.
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-agenda-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-agenda-tasks.sqlite3 scripts/ctos-ai agenda-confirm latest --yes`
- `CTOS_AI_DB=/tmp/ctos-agenda-tasks.sqlite3 scripts/ctos-agenda list --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-voice-agenda-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-voice-agenda-tasks.sqlite3 scripts/ctos-voice route "ajoute acheter du pain demain" --save-agenda --no-speak`
- `scripts/ctos-voice route "ajoute acheter du pain demain" --save-agenda --execute-safe --no-speak` refused with rc `2`.
- `python3 -m py_compile scripts/ctos-ai scripts/ctos-voice ai/action_planner.py ai/agenda_parser.py scripts/ctos-agenda`

Consequence:

The next Jarvis step can improve the operator-facing confirmation UX and then connect a mature STT backend to this queue. It should not broaden voice authority to VM lifecycle, package installs, firewall, or shell commands until those action families have equally explicit proposal schemas and approval surfaces.

## ADR-0061: Make voice agenda review read-only

Date: 2026-07-07
Status: accepted

Decision:

Add `ctos-ai agenda-review` as the default pending-proposal review surface, and add the safe voice intent `ctos_agenda_review` for phrases such as `propositions agenda`, `validation agenda`, and `agenda en attente`. The command lists pending agenda proposals and prints exact typed confirm/reject commands. It does not confirm or reject by voice.

Context:

The saved proposal queue makes voice useful for staging agenda changes, but a noisy STT phrase should not be able to approve a local mutation by accident. The operator still needs a fast way to ask "what is waiting?" without remembering SQL-like or approval-queue commands.

Constraints:

- Keep voice review read-only.
- Keep confirmation as explicit typed `ctos-ai agenda-confirm latest --yes`.
- Do not change existing `agenda` intent semantics; it continues to show the day plan.
- Preserve the same CTOS action planner boundary for Vosk, Speech-to-Phrase, Whisper, and typed text.

Sources:

- ADR-0060 saved agenda proposal loop.
- Local implementation files: `scripts/ctos-ai`, `scripts/ctos-voice`, `ai/voice_intents_fr.json`.

Rationale:

Separating "show pending proposals" from "confirm pending proposals" gives the Jarvis workflow a useful operator loop while keeping accidental voice activation harmless. It also gives future assistant UIs a stable read-only endpoint before adding richer visual review.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile scripts/ctos-ai scripts/ctos-voice ai/action_planner.py ai/agenda_parser.py ai/voice_intents.py scripts/ctos-agenda scripts/ctos-voice-v2`
- `python3 -m json.tool ai/voice_intents_fr.json`
- `ctos-voice-v2 match "propositions agenda"` matched `ctos_agenda_review`.
- With temporary `/tmp` proposal state, `ctos-ai agenda-review`, `ctos-ai agenda-review --json`, and `ctos-voice command --no-speak "propositions agenda"` displayed a pending proposal and did not commit it.

Consequence:

The next UX step can be a compact cockpit panel or a spoken summary for pending agenda proposals. Direct voice confirmation should remain deferred unless CTOS adds a stronger confirmation protocol than a single transcribed phrase.

## ADR-0062: Add a bounded Jarvis assistant bridge before full voice-backend onboarding

Date: 2026-07-07
Status: accepted

Decision:

Add `ctos-voice assistant` and `ctos-voice assistant-once` as the practical interim Jarvis surface. The command order is:

1. Route recognized text through the CTOS safe action planner.
2. Stage agenda proposals only when `--save-agenda` is explicit.
3. Fall back to the local Ollama model through a restricted CTOS prompt.

The fallback model has no tool authority. It cannot execute shell commands, install packages, change firewall rules, start or stop VMs, approve agenda writes, or mutate system state from its own response.

Context:

The user reported that the current push-to-talk command path mostly works, but missed `agenda`. Tuning single words would not scale and could turn into months of brittle phrase work. Current research still points to a hybrid stack: mature local voice infrastructure for capture/STT/TTS and CTOS for action routing, permissions, and auditability.

Constraints:

- Keep microphone use push-to-talk for now.
- Do not persist audio by default.
- Do not let open-ended model text become shell commands.
- Keep Home Assistant Assist/Wyoming/Speech-to-Phrase as the mature deterministic rail once token onboarding is complete.
- Treat OpenVoiceOS, Open Interpreter/01-style work, GLM-family models, and AirLLM-style offload as inspiration or runtime candidates, not as the CTOS authority boundary.

Sources:

- ADR-0056 mature hybrid voice stack decision.
- ADR-0057 shared CTOS action planner decision.
- ADR-0058 permissioned natural-language agenda proposal loop.
- ADR-0059 push-to-talk planner route.
- ADR-0060 saved agenda proposal loop.
- ADR-0061 read-only voice agenda review.
- Home Assistant voice documentation: https://www.home-assistant.io/voice_control/
- Home Assistant local assistant documentation: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Speech-to-Phrase project: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming protocol project: https://github.com/rhasspy/wyoming
- OpenVoiceOS project: https://github.com/OpenVoiceOS/OpenVoiceOS
- Open Interpreter project: https://github.com/OpenInterpreter/open-interpreter
- GLM-5.2 / GLM project organization/repo: https://github.com/zai-org/GLM-5
- AirLLM reference implementation: https://github.com/lyogavin/Anima/tree/main/air_llm
- Local implementation files: `scripts/ctos-voice`, `scripts/ctos-ai`, `scripts/ctos-voice-v2`, `ai/action_planner.py`, and `ai/local_api.py`.

Rationale:

This avoids two bad extremes: building an entire voice assistant platform from scratch, or handing CTOS authority to a generic open-source assistant before its permissions are clear. The user gets a usable Jarvis-like loop now, and the system can later swap Vosk for Speech-to-Phrase, Whisper-compatible STT, Home Assistant Assist, or another local backend without changing the action boundary.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile scripts/ctos-voice scripts/ctos-ai scripts/ctos-voice-v2 ai/action_planner.py ai/agenda_parser.py ai/voice_intents.py ai/local_api.py ai/ctos_prompt.py`
- `ctos-voice assistant agenda --no-speak --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-assistant-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-assistant-tasks.sqlite3 ctos-voice assistant "ajoute acheter du pain demain 30 min priorité 4" --save-agenda --no-speak --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-assistant-proposals.sqlite3 ctos-ai agenda-proposals --json`
- `ctos-voice assistant "explique en une phrase ce que tu peux faire" --no-speak --json`
- `ctos-voice --help`
- `ctos-voice-v2 next-commands`
- `ctos-ai capabilities --json`
- targeted `git diff --check`

Consequence:

The immediate next user-facing path is `ctos-voice assistant-once --seconds 4`, not more exact synonym tuning. Home Assistant onboarding/token creation remains the blocker for the deterministic Speech-to-Phrase rail, and full persistent voice service work stays deferred until that rail and the open-ended STT rail both pass.

## ADR-0063: Add `ctos-jarvis` as the operator facade, not a new authority layer

Date: 2026-07-07
Status: accepted

Decision:

Add `scripts/ctos-jarvis` as the daily operator entrypoint for the current Jarvis work. It wraps:

- `brief`
- `smoke`
- `doctor`
- `next`
- typed assistant text with `text` / `ask`
- one push-to-talk phrase with `voice`
- read-only agenda proposal review with `review`
- explicit typed agenda proposal `confirm` / `reject`
- `unlock-voice` for the mature Home Assistant/Speech-to-Phrase rail gate
- `setup-voice` for the mature Home Assistant/Wyoming backend gate

`ctos-jarvis` does not introduce a new permission model, daemon, package, socket, or model authority. It calls the existing CTOS commands and therefore inherits their safety boundaries.
`smoke` is local and non-destructive by default: it uses temporary `/tmp` agenda databases for mutation-shaped tests, and it includes `ctos-core`/model checks only when requested with `--full` or `--with-model`.
`unlock-voice` is also only a wrapper: by default it performs the idempotent localhost Home Assistant tunnel check/start and summarizes `ctos-voice-v2 doctor --json`. It does not create Home Assistant credentials or run microphone recognition unless the operator explicitly uses `--interactive` or `--test`. It starts the Speech-to-Phrase container only when the doctor reports `ready_to_start_speech_to_phrase` and the operator uses `--start` or `--test`.

Context:

The current Jarvis stack has become powerful enough that the operator should not need to remember internal commands such as `ctos-voice assistant-once`, `ctos-ai agenda-review`, or `ctos-voice-v2 hass-context readiness` for normal use. At the same time, making a more convenient command must not accidentally bypass the action planner, agenda proposal queue, Home Assistant token gate, or no-shell-authority rule.

Constraints:

- Keep all mutable state writes behind the existing proposal/confirmation flow.
- Keep voice push-to-talk for now.
- Do not add a persistent service.
- Do not give local model output a command execution path.
- Keep lower-level commands available for debugging.

Sources:

- ADR-0062 bounded Jarvis assistant bridge decision.
- Local implementation files: `scripts/ctos-jarvis`, `scripts/ctos-voice`, `scripts/ctos-ai`, `scripts/ctos-voice-v2`, and `scripts/ctos-install-user-bin`.

Rationale:

A single operator facade makes the system feel like one assistant instead of a pile of backend experiments. Keeping it as a thin wrapper preserves auditability and reduces risk: the UX becomes simpler while the permission boundary remains exactly where CTOS already enforces it.

Verification:

Completed on 2026-07-07:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice scripts/ctos-ai scripts/ctos-voice-v2`
- `bash -n scripts/ctos-install-user-bin`
- `ctos-jarvis --help`
- `ctos-jarvis next`
- `ctos-jarvis smoke`
- `ctos-jarvis smoke --json`
- `ctos-jarvis smoke --with-model --json`
- `ctos-jarvis unlock-voice`: expected locked state `missing_token`, tunnel OK, next `ctos-jarvis unlock-voice --interactive`
- `ctos-jarvis unlock-voice --json`: valid JSON with `ready=false`, `state=missing_token`, one blocker, and parsed doctor payload
- `ctos-jarvis unlock-voice --test`: expected locked state `missing_token`, no Speech-to-Phrase start attempted before the token gate
- `ctos-jarvis text agenda --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-tasks.sqlite3 ctos-jarvis text "ajoute acheter du pain demain 30 min priorité 4" --save-agenda --json`
- `scripts/ctos-install-user-bin --dry-run`
- targeted `git diff --check`

Consequence:

Daily testing should now prefer `ctos-jarvis voice --seconds 4` and `ctos-jarvis text "..."`. Lower-level `ctos-voice*` and `ctos-ai` commands remain the debugging and implementation surface.

## ADR-0064: Prioritize mature open STT over endless phrase tuning

Date: 2026-07-07
Status: accepted

Decision:

Do not make phrase-by-phrase command tuning the main Jarvis path. Keep the current Vosk/intent catalog and Speech-to-Phrase work as useful fixed-command rails, but prioritize a mature open-ended STT backend for natural French requests. Candidate backends should be treated as replaceable input adapters. CTOS remains the only layer that turns transcript text into actions, approvals, agenda writes, VM operations, or system changes.

Context:

The operator tested the voice command path and it mostly worked, but the single word `agenda` was not recognized reliably. That is a useful signal: tuning one missed phrase at a time will not scale into the desired Jarvis assistant. The desired UX is closer to "organise ma journée", "ajoute un rendez-vous demain", and "aide-moi à bosser" than to a fixed CLI menu spoken aloud.

Constraints:

- Keep push-to-talk first.
- Do not persist recordings or transcripts by default.
- Do not let any STT/LLM output execute shell directly.
- Keep mutable actions behind CTOS planning and approval.
- Prefer local or localhost-tunneled services on owned machines.

Sources:

- Home Assistant Assist voice documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Wyoming protocol project, accessed 2026-07-07: https://github.com/rhasspy/wyoming
- Wyoming faster-whisper project lookup, accessed 2026-07-07: https://github.com/rhasspy/wyoming-faster-whisper
- Speech-to-Phrase project, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- OpenVoiceOS project, accessed 2026-07-07: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter project, accessed 2026-07-07: https://github.com/OpenInterpreter/open-interpreter
- AirLLM repository lookup, accessed 2026-07-07: https://github.com/lyogavin/airllm
- GLM family repository lookup, accessed 2026-07-07: https://github.com/zai-org/GLM-4.5

Rationale:

Speech-to-Phrase is good for deterministic commands, but it is the wrong center of gravity for natural conversation. A Whisper-class STT rail can produce better open-ended French transcripts, then CTOS can parse, ask for confirmation, and act safely. Full assistant platforms and agent frameworks remain useful references, but they should not become the unattended authority layer for the T480 or `ctos-core`.

Verification:

Completed on 2026-07-07:

- `ctos-voice-v2 open-stt-plan`
- `ctos-jarvis next`
- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- targeted `git diff --check`

Consequence:

The next Jarvis implementation should choose one local open-STT backend candidate for a temporary push-to-talk test before spending more time on exact phrase tuning. Speech-to-Phrase remains valuable for a small command set, not for the full Jarvis conversation surface.

## ADR-0065: Select `wyoming-faster-whisper` as the first open-STT smoke candidate

Date: 2026-07-07
Status: accepted

Decision:

Use `wyoming-faster-whisper` as the first open-ended STT candidate for a temporary CTOS smoke test, but prefer the official `docker.io/rhasspy/wyoming-whisper` container as the first runnable path. Keep `whisper.cpp` and direct `faster-whisper` adapters as fallbacks. The first implementation surface is `ctos-voice-v2 open-stt-candidates`, which renders an auditable manual plan only. It does not install packages, download models, start a daemon, or enable an always-on microphone.

Context:

The live voice path worked roughly, but missing a simple word like `agenda` proves that exact phrase tuning cannot be the main road to Jarvis. CTOS needs a natural French transcript rail that can handle requests such as "organise ma journée" and "ajoute une tâche demain" while preserving CTOS as the only action/approval layer.

Constraints:

- Keep the first rail push-to-talk.
- Bind services to localhost on owned machines.
- Prefer `ctos-core` for heavier model runtime and cache placement.
- Do not persist raw recordings/transcripts by default.
- Do not let STT output execute shell, VM, package, network, or approval actions.

Sources:

- Wyoming faster-whisper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-faster-whisper
- Wyoming Whisper image, accessed/tested 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-whisper
- Wyoming protocol repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming
- faster-whisper repository, accessed 2026-07-07: https://github.com/SYSTRAN/faster-whisper
- whisper.cpp repository, accessed 2026-07-07: https://github.com/ggml-org/whisper.cpp
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/

Rationale:

`wyoming-faster-whisper` is the smallest next step that fits the current architecture. It speaks the Wyoming service shape that CTOS already uses for the mature voice rail, but it can still be tested as a single localhost-only STT backend. The container path is preferred for the first runtime test because the direct venv install on `ctos-core` failed under the current Python 3.14 toolchain while building `pysilero-vad`; the official container isolates those dependencies. This avoids adopting a full assistant platform as an authority layer and avoids spending weeks expanding deterministic phrase lists.

Verification:

Completed on 2026-07-07:

- `ctos-voice-v2 open-stt-candidates`
- `ctos-voice-v2 open-stt-candidates --json`
- `ctos-voice-v2 next-commands`
- `ctos-jarvis next`
- `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-jarvis`
- `python3 -m json.tool ai/voice_backends.json`
- targeted `git diff --check`
- `ctos-core` clone/help probe for the upstream repository: direct `script/setup` failed on `pysilero-vad` build metadata under Python 3.14.
- `podman run --rm --pull=missing docker.io/rhasspy/wyoming-whisper --help` passed on `ctos-core`.
- Temporary `docker.io/rhasspy/wyoming-whisper` container on `ctos-core` started on localhost port `10301` with `base-int8`.
- Synthetic French WAV reached CTOS through `ctos-voice-v2 stp-transcribe --wyoming-port 10301 --target-tunnel --route`; transcript quality was imperfect but the Wyoming transport and CTOS route worked.
- Live T480 microphone recordings reached the backend but returned empty transcripts; audio capture/gain cleanup is the next blocker before model tuning.
- Follow-up testing reduced T480 mic gain below clipping and compared `base-int8` with `small-int8`. The backend and CTOS Wyoming route remained functional, but unnormalized live recordings still returned empty transcripts and normalized low-speech/noise samples produced a classic Whisper hallucination (`Sous-titres réalisés...`). This confirms the pivot away from phrase-by-phrase tuning. `ctos-voice-v2 stp-transcribe` now fails closed with a transcript guard plus `--preprocess auto`: an energy-based activity check, trim, and normalization that refuses low-activity samples before contacting Whisper.

Consequence:

The next live step is a fresh human push-to-talk transcript through the temporary container using `ctos-voice-v2 stp-transcribe --wyoming-port 10301 --target-tunnel --preprocess auto --route`. No persistent service should be created until that transcript reaches CTOS and routes correctly without empty transcripts or silence hallucinations.

Update 2026-07-07:

`ctos-voice-v2 open-stt status|start|logs|stop` is now the accepted operator surface for this temporary smoke backend. It replaces ad hoc SSH/podman snippets with a reproducible command, but keeps the same boundary: rootless container on `ctos-core`, `--rm`, localhost-only `127.0.0.1:10301`, model data under `/srv/ctos/models/open-stt`, no systemd unit, and no always-on microphone.

Verification: live status/start/logs/stop reached `ctos-core`; the container reported `Ready`, then stopped cleanly enough to leave no container and port `10301` free. A longer open-STT stop timeout was set to reduce forced-stop noise on future tests.

Update 2026-07-07:

`ctos-jarvis listen` is now the accepted operator shortcut for the open-ended STT smoke path. It does not add a new authority layer; it wraps `ctos-voice-v2 open-stt status/start/stop` plus `stp-transcribe --target-tunnel --preprocess auto` and routes the transcript through the existing CTOS planner. The command starts the temporary backend only when needed, stops it again if it started it, and offers `--keep-backend` only for an explicit repeated-test window.

`ctos-voice-v2 stp-transcribe --save-agenda` now routes a recognized transcript into the same agenda proposal queue as `ctos-voice route --save-agenda`. It is mutually exclusive with `--execute-safe`; agenda writes still require explicit typed confirmation through `ctos-jarvis confirm latest --yes`.

Verification: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-jarvis listen --help`, and `ctos-jarvis listen --plan --seconds 5 --save-agenda` passed before live microphone testing. The local Wyoming self-test passed outside the sandbox and routed transcript `agenda` to `ctos_agenda`. `ctos-voice-v2 open-stt status --json` confirmed `ctos-open-stt-smoke` was missing and port `10301` was free; `ctos-jarvis listen --no-start --json` then refused with `backend_not_running` before recording audio or starting the container.

## ADR-0066: Select a hybrid mature Jarvis stack instead of phrase-by-phrase tuning

Date: 2026-07-07
Status: accepted

Decision:

Use a hybrid local/open-source Jarvis stack rather than continuing to tune every missed spoken phrase. The selected path is:

- `ctos-jarvis` as the operator facade;
- Home Assistant Assist/Wyoming as the primary mature local voice ecosystem target;
- Speech-to-Phrase through Wyoming as the deterministic fixed-command rail;
- Wyoming Whisper/faster-whisper as the open-ended French STT rail;
- Piper/Wyoming Piper as planned local TTS;
- Ollama on `ctos-core` as the first local model runtime;
- CTOS proposals and approvals as the only action authority.

Context:

The operator confirmed that the current voice path works roughly, but a simple word such as `agenda` can still be missed. Continuing to add synonyms one by one is the wrong scaling path for the requested Jarvis goal. CTOS needs an already-mature voice ecosystem for input/output and a strict CTOS-owned action boundary for agenda, desktop, VM, and future computer-control work.

Constraints:

- Keep push-to-talk first.
- Do not enable an always-on microphone yet.
- Do not use cloud STT by default.
- Do not let transcript text or model output execute shell/system actions directly.
- Do not approve mutable actions by voice.
- Do not store secrets, tokens, recordings, or transcripts in Git.

Sources:

- Home Assistant voice control documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant Wyoming integration documentation, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Wyoming protocol repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming
- Speech-to-Phrase repository, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming faster-whisper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-faster-whisper
- Wyoming Whisper container page, accessed 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-whisper
- Wyoming Piper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-piper
- OpenVoiceOS core repository, accessed 2026-07-07: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter 01 repository, accessed 2026-07-07: https://github.com/OpenInterpreter/01
- AirLLM reference implementation lookup, accessed 2026-07-07: https://github.com/lyogavin/Anima/tree/main/air_llm
- GLM-family repository lookup, accessed 2026-07-07: https://github.com/zai-org/GLM-5

Rationale:

Home Assistant Assist/Wyoming fits the current Speech-to-Phrase/Piper/Wyoming direction and gives CTOS a mature local voice bus without handing it authority. OpenVoiceOS, Leon, and Open Interpreter/01 are useful references or sandbox candidates, but they are too broad to become the unattended authority layer on CTOS machines. GLM-5.2 family models and AirLLM-style offload are model-serving research, not the first Jarvis product layer for current T480/core hardware.

Verification:

Completed on 2026-07-07:

- `python3 -m json.tool ai/jarvis_stack.json`
- `python3 -m py_compile scripts/ctos-jarvis`
- `ctos-jarvis stack`
- `ctos-jarvis stack --json`
- targeted `git diff --check`

Consequence:

The next practical loop is not more one-word tuning. Run `ctos-jarvis calibrate`, inspect the audio/transcript/route report, and only then rerun `ctos-jarvis calibrate --save-agenda` if the proposal is correct. Review the resulting proposal with `ctos-jarvis review`, and confirm it only with typed approval if correct. If transcription quality is weak, fix capture/preprocessing first.

Update 2026-07-07:

`ctos-voice-v2 open-stt start` now waits for the temporary container logs to report `Ready` before returning success. This fixes a real startup race observed through `ctos-jarvis listen --from-wav`: the first synthetic test saw an open port but hit `Broken pipe` because the backend was not ready. After the fix, the same synthetic French WAV returned a Wyoming transcript and CTOS routed it safely. The transcript from `espeak-ng` was too degraded to parse as an agenda proposal, so CTOS refused agenda staging. This is the correct fail-closed behavior and means the next proof must be a human push-to-talk sample, not more synthetic TTS.

Verification:

- `espeak-ng ... -w /tmp/ctos-jarvis-agenda-raw.wav`
- `ffmpeg ... /tmp/ctos-jarvis-agenda-16k.wav`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-stack-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-stack-agenda.sqlite3 scripts/ctos-jarvis listen --from-wav /tmp/ctos-jarvis-agenda-16k.wav --save-agenda --json --no-speak`
- `scripts/ctos-voice-v2 open-stt status --json`: confirmed `CONTAINER missing` and `PORT free`

Update 2026-07-07:

Add `ctos-jarvis calibrate` as the preferred operator loop for open-STT testing. It wraps the existing `listen` path, keeps raw/preprocessed WAVs for debugging, and prints the relevant state instead of requiring the operator to parse JSON: mic level, STT audio level, transcript, guard result, CTOS route, agenda proposal, and next action. It still does not write agenda state unless `--save-agenda` is explicit.

The transcript guard now also blocks unreadable normalized text, repeated non-speech symbol runs, and high symbol-noise transcripts before routing to CTOS. This is a fail-closed response to a degraded synthetic French TTS sample; it is not a model-quality claim. The next proof must be a human push-to-talk sample.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis calibrate --help`
- `ctos-jarvis next`
- `ctos-jarvis calibrate --no-start --seconds 0.1 --clean`
- `ctos-jarvis calibrate --from-wav /tmp/ctos-jarvis-calibrate-16k.wav --stop`: reached `ctos-core`, returned a degraded synthetic transcript, and produced no agenda proposal.
- `ctos-voice-v2 open-stt status --json`: confirmed `CONTAINER missing` and `PORT free`.

Update 2026-07-07:

`ctos-jarvis calibrate` now parses the flat route payload emitted by `ctos-voice route --json`, not only a nested `route` object. The report exposes the route reason, best CTOS candidate, agenda-save attempt state, and refusal reason. This keeps the operator from mistaking a degraded transcript for an actionable agenda command.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis calibrate --help`
- `ctos-jarvis calibrate --no-start --seconds 0.1 --clean`: expected `backend_not_running`.
- `ctos-jarvis calibrate --from-wav /tmp/ctos-jarvis-calibrate-16k.wav --save-agenda --stop`: reached `ctos-core`, returned a degraded transcript, showed best candidate `ctos_agenda_review`, refused agenda staging with `reason=no recognized agenda proposal`, and wrote no agenda proposal.
- `scripts/ctos-voice-v2 open-stt status --json`: confirmed `CONTAINER missing` and `PORT free`.

Update 2026-07-07:

Add `ctos-jarvis session` as the repeated human testing loop. It runs multiple readable calibration rounds, keeps the temporary open-STT backend warm between rounds, and stops it at the end unless `--keep-backend` is explicit. This reduces operator friction while preserving the same safety model: voice can stage a proposal with `--save-agenda`, but cannot approve agenda writes or broaden CTOS action authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis session --help`
- `ctos-jarvis next`
- `ctos-jarvis session --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean`: expected `backend_not_running` through the existing calibration guard.

Update 2026-07-07:

`ctos-jarvis session --save-agenda` now runs the read-only pending proposal review at the end by default. This removes one manual step from the real voice-to-agenda loop while preserving the approval boundary: the session can show staged proposals, but agenda writes still require typed `ctos-jarvis confirm latest --yes`. `--no-review` disables the automatic review, and `--review` can be used without `--save-agenda`.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis session --help`
- `ctos-jarvis session --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean --save-agenda`: expected `backend_not_running`, printed the read-only agenda review, and did not write agenda state.

Update 2026-07-07:

Add a read-only preflight to `ctos-jarvis session`: microphone status, open-STT backend status, and pending agenda review. The preflight warns by default so a sandboxed or temporarily unavailable audio/SSH context does not hide the rest of the flow. `--strict-preflight` stops before recording if any preflight check warns. No service is started and no agenda state is written during preflight.

Verification:

- `ctos-jarvis session --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean --save-agenda`: preflight printed microphone/open-STT warnings plus agenda review, then expected-failed at `backend_not_running`.
- `ctos-jarvis session --rounds 1 --no-prompt --no-start --seconds 0.1 --strict-preflight --clean`: stopped at `state preflight_failed` before recording.

Update 2026-07-07:

Add `ctos-jarvis run` as the daily operator shortcut above `session`. It runs the open-STT session loop, stages agenda proposals by default, shows the read-only review, and prints the typed confirmation command. It does not approve agenda proposals, add package/service state, or grant voice/model output any additional action authority.

Verification:

- `ctos-jarvis run --plan`: prints the lower-level `ctos-jarvis session --save-agenda --review` command and the typed-confirmation boundary.
- `ctos-jarvis run --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean`: expected-failed with `backend_not_running`, printed preflight warnings and read-only agenda review, and did not attempt a real open-STT recording because backend start was disabled.

Update 2026-07-07:

After the operator reported that real voice works roughly but missed `agenda`,
CTOS keeps the mature hybrid stack as the product path instead of spending
months tuning isolated words. Current research rechecked official Home
Assistant voice/Wyoming docs, Speech-to-Phrase, OpenVoiceOS, Open
Interpreter/01, AirLLM, and GLM-family references. Decision: use Home
Assistant/Wyoming-compatible local components as replaceable voice/model
infrastructure, keep `ctos-jarvis` as the operator facade, keep CTOS as the
only action/approval boundary, and treat OpenVoiceOS, Open Interpreter/01,
AirLLM, and GLM-style projects as references or later experiments unless they can fit
behind CTOS proposals. No new package, service, always-on microphone, or direct
model-to-shell authority is added by this decision.

Add `ctos-jarvis sample` to capture or register reusable labeled voice samples
outside the repo under XDG local state. This makes missed phrases such as
`agenda` replayable against open-STT, Speech-to-Phrase, or later local backends
without forcing repeated live recordings. The command writes a JSONL manifest
row with audio level metadata, `expected_text`, and replay commands, but does
not grant model/action authority or write agenda state.

Update 2026-07-07:

`ctos-voice-v2 regression` now understands open-ended sample manifests as well
as fixed-command manifests. If a sample has `intent_id`, the fixed CTOS intent
match remains authoritative. If it has no `intent_id`, regression scores the
transcript against `expected_text` or `label` with `--text-threshold`. This
keeps samples useful for Whisper-class natural STT evaluation before a CTOS
intent should exist.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-voice-v2 regression --manifest /tmp/ctos-jarvis-regression-text.jsonl --json`
- `ctos-jarvis sample "agenda" --plan`
- `ctos-jarvis smoke`
- `ctos-install-user-bin --dry-run`: confirmed `ctos-jarvis` is linked through `~/.local/bin`
- targeted `git diff --check`

Update 2026-07-07:

Add `ctos-jarvis mature-plan` as the operator-facing adoption map for the
mature open-source Jarvis substrate. This records the current product choice in
an executable/readable CLI instead of leaving it only in chat: adopt
Home Assistant/Wyoming, Wyoming Whisper/faster-whisper, Speech-to-Phrase,
Piper, and Ollama behind CTOS; keep Open Interpreter/01, OpenVoiceOS,
GLM-family model work, and AirLLM-style offload as sandbox/reference tracks
until they can be mediated by CTOS proposals and typed approvals. This reinforces
that the project should not spend months tuning isolated word misses as the main
voice path.

Sources rechecked:

- Home Assistant voice control documentation, accessed 2026-07-07:
  https://www.home-assistant.io/voice_control/
- Home Assistant Wyoming integration documentation, accessed 2026-07-07:
  https://www.home-assistant.io/integrations/wyoming/
- Wyoming faster-whisper repository, accessed 2026-07-07:
  https://github.com/rhasspy/wyoming-faster-whisper
- OpenVoiceOS core repository, accessed 2026-07-07:
  https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter repository, accessed 2026-07-07:
  https://github.com/OpenInterpreter/open-interpreter

Verification:

- `python3 -m py_compile scripts/ctos-jarvis`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis mature-plan`
- `ctos-jarvis mature-plan --commands`
- `ctos-jarvis mature-plan --json`
- `ctos-jarvis smoke`

Update 2026-07-07:

Add `ctos-jarvis mature-check` as a read-only readiness command for the same
mature-stack path. Default mode checks the local Jarvis/voice foundation,
audio controls, and reusable sample manifest. `--full` may include `ctos-core`
SSH/backend probes. `--prefer open-stt|deterministic` chooses whether the next
recommended command points toward the open-ended Whisper rail or the
Home Assistant/Speech-to-Phrase deterministic rail. The command does not install
packages, start long-lived services, keep the microphone open, write agenda
state, or grant model/voice output any new authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis mature-check`
- `ctos-jarvis mature-check --json`
- `ctos-jarvis mature-check --prefer deterministic`
- `ctos-jarvis mature-check --smoke`

Update 2026-07-07:

Make T480 audio control permanently reachable from the desktop instead of
depending on hidden multimedia keys or memorized shell commands. Keep the
existing PipeWire/WirePlumber `wpctl` approach and existing `pavucontrol`
mixer; add no package, daemon, or always-on microphone listener. Add
`ctos-audio report` and `ctos-audio panel`, route Waybar left-click and
`SUPER+A` to that panel, keep the full mixer on Waybar middle-click and
`SUPER+SHIFT+A`, add microphone gain/mute binds, and surface `VOL`/`MIC` in
the CTRL cockpit.

Rationale:

The voice stack may work technically while still being unusable if the operator
cannot quickly adjust speaker volume or microphone gain. A small repo-owned
panel plus visible cockpit state is simpler and more auditable than adding a
new desktop audio app or background service.

Verification:

- `bash -n scripts/ctos-audio scripts/ctos-install-desktop`
- `python3 -m py_compile control/status.py control/tui.py`
- `python3 -m json.tool waybar/config`
- `ctos-audio report`
- live `ctos-audio status`
- live `ctos-audio mic-status`
- `scripts/ctos-install-desktop`
- `hyprctl reload`
- Waybar restart
- `hyprctl configerrors`

Update 2026-07-07:

Add `ctos-jarvis samples` and `ctos-jarvis regression` so the reusable voice
sample loop has a daily operator surface. The commands default to
`~/.local/state/ctos/jarvis-samples/manifest.jsonl`, list captured samples, and
wrap `ctos-voice-v2 regression` for either the local fallback recognizer or the
open-STT/Wyoming rail with `--backend open-stt --target-tunnel`. This changes no
recognizer, package, service, permission tier, or action authority; it only
removes long path-copying from the "missed word -> sample -> replay" loop.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis`
- `ctos-jarvis samples --json`
- `ctos-jarvis regression --plan`
- `ctos-jarvis regression --backend open-stt --target-tunnel --plan`
- `ctos-jarvis next`

Update 2026-07-07:

Add `ctos-jarvis collect` as the preferred first step when no reusable Jarvis
voice samples exist. This keeps the project from spending time on isolated
phrase fixes: the default `core` preset captures a compact operator corpus
(`agenda`, `brief`, `ouvre desk`, `ouvre vms`, and one natural agenda request)
into the same local manifest used by `ctos-jarvis sample`. Known fixed commands
receive `intent_id` values for strict regression, while the natural agenda
sample remains transcript-scored through `expected_text`. The command adds no
package, daemon, always-on microphone, model runtime, or action authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis collect --help`
- `ctos-jarvis collect --plan`
- `ctos-jarvis mature-check --json`
- `ctos-voice-v2 next-commands`
- `python3 -m json.tool ai/jarvis_stack.json`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-audio doctor [--json]` as the read-only audio diagnostic used by
Jarvis preflight. Keep the existing PipeWire/WirePlumber `wpctl` control path
and do not add a package, service, daemon, or always-on microphone listener.
The reason is operational clarity: `ctos-audio status` and `mic-status` can
fail from a restricted execution context even when the live desktop audio works.
The doctor command reports structured reasons such as `pipewire_context_denied`,
`pipewire_unreachable`, or `missing_wpctl`, letting `ctos-jarvis mature-check`
warn accurately without mutating audio settings.

Verification:

- `bash -n scripts/ctos-audio`
- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-audio doctor` and `ctos-audio doctor --json` intentionally returned
  `rc=1` with `pipewire_context_denied` in the restricted Codex context.
- `ctos-jarvis mature-check --json`
- `ctos-jarvis status`
- `ctos-jarvis status --json`
- `ctos-audio --help`
- `ctos-jarvis collect-next`
- live desktop `ctos-audio doctor --json` returned `rc=0` and reported output
  77% plus microphone 20%.

Update 2026-07-08:

Add `ctos-jarvis bootstrap` as the one-step operator loop over the existing
Jarvis commands. The command reads `ctos-jarvis status`, picks the first next
action, and shows it without changing state. With `--run`, it executes exactly
that existing command and then rechecks status. JSON run mode refuses
interactive audio unless `--yes` is explicit. This keeps the bootstrap path
auditable and avoids granting any new action authority; it adds no package,
service, daemon, model runtime, always-on microphone listener, or direct shell
execution from voice/model output.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis bootstrap`
- `ctos-jarvis bootstrap --json`
- `ctos-jarvis bootstrap --json --run` expected-refused interactive audio
  capture without `--yes`.
- `ctos-jarvis --help`

Update 2026-07-08:

Rechecked the mature-stack decision after the operator asked whether a more
sophisticated recent local/open-source resource should replace slow
word-by-word tuning. Keep the existing hybrid decision. A missed command word
such as `agenda` is a corpus/evaluation signal, not a reason to hand-build a
full voice assistant. Continue to use Home Assistant/Wyoming-compatible
components for voice transport, Whisper/Wyoming for natural French STT,
Speech-to-Phrase for deterministic commands, Piper for TTS, and Ollama on
`ctos-core` for bounded local model work. OpenVoiceOS and Open Interpreter/01
remain references or sandboxes; GLM-5.2-family and AirLLM-style work remain
model/runtime research until hardware and CTOS approval schemas are stronger.
No new package, service, microphone listener, model, or action authority was
selected in this refresh.

Update 2026-07-08:

Add a read-only audio preflight to `ctos-jarvis collect`. The corpus collection
path now checks `ctos-audio status` and `ctos-audio mic-status` before recording
the phrase suite. Default behavior warns but continues, so a transient desktop
or sandbox audio warning does not hide the rest of the workflow.
`--strict-preflight` stops before recording if either check warns, and
`--no-preflight` exists for deliberate capture debugging. This adds no package,
daemon, backend start, always-on microphone, model runtime, or action
authority; it only prevents avoidable low-quality corpus captures.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis collect --help`
- `ctos-jarvis collect --plan`
- `ctos-jarvis collect --plan --no-preflight`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis triage` as the read-only next-action verdict for the reusable
Jarvis voice corpus. It wraps the existing corpus and sample checks and returns
a concrete operator decision (`capture_corpus`, `complete_corpus`,
`repair_sample_files`, `repair_manifest`, `recapture_weak_audio`,
`benchmark_backends`, or `inspect_state`). This avoids making the operator infer
the next move from separate `samples`, `corpus`, and `evaluate` commands. It
does not record audio, run recognition, start open-STT/Home Assistant, download
models, or mutate agenda/desktop/VM state.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis triage --help`
- `ctos-jarvis triage --json` expected-failed on the real empty manifest with
  verdict `capture_corpus`.
- `ctos-jarvis triage --manifest /tmp/ctos-jarvis-triage-ready/manifest-ready.jsonl`
  passed with verdict `benchmark_backends`.
- `ctos-jarvis triage --manifest /tmp/ctos-jarvis-triage-ready/manifest-weak.jsonl`
  expected-failed with verdict `recapture_weak_audio`.
- `ctos-jarvis mature-plan --commands`
- `ctos-voice-v2 next-commands`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis evaluate` as the one-command measurable path after corpus
collection. The command runs the same read-only corpus gate first and refuses to
launch recognition regression when the real sample manifest is empty,
incomplete, invalid, or missing WAV files. Once the corpus is ready, it can run
the local fallback regression or compare local fallback plus open-STT/Wyoming
with `--backend both`. This adds no recognizer, package, service, microphone
listener, model runtime, or action authority; it only prevents premature and
untracked regression attempts.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis evaluate --plan`
- `ctos-jarvis evaluate --backend both --plan`
- `ctos-jarvis evaluate --json` expected-failed with state `empty` and ran no regression.
- `ctos-jarvis collect --plan`
- `ctos-jarvis mature-plan --commands`
- `ctos-voice-v2 next-commands`

Update 2026-07-08:

Add `ctos-jarvis status` as the compact read-only mission view for the current
Jarvis phase. The command aggregates existing safe checks instead of adding a
new subsystem: mature readiness, corpus/improvement state, the next corpus
capture phrase, and pending agenda proposals. It then prints one next operator
action. It exists because the operator should not need to remember whether the
next useful command is `mature-check`, `improve`, `collect-next`, `evaluate`,
or `review`. It adds no package, service, daemon, model runtime, always-on
microphone, or new action authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis status`
- `ctos-jarvis status --json`
- `ctos-jarvis now`
- ready/weak temporary manifests selected backend evaluation or one phrase to
  recapture.
- `ctos-jarvis --help`
- `ctos-jarvis next`
- `ctos-voice-v2 next-commands`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis collect-next` as the one-phrase corpus capture/resume
command. The operator can now advance the reusable voice corpus without
recording the full preset every time. The command reads the manifest, selects
the first missing preset phrase or first weak-audio sample, and prints one
exact sample command. It records only with `--run`; plan and JSON modes remain
read-only unless `--run --yes` is explicit. If the corpus is ready, it points
to `ctos-jarvis evaluate --backend both`. This adds no package, service,
daemon, model runtime, always-on microphone, or new action authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis collect-next --help`
- `ctos-jarvis collect-next`
- `ctos-jarvis collect-next --json`
- `ctos-jarvis collect-next --json --run` expected-refused interactive
  capture on the real empty corpus without `--yes`.
- ready/weak temporary manifests selected evaluation or one phrase to recapture.
- `ctos-jarvis next`
- `ctos-voice-v2 next-commands`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis improve` as the safe orchestration loop above corpus triage
and evaluation. The command exists because the operator should not need to
remember whether the next step is `collect`, `corpus`, `triage`, or
`evaluate --backend both`. It first runs read-only triage, then selects exactly
one next step: strict guided collection when the corpus is empty/incomplete or
has weak audio, backend evaluation when the corpus is ready, or sample/manifest
inspection when repair is needed. Without `--run`, it prints only the selected
command. With `--run`, it delegates to the existing guarded command. This adds
no package, service, daemon, model runtime, always-on microphone, or new action
authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis improve --help`
- `ctos-jarvis improve`
- `ctos-jarvis improve --json`
- `ctos-jarvis improve --json --run` expected-refused interactive audio
  capture on the real empty corpus without `--yes`.
- ready/weak temporary manifests selected evaluation or strict collection.
- `ctos-jarvis mature-plan --commands`
- `ctos-voice-v2 next-commands`
- targeted `git diff --check`

Update 2026-07-08:

Keep `ctos-ai open-vms` as a Tier 1 reversible UI launcher, but do not suppress
Hyprland/launcher diagnostics. The command now reports the exact `hyprctl`
launch and manual fallback when the compositor is unavailable, while preserving
the existing live-desktop behavior. This makes Jarvis voice/text routes
auditable without adding new action authority.

Verification:

- `python3 -m py_compile scripts/ctos-ai scripts/ctos-jarvis ai/action_planner.py ai/agenda_parser.py`
- `ctos-ai open-vms --print-only`
- `ctos-ai open-vms` in the restricted Codex context expected-failed with a
  useful Hyprland socket diagnostic.
- Live desktop `ctos-ai open-vms` passed and opened the VMS panel.
- Live desktop `ctos-jarvis text "ouvre vms" --json` passed with `rc=0`.

Update 2026-07-08:

Repair the Jarvis JSON split. `ai/voice_intents_fr.json` is the CTOS-owned
French phrase/intent catalog. `ai/jarvis_stack.json` is the mature Jarvis stack
selection manifest with `mature_adoption`, selected layers, candidate positions,
operator path, and authority boundary. These files must not be collapsed into
one artifact: `ctos-jarvis mature-plan`, `mature-check`, `status`, and
`bootstrap` depend on the stack manifest, while voice matching depends on the
intent catalog.

Rationale:

- The current `ctos-jarvis status` path treated missing `mature_adoption` as a
  stack failure and incorrectly pushed the operator toward `ctos-jarvis doctor`.
- Restoring the stack manifest makes the current real next step visible again:
  capture the missing operator voice corpus with `ctos-jarvis collect-next
  --run`.
- No package, service, daemon, model runtime, microphone listener, or action
  authority was added.

Verification:

- `python3 -m json.tool ai/jarvis_stack.json`
- `ctos-jarvis stack`
- `ctos-jarvis mature-plan --commands`
- `ctos-jarvis mature-plan --json`
- `ctos-jarvis mature-check --json`
- `ctos-jarvis status`
- `ctos-jarvis status --json`
- `ctos-jarvis bootstrap`
- `ctos-jarvis collect-next`

Update 2026-07-08:

Add two read-only Jarvis operator gates:

- `ctos-jarvis stack-check` validates that `ai/jarvis_stack.json` remains the
  mature stack manifest and `ai/voice_intents_fr.json` remains the French
  intent catalog.
- `ctos-jarvis daily` aggregates stack integrity, `ctos-ai brief`,
  `ctos-agenda plan-day`, pending agenda proposals, and `ctos-jarvis status`
  into a single text-first daily cockpit view.

Rationale:

- The stack/intent split had already failed once, so an explicit integrity
  command is safer than relying on memory.
- The next Jarvis milestone should be usable in text before voice. `daily`
  gives a stable daily surface for status, agenda, proposals, and the next
  action without requiring microphone capture or model output.
- No package, service, daemon, model runtime, microphone listener, agenda write,
  VM action, or desktop mutation was added.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis`
- `ctos-jarvis stack-check`
- `ctos-jarvis stack-check --json`
- `ctos-jarvis daily`
- `ctos-jarvis daily --json`
- `ctos-jarvis next`

Update 2026-07-08:

Add `ctos-jarvis draft` as the text-first staging rail between raw natural
language and CTOS actions. The command delegates to `ctos-ai route-text`, shows
the deterministic intent or agenda proposal, and performs no action by default.
With `--save`, it can save only a recognized agenda proposal as pending review;
the final agenda write still requires `ctos-jarvis confirm latest --yes`.

Rationale:

- Jarvis needs a reliable typed surface before voice becomes default.
- Voice/STT output should feed a bounded proposal rail, not direct mutations.
- Safe deterministic intents such as `ouvre vms` are shown as executable plans
  but are not executed by `draft`.
- No package, service, daemon, model runtime, microphone listener, final agenda
  write, VM action, or desktop mutation was added.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis`
- `ctos-jarvis draft "ajoute acheter du pain demain 30 min priorite 4"`
- `ctos-jarvis draft "ouvre vms" --json`
- Temporary DB check:
  `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-draft-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-draft-agenda.sqlite3 ctos-jarvis draft "ajoute acheter du pain demain 30 min priorite 4" --save --json`
- Temporary DB review:
  `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-draft-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-draft-agenda.sqlite3 ctos-jarvis review --json`
- `ctos-jarvis draft "ouvre vms" --save` expected-refused with
  `not_saveable`.
- `ctos-jarvis next`

Update 2026-07-08:

Route the open-STT Jarvis voice path through `ctos-jarvis draft` by default.
`ctos-jarvis listen`, `calibrate`, `session`, and `run` now keep
`--execute-safe` as the explicit direct-action path, but normal transcripts and
`--save-agenda` requests are staged through `ctos-jarvis draft --source stt`.

Rationale:

- The operator needs Jarvis to understand and stage work before it mutates the
  machine.
- STT output is probabilistic, so it should pass through the same typed draft
  rail as manual text.
- `--save-agenda` still creates only pending proposals; final agenda writes
  still require typed confirmation.
- No package, service, daemon, model runtime, microphone listener, final agenda
  write, VM action, or desktop mutation was added.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis`
- `ctos-jarvis listen --plan`
- `ctos-jarvis listen --plan --save-agenda`
- `ctos-jarvis listen --plan --execute-safe`
- `ctos-jarvis run --plan --rounds 1 --no-prompt`
- `ctos-jarvis listen --no-start --json` expected-failed locally because the
  sandbox cannot reach `ctos-core`, while preserving the structured
  `backend_not_running` error.
- In-memory `cmd_listen` test with mocked open-STT status/transcript verified
  that a transcript calls `ctos-jarvis draft <transcript> --source stt --save`
  and returns `saved_pending`.

Update 2026-07-07:

Add `ctos-jarvis corpus` as a read-only gate between sample collection and
sample regression. The command checks the reusable Jarvis sample manifest for
preset coverage, minimum sample count, referenced WAV existence, and non-OK
audio-state metadata. It returns a clear state (`empty`, `incomplete`, `broken`,
`invalid`, or `ready`) plus the next command. This keeps the operator flow
auditable: collect real phrases first, inspect corpus readiness second, then run
regression against Vosk or open-STT/Wyoming. It adds no recorder, recognizer,
service, package, microphone listener, or action authority.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`
- `ctos-jarvis corpus --json` expected-failed with state `empty` because the real operator sample manifest does not exist yet.
- `ctos-jarvis corpus --manifest /tmp/ctos-jarvis-corpus-test-ready.jsonl --json` passed with state `ready`.
- `ctos-jarvis corpus --manifest /tmp/ctos-jarvis-corpus-test-incomplete.jsonl --allow-incomplete` passed with state `incomplete`.
- `ctos-jarvis collect --plan`
- `ctos-jarvis mature-plan --commands`
- `ctos-voice-v2 next-commands`
- `python3 -m json.tool ai/jarvis_stack.json`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis inbox` as the read-only mutation queue for Jarvis. It combines
pending agenda proposals from `ctos-jarvis review --json` with generic CTOS
approval records from `ctos-ai approvals --json`. `ctos-ai approvals` now uses a
read-only SQLite connection and returns an empty list when the approval database
or table does not exist, so inspecting the queue does not create local state.

Rationale:

- Jarvis is becoming useful only if review/approval is easy to see.
- The operator should not need to remember separate agenda and generic approval
  commands before deciding the next mutation.
- The queue must not write agenda tasks, execute approvals, start services,
  install packages, or create an approval DB merely by being opened.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-ai`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-empty.sqlite3 ctos-jarvis inbox --json`
- Temporary DB proposal path:
  `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-inbox-agenda.sqlite3 ctos-jarvis draft "ajoute acheter du pain demain 30 min priorite 4" --save --json`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-inbox-agenda.sqlite3 ctos-jarvis inbox`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-proposals.sqlite3 CTOS_AI_DB=/tmp/ctos-jarvis-inbox-agenda.sqlite3 ctos-jarvis inbox --json`
- Generic approval queue check:
  `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-generic.sqlite3 ctos-ai propose kali-console --note "temporary inbox test"`
- `CTOS_AI_APPROVAL_DB=/tmp/ctos-jarvis-inbox-generic.sqlite3 ctos-jarvis inbox`
- `ctos-jarvis next`
- targeted `git diff --check`

Update 2026-07-08:

Route the normal Jarvis voice loop to the consolidated inbox. `ctos-jarvis
session --save-agenda` and the default `ctos-jarvis run` path now show
`ctos-jarvis inbox` after staging proposals. `--no-inbox` keeps the old
agenda-only `review` fallback, `--no-review` suppresses automatic review output,
and contradictory `--inbox` combinations are rejected.

Rationale:

- After voice/STT stages a proposal, the operator needs one decision surface,
  not separate agenda and generic approval views.
- Inbox remains read-only and does not execute approvals or write agenda tasks.
- The explicit typed confirmation boundary remains unchanged:
  `ctos-jarvis confirm latest --yes` is still required for agenda writes.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-ai`
- `ctos-jarvis run --plan --rounds 1 --no-prompt`
- `ctos-jarvis run --plan --rounds 1 --no-prompt --no-inbox`
- `ctos-jarvis run --plan --rounds 1 --no-prompt --execute-safe`
- In-memory mocked `cmd_session` test verified default `--save-agenda` calls
  `ctos-jarvis inbox`, `--no-inbox` calls `ctos-jarvis review`, and
  `--no-review` calls neither.
- Expected-refusal checks for `--inbox --review` and `--inbox --no-inbox`
  passed on both `run` and `session`.

Update 2026-07-08:

Return agenda decisions to the consolidated inbox. `ctos-jarvis confirm` and
`ctos-jarvis reject` now wrap the lower-level `ctos-ai agenda-confirm` /
`ctos-ai agenda-reject` commands and show `ctos-jarvis inbox` after a
successful decision unless `--no-inbox` is explicit. Both wrappers expose JSON
output for scripted callers, and `reject` exposes a stored `--reason`.

Rationale:

- The operator should be able to move through pending Jarvis proposals without
  remembering separate review commands after each decision.
- The mutation boundary is unchanged: confirming still requires `--yes`, while
  inbox remains read-only.
- Rejections need a reason trail but must not write agenda tasks or approve
  generic CTOS actions.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-ai`
- Temporary DB confirm path:
  `ctos-jarvis draft "ajoute appeler le garage demain 20 min priorite 3" --save`
  followed by `ctos-jarvis confirm latest --yes` returned to an empty inbox.
- Temporary DB JSON confirm path returned `mode=ctos-jarvis-confirm`,
  `ok=true`, and embedded `mode=ctos-jarvis-inbox` with zero pending items.
- Temporary DB reject path:
  `ctos-jarvis reject latest --reason "temporary reject test"` returned to an
  empty inbox.
- Temporary DB JSON reject path returned `mode=ctos-jarvis-reject`, `ok=true`,
  stored the rejection reason, and embedded an empty inbox.
- `ctos-jarvis confirm latest --yes --no-inbox` committed without printing the
  inbox follow-up.
- `ctos-jarvis next`
- targeted `git diff --check`

Update 2026-07-08:

Add `ctos-jarvis request` as the daily text-first Jarvis shortcut. It routes
operator text through the existing draft rail, auto-stages only recognized
agenda proposals as pending, and then shows the consolidated read-only inbox.
It does not execute desktop/VM actions, does not approve generic CTOS actions,
and does not write final agenda tasks.

Rationale:

- The normal operator path should be one command: type a natural request, see
  the staged result, then explicitly confirm or reject.
- `draft --save` remains useful for low-level debugging, but it is too easy to
  forget during daily use.
- The shortcut must not widen authority. It may create a pending proposal, but
  final agenda mutation still requires `ctos-jarvis confirm latest --yes`.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-ai`
- Temporary DB text request:
  `ctos-jarvis request "ajoute relire les notes demain 25 min priorite 3"`
  created one pending proposal and printed the inbox.
- Temporary DB JSON request:
  `ctos-jarvis request "ajoute verifier jarvis demain 15 min priorite 2" --json`
  returned `mode=ctos-jarvis-request`, `saved_attempted=true`, and embedded
  an inbox with one pending agenda proposal.
- Temporary DB no-save request:
  `ctos-jarvis request "ajoute verifier jarvis demain 15 min priorite 2" --no-save`
  stayed in planned state and did not stage a proposal.
- Deterministic intent request:
  `ctos-jarvis request "ouvre vms" --inbox` reported the safe intent and showed
  an empty inbox without executing the action.

Update 2026-07-08:

Expose the local model chat rail as `ctos-jarvis chat`. The command wraps
`ctos-ai-chat` with a CTOS-specific system prompt: explain and plan, propose
explicit CTOS commands for mutations, and never claim execution. `--brief`
injects the current `ctos-ai brief`, `--plan` prints the lower-level command
without model/runtime contact, and `--json` gives UI callers a structured result
or failure.

Rationale:

- The Jarvis goal needs conversation, not only deterministic command routing.
- The existing `ctos-ai-chat` rail should be reachable from the Jarvis namespace
  so the operator has one mental entry point.
- The chat surface must stay read-only until CTOS adds stronger proposal and
  confirmation rails for each action class.

Verification:

- `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-ai scripts/ctos-ai-chat`
- `ctos-jarvis chat --plan "resume CTOS en une phrase"` printed the
  lower-level `ctos-ai-chat` command and the read-only authority note.
- `ctos-jarvis chat --plan --json --brief "resume la situation"` returned
  `mode=ctos-jarvis-chat`, embedded a successful `ctos-ai brief` step, and did
  not contact the model runtime.
- `ctos-jarvis chat --json --no-ensure-server "resume CTOS en une phrase"`
  returned a structured failure because `ctos-ai-api-server` was stopped, proving
  the wrapper does not silently pretend that chat is available.
- `ctos-jarvis next`

Update 2026-07-09:

Keep 9Router and Agent Reach as optional cost-saving/capability layers, not as
direct CTOS authorities.

Rationale:

- `decolua/9router` is a current MIT GitHub project that exposes a local
  OpenAI-compatible router, token-saving features, provider fallback, and support
  claims for Codex/Claude Code/Cursor-style clients. This is useful for a
  "cheap/free lane", but it routes prompts to multiple external providers and
  therefore needs a secrets/privacy boundary before any private repo context is
  allowed through it.
- `Panniantong/Agent-Reach` is a current MIT GitHub project that installs and
  health-checks read/search tools for web, GitHub, YouTube, RSS, and selected
  social platforms. It is a capability layer for research, not an execution
  authority. Some channels rely on cookies/browser sessions, so CTOS should test
  it in safe/dry-run mode first.
- CTOS already has local Ollama on `ctos-core`, `ctos-ai ask-local`, the
  localhost API tunnel, and `ctos-jarvis chat`. The smallest safe extension is
  routing low-risk summarization/planning/research through local or cheap
  adapters while reserving Codex for high-value implementation, review, and
  architecture.

Sources:

- https://github.com/decolua/9router
- https://github.com/Panniantong/Agent-Reach
- https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md

Verification:

- GitHub repository metadata was fetched on 2026-07-09 for both projects.
- README files for both projects were read from their default branches.
- No package, daemon, API key, provider account, cookie, or system service was
  installed or configured.

Update 2026-07-10:

Expose a CTOS cheap/free AI lane without installing external coding tools.

Decision:

- Add inert runtime profiles for `aider-cli-local`, `9router-local-proxy`, and
  `agent-reach-local-tools`.
- Add `ctos-ai cheap-lane` and `ctos-ai cheap-plan` as read-only inspection and
  planning commands.
- Add `ctos-ai code-draft` as the first operator-facing cheap draft command. It
  sends only the explicit prompt to local Ollama on `ctos-core`; it does not
  read files, inspect git state, execute commands, or edit the repo.
- Use `qwen2.5-coder:1.5b` as the default `code-draft` model because the 0.5B
  path is fast but too noisy for useful coding/planning drafts.

Rationale:

There is no free GitHub product that makes frontier Codex-Pro-level model
compute free. The practical reduction path is a layered workflow: local Ollama
for cheap private drafts, Aider later as an optional explicit-file coding
client, 9Router only after privacy/secrets review, Agent-Reach only as a
read/search layer, and Codex kept for risky edits, architecture, and final
review.

Sources:

- https://github.com/Aider-AI/aider
- https://aider.chat/docs/
- https://github.com/decolua/9router
- https://github.com/Panniantong/Agent-Reach

Verification:

- `python3 -m json.tool ai/runtime_profiles.json`
- `python3 -m py_compile scripts/ctos-ai ai/agenda_parser.py ai/action_planner.py ai/ctos_prompt.py`
- `ctos-ai cheap-lane`
- `ctos-ai cheap-plan --tool aider`
- `ctos-ai runtime-check aider-cli-local`
- `ctos-ai runtime-check 9router-local-proxy`
- `ctos-ai runtime-check agent-reach-local-tools`
- `ctos-ai code-draft --print-prompt "test rapide"`
- Live owned-node smoke outside the sandbox:
  `ctos-ai code-draft --max-tokens 90 "..."`

Update 2026-07-10:

Classify OpenJarvis and Free Claude Code as candidates only; do not install
either on the T480 host yet.

Decision:

- OpenJarvis becomes a sandbox research candidate for the CTOS Jarvis
  architecture, skill model, scheduled agents, local-first execution, and
  evaluation loop.
- Free Claude Code becomes an optional proxy candidate for the cheap coding
  lane, behind a strict privacy/secrets review and a synthetic-repo test.
- Neither project should replace the existing CTOS action boundary. CTOS keeps
  typed proposals, explicit confirmations, local Ollama draft commands, and
  Codex for high-risk implementation/review.

Rationale:

OpenJarvis is closely aligned with the long-term Jarvis target, but it is new
and its agent presets can touch files, shell, scheduled tasks, and OAuth
integrations. Free Claude Code can reduce friction with Codex/Claude-compatible
clients, but it is a prompt/tool proxy and launcher shim, so it must be treated
as sensitive infrastructure rather than a normal app.

Sources:

- https://github.com/open-jarvis/OpenJarvis
- https://open-jarvis.github.io/OpenJarvis/
- https://openjarvis.stanford.edu/
- https://arxiv.org/abs/2605.17172
- https://github.com/Alishahryar1/free-claude-code

Verification:

- Repository metadata and READMEs were reviewed on 2026-07-10.
- No package, daemon, API key, provider account, OAuth token, or client config
  was installed or modified.

Update 2026-07-10:

Install OpenJarvis as an isolated CTOS voice/chat sandbox, not as a host-wide
authority.

Decision:

- Install OpenJarvis manually under `~/.local/share/ctos/openjarvis` using
  `uv` and Python 3.13 because the host Python is 3.14 while OpenJarvis
  declares Python `<3.14`.
- Do not run the upstream one-line installer. It can install uv/Ollama, pull a
  default model, install commands, configure state, and start background
  orchestration.
- Do not install a new Ollama runtime or pull OpenJarvis' default model. Use
  the existing CTOS Ollama runtime on `ctos-core` through the local tunnel
  `127.0.0.1:11435`.
- Add `scripts/ctos-openjarvis` as the only normal CTOS entrypoint. It supports
  `status`, `ask`, `chat`, `voice-once`, and `codex-brief`.
- Keep OpenJarvis as local chat/planning only. CTOS remains the action and
  approval boundary; Codex remains the implementation handoff.

Rationale:

The operator wants a voice-first Jarvis path quickly, but OpenJarvis includes
agent, tool, file, shell, scheduler, OAuth, telemetry, and update surfaces.
The safe first step is to use it as an isolated local assistant brain behind
the existing CTOS voice/tunnel stack, while preventing accidental host
authority or background services.

Sources:

- OpenJarvis repository cloned on 2026-07-10:
  https://github.com/open-jarvis/OpenJarvis
- OpenJarvis installer inspected on 2026-07-10:
  `scripts/install/install.sh` from the upstream repository.
- OpenJarvis config/runtime docs inspected locally on 2026-07-10:
  `docs/architecture/engine.md`, `docs/user-guide/chat-simple.md`,
  `src/openjarvis/core/paths.py`, `src/openjarvis/cli/_version_check.py`.
- uv installer inspected on 2026-07-10:
  https://astral.sh/uv/install.sh

Verification:

- `/home/operator/.local/bin/uv --version` returned `uv 0.11.28`.
- `uv venv --python 3.13 ~/.local/share/ctos/openjarvis/.venv`.
- `uv pip install --python ~/.local/share/ctos/openjarvis/.venv/bin/python -e ~/.local/share/ctos/openjarvis/src`.
- `~/.local/share/ctos/openjarvis/.venv/bin/jarvis --help`.
- `python3 -m py_compile scripts/ctos-openjarvis`.
- `scripts/ctos-openjarvis status --json` reported OpenJarvis installed,
  tunnel OK, Ollama `0.30.8`, and `qwen2.5-coder:1.5b` available.
- `scripts/ctos-openjarvis ask "reponds juste OK" --max-tokens 20` returned
  `OK` without the OpenJarvis banner or update warning.
- `scripts/ctos-openjarvis voice-once --plan --seconds 3`.
- `scripts/ctos-openjarvis codex-brief "ouvre le cockpit et resume l'etat"`.
- `scripts/ctos-install-user-bin --force` linked `ctos-openjarvis` into
  `~/.local/bin`.

Consequences:

OpenJarvis is now usable as a local chat/voice experiment. It is not a daemon,
not an always-on microphone, not a shell executor, not a repo editor, and not a
Codex replacement. The next live step is operator microphone testing with:
`ctos-openjarvis voice-once --seconds 5` and
`ctos-openjarvis voice-once --mode codex --seconds 5`.

## ADR-0044: Add a localhost browser voice console for slow Jarvis chat

Date: 2026-07-10
Status: accepted

Decision:

Add `control/voice_console.py`, `control/static/voice.html`,
`control/static/voice.css`, `control/static/voice.js`, and
`scripts/ctos-voice-console` as a local-only browser interface for CTOS voice
chat. The console binds to `127.0.0.1:8770`, records microphone audio in the
browser with explicit button control, converts uploads to mono WAV with
existing `ffmpeg`, transcribes through `scripts/ctos-voice`, and routes text to
`scripts/ctos-openjarvis`.

Context:

The operator wants a custom interface close to a slow GPT-style voice chat:
record, pause, resume, replay, typed fallback, and spoken answers. The current
CLI path works but is too rigid for long daily use. CTOS already has local
OpenJarvis/Ollama, Vosk/STT wrappers, and TTS wrappers, so a new framework or
daemon is unnecessary for V0.

Options considered:

- Full desktop app: rejected for V0 because it adds package and UI-framework
  decisions too early.
- Always-on voice daemon: rejected because it increases privacy, accidental
  trigger, and debugging risk.
- Local browser console: accepted because localhost browser microphone access
  is enough for an interactive prototype and keeps the action boundary small.

Sources:

- Existing repo voice wrapper: `scripts/ctos-voice`.
- Existing repo OpenJarvis wrapper: `scripts/ctos-openjarvis`.
- Existing repo localhost dashboard pattern: `control/server.py` and
  `scripts/ctos-control`.
- Browser APIs used: `MediaRecorder` and `getUserMedia`.
- Python APIs used: `http.server` and `subprocess`.

Rationale:

This gives a real conversational surface without installing packages, exposing
network services, storing durable recordings, or letting a voice transcript
directly mutate the machine. `Chat` remains local assistant mode, while
`Codex` produces a handoff brief only.

Verification:

- `python3 -m py_compile control/voice_console.py`.
- `bash -n scripts/ctos-voice-console`.
- `node --check control/static/voice.js`.
- `python3 -m py_compile scripts/ctos-openjarvis scripts/ctos-voice`.
- `scripts/ctos-voice-console restart`.
- `scripts/ctos-voice-console status` showed the server running on
  `127.0.0.1:8770`, `ctos-openjarvis`, `ctos-voice`, `ffmpeg`, Ollama
  `0.30.8`, and model `qwen2.5-coder:1.5b` available.
- `curl -fsS http://127.0.0.1:8770/voice.html`.
- Local POST to `/api/voice/ask-text` with `reponds juste OK` returned `OK`.
- `scripts/ctos-install-user-bin --force` linked `ctos-voice-console`.
- `git diff --check`.

First browser microphone capture remains the next live operator test.

Consequences:

The console is a V0 operator tool, not the final Jarvis runtime. Future work
can add streaming partial transcripts, a richer conversation database, and
explicit CTOS action approval buttons after the basic loop is stable.

Update 2026-07-10:

Add a deterministic `Brief` mode and automatic status/config/network intent
routing for `Chat`. The brief route reads `ctos-ai brief`, `ctos-netwatch
status`, and `ctos-openjarvis status --json`, then returns a compact CTOS state
summary. This prevents the small local model from hallucinating when the
operator asks for "etat des lieux", "configuration", "capacite", or "reseau".
The route remains read-only.

## ADR-0045: Use official Firefox for localhost CTOS browser tools

Date: 2026-07-10
Status: accepted

Decision:

Use the official Arch `extra/firefox` package as the first browser for local
CTOS web tools, including `http://127.0.0.1:8770` voice console microphone
access. Do not use AUR browsers or Electron wrappers for this role.

Context:

The T480 currently has no browser command available, while the voice console
needs a browser with microphone support. The user asked whether to install
Firefox or use a more local/secure alternative.

Options considered:

- Firefox from Arch `extra`: accepted; official package, mainstream Wayland
  desktop support, WebRTC/getUserMedia support, no AUR.
- VS Code embedded/simple browser: rejected for voice-console use because it is
  not a reliable microphone/browser surface.
- AUR/third-party browsers: rejected for V0 because they widen supply-chain
  and package-management scope.

Sources:

- Local package metadata on 2026-07-10: `pacman -Si firefox` reported
  `extra/firefox 151.0.1-1`, MPL-2.0, installed size 284.34 MiB.
- Arch Linux package page, accessed 2026-07-10:
  https://archlinux.org/packages/extra/x86_64/firefox/
- Mozilla Firefox project page:
  https://www.mozilla.org/firefox/

Rationale:

Firefox is the smallest sane browser decision for a local voice UI: official
repository, current desktop integration, and no new service. Security posture
comes from binding CTOS tools to localhost, not from avoiding a maintained
browser.

Verification:

Install attempted from Codex, but sudo required an operator password in a TTY.
Installation remains an operator command:

```bash
sudo pacman -S --needed firefox
```

After install, verify:

```bash
firefox --version
ctos-voice-console serve
firefox http://127.0.0.1:8770
```

Consequences:

Firefox becomes the local UI surface for CTOS cockpit/voice tools. Browser
profiles, extensions, sync, and remote-access exposure remain out of scope
unless separately decided.

## ADR-0046: Start network visibility with metadata-first local tools

Date: 2026-07-10
Status: accepted

Decision:

Add `scripts/ctos-netwatch` and `docs/NETWORK_VISIBILITY.md` as the first
network visibility layer. Use existing `ip`, `ss`, `nft`, `tcpdump`, and
`tshark` tooling. Do not install a GUI analyzer or long-running network
dashboard yet.

Context:

The operator wants, later, a tool to see all network traffic. CTOS should make
traffic visible without creating unnecessary packet logs, durable sensitive
captures, or a new exposed service.

Options considered:

- Metadata-first local snapshots: accepted for V0.
- Wireshark GUI: useful later for deep manual inspection, but not needed now.
- `ntopng`: potentially useful dashboard later, but requires a separate
  service/storage/privacy decision.
- Always-on packet capture: rejected for normal operation.

Sources:

- Local package ownership on 2026-07-10:
  `/usr/bin/tcpdump` owned by `tcpdump 4.99.6-1`;
  `/usr/bin/tshark` owned by `wireshark-cli 4.6.6-1`.
- Local versions: `tcpdump --version`, `tshark --version`.
- Wireshark/TShark project documentation:
  https://www.wireshark.org/docs/man-pages/tshark.html
- tcpdump man page:
  https://www.tcpdump.org/manpages/tcpdump.1.html

Rationale:

Socket/interface/counter metadata answers most operational questions with far
less privacy risk than full packet capture. Packet capture remains explicit,
short, and never stored in the repo.

Verification:

- `bash -n scripts/ctos-netwatch scripts/ctos-install-user-bin`.
- `scripts/ctos-netwatch tools` reported `ip`, `ss`, `nft`, `tcpdump`, and
  `tshark` available.
- `scripts/ctos-netwatch status` works outside the Codex sandbox and confirmed
  host interfaces, routes, listening DNS/DHCP services, SSH, local Ollama
  tunnel, cockpit, and voice console ports.
- `scripts/ctos-install-user-bin --force` linked `ctos-netwatch` into
  `~/.local/bin`.

Consequences:

Future cockpit network panels should read from metadata and counters first.
Packet capture and dashboards require explicit operator action and separate
storage/security decisions.

## ADR-0047: Trial Piper as the first clear local French TTS voice

Date: 2026-07-10
Status: accepted

Decision:

Use Piper as the first higher-quality local TTS engine for CTOS voice output.
Install it in the user-owned CTOS AI state directory, download one French voice
model outside Git, and make it selectable through `ctos-voice`. The Voice
Console and push-to-talk launcher may use Piper automatically only when the
binary and model files are present. Do not add cloud TTS, a system service, or
always-on audio.

Context:

The operator reported that the current voice is horrible and hard to
understand. Local inspection showed the T480 only had `espeak-ng`/`espeak`
available for spoken output, so the harsh voice quality was expected.

Options considered:

- Piper local TTS: accepted for V0. It is small enough to test now, works
  offline after model download, and fits the Home Assistant/Wyoming direction.
- Continue tuning `espeak-ng`: rejected as the main path; speed/amplitude
  tuning helped volume but not natural intelligibility.
- Cloud TTS: rejected for default CTOS voice because it creates privacy,
  network, quota, and cost dependencies.
- Full voice framework first: rejected here; this slice only replaces the
  output voice without changing CTOS authority or STT routing.

Sources:

- Piper project note, accessed 2026-07-10:
  https://github.com/rhasspy/piper
- OHF-Voice Piper continuation, accessed 2026-07-10:
  https://github.com/OHF-Voice/piper1-gpl
- Hugging Face `rhasspy/piper-voices` French `fr_FR/siwis/medium` voice,
  accessed 2026-07-10:
  https://huggingface.co/rhasspy/piper-voices/tree/main/fr/fr_FR/siwis/medium
- Local package check on 2026-07-10: Arch repos did not provide a suitable
  official `piper-tts` package for this host; the name `piper` in repo search
  referred to a gaming mouse configuration tool, not TTS.
- Live install on 2026-07-10: `pip` installed `piper-tts 1.4.2` plus
  `onnxruntime 1.27.0` inside `~/.local/share/ctos-ai/venvs/piper`.

Rationale:

The V0 need is clear speech, not a new authority layer. A local venv keeps the
TTS experiment reversible and avoids global Python installs. Model files stay
under `~/.local/share/ctos-ai/tts/piper/`, never in the repo. `ctos-voice` now
has explicit `tts-probe`, `setup-piper`, `tts-test`, and `--engine` controls,
so failures are visible rather than silently falling back.

Verification:

- `python3 -m py_compile scripts/ctos-voice control/voice_console.py`.
- `scripts/ctos-voice tts-probe --json` initially reported Piper missing.
- `scripts/ctos-voice setup-piper --print-commands`.
- `scripts/ctos-voice setup-piper --yes` installed the local venv, downloaded
  `fr_FR-siwis-medium.onnx` and `.onnx.json`, and reported `ready=true`.
- `scripts/ctos-voice tts-test --engine piper` passed in the live audio
  session.
- `scripts/ctos-voice-console status` now reports `tts.default_engine=piper`
  and `piper.ready=true`.
- POST `/api/voice/say` with `Test Piper depuis la console CTOS.` returned
  `ok=true`.

Consequences:

Piper is now the preferred local voice for the browser Voice Console and
push-to-talk launcher when available. The low-level CLI still accepts explicit
engine selection for debugging. Future work can add more voices and a UI voice
selector, but the current default remains local/offline and bounded.

## ADR-0048: Gate Voice Console actions through existing CTOS approval queues

Date: 2026-07-10
Status: accepted

Decision:

Add a Voice Console `Action` mode that previews deterministic CTOS actions and
queues only allowlisted items into the existing `ctos-ai` approval stores.
Execution requires an explicit browser click on `Approve`; unknown speech and
free-form text are never executed.

Context:

The operator wants Jarvis-style spoken control, but CTOS must not turn speech
recognition mistakes into direct host/VM mutations. The repo already has
`ctos-ai route-text`, generic approvals, and agenda proposal queues.

Options considered:

- Execute safe voice intents immediately: rejected for V0 because STT mistakes
  are still common.
- Add a new Voice Console queue database: rejected because it would duplicate
  review state and create two approval systems.
- Reuse `ctos-ai` approvals and agenda proposals: accepted.
- Let the browser submit arbitrary commands: rejected.

Sources:

- Local `scripts/ctos-ai actions --json` allowlist on 2026-07-10.
- Local `scripts/ctos-ai route-text`, `propose`, `approvals`, `approve`,
  `reject`, `agenda-propose`, `agenda-proposals`, `agenda-confirm`, and
  `agenda-reject` command behavior on 2026-07-10.
- Local `ai/action_planner.py` and `ai/agenda_parser.py` routing/parsing
  behavior.

Rationale:

The approval stores already record target, risk, rollback, command payload,
status, and result. Reusing them keeps action authority auditable and avoids a
new privileged path. The browser can propose and review intent, but it only
calls bounded CTOS subcommands.

Verification:

- `python3 -m py_compile control/voice_console.py`.
- `node --check control/static/voice.js`.
- `python3 -m py_compile scripts/ctos-ai ai/action_planner.py
  ai/agenda_parser.py ai/voice_intents.py`.
- Temporary DB smoke tests:
  `demarre kali` queued `approval:kali-start`;
  `ouvre kali` queued `approval:kali-console`;
  `ajoute appeler la banque demain priorite 3 30 minutes` queued an agenda
  proposal;
  `raconte moi une blague` stayed unqueued.

Consequences:

Voice actions are now slower than direct command execution, but safer. Future
work can add more allowlisted actions and richer confirmation text without
changing the security boundary.

## ADR-0049: Add bounded action vocabulary aliases before changing STT stack

Date: 2026-07-10
Status: accepted

Decision:

Improve Voice Console Action mode with a small hardcoded vocabulary correction
layer for common `Kali` transcription errors and add quick buttons for the
high-frequency Kali actions. Do not change STT model, add cloud STT, or bypass
the approval queue.

Context:

The operator could not test spoken Kali actions because the transcript missed
the word `Kali`. The existing action queue is safe, but brittle if a single
keyword is misheard.

Options considered:

- Replace STT immediately: deferred; larger change, more tuning, and not
  required to unblock Kali action testing.
- Add broad fuzzy natural-language matching: rejected for V0.1 because it can
  create false positives for actions.
- Add bounded aliases plus quick buttons: accepted.

Sources:

- Local Voice Console transcript behavior reported by the operator on
  2026-07-10.
- Local `control/voice_console.py` action allowlist and routing behavior.
- Local `scripts/ctos-ai` approval commands.

Rationale:

Aliasing only known `Kali` variants keeps the action surface narrow while
fixing the observed failure. Quick buttons give a no-STT fallback but still
create only pending approvals, so accidental execution remains blocked.

Verification:

- `python3 -m py_compile control/voice_console.py`.
- `node --check control/static/voice.js`.
- Temporary DB tests confirmed:
  `demarre cali` and `demarre quali` map to `approval:kali-start`;
  `ouvre callie` maps to `approval:kali-console`;
  `eteins ka li` maps to `approval:kali-shutdown`;
  `checkpoint qu a lit` maps to `approval:kali-checkpoint`.

Consequences:

The voice path is more usable without new dependencies. Alias coverage remains
intentionally small and should grow only from observed transcript failures.

## ADR-0050: Heal DESK remote by VNC handshake, not port presence

Date: 2026-07-12
Status: accepted

Decision:

Treat the T480-to-`ctos-core` DESK stream as healthy only when the local
forwarded VNC port returns a real `RFB` handshake. If a localhost listener
exists but the handshake fails, rebuild the SSH tunnel and let the DESK guard
restart the viewer when needed. Reduce the guard loop default from 20 seconds
to 5 seconds so DESK returns quickly after T480/tower boot or resume.

Context:

After a T480 reboot, the operator reported the desktop link broken even though
the previous remote-access patch was present. The existing guard checked only
for a local listener on `127.0.0.1:5902`, which can stay true for a stale
`ssh -L` process even when the remote VNC stream is not usable.

Options considered:

- Leave manual `ctos-ai open-desk` recovery: rejected because DESK is expected
  to be a normal boot surface.
- Move VNC to a LAN listener: rejected because direct VNC exposure is not
  needed and weakens the current localhost-only boundary.
- Add a real VNC handshake probe and rebuild stale tunnels: accepted.

Sources:

- Local `scripts/ctos-desk-remote` and `scripts/ctos-desk-guard` behavior.
- Live `scripts/ctos-desk-guard status` after T480 reboot:
  SSH ready on port `22`, remote X11 ready, remote `x0vncserver` on
  `127.0.0.1:5902`.

Rationale:

The VNC server already sends an `RFB` banner before authentication. Reading
that banner is a narrow, protocol-level health check that proves the local port
is not merely bound, but actually connected to the remote desktop stream. The
VNC service remains localhost-only on `ctos-core` and reachable from the T480
only through SSH.

Verification:

- `bash -n scripts/ctos-desk-remote`
- `bash -n scripts/ctos-desk-guard`
- Live `scripts/ctos-desk-guard status` returned:
  `local_tunnel: listening 127.0.0.1:5902 handshake=ok`.

Consequences:

DESK recovery may rebuild old SSH tunnels more aggressively, but only for the
CTOS VNC tunnel port. The guard now polls more often, adding a tiny SSH/status
check every 5 seconds while the T480 session is active.

## ADR-0051: Persist tower Internet egress on the T480 bastion

Date: 2026-07-13
Status: accepted

Decision:

Keep `ctos-core` dependent on the T480 for Internet egress over the direct
Ethernet link, but install the forwarding and masquerade path in persistent
T480 host configuration: `/etc/nftables.conf` for filter/NAT rules and
`/etc/sysctl.d/90-ctos-ip-forward.conf` for IPv4 forwarding. Runtime rescue
rules remain useful for emergency recovery, but are no longer the desired
steady state.

Context:

After a T480 reboot, the operator reported extremely poor Internet throughput
on the tower. Live checks showed the T480 Wi-Fi WAN was healthy, the
T480-to-tower Ethernet link was `1000/full`, and tower-to-T480 ping was healthy.
The tower could not ping `1.1.1.1` or resolve DNS, which identifies the fault as
missing egress/NAT on the T480 rather than a slow LAN or Wi-Fi link.

Options considered:

- Keep re-running `scripts/ctos-firewall-fix-tower-egress`: rejected because it
  installs runtime-only rules that can disappear after reboot.
- Give the tower independent Wi-Fi again: deferred because the current design
  intentionally uses the T480 as bastion and the external Wi-Fi adapter has been
  unreliable.
- Persist tower egress in nftables/sysctl with backup-on-change: accepted.

Sources:

- Local `scripts/ctos-firewall-fix-tower-egress`.
- Local `/etc/nftables.conf` observed on 2026-07-13.
- Live link checks from `ctos-node` and `ctos-core` on 2026-07-13.

Rationale:

The T480 already owns the Internet path and firewall boundary. Persisting the
same narrow LAN-to-WAN forwarding and masquerade rules makes the topology
survive reboot without widening the tower exposure. A dedicated installer script
keeps the change auditable and backs up `/etc/nftables.conf` before editing.

Verification:

- `bash -n scripts/ctos-install-tower-egress`
- T480 WAN checks passed before fix: ping to `1.1.1.1` and `endeavouros.com`.
- Tower LAN checks passed before fix: `10.42.0.2 -> 10.42.0.1`.
- Privileged apply installed `/etc/nftables.conf` backup
  `/etc/nftables.conf.ctos-backups/nftables.conf.20260713-002615`.
- Persistent config inspection found CTOS tower egress rules in
  `/etc/nftables.conf` and `net.ipv4.ip_forward = 1` in
  `/etc/sysctl.d/90-ctos-ip-forward.conf`.
- Post-fix tower checks passed: `10.42.0.1` ping 0% loss, `1.1.1.1` ping 0%
  loss at about 13 ms, DNS resolved `endeavouros.com`, and a 10 MB HTTP
  download from Cloudflare reached about 24 MB/s.

Consequences:

If the T480 Wi-Fi interface name changes from `wlan0` or the Ethernet LAN
interface changes from `enp0s31f6`, the script must be re-run with explicit
`WAN_IF` or `LAN_IF`. The tower remains intentionally dependent on the T480 for
Internet access.

## ADR-0067: Use Apple-supported iPhone recovery and preserve-first triage

Date: 2026-07-17
Status: accepted

Decision:

For the owner-authorized family iPhone in Security Lockout, stop passcode
attempts and do not install or run brute-force, bypass, or forensic tooling.
First test only the supported iOS 17+ previous-passcode path when the passcode
was changed within 72 hours. Otherwise inventory and archive existing iCloud
Photos/backups and computer backups, verify the linked Apple Account, then use
Apple's erase-and-restore flow only after the owner accepts any uncovered data
loss.

Context:

The phone reportedly contains irreplaceable family photos, is powered on, and
shows a 15-minute lockout after several guesses. The owner authorizes access
and accepts erasure, but preservation has higher value than quick reuse. Exact
model, iOS version, passcode-change history, Apple Account access, iCloud state,
and backup state are not yet known. Read-only USB inventory on the T480 did not
detect an Apple USB device, so the device state could not be verified locally.

Options considered:

- Continue manual guesses or automate brute force: rejected. Apple enforces
  escalating Secure Enclave delays, and the optional Erase Data setting removes
  content after 10 consecutive wrong attempts.
- Install third-party bypass/forensic tooling in Kali: rejected. Reliability,
  device/version compatibility, provenance, and data-preservation claims are
  unverified, while the repo boundary keeps offensive workflows isolated and
  excludes credential-bypass work on personal data.
- Erase immediately: rejected until cloud/local copies and Activation Lock
  credentials are checked.
- Use the prior passcode within Apple's 72-hour iOS 17+ window, otherwise
  preserve-first inventory followed by official erase/restore: accepted.

Sources:

- Apple Security Lockout reset: https://support.apple.com/en-ie/105090
- Apple forgotten-passcode recovery: https://support.apple.com/en-ie/118430
- Apple previous-passcode reset: https://support.apple.com/en-au/105039
- Apple Platform Security passcodes: https://support.apple.com/en-lamr/guide/security/sec20230a10d/web
- Apple iCloud Backup contents: https://support.apple.com/en-us/108770
- Apple iCloud Photos: https://support.apple.com/en-us/108782
- Apple local backup discovery: https://support.apple.com/en-us/108809
- Apple trusted computers: https://support.apple.com/en-euro/109054
- Apple Activation Lock: https://support.apple.com/en-ie/108794

Rationale:

Without the passcode, a newly attached computer cannot establish trust and
create a new backup. Apple's supported forgotten-passcode recovery otherwise
erases the device. Therefore the only defensible non-erasing attempt is the
explicit previous-passcode feature; all remaining preservation opportunity is
in data already synchronized or backed up.

Verification:

- Official Apple support and Platform Security pages reviewed 2026-07-17.
- `lsusb` showed no Apple USB device.
- `idevice_id -l` failed to retrieve a device list.
- `ideviceinfo` reported no device; no write or pairing command was issued.
- No package, VM tool, bypass utility, or forensic utility was installed or run.

Consequences:

If no previous-passcode option and no backup/sync copy exist, the family must
choose between retaining the locked phone unchanged in hope of a future lawful
recovery option and erasing it for reuse. Apple-supported reset cannot preserve
data that exists only on the locked device. Activation Lock may still require
the linked Apple Account after erasure.

USB identification follow-up 2026-07-17:

Read-only host inspection verified active T480 xHCI and Thunderbolt/USB-C root
hubs but no enumerated Apple device or recent connection event. Apple documents
that a locked iPhone does not communicate with a wired accessory by default.
Installing `usbmuxd`, entering recovery/DFU, or changing host USB policy solely
to obtain a model name is rejected: user-space software cannot query a device
absent from the USB bus, while recovery/DFU changes boot state and conflicts
with preserving the only copy of family data. Use the physical `Axxxx` marking
inside the SIM-tray slot; do not collect the adjacent IMEI.

## ADR-0068: Build a supported Windows 11 Apple recovery VM with gated USB-C controller passthrough

Date: 2026-07-17
Status: accepted and amended during implementation

Decision:

Build the future `ctos-apple-recovery` domain as a supported Windows 11 x64
Q35/UEFI VM with Secure Boot, private emulated TPM 2.0, Windows inbox AHCI and
e1000e drivers, CTOS NAT, and Apple Devices only from Microsoft Store product
`9NP83LWLPZ9K`. Accept optional VirtIO drivers only from Microsoft Update.
Prefer managed PCI passthrough of the dedicated JHL6240 USB-C
xHCI controller, but define it only after an `intel_iommu=on` preflight proves
an isolated group, correct physical port, uninterrupted host charging, and safe
detach/reattach. Reject ACS override. Use an offline clean baseline and
disposable per-phone disk/NVRAM/TPM session state.

Licensing amendment 2026-07-17: the operator confirmed that no Windows licence
is available for this VM. Continue only host preparation and declarative
scaffolding. Do not acquire/install consumer media or seal a durable baseline
until an entitlement explicitly covering this VM is identified. Microsoft's
official Windows 11 Enterprise Evaluation may be used only after separate
explicit approval as a disposable 90-day compatibility test; it requires a
Microsoft account and becomes subject to hourly shutdown after expiry.

Implementation hardening amendment 2026-07-17: keep incomplete lifecycle
features explicitly unavailable. The repo helper must enforce the entitlement
record, detect non-enumerated Type-C source/host partners, compare active and
inactive libvirt XML against an exact device allowlist, inspect Secure Boot
variables/certificates with `virt-fw-vars`, and require real Mains telemetry.
The allowlist covers security-relevant attributes and recursively rejects
unknown device-child tags; this specifically prevents host serial-log paths,
SPICE rendernodes, interface ROM files, nested video acceleration, or TPM
backend additions from hiding below an otherwise approved device.
Pre-install NVRAM plus empty private TPM state may be generated atomically with
no Windows media/domain/disk. Maintenance transition, authenticated ISO import,
USB qualification success, consistency-set sealing, disposable sessions, and
cleanup stay fail-closed until their evidence workflows exist.

Secure-state ownership amendment 2026-07-17: resolve `root`, `libvirt-qemu`,
`tss`, and `libvirt` through the local account database on every preparation;
never encode numeric IDs. Require the canonical state root as
`root:libvirt 0751`, NVRAM as `libvirt-qemu:libvirt 0640`, the strictly empty
pre-install TPM directory as `tss:libvirt 0750`, and its attestation as
`root:libvirt 0640`. Refuse missing identities, symlinked/non-canonical paths,
ownership or mode drift, hard-linked state files, unreadable USB vendor
inventory, and any attempt to start the unimplemented maintenance profile.
Local evidence is `getent`, `/etc/libvirt/qemu.conf`, and effective operator
group membership; the constraints are QEMU write access, swtpm write access,
operator read-only audit access, and no group modification rights.

Licensing clarification 2026-07-17: Microsoft permits selecting “I don't have
a product key” during first-time setup only as a path to purchasing a digital
licence after installation; it does not turn an unactivated VM into a free
durable entitlement. Keep the exact profile values
`blocked-no-eligible-vm-entitlement` and
`not-authorized-disposable-only`. Do not infer VM rights from the T480's OEM
licence: Microsoft's current virtualization guidance says an OEM-only licence
typically does not include them. The official 90-day Enterprise Evaluation is
a separate product and remains unauthorized until an explicit disposable-test
decision.

Authenticated-media amendment 2026-07-17: implement `import-media` now, but
place the root, entitlement, infrastructure, host-safety, and XML preflight
before any source-path access. Accept only the fixed canonical basename and
published SHA-256, owned by the invoking operator, single-linked, and not
group/world writable. Hash the open source before and after copying; hash the
same-filesystem staging copy; publish the ISO and strict root-owned attestation
with hard-link no-replace semantics and directory `fsync`; then refresh the
libvirt pool and verify its exact path. An exact existing target is
idempotent; any incompatible target or attestation is preserved and refused,
never overwritten. This makes the future licensed action auditable without
weakening today's no-licence refusal.

Context:

The operator wants a reusable VM for official Apple restore workflows, first
for an iPhone XS. The T480 has sufficient CPU, about 16 GiB RAM, and about
195 GiB available storage. CTOS pools/network are ready and Kali is shut off.
Q35 Secure Boot firmware exists, but `swtpm`, `virt-firmware`, enrolled OVMF
keys, and usable PCI IOMMU groups are not present in the current boot state.
The iPhone changes USB state during recovery/restore, so a single ephemeral USB
bus/device mapping is not an adequate reliability boundary.

Options considered:

- Windows 10: rejected because normal support ended and a new reusable recovery
  workstation should start on a supported OS.
- Modified Windows image or requirement bypass: rejected as unsupported and
  unnecessary on the i7-8550U/Q35/TPM-capable host.
- Apple Devices from Microsoft Store: accepted as Apple's current official
  Windows restore application.
- Community virtio-win stable ISO as installation media: rejected during
  implementation because neither the ISO, RPM, nor repository metadata has an
  independent upstream signature/hash chain; the repository explicitly uses
  `gpgcheck=0`.
- Windows inbox AHCI/SATA and e1000e for bootstrap: accepted. They avoid a
  third-party media trust dependency and are adequate for this recovery VM.
- Optional `PCI\\VEN_1AF4` drivers from Windows Update/Microsoft Update
  Catalog: accepted only when Windows validates their publisher/signature.
- iTunes or third-party Apple installers: rejected as a silent downgrade while
  the supported Apple Devices path has not failed verification.
- Individual USB hostdev by bus/device or one product ID: rejected because the
  phone can disconnect and re-enumerate under different USB identities.
- Whole JHL6240 controller passthrough: preferred if isolation is proven.
- SPICE usbredir filtered to Apple VID: conditional investigation only if safe
  controller isolation fails and only after repeated re-enumeration proof.
- PCIe ACS override: rejected because it manufactures apparent grouping rather
  than proving hardware isolation.

Sources:

- Microsoft Windows download and VM requirements:
  https://www.microsoft.com/en-us/software-download/windows11
  https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements
- Microsoft activation/no-key purchase path:
  https://support.microsoft.com/en-us/windows/activation/activate-windows
- Microsoft Enterprise Evaluation and VM licensing guidance:
  https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise
  https://www.microsoft.com/licensing/guidance/Windows-11-Licensing-for-Virtual-Desktops
- Microsoft Secure Boot 2026 transition:
  https://support.microsoft.com/en-US/servicing/os/secure-boot/2025/06/windows-secure-boot-certificate-expiration-and-ca-updates
- Apple Devices and recovery procedures:
  https://support.apple.com/en-us/118290
  https://support.apple.com/en-us/118106
  https://support.apple.com/en-us/118107
- Libvirt hostdev/TPM and snapshots:
  https://libvirt.org/formatdomain.html
  https://libvirt.org/formatsnapshot.html
- Arch libvirt/passthrough/full-upgrade guidance:
  https://wiki.archlinux.org/title/Libvirt
  https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF
  https://wiki.archlinux.org/index.php/Package_Management_FAQs
- Detailed local plan: `context/23_windows_apple_recovery_vm_plan.md`.
- VirtIO provenance evidence and Microsoft authenticated alternative:
  https://fedorapeople.org/groups/virt/virtio-win/virtio-win.repo
  https://github.com/virtio-win/virtio-win-pkg-scripts/issues/108
  https://www.catalog.update.microsoft.com/Search.aspx?q=PCI%5CVEN_1AF4

Rationale:

Whole-controller ownership is the smallest architecture that naturally keeps
USB resets and product-ID changes inside the guest. The preflight gate prevents
that reliability advantage from weakening host DMA isolation or capturing
host-critical devices. A clean baseline plus disposable complete session state
limits persistent Apple firmware, logs, and device traces without rolling a
Windows disk back against unrelated TPM/NVRAM state.

Using Windows inbox storage/network drivers removes an unnecessary unsigned
media provenance dependency. Performance from VirtIO is not required for an
Apple firmware restore workstation; authenticity and reproducibility take
precedence. There is no silent mirror or unverified ISO fallback.

Verification required before acceptance:

- full Arch update and official `swtpm`/`virt-firmware` install (completed
  2026-07-17: QEMU `11.0.2-3`, libvirt `12.5.0-1`, swtpm `0.10.1-2`,
  virt-firmware `26.7.1-1`);
- supported Windows media hash matched to Microsoft's live page;
- Microsoft 2011+2023 Secure Boot transition keys inspected in guest NVRAM;
- TPM 2.0, Secure Boot, inbox/authenticated drivers, Windows Update, Defender, and Apple
  Devices verified inside Windows;
- IOMMU group/port/charging/detach/reattach checks pass with no phone;
- non-sensitive USB re-enumeration test passes;
- phone connection and Restore remain separate explicit approval gates.

Consequences:

The implementation requires at least one host package/update/IOMMU reboot and one
IOMMU qualification reboot before VM definition. Controller passthrough may be
blocked by real hardware grouping; that is an acceptable blocker, not grounds
for ACS override. Windows installation is blocked because no eligible VM
entitlement is currently available; the disposable Evaluation choice and
Store account handling remain explicit open questions. The iPhone remains
outside the VM until the separate restore approval window.

Static verification after the hardening review: 46 combined unit tests passed,
both Apple domain XML files passed `virt-xml-validate`, Python compilation and
`git diff --check` passed, and a live read-only libvirt plan observed healthy
CTOS pools/network, Kali shut off, no Apple domain/volume, and both the licence
and connected-Type-C refusals. No scaffold mutation was executed.

## ADR-0052: Reconnect BXEB as a status-only fleet candidate

Date: 2026-07-18
Status: accepted

Decision:

Add the old EliteBook/ZLiteBook laptop as `ctos-zlitebook` in
`fleet/nodes.json` with role `worker-candidate`, status `active`, OS
`Ubuntu 24.04`, and SSH control target `ben@192.168.1.24`. Extend
`scripts/ctos-fleet` with a generic read-only Linux SSH status probe for
non-core nodes. Do not install packages, configure sudo, sync repo state, or
start worker services on this laptop yet.

Context:

The operator asked to reconnect the laptop previously used to bootstrap the
T480. Existing context only recorded that the T480 was reachable from the
EliteBook in May 2026; it did not record the laptop's own current address or
user. LAN discovery on 2026-07-18 identified `bxeb.home` / `192.168.1.24` as
an Intel-backed Ubuntu host with OpenSSH on TCP `22` and nginx on TCP `8080`
serving `Snake Surge`. The operator confirmed the SSH user is `ben`, installed
the T480 public key with `ssh-copy-id`, and key-only SSH then succeeded.

Options considered:

- Leave the laptop out of inventory until it is converted to EndeavourOS:
  rejected because it is reachable now and useful as a known fleet candidate.
- Treat it as a full CTOS worker immediately: rejected because it is still
  Ubuntu and no role, storage, data-retention, or worker-service boundary has
  been decided.
- Add it as a status-only SSH candidate: accepted.

Sources:

- Local context notes under `context/04_open_questions.md`.
- LAN scan result on 2026-07-18: OpenSSH `9.6p1 Ubuntu 3ubuntu13.18`, nginx
  `1.27.5`.
- Live SSH check on 2026-07-18: hostname `BXEB`, user `ben`, Ubuntu `24.04`,
  kernel `6.17.0-40-generic`.

Rationale:

Inventorying the laptop gives CTOS a real multi-machine view without expanding
authority. The generic SSH probe reads only basic health fields and uses
`BatchMode=yes`; failure remains visible instead of prompting or falling back.
Keeping the node as `worker-candidate` preserves the fleet target of
EndeavourOS workers while allowing this Ubuntu machine to be observed and used
deliberately.

Verification:

- `ssh -F /dev/null -o BatchMode=yes ben@192.168.1.24 'hostname; whoami; uname -a'`
  succeeded.
- `python -m json.tool fleet/nodes.json`
- `python -m py_compile scripts/ctos-fleet`
- `scripts/ctos-fleet status --json` includes live `ctos-zlitebook` status.

Consequences:

The current address is DHCP on the Wi-Fi LAN and may change. A later step should
choose whether to reserve `BXEB` in the router, use mDNS/hostname discovery,
or move it behind a CTOS-controlled link. Any package install, worker service,
repo sync, sudo rule, or OS conversion remains a separate explicit decision.

## ADR-0069: Make a validated local task spec the only voice input to Codex

Date: 2026-07-18
Status: accepted for architecture; implementation pending

Decision:

Use the authenticated Codex CLI as the primary coding and reasoning executor
for the voice orchestrator. Integrate it through the supported non-interactive
`codex exec` command, not through Selenium, pixel-level UI control, or the
experimental Codex app-server.

The speech transcript must stop at a local CTOS boundary. A local,
non-authoritative spec compiler may transform it into a strict task object, but
deterministic code must validate and redact that object and the operator must
be able to review the exact canonical spec. Only that validated spec may be
passed to Codex. The schema must not contain raw transcript/audio, arbitrary
shell, credential, token, or unbounded context fields.

The first runner must use `codex exec --ephemeral --sandbox read-only` against
an explicit Git workspace. A later workspace-write mode requires a separate
visible approval transition and keeps Codex's own sandbox/approval boundary.
Authentication, usage-limit, and service failures remain visible; do not
silently substitute a lower-quality local model. Ollama remains a local
voice/spec-compilation aid, not the primary Codex replacement.

Context:

The operator supplied a fifteen-point voice-orchestrator proposal and then
explicitly confirmed that paid Codex access may be used. Live checks found
Codex CLI `0.133.0` installed on the T480 and authenticated through ChatGPT.
The CLI exposes `exec`, `--ephemeral`, `--sandbox`, JSONL events, and structured
output schemas. VS Code and the OpenAI Codex extension are installed; no MCP
server is configured.

Most speech plumbing already exists: Vosk/Piper are ready locally,
Wyoming/faster-whisper artifacts exist on `ctos-core`, OpenJarvis and Ollama
are usable on demand, and CTOS already owns deterministic actions and approval
queues. The missing boundary is the important one: current
`scripts/ctos-openjarvis` `codex_handoff()` repeats the supplied text verbatim
and only prints it. It neither creates a clean schema nor invokes Codex.

Options considered:

- Forward the raw STT transcript to `codex exec`: rejected because it violates
  the explicit operator requirement, preserves recognition noise, and weakens
  scope/approval review.
- Keep the current printable `codex-brief` as the final integration: rejected
  because it is not an orchestrator and duplicates the raw input.
- Drive the Codex TUI or VS Code with Selenium/pixel automation: rejected as
  fragile and unnecessary while a supported stable CLI surface exists.
- Use the experimental app-server as V1: rejected because the stable
  non-interactive command already provides the required pipeline surface.
- Give OpenJarvis or a local model direct repository/system authority:
  rejected because it duplicates and weakens the established CTOS boundary.
- Replace Codex with Qwen/Gemma on current local hardware: rejected. The
  current nodes can evaluate small models for bounded spec compilation, but
  not match the intended coding/reasoning role, and the operator has authorized
  Codex usage.
- Validated spec -> direct `codex exec`: accepted.

Sources:

- Codex non-interactive mode, accessed 2026-07-18:
  https://learn.chatgpt.com/docs/non-interactive-mode
- Codex CLI command reference, accessed 2026-07-18:
  https://learn.chatgpt.com/docs/developer-commands?surface=cli
- Codex approvals and sandboxing, accessed 2026-07-18:
  https://learn.chatgpt.com/docs/agent-approvals-security
- Codex MCP configuration, accessed 2026-07-18:
  https://learn.chatgpt.com/docs/extend/mcp
- Codex IDE settings, accessed 2026-07-18:
  https://learn.chatgpt.com/docs/developer-settings?surface=ide
- Live `codex --version`, `codex exec --help`, `codex login status`,
  `codex mcp list`, `code --version`, and extension inventory on 2026-07-18.
- Detailed intake and live comparison:
  `context/25_voice_codex_orchestrator_intake.md`.

Rationale:

This is the shortest path that turns the existing components into the product
the operator described. It spends the paid frontier capability on repository
reasoning and changes, while keeping noisy/private audio handling and cheap
classification local. A schema and deterministic validator make scope,
constraints, requested output, acceptance checks, and risk visible before a
cloud coding agent acts. Direct CLI integration removes an unnecessary UI
automation failure mode and preserves Codex sandbox semantics.

Verification required before live acceptance:

- a versioned task-spec schema rejects transcript/audio/secret/arbitrary-shell
  fields, unknown properties, excessive sizes, and targets outside the selected
  workspace;
- synthetic tests prove redaction, ambiguity/clarification handling, exact
  canonical rendering, and no raw-input field in the Codex process payload;
- plan mode prints the exact `codex exec` arguments without execution;
- one synthetic, secret-free invocation runs with `--ephemeral` and
  `--sandbox read-only`, produces structured output, and cannot modify the
  workspace;
- authentication, quota, network, validation, and Codex failure states fail
  closed and never trigger a local-model fallback;
- logs contain stage/status/timing metadata only, with no transcript, audio,
  token, auth state, or complete Codex prompt/output by default;
- workspace-write remains unreachable until its explicit approval design and
  tests are accepted.

Consequences:

Normalized task specs sent to Codex cross the local-machine boundary even when
raw audio/transcripts do not. Specs therefore must remain secret-free and
operator-reviewable. Local model quality can cause an ambiguous or incomplete
spec; the correct response is clarification, not guessing. MCP remains
optional and should be added only for a concrete tool/context need. Exact
subscription limits are not inferred from the operator's payment or current
login state.

## ADR-0070: Keep the EliteBook-to-home voice path private and staged

Date: 2026-07-18
Status: LAN boundary accepted; outside-home transport implementation pending

Decision:

For voice V1, use `BXEB` as the operator, browser, and microphone endpoint and
keep the T480 as the home Voice Console, spec-validation, and Codex node. On
the home LAN, preserve the Voice Console's `127.0.0.1:8770` bind and reach it
through the already-verified key-based OpenSSH local forward. Do not widen the
HTTP listener.

Treat outside-home access as a separate private-network and availability
slice, not as a prerequisite for the LAN voice POC. Reject router port
forwarding and public exposure of SSH, Voice Console, VNC, or the current web
services. The recommended candidate is a private Tailscale tailnet used only
as transport, with the existing OpenSSH keys retained inside it. Do not enable
Tailscale SSH or Funnel in V1. Installation remains pending operator acceptance
of the hosted control-plane/identity-provider tradeoff and a minimal access
policy.

Context:

The operator works from the EliteBook while the T480 normally stays at home.
Live LAN verification on 2026-07-18 proved key-only SSH from `BXEB` user `ben`
to T480 user `operator`. The browser can capture the EliteBook microphone and
send it over a loopback SSH forward to the T480 Voice Console. The console
currently performs ffmpeg conversion and Vosk transcription on the T480.

The existing TTS route is not remote audio: `/api/voice/say` launches Piper and
the playback command on the T480, returning JSON to the browser. Browser-audible
Piper therefore requires an explicit render-and-stream endpoint. The current
Codex mode is also not a real test: it only prints a raw-transcript handoff and
must remain disconnected from `codex exec` until ADR-0069 is implemented.

Options considered:

- Bind the Voice Console or SSH publicly: rejected. It expands exposure and
  operating burden without being necessary for either LAN or remote use.
- Tailscale Funnel: rejected because it intentionally publishes a service to
  the public Internet.
- Enable Tailscale SSH immediately: rejected for V1 because existing key-based
  OpenSSH is already verified and replacing its authentication path adds no
  required capability.
- Private Tailscale transport plus existing OpenSSH: recommended as the
  smallest outside-home candidate. NAT traversal and relay avoid router port
  forwarding, at the cost of a hosted control plane and identity dependency.
- Direct WireGuard: retained as a later self-hosted option. It requires public
  endpoint/CGNAT discovery, DDNS or stable addressing, UDP forwarding,
  firewall rules, and peer lifecycle work.

Sources accessed 2026-07-18:

- Tailscale Linux installation:
  https://tailscale.com/docs/install/linux
- Tailscale connection types and firewall behavior:
  https://tailscale.com/docs/reference/connection-types
  https://tailscale.com/docs/integrations/firewalls
- Tailscale grants and device visibility:
  https://tailscale.com/docs/features/access-control/grants
  https://tailscale.com/docs/concepts/device-visibility
- Tailscale device approval, key expiry, SSH, and Funnel:
  https://tailscale.com/docs/features/access-control/device-management/device-approval
  https://tailscale.com/docs/features/access-control/auth-keys
  https://tailscale.com/docs/features/tailscale-ssh
  https://tailscale.com/docs/features/tailscale-funnel
- WireGuard official quick start:
  https://www.wireguard.com/quickstart/
- OpenSSH server configuration reference:
  https://man.openbsd.org/sshd_config
- Live nested SSH, listener, Voice Console, browser, and TTS path inspection on
  2026-07-18; detailed test plan:
  `context/26_elitebook_voice_codex_test_plan.md`.

Rationale:

The LAN path already provides encryption, authentication, and a loopback-only
application boundary. Preserving it is smaller and more auditable than adding
an application listener or public ingress. A private overlay can later extend
the same SSH tunnel without changing the Voice Console trust model.

Availability remains independent from network reachability. Neither Tailscale
nor WireGuard can reach a T480 that is off, suspended, hibernated, disconnected,
or missing its boot services. Power/lid policy and any wake-on-LAN path through
`ctos-core` require separate verification and documentation.

Verification required before outside-home acceptance:

- MFA and device approval on the selected private network;
- a tested minimum policy permitting only `BXEB` to T480 TCP `22` initially;
- effective key-only, non-root OpenSSH controls and no router forwards;
- SSH tunnel and Voice Console test from a phone hotspot;
- reboot plus sleep/resume recovery tests;
- visible failure when the T480 is deliberately offline.

Consequences:

The first useful LAN test is independent of VPN choice and can run immediately.
A first outside-home SSH connection is estimated at 45-90 minutes; a properly
constrained and reboot/sleep-tested setup is 1.5-3 hours. Direct WireGuard is
at least 2-4 hours in the best case and can take longer behind CGNAT or a
restricted router. These transport estimates exclude the independently
implemented voice-to-Codex boundary recorded in ADR-0071.

## ADR-0071: Enforce a spec-only read-only Codex boundary and browser-delivered Piper

Date: 2026-07-18
Status: implemented and locally verified; one informed live-cloud acceptance
run pending

Decision:

Implement voice-to-Codex as an explicit two-stage boundary. Local Vosk and the
loopback Ollama model may compile the operator's ephemeral text into a closed
`ctos.voice_task.v1` object. A deterministic validator, not the model, owns the
exact workspace, read-only class, bounded fields, forbidden secret/raw/shell
names, canonical JSON, digest, and path constraints. When an operator names a
repository file explicitly, that path is a hard scope ceiling.

The console may return only the validated canonical spec for editable review.
Revalidation creates an unpredictable ten-minute token tied only to its digest;
the server stores neither the transcript nor the spec in that token registry.
Execution consumes the token once, requires a separate confirmation, and calls
`codex exec --ephemeral --ignore-user-config -c project_doc_max_bytes=0 -c
'web_search="disabled"' --sandbox read-only -C /home/operator/T480
--output-schema ... -` with a fixed instruction plus canonical spec over
stdin. The instruction limits inspection to declared `allowed_scope`; because
that limit is not an OS per-file read jail, informed approval must still treat
the workspace as technically readable. There is no local-model fallback from
a Codex failure.

Keep live Codex execution disabled by default. It may be enabled with
`CTOS_VOICE_CODEX_RUN_ENABLED=1` only for an informed acceptance window because
read-only sandboxing prevents writes but does not prevent the reviewed spec and
permitted repository content from being sent to OpenAI. The browser alone
cannot open this gate.

For remote TTS, render Piper to a bounded temporary WAV, return it from the
loopback console as `audio/wav` with `Cache-Control: no-store`, play it in the
EliteBook browser, and unlink it in all exit paths. Pass speech text over stdin,
not the process argument list. Do not invoke T480-side playback from the browser
path.

Sources accessed 2026-07-18:

- Codex non-interactive mode and stable `codex exec`, stdin, `--ephemeral`,
  sandbox, and output-schema behavior:
  https://learn.chatgpt.com/docs/non-interactive-mode
- Ollama structured outputs and JSON-schema `format` guidance:
  https://docs.ollama.com/capabilities/structured-outputs
- Ollama generate API, including non-streaming requests:
  https://docs.ollama.com/api/generate
- Existing repository privacy/authority requirements in ADR-0069 and
  `context/25_voice_codex_orchestrator_intake.md`.

Verification:

- 48 focused boundary/compiler/console/TTS tests pass.
- A real local Qwen compilation initially broadened one explicit file to
  directories; the deterministic path ceiling was added and the repeated live
  result allowed only `ai/voice_task_spec.py`.
- A live preview passed through the EliteBook SSH tunnel without returning the
  raw input. A live Piper response through that tunnel was a valid 117292-byte
  RIFF/WAVE response marked `no-store`.
- The Voice Console manager now falls back to matching-process discovery when
  its PID file is stale; a final stop/start/status cycle passed through the
  EliteBook tunnel.
- The first real Codex acceptance attempt was stopped before process/network
  execution at the informed external-disclosure gate. It is pending open
  question 52 and is not evidence of a Codex runtime failure.

Consequences:

The implemented POC can be exercised locally through preview, edit, digest,
and browser TTS without cloud disclosure. It cannot yet claim end-to-end live
Codex acceptance or human-perceived audio/STT quality. Workspace-write remains
absent, outside-home networking remains a separate decision, and future schema
expansion requires another documented review rather than silent field growth.

Incident amendment 2026-07-19:

Treat Voice Console HTML, CSS, JavaScript, API JSON, and WAV responses as
non-cacheable operational control data. Send `Cache-Control: no-store` on every
response, add explicit version query strings to static assets, and require an
exact client/server build match. Bind every asynchronous response to the mode
captured when its request was sent and disable mode switching while busy.
Display request failures in the main Answer panel, scroll validated Codex
previews into view, and treat an empty Chat stdout as failure rather than HTTP
200 success. Retire the obsolete browser `/api/voice/say` route with HTTP 410;
local CLI speech remains available, but a stale page cannot play on the T480.

The decision follows RFC 9111 section 5.2.2.5: a `no-store` response directive
prevents compliant caches from storing or reusing the response. The versioned
URL is still required to escape an already-cached pre-fix asset once; no-store
then prevents recurrence. Source accessed 2026-07-19:
https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5

Live evidence was an obsolete EliteBook client calling `/api/voice/say` and
playing audio on the T480 despite the current source using only
`/api/voice/synthesize`. After the fix, Firefox fetched build
`2026-07-19.3`; Chat returned `OK`, local Codex preview remained non-runnable,
Piper returned a 73260-byte browser WAV through the tunnel, and the legacy
route returned HTTP 410 without playback. The expanded focused suite passes 52
tests.

Decision 2026-08-04 — retire the planned Windows Apple-recovery VM for now:

The operator explicitly abandoned the Windows VM work. Read-only libvirt and
storage inventory found no `ctos-apple-recovery` domain, volume, NVRAM, TPM, or
managed ISO artifact; only the unrelated shut-off `ctos-kali` domain and its
volumes exist. Therefore no live deletion was performed. The downloaded
Windows ISO and repository design files are installation inputs/source, not a
VM, and are retained unless separately requested. This avoids deleting useful
source material under an ambiguous meaning of “delete the VM.”
