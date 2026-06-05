# Docker stack update order

- `runc`
- `containerd`
- `buildkit`
- `moby`
- `docker`
- `docker-buildx`
- `docker-compose`

## Notes

- `moby` and `docker` should be bumped together (same version)
- `buildkit` is separate from the engine but should be updated before `docker-buildx`
- `conmon`, `buildah`, and other podman packages are a separate stack

## Tips

- To get the git commit for a tag: `git ls-remote <upstream .git> refs/tags/v<version> | awk '{print $1}'`
- Use `refs/tags/v<version>^{}` for annotated tags
- `moby` uses `refs/tags/docker-v<version>`
- The recipes already resolve and embed the commit at build time
