# skylab-flux-blackwell

Public GHCR image for running [FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) on Blackwell GPUs (RTX 5090, RTX PRO 6000 Blackwell) via SkyPilot + Vast.ai.

**Registry:** `ghcr.io/oliverrzhu/skylab-flux-blackwell`

## What's in the image

| Layer | Detail |
|---|---|
| Base | `nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04` (CUDA 12.8, cuDNN 9) |
| Python | 3.11 (system package) |
| PyTorch | nightly `cu128` — includes SM 100/120 (Blackwell) kernels |
| ML libs | `transformers>=4.44`, `accelerate`, `sentencepiece`, `protobuf`, `huggingface_hub` |
| diffusers | pinned git commit (`DIFFUSERS_REF` ARG, default is a tested SHA on `main`) — provides `Flux2KleinPipeline` |

## What is NOT in the image

- HuggingFace tokens or API keys
- Model weights (FLUX.2-klein-4B is downloaded at runtime from the HF Hub into `/workspace/.cache/huggingface`)
- SSH keys or any other credentials
- Local outputs or PNG files
- Anything from `.dockerignore`

**The image is safe to make public.** Anyone who pulls it gets only the ML runtime — no private data.

## Public image safety boundaries

```
SAFE to bake in          NEVER bake in
─────────────────────    ──────────────────────────────
Python packages          HF_TOKEN / secrets of any kind
PyTorch nightly cu128    Model weights (*.safetensors, *.bin)
transformers / diffusers Org-private data or fine-tune checkpoints
CUDA runtime             SSH keys, cloud credentials
```

## Making the GHCR package public

After the first push the package is private by default. To make it public:

1. Go to **github.com/OliverrZhu** → **Packages** → `skylab-flux-blackwell`
2. **Package settings** → **Change visibility** → **Public**

Vast.ai and SkyPilot pull without `imagePullSecrets` only when the package is public.

## Pulling the image (no auth required once public)

```bash
docker pull ghcr.io/oliverrzhu/skylab-flux-blackwell:latest
# Pin to a specific build:
docker pull ghcr.io/oliverrzhu/skylab-flux-blackwell:sha-<git-sha>
```

## Building locally

```bash
# From repo root:
docker build --platform linux/amd64 \
  -t skylab-flux-blackwell:local \
  images/skylab-flux-blackwell/

# Optionally pin the diffusers commit:
docker build --platform linux/amd64 \
  --build-arg DIFFUSERS_REF=<commit-sha> \
  -t skylab-flux-blackwell:local \
  images/skylab-flux-blackwell/
```

The build runs `/opt/skylab/runtime_smoke.py` (same as below). If it fails, the pipeline class may be missing from `DIFFUSERS_REF` or the torch wheel is not cu128 — fix the ref or install spec.

## Runtime smoke (pulled image or GPU host)

The image ships `python /opt/skylab/runtime_smoke.py` — same import and `cu128` / CUDA 12.8 checks as the Dockerfile build. On a machine with NVIDIA Container Toolkit:

```bash
IMAGE=ghcr.io/oliverrzhu/skylab-flux-blackwell:latest

# Optional imports + versions; prints GPU info when CUDA is visible
docker run --rm --gpus all "$IMAGE" python /opt/skylab/runtime_smoke.py

# Fail if PyTorch cannot see a GPU (good right after scheduling on Vast / k8s)
docker run --rm --gpus all "$IMAGE" python /opt/skylab/runtime_smoke.py --require-gpu
```

Without `--gpus all`, the script still validates the Python stack; it exits 0 even when `cuda_available=False`.

## Bumping versions

### PyTorch nightly

The default installs the latest nightly at build time. The image digest is the reproducibility pin; there is no need to hardcode a nightly date in the Dockerfile.

To test a specific nightly date:
```bash
docker build --build-arg \
  TORCH_SPEC="torch==2.7.0.dev20260501+cu128 --pre --index-url https://download.pytorch.org/whl/nightly/cu128" \
  ...
```

### diffusers

Default `DIFFUSERS_REF` in the Dockerfile is a full commit SHA (reproducible builds). To move to newer upstream:

1. Pick a commit on [diffusers `main`](https://github.com/huggingface/diffusers/commits/main) that still exports `Flux2KleinPipeline`.
2. Update the `ARG DIFFUSERS_REF=...` line in `Dockerfile` (or pass `--build-arg DIFFUSERS_REF=<sha>` locally).
3. Rebuild; `runtime_smoke.py` fails fast if the pipeline import breaks.

Quick check for a candidate ref:

```bash
pip install --dry-run "git+https://github.com/huggingface/diffusers.git@<ref>#egg=diffusers"
```

### Base CUDA image

Update the `ARG CUDA_IMAGE` line in the Dockerfile and the equivalent comment in the GHA workflow, then rebuild and push.

To find the current linux/amd64 digest:
```bash
docker pull --platform linux/amd64 nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
docker inspect --format='{{index .RepoDigests 0}}' nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
```

## SkyPilot task integration

The corresponding SkyPilot task in the private `homelab` repo (`modules/skylab/tasks/image/flux-klein-brand.yaml`) references this image as:

```yaml
image_id: docker:ghcr.io/oliverrzhu/skylab-flux-blackwell:latest
```

With this image, the `setup` script no longer downloads torch/transformers/diffusers. Only model weights are streamed at runtime (from the public HF Hub — no token needed for FLUX.2-klein-4B).

## Security

- Vulnerability scanning runs on every push via Trivy (SARIF uploaded to GitHub Security tab).
- SBOM (SPDX JSON) is generated and attached to each GitHub Actions run as a workflow artifact.
- The base image tag is documented; pinning to `@sha256:<digest>` is recommended for production.
- No runtime secrets are required by the GHA workflow beyond the automatic `GITHUB_TOKEN`.
