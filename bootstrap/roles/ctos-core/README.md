# ctos-core Role

`ctos-core` is the first fixed tower role.

V1 goals:

- EndeavourOS on bare metal.
- Simple Xfce desktop for a reliable same-day install on the current 8 GiB RAM state.
- Native SSH reachable from the T480 after first boot.
- Repo-owned bootstrap copied to `/opt/ctos/repo`.
- Service/cache/model/work directories under `/srv/ctos`.
- SATA SSD initialized separately, only after explicit disk confirmation.
- First non-daemon service layout under `/srv/ctos`.
- T480-controlled repo subset sync to `/srv/ctos/repo/t480`.

Deferred:

- custom ISO;
- automatic destructive partitioning;
- permanent secrets distribution;
- network-exposed package/model cache services;
- AI runtime services;
- polished desktop theming.
