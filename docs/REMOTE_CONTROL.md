# CTOS Remote Control

Date: 2026-06-15

Scope: first T480-to-`ctos-core` remote-control path.

## Boundary

V1 keeps SSH as the root control channel. No desktop-control service should be exposed on the LAN by default.

The first helper is:

```bash
scripts/ctos-remote status
scripts/ctos-remote plan
scripts/ctos-remote install-commands
scripts/ctos-remote krdp-localhost --start
scripts/ctos-remote tunnel-command --protocol rdp
scripts/ctos-remote client-command --protocol rdp
scripts/ctos-remote service-command status
```

`scripts/ctos-remote` is deliberately non-mutating. It probes local viewer packages, remote server packages, graphical sessions, unit files, and common RDP/VNC listeners. It can print an SSH tunnel command, but it does not install packages, start services, open firewall rules, or keep a long-running tunnel by itself.

## Current State

Current probe state on 2026-06-15 after the first KRDP pass:

- `ctos-core` is reachable over SSH at `ctos@10.42.0.2`.
- SDDM and a KDE Wayland desktop session are active on the tower.
- `krdp 6.6.5-1` is installed on the tower.
- `freerdp 3.26.0-1` and `remmina 1.4.43-2` are installed on the T480.
- KRDP is active as a user service, disabled for autostart, and listening only on `127.0.0.1:3389`.
- A temporary SSH tunnel from `127.0.0.1:3390` on T480 to `127.0.0.1:3389` on the tower was TCP-tested, then closed.

## Preferred V1 Lane

Use the current KDE desktop session if possible:

1. Try KDE/Plasma RDP first with `krdp` on `ctos-core`.
2. Use `freerdp` or `remmina` on the T480 as the client.
3. Keep the service tunnel-only first:

```bash
ssh -F /dev/null -N -L 127.0.0.1:3390:127.0.0.1:3389 ctos@10.42.0.2
```

4. Connect the viewer to `127.0.0.1:3390`.
5. Only after tunnel validation, decide whether a controlled LAN listener is justified.

## KRDP Test Sequence

Install the client on the T480:

```bash
sudo pacman -S --needed freerdp remmina
```

Install the server on `ctos-core`:

```bash
ssh -tt -F /dev/null ctos@10.42.0.2 'sudo pacman -S --needed krdp'
```

Configure the tower for localhost-only KRDP:

```bash
scripts/ctos-remote krdp-localhost --start
```

That command:

- writes a user systemd override for `app-org.kde.krdpserver.service`;
- starts KRDP with `--address 127.0.0.1 --plasma`;
- enables PAM login for the current `ctos` system user;
- keeps KRDP disabled for autostart;
- creates a local TLS certificate under `~/.local/share/krdpserver/`;
- refuses success if KRDP listens on a non-localhost address.

Status/start commands can still be generated from the T480:

```bash
scripts/ctos-remote service-command status
scripts/ctos-remote service-command start
```

Start the tunnel from the T480:

```bash
ssh -F /dev/null -N -L 127.0.0.1:3390:127.0.0.1:3389 ctos@10.42.0.2
```

Connect from another T480 terminal:

```bash
xfreerdp3 /v:127.0.0.1:3390 /u:ctos /cert:ignore /gfx:AVC420:on,AVC444:on /network:lan -dynamic-resolution /w:1280 /h:720 +clipboard
```

This is the conservative first-render profile. It uses the X11 FreeRDP client,
the RDP graphics pipeline required by KRDP, advertises AVC/H264 support that
KRDP currently requires, fixed 1280x720 geometry, and certificate ignore because
the RDP server is only reached through the SSH localhost tunnel.
Do not expose KRDP directly on the LAN with this client profile.

If that profile still shows a blank window, try the SDL FreeRDP client:

```bash
sdl-freerdp3 /v:127.0.0.1:3390 /u:ctos /cert:ignore /gfx:AVC420:on,AVC444:on /network:lan -dynamic-resolution /w:1280 /h:720 +clipboard
```

The previous `wlfreerdp3` profile reached KRDP but produced a blank screen after
login on 2026-06-15 while logging VAAPI/libavcodec initialization failures.
A first `xfreerdp3` software-only command was also rejected by KRDP because the
client did not advertise the required graphics pipeline. A no-AVC RDPGFX command
was rejected with `Client does not support H.264 in YUV420 mode!`. Keep
`wlfreerdp3` as a later tuning path, not as the V1 default.

Do not pass the `ctos` password on the command line. Let FreeRDP prompt for it interactively.

## VNC Fallback Sequence

The KRDP path reached authentication and RDPGFX negotiation, but repeated visual
tests on 2026-06-15/2026-06-16 still ended in a blank window or server-side
session close. The next current-session fallback is KDE Desktop Sharing / VNC
with `krfb`.

Install the VNC client support on the T480:

```bash
sudo pacman -S --needed tigervnc remmina libvncserver
```

TigerVNC `vncviewer` is the V1 test client because the first Remmina launch on
2026-06-16 blocked on a desktop keyring unlock prompt. `libvncserver` is still
recorded because Remmina's installed VNC plugin failed to load without
`libvncclient.so.1`.

Install the server on `ctos-core`:

```bash
ssh -tt -F /dev/null ctos@10.42.0.2 'sudo pacman -S --needed krfb'
```

Start and configure KDE Desktop Sharing from the active tower session, not from
repo secrets. Do not put a VNC password in this repo or chat. After the server is
started, verify the listener before connecting:

```bash
ssh -F /dev/null ctos@10.42.0.2 'ss -lntp | grep 5900'
```

Runtime finding on 2026-06-16: `krfb` listened on `0.0.0.0:5900` and
`[::]:5900`. Until a localhost-only KRFB setting is verified, block direct LAN
VNC before use:

```bash
ssh -tt -F /dev/null ctos@10.42.0.2 'sudo firewall-cmd --zone=public --add-rich-rule='\''rule family="ipv4" port port="5900" protocol="tcp" reject'\'' && sudo firewall-cmd --zone=public --add-rich-rule='\''rule family="ipv6" port port="5900" protocol="tcp" reject'\'''
```

Those commands are runtime rules. Make them permanent only after the remote
desktop path is accepted as the stable V1 fallback.

Keep the client path behind an SSH tunnel:

```bash
ssh -F /dev/null -N -L 127.0.0.1:5901:127.0.0.1:5900 ctos@10.42.0.2
```

Then connect from the T480:

```bash
vncviewer -RemoteResize=0 -Shared 127.0.0.1:5901
```

Remmina remains an optional fallback if the keyring prompt is handled:

```bash
remmina -c vnc://127.0.0.1:5901
```

Runtime finding on 2026-06-16: TigerVNC connected to KRFB, but the first test
had no remote input and appeared to stay on a fixed frame. KRFB exposes an
`allowDesktopControl` setting; if the KRFB GUI has not enabled remote control,
write and reload it:

```bash
ssh -F /dev/null ctos@10.42.0.2 'kwriteconfig6 --file krfbrc --group Security --key allowDesktopControl true'
```

Restart KRFB after changing that value. If the stream is still non-interactive
or static, treat KRFB/Wayland/PipeWire as not validated for CTOS remote control
V1.

## TigerVNC Attached-Screen Fallback

TigerVNC also provides attached-screen servers. These are preferred over
continuing to tune KRFB if KRFB remains static:

- `w0vncserver`: current Wayland compositor through the remote desktop portal.
- `x0vncserver`: existing X11 display, after logging the tower into Plasma X11.

Install TigerVNC on both machines:

```bash
sudo pacman -S --needed tigervnc
ssh -tt -F /dev/null ctos@10.42.0.2 'sudo pacman -S --needed tigervnc'
```

First optional Wayland attached-screen test:

```bash
ssh -F /dev/null ctos@10.42.0.2 'env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus WAYLAND_DISPLAY=wayland-0 nohup w0vncserver -localhost -rfbport 5902 -SecurityTypes None -AlwaysShared >/tmp/ctos-w0vnc.log 2>&1 &'
ssh -F /dev/null -N -L 127.0.0.1:5902:127.0.0.1:5902 ctos@10.42.0.2
vncviewer -RemoteResize=0 -Shared 127.0.0.1:5902
```

Use `SecurityTypes None` only with `-localhost` and the SSH tunnel. Do not bind
this service to the LAN.

Runtime finding on 2026-06-16: `w0vncserver` was clean from a network boundary
perspective, listening only on `127.0.0.1:5902` and `[::1]:5902`. TigerVNC on
the T480 connected through the SSH tunnel and negotiated `SecurityTypes None`,
but the server later reported `Framebuffer updates: 0` and the viewer never
created a visible Hyprland window. Treat `w0vncserver` on the current Plasma
Wayland session as rejected for V1.

If Wayland remains unreliable, switch the tower login session to Plasma X11 and
use `x0vncserver`:

```bash
ssh -F /dev/null ctos@10.42.0.2 'env DISPLAY=:0 XAUTHORITY=/home/ctos/.Xauthority nohup x0vncserver -display :0 -localhost -rfbport 5902 -SecurityTypes None -AlwaysShared -AcceptKeyEvents -AcceptPointerEvents >/tmp/ctos-x0vnc.log 2>&1 &'
ssh -F /dev/null -N -L 127.0.0.1:5902:127.0.0.1:5902 ctos@10.42.0.2
vncviewer -RemoteResize=0 -Shared 127.0.0.1:5902
```

Open question: verify whether `krfb` can be forced to bind only to localhost in
this KDE version. Until that is confirmed, treat `krfb` as a manual fallback and
verify/firewall its listener before relying on it.

## Deferred Paths

- `xrdp`: deferred because it was not visible in the official pacman repository check on the T480 on 2026-06-15. Do not introduce AUR as a dependency until explicitly approved.
- `waypipe`: useful for individual Wayland apps later, not a full desktop-control baseline.
- Sunshine/Moonlight: good future high-performance desktop/game streaming path, not the first admin-control primitive.

## Sources

- Local package database check on 2026-06-15: `pacman -Si krdp krfb freerdp remmina tigervnc waypipe wayvnc moonlight-qt`.
- Local package file inspection on 2026-06-15: `krdp` provides `usr/bin/krdpserver`, `app-org.kde.krdpserver.service`, and `kcm_krdpserver`; `freerdp` provides `wlfreerdp3` and `xfreerdp3`.
- KDE KRdp source inspection on 2026-06-15: `server/main.cpp` documents `--address`, `--port`, PAM auth, and username/password options; `krdpserversettings.kcfg` documents `ListenPort`, `Users`, `SystemUserEnabled`, and `Autostart`.
- KDE KRFB Desktop Sharing app page: https://apps.kde.org/krfb/
- FreeRDP project: https://www.freerdp.com/
- TigerVNC project: https://www.tigervnc.org/
- Waypipe project: https://gitlab.freedesktop.org/mstoeckl/waypipe
