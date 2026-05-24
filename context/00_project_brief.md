# Project Brief

Date: 2026-05-04

## Goal

Build a Git repository that can recreate a personal Arch Linux workstation/lab setup quickly when moving between laptops, with strong reproducibility, isolation, and low local trace retention.

The target is not one laptop only. The long-term objective is to maintain the same full configuration, tools, knowledge, and operating model across many independent machines, first with local repo/bootstrap workflows and later through a personal server.

The workstation should be self-sufficient for:

- authorized red-team and bug bounty work
- custom security tool development
- local AI-assisted research and triage
- homelab experimentation
- reusable personal knowledge capture

## Target Machines

- Current target: ThinkPad T480, 16 GB RAM.
- Long-term target: reproducible full-in fleet model across many laptops/workstations. Each machine should be able to operate independently.
- Current OS state from handover: Arch-based minimal setup, described as EndeavourOS minimal, with Hyprland, Waybar, tooling, Wi-Fi, Git, libvirt, and network already done.

## Current Architecture From Handover

- Host: minimal Arch/EndeavourOS, Hyprland, LUKS, Btrfs, systemd-boot.
- UI direction: black base `#0b0b0c`, dark red `#8b0000`, minimal CTOS-like HUD.
- Workspaces:
  - 1 RECON
  - 2 EXPLOIT
  - 3 REVERSE
  - 4 DEV
  - 5 AI
  - 6 LOGS
  - 7 VAULT
  - 8 COMMS
  - 9 LAB
- Local tree target: `~/ctos/` with tools, wordlists, payloads, loot, reports, notes, lab, ai, scripts, containers.
- Tooling listed: git, neovim, tmux, btop, ripgrep, nmap, metasploit, sqlmap, john, hashcat, gobuster, ffuf via yay, dirsearch via venv only.
- Network: NetworkManager active, Avahi disabled.
- OPSEC plan: nftables, kill-switch, DNS control, future self-hosted VPN.
- Virtualization: qemu, libvirt, virt-manager, default NAT, images under `/var/lib/libvirt/images`.
- VM rules: host is hypervisor only; Kali and Arch Dev VMs; offensive work never on host; VMs not run in parallel.
- AI plan: local Jarvis, RAG/KB, programmable accuracy; future Ollama and Qdrant; modes DEV, OPS, AI, MIX.
- RAM strategy: host 2-3 GB, Kali 6 GB, Arch Dev 6 GB.

## Current Status From Handover

Done:

- OS
- Hyprland
- Waybar
- tooling
- Wi-Fi
- Git
- libvirt
- network

In progress:

- Kali VM

Todo:

- AI
- firewall
- scripts
- orchestration

## Engineering Interpretation

This repo should become a reproducible operations repository, not just a dotfiles dump. It needs:

- Declarative package manifests and bootstrap scripts.
- Dotfiles managed with clear ownership and safe install semantics.
- Host/VM/AI/security boundaries documented before automation, while still installing the complete operator environment on each machine.
- Decision logs for every meaningful technology choice.
- Explicit rules for trace minimization without compromising legality, reliability, or auditability.

The core product is an operator environment: host baseline, desktop, lab isolation, AI knowledge stack, bug bounty workflow, custom tooling workspace, and future personal-server sync.
