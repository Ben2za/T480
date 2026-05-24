# Research Protocol

Date: 2026-05-04

## Rule

No meaningful technical choice is final until it has current, targeted source support.

## When Research Is Mandatory

- Installing or removing packages.
- Choosing Arch repositories, AUR helpers, kernels, bootloader, filesystem layout, firewall, DNS, VPN, virtualization, AI stack, editor, or Codex setup.
- Security/OPSEC changes.
- Anything described as latest, current, cutting edge, recommended, best, hardened, or modern.

## Source Priority

1. Official upstream documentation.
2. Arch Wiki and Arch package metadata for Arch-specific behavior.
3. Upstream release notes, changelogs, and GitHub/GitLab repositories.
4. Security advisories, CVEs, man pages, and distro packaging notes.
5. Reputable engineering writeups only as secondary context.

## Required Decision Output

Every decision record must include:

- Date researched.
- Exact question being answered.
- Options compared.
- Sources with URLs.
- Constraints from the current hardware and existing setup.
- Decision and rejected alternatives.
- Verification command or manual check.

## No Fallback Policy

"No fallback" means no silent downgrade, no legacy path kept around for comfort, and no unverified backup implementation.

Operational handling:

- If the leading option is verified and reliable, implement it.
- If it is verified but unsuitable, reject it with evidence.
- If it cannot be verified, mark the decision blocked.
- Do not install older alternatives just to make progress unless the user explicitly accepts the tradeoff in the decision log.

## Query Shape

Use focused searches such as:

- `site:wiki.archlinux.org nftables systemd-resolved dns over tls arch`
- `site:archlinux.org/packages visual-studio-code-bin arch linux`
- `site:github.com/openai/codex releases linux x86_64 install`
- `site:developers.openai.com/codex AGENTS.md config.toml hooks`

Record final links in `06_source_registry.md`.
