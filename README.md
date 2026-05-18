# homelab-public-images

Public Docker images for GPU workloads run via [SkyPilot](https://skypilot.readthedocs.io) and [Vast.ai](https://vast.ai).
Build scripts and GitHub Actions workflows only — no secrets, model weights, or private data.

## Images

| Image | Tag | Purpose |
|---|---|---|
| `ghcr.io/oliverrzhu/skylab-flux-blackwell` | `latest` · `sha-<git-sha>` · `YYYYMMDD` | FLUX.2-klein-4B inference on Blackwell GPUs (RTX 5090, RTX PRO 6000) |

Each image is built and scanned on every push to `main`.
Trivy CRITICAL CVEs block publication; HIGH CVEs are reported to the [Security tab](https://github.com/OliverrZhu/homelab-public-images/security/code-scanning).

## Using an image

Images are public — no auth required once the GHCR package visibility is set to Public.

```bash
# Latest build
docker pull ghcr.io/oliverrzhu/skylab-flux-blackwell:latest

# Immutable build pin (preferred for production)
docker pull ghcr.io/oliverrzhu/skylab-flux-blackwell:sha-<git-sha>
```

In a SkyPilot task YAML (private `homelab` repo):
```yaml
resources:
  image_id: docker:ghcr.io/oliverrzhu/skylab-flux-blackwell:latest
```

## Building locally

Requires Docker with BuildKit (or Buildx).

```bash
docker build --platform linux/amd64 \
  -t skylab-flux-blackwell:local \
  images/skylab-flux-blackwell/
```

See each image's own README for available `--build-arg` options and version-bump instructions.

## Repository layout

```
images/
  skylab-flux-blackwell/   # Dockerfile, .dockerignore, README
.github/
  workflows/
    lint.yml               # pre-commit on every push/PR
    reusable-push-image-ghcr.yml
    push-skylab-flux-blackwell-ghcr.yml  # per-image wrapper
  dependabot.yml           # weekly GHA action updates
  CODEOWNERS
  pull_request_template.md
.pre-commit-config.yaml    # hadolint + detect-secrets + yamllint
.hadolint.yaml
.yamllint.yml
LICENSE                    # Apache 2.0
SECURITY.md
```

## Contributing

1. Install tooling: `hadolint` on your `PATH` (e.g. `brew install hadolint` on macOS) and `pip install pre-commit && pre-commit install`
2. Make changes in a branch, open a PR — the template checklist guides dependency bumps
3. CI runs lint (hadolint, yamllint, detect-secrets) and, on merge, builds + scans the image

To add a new image, create `images/<name>/` and copy an existing
`push-*-ghcr.yml` workflow wrapper. Point `image_name`, `context`, and
`dockerfile` at the new image; the reusable workflow handles GHCR publishing,
SBOM generation, and Trivy scanning.

## License

Apache 2.0 — see [LICENSE](LICENSE).
The images bundle third-party packages under their own licenses (PyTorch BSD, transformers Apache 2.0, diffusers Apache 2.0).
