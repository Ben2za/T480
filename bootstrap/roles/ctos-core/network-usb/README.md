# ctos-core Network USB Fix

Use this when the newly installed tower has no working Internet and no SSH link yet.

From the tower, mount/open the CTOS USB and run:

```bash
cd /run/media/*/*/ctos-core-netfix 2>/dev/null || cd /mnt/ctos-core-netfix
./ctos-core-netfix diag
sudo ./ctos-core-netfix iphone
sudo ./ctos-core-netfix wifi
```

If Wi-Fi connection failed with:

```text
802-11-wireless-security.key-mgmt: property is missing
```

run:

```bash
sudo ./ctos-core-netfix wifi
```

Default key management is `wpa-psk`, which is correct for most WPA/WPA2 mixed home networks and iPhone hotspot. If the network is WPA3-only, choose `sae`.

The script writes reports under:

```text
outputs/netdiag-*/
```

It does not write the Wi-Fi password to the report.
