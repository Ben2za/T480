# CTOS Ethernet Rescue

Use this on the tower when it is connected directly to the T480 by Ethernet.

The T480 has already been configured as:

```text
Ethernet: 10.42.0.1/24
Mode: NetworkManager shared
Internet source: T480 Wi-Fi
```

On the tower, open a terminal in this folder and run:

```bash
sudo ./ctos-ethernet-rescue auto
```

If that fails, run the steps manually:

```bash
sudo ./ctos-ethernet-rescue dhcp
sudo ./ctos-ethernet-rescue static
./ctos-ethernet-rescue diag
```

Success looks like:

```text
ping 10.42.0.1       works
ping 1.1.1.1         works
ping endeavouros.com works
```

If it still fails, bring this USB back to the T480 and inspect:

```text
ctos-ethernet-rescue/outputs/
```

If the script picks the wrong Ethernet interface, rerun with:

```bash
sudo CTOS_ETH_IFACE=enpXsY ./ctos-ethernet-rescue auto
```

Replace `enpXsY` with the Ethernet device shown by:

```bash
nmcli dev status
```
