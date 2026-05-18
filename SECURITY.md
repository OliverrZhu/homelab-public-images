# Security Policy

## Scope

This repository publishes **Docker build scripts and GitHub Actions workflows only**.
The images contain an ML runtime (Python, PyTorch, transformers, diffusers) and no
user data, credentials, or model weights.

If you discover a leaked secret or credential in an image layer or in this repository,
that is a **critical** issue — please report it immediately via the channel below.

## Reporting a vulnerability

Open a [GitHub Security Advisory](https://github.com/OliverrZhu/homelab-public-images/security/advisories/new)
(private, visible only to maintainers).

Include:
- Which image or file is affected
- Steps to reproduce / how you found it
- For leaked secrets: the exact string or layer SHA (do **not** paste the actual secret value)

Expected response time: **48 hours** for triage, **7 days** for a fix or mitigation plan.

## Vulnerability scanning

Every image push runs [Trivy](https://github.com/aquasecurity/trivy) automatically:

- **CRITICAL** CVEs → build fails; image is not published until resolved
- **HIGH** CVEs → SARIF results uploaded to the [Security tab](https://github.com/OliverrZhu/homelab-public-images/security/code-scanning)

To scan a local build yourself:
```bash
trivy image ghcr.io/oliverrzhu/skylab-flux-blackwell:latest
```

## Supply chain

| Component | Pin mechanism |
|---|---|
| CUDA base image | Tag (`12.8.1`); optionally pin to `@sha256:<digest>` |
| PyTorch nightly | Image digest (no in-build pin; see [README](images/skylab-flux-blackwell/README.md#bumping-versions)) |
| diffusers | `DIFFUSERS_REF` ARG — default is a full commit SHA in the Dockerfile |
| GitHub Actions | Dependabot weekly PRs |

## What is never included in images

- HuggingFace tokens or any API keys
- SSH keys or cloud credentials
- Model weights or private fine-tune checkpoints
- Any file matched by `.dockerignore`

Human-readable check: `docker history --no-trunc <image>` should contain no tokens, passwords, or file paths outside `/usr/`, `/opt/`, or `/workspace/`.
