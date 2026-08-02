# Update order

Suggested update order for the Podman stack (dependencies first):

- `crun`
- `conmon`
- `passt`
- `netavark`
  - This recipe also builds `aardvark-dns`; keep it on the same minor.
- `skopeo`
  - Keep `container-libs` `common/v*` aligned with Skopeo's `go.mod`.
  - Ships shared defaults under `/usr/share/containers/` (not `/etc`).
- `buildah`
- `podman`

`crun`, `conmon`, and `passt` are independent leaves and can be updated in any
order among themselves.

Netavark v2 drops iptables (nftables only) and changes default network isolation.
