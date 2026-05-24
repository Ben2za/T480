# 🧠 CTOS OPERATOR ENV — FULL HANDOVER

## 🎯 Vision globale

Machine cible : ThinkPad T480 (16GB RAM)

Objectifs :
- Host minimal (Arch + Hyprland CTOS)
- IA locale (Jarvis + knowledge base)
- Lab virtualisé isolé (Kali + Arch Dev)
- Sécurité / OPSEC
- Reproductibilité totale

---

# 🧱 1. HOST SYSTEM

- Arch Linux (EndeavourOS minimal)
- Hyprland
- LUKS + Btrfs
- systemd-boot

Hyprland config clé :
``` json
misc {
    disable_hyprland_logo = true
    disable_splash_rendering = true
}
```
---

# 🎨 2. UI CTOS

Design :
- Fond noir (#0b0b0c)
- Rouge (#8b0000)
- HUD minimal

Workspaces :
``` json
1 → RECON
2 → EXPLOIT
3 → REVERSE
4 → DEV
5 → AI
6 → LOGS
7 → VAULT
8 → COMMS
9 → LAB
```
---

# 🗂 3. STRUCTURE

~/ctos/
``` json
├── tools/
├── wordlists/
├── payloads/
├── loot/
├── reports/
├── notes/
├── lab/
├── ai/
├── scripts/
├── containers/
```
---

# ⚙️ 4. TOOLING

Installed :
``` json
- git
- neovim
- tmux
- btop
- ripgrep
- nmap
- metasploit
- sqlmap
- john
- hashcat
- gobuster
- ffuf (via yay)
```
dirsearch via venv uniquement

---

# 🔐 5. GIT

git config --global user.name
git config --global user.email

Auth :
- HTTPS (simple)
- SSH (propre)

---

# 🌐 6. NETWORK

nmcli device wifi connect "SSID" password "PASS"

NetworkManager actif
avahi désactivé

---

# 🛡 7. OPSEC PLAN

À implémenter :
``` json
- nftables
- kill-switch
- DNS control
```
VPN futur → self-hosted

---

# 🧪 8. VIRTUALIZATION

Stack :
``` json
- qemu
- libvirt
- virt-manager
```
libvirtd actif

Réseau :

default (NAT)

Storage :

/var/lib/libvirt/images

---

# 🧠 9. VM ARCHITECTURE

Host = hyperviseur

VM1 → Kali (offensive)
VM2 → Arch Dev

Règle :

- jamais en parallèle
- jamais offensive sur host

---

# 🧠 10. IA PLAN

Objectif :

- Jarvis local
- RAG + KB
- programmable accuracy

Modes :

DEV / OPS / AI / MIX

Stack futur :

- Ollama
- Qdrant

---

# ⚙️ 11. RAM STRATEGY

Host → 2-3GB
Kali → 6GB
Arch Dev → 6GB

---

# 🚧 12. STATUS
``` json
DONE :
- OS
- Hyprland
- Waybar
- tooling
- wifi
- git
- libvirt
- network

IN PROGRESS :
- Kali VM

TODO :
- IA
- firewall
- scripts
- orchestration
```
---

# 🎯 NEXT STEPS

1. Kali VM install
2. Arch Dev VM
3. Mode scripts
4. IA stack
5. nftables

---

# 🧠 PRINCIPLES

- Host clean
- Isolation
- Reproducible
- No global pip
- Minimal UI
- Automation later