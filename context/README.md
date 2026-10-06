# CTOS Local Context

This folder is the working memory for the Arch rebuild ecosystem repo.

Use it to keep decisions, research, open questions, and task state durable across sessions. `AGENTS.md` stays short and directive; this folder carries the detailed knowledge.

## Files

- `00_project_brief.md`: normalized handover from existing notes.
- `01_working_agreements.md`: collaboration and quality rules.
- `02_decision_log.md`: architecture decisions with sources and rationale.
- `03_research_protocol.md`: how choices must be researched and cited.
- `04_open_questions.md`: ambiguity register for brainstorm.
- `05_task_board.md`: current task plan and status.
- `06_source_registry.md`: sources already consulted.
- `07_repo_blueprint.md`: proposed repository shape.
- `08_host_audit.md`: current T480 repo and host orientation snapshot.
- `09_cockpit_roadmap.md`: host cockpit, VM, AI, and game-mode roadmap.
- `10_libvirt_inventory.md`: read-only libvirt inventory for the host cockpit.
- `11_vm_lifecycle_model.md`: CTOS-managed VM connection, storage, network, and snapshot model.
- `12_libvirt_infra_state.md`: live CTOS libvirt network/pool state after infra apply.
- `13_kali_domain_state.md`: live `ctos-kali` shutoff install-phase domain state.
- `14_kali_install_start.md`: first visible Kali installer start and ISO pool fix.
- `15_kali_post_install_boot.md`: transition from Kali installer boot to installed-system boot.
- `16_kali_baseline_snapshot.md`: Kali post-install baseline snapshot and post-battery-cut recovery state.
- `17_archipelago_fleet_model.md`: secondary fleet model for the T480, tower core, and future EndeavourOS worker nodes.
- `18_tower_diagnostic_state.md`: recovered Windows tower diagnostic summary and temporary SSH bridge state.
- `19_tower_ctos_core_install_v1.md`: first same-day EndeavourOS wipe/install plan for the recovered tower as `ctos-core`.
- `20_ctos_ai_v0_model.md`: first CTOS AI/Jarvis architecture model, inspiration scan, permission tiers, and V0 roadmap.
- `21_ctos_voice_backend_v2.md`: second voice/Jarvis backend spike after Vosk V1, keeping CTOS as the action boundary.
- `22_jarvis_stack_selection.md`: selected mature local/open-source Jarvis stack and CTOS authority boundary.
- `23_windows_apple_recovery_vm_plan.md`: researched Windows 11/Apple Devices recovery VM architecture, USB-C passthrough gates, and implementation runbook.
- `24_windows_apple_recovery_vm_state.md`: applied package state, active safety gates, provenance amendment, and exact continuation point for the implementation.
- `25_voice_codex_orchestrator_intake.md`: normalized operator requirements, three-node live audit, gap matrix, and the validated spec-only Codex integration target.
- `26_elitebook_voice_codex_test_plan.md`: implemented EliteBook/T480 LAN voice path, validated read-only Codex boundary, browser Piper result, remaining informed live-run/human gates, and private outside-home boundary.

## Current Input State

- Found: `CTOS_HANDOVER.md`.
- Found: `Assets/BackGround/4.webp`.
- Missing: `Setup.md` was open in the IDE but does not exist in `/home/ben/Desktop/T480` as of 2026-05-04.
