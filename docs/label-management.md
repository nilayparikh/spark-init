# GHCR Label Management

This document describes how OCI labels, tags, and retention are managed for containers published to `ghcr.io/nilayparikh/`.

## Image Registry

All images are published to **GitHub Container Registry (GHCR)** under the `nilayparikh` organization:

| Image | GHCR Repository |
|-------|-----------------|
| `llama-cpp-dgx` | `ghcr.io/nilayparikh/llama-cpp-dgx` |
| `claude-code` | `ghcr.io/nilayparikh/claude-code` |

Authentication is handled automatically by GHA via `secrets.GITHUB_TOKEN` with `packages: write` permission.

## OCI Standard Labels

Every image carries the full set of [OCI image-spec annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md).
These are injected by the CI workflows via `docker/metadata-action` and also baked directly into each Dockerfile as fallback defaults.

| Label | Source | Purpose |
|-------|--------|---------|
| `org.opencontainers.image.title` | Workflow | Short name of the image |
| `org.opencontainers.image.description` | Workflow | Single-line purpose statement |
| `org.opencontainers.image.url` | Workflow | Project homepage |
| `org.opencontainers.image.source` | Workflow | GitHub source repo |
| `org.opencontainers.image.licenses` | Static | MIT |
| `org.opencontainers.image.vendor` | Static | Nilay Parikh |
| `org.opencontainers.image.authors` | Static | Maintainer contact |
| `org.opencontainers.image.version` | Workflow | Git ref name or semver tag |
| `org.opencontainers.image.revision` | Workflow | Full git commit SHA |
| `org.opencontainers.image.created` | Workflow | Build timestamp |

These labels are visible in the GHCR web UI under "Image Details" and are queryable via the `gh` CLI:

```bash
gh api /users/nilayparikh/packages/container/llama-cpp-dgx/versions
```

## Tag Strategy

Tags are generated deterministically by `docker/metadata-action` using these rules:

| Tag Pattern | When | Example |
|-------------|------|---------|
| `latest` | Push to `main` | `ghcr.io/nilayparikh/llama-cpp-dgx:latest` |
| `sha-<abbrev>` | Every push | `ghcr.io/nilayparikh/llama-cpp-dgx:sha-a1b2c3d` |
| `<branch>` | Push to named branch | `ghcr.io/nilayparikh/llama-cpp-dgx:feature-x` |
| `<tag>` | Push with git tag | `ghcr.io/nilayparikh/llama-cpp-dgx:v1.0.0` |
| `<major>.<minor>` | Semver git tag | `ghcr.io/nilayparikh/llama-cpp-dgx:1.0` |
| `<version>` | Semver git tag | `ghcr.io/nilayparikh/llama-cpp-dgx:1.0.0` |

### `llama-cpp-dgx` special tags

Since the image is versioned by `LLAMA_CPP_TAG` and CUDA version, CI also tags with the CUDA + build tag combo baked into the Docker image itself: `cuda13.1.2-<llama_cpp_tag>`.

### `claude-code` special tags

Tagged on release cadence: `v<major>.<minor>.<patch>`.

## Retention Policy

GHCR [retention defaults](https://docs.github.com/en/packages/guides/about-github-container-registry) apply:

- **Unused tags** are never auto-deleted (no age-based cleanup by default).
- **Free accounts**: there is no enforced storage limit for public packages.
- **Organization limits**: GB cap applies; monitor usage under `https://github.com/orgs/<org>/packages`.

### Recommended pruning

To keep the registry clean, run periodically (or as a scheduled GHA workflow):

```bash
# Delete all tags except 'latest' and semver tags, for images older than 90 days
gh api --paginate /users/nilayparikh/packages/container/llama-cpp-dgx/versions \
  --jq '.[] | select(.metadata.container.tags | any(. == "latest" or test("^v?[0-9]+\\.[0-9]+")) | not) | .id' \
  | xargs -I{} gh api -X DELETE /users/nilayparikh/packages/container/llama-cpp-dgx/versions/{}
```

Add this as a scheduled workflow: `.github/workflows/ghcr-cleanup.yml`.

## Adding a New Image

To add a new Docker image to this registry:

1. Create `docker/<image-name>/Dockerfile` with inline OCI labels
2. Create `.github/workflows/docker-build-<image-name>.yml` using the template below
3. Update `docker/README.md` with the new entry
4. Update `CLAUDE.md` file map

### Workflow Template

```yaml
name: Docker Build - <image-name>

on:
  push:
    branches: [main]
    tags: ["v*"]
    paths:
      - "docker/<image-name>/**"
      - ".github/workflows/docker-build-<image-name>.yml"
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository_owner }}/<image-name>

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
            type=sha,prefix=
            type=ref,event=tag
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
          labels: |
            org.opencontainers.image.title=<image-name>
            org.opencontainers.image.description=<short description>
            org.opencontainers.image.url=https://github.com/${{ github.repository }}
            org.opencontainers.image.source=https://github.com/${{ github.repository }}
            org.opencontainers.image.licenses=MIT
            org.opencontainers.image.vendor=Nilay Parikh
            org.opencontainers.image.authors=Nilay Parikh <nilay.parikh@gmail.com>
            org.opencontainers.image.version=${{ github.ref_name }}
            org.opencontainers.image.revision=${{ github.sha }}

      - uses: docker/build-push-action@v6
        with:
          context: docker/<image-name>
          file: docker/<image-name>/Dockerfile
          platforms: linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Best Practices

1. **Never override `latest` manually** — it's managed by CI on every `main` push.
2. **Use git tags for releases** — `git tag v1.0.0 && git push origin v1.0.0` triggers a build with full semver tags.
3. **Keep the Dockerfile in sync with CI** — inline labels in the Dockerfile are fallback defaults; CI metadata-action overrides them at build time.
4. **Monitor GHCR storage** — visit `https://github.com/orgs/nilayparikh/packages` to check usage.
5. **Add provenance attestations** — for supply-chain security, append `provenance: true` and `sbom: true` to `docker/build-push-action` inputs.
