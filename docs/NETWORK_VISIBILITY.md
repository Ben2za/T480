# CTOS Network Visibility

Goal: see what owned CTOS machines are doing on the network without turning
normal workstations into noisy packet-logging boxes.

## V0

Use metadata-first commands:

```bash
ctos-netwatch status
ctos-netwatch flows
ctos-netwatch tools
```

This reads interfaces, addresses, routes, DNS, listening sockets, and current
TCP/UDP socket state. It does not create packet captures.

## Existing Tools

Current host already has:

- `ip` and `ss` from `iproute2`.
- `nft` from `nftables`.
- `tcpdump`.
- `tshark` from `wireshark-cli`.

## Capture Rules

- Do not capture packet payloads by default.
- Do not store `.pcap` files in the repo.
- Prefer short live captures and summaries.
- Treat DNS names, IPs, URLs, cookies, and packet bodies as private data.
- Use packet capture only on owned interfaces and owned systems.

## Explicit Capture Examples

Short live packet summary:

```bash
sudo tcpdump -ni any -c 100
```

DNS-only:

```bash
sudo tcpdump -ni any -vv 'udp port 53 or tcp port 53'
```

HTTP/TLS metadata without body capture:

```bash
sudo tshark -i any -f 'tcp port 80 or tcp port 443' \
  -T fields \
  -e frame.time \
  -e ip.src \
  -e ip.dst \
  -e tcp.dstport \
  -e tls.handshake.extensions_server_name
```

## Future Dashboard

The clean CTOS path is:

1. Add a cockpit panel fed by `ss`, `ip`, and nftables counters.
2. Add optional short `tshark` summaries for live debugging.
3. Add per-node fleet reporting from `ctos-core`.
4. Consider Wireshark GUI for manual deep inspection.
5. Consider `ntopng` only after a separate storage/privacy/service decision.
