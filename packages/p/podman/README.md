# Podman Stack Build Order

When updating the Podman stack, build the lower-level runtime and shared
container tooling first, then build Podman last.

Practical order:

1. `crun`
2. `conmon`
3. `netavark`
   - This recipe also builds `aardvark-dns`; update the bundled source there.
4. `skopeo`
   - Keep the `container-libs` `common/v*` source aligned with Skopeo's `go.mod`.
   - This package installs the shared `/etc/containers/` config files.
5. `buildah`
6. `podman`

Notes:

- `podman` has runtime dependencies on `conmon`, `netavark`, and `skopeo`, so it
  should be built after those are available.
- `buildah` also uses `netavark` and `skopeo`, so build it after those packages.
- `crun` is independent from the recipe dependency chain, but it is part of the
  practical container runtime stack and is safest to build before testing the
  higher-level tools.
