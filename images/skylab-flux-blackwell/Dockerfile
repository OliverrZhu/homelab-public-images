# syntax=docker/dockerfile:1
#
# skylab-flux-blackwell — public GHCR image for FLUX.2-klein-4B on Blackwell GPUs.
#
# Bakes in: CUDA 12.8 + PyTorch nightly cu128 + transformers + diffusers (Flux2KleinPipeline)
# Excludes:  HF tokens, model weights, SSH keys, local caches, credentials of any kind.
#
# Target GPUs: RTX5090 (SM 120), RTXPRO6000WS (SM 120)
# PyTorch index: https://download.pytorch.org/whl/nightly/cu128
#
# ---- Pinning strategy ---------------------------------------------------------
# The image tag (git SHA / date) IS the reproducibility pin — callers lock to a
# digest, not to a specific nightly wheel date.
#
# To pin the base digest, run on a linux/amd64 host:
#   docker pull --platform linux/amd64 nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
#   docker inspect --format='{{index .RepoDigests 0}}' nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
# Then append @sha256:<digest> to the FROM line and update BASE_IMAGE_DIGEST in
# the GHA workflow for documentation parity.
# -------------------------------------------------------------------------------

ARG CUDA_IMAGE=nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
FROM ${CUDA_IMAGE}

# Propagate after FROM so ARG is visible to RUN steps below.
ARG CUDA_IMAGE

LABEL org.opencontainers.image.title="skylab-flux-blackwell"
LABEL org.opencontainers.image.description="PyTorch nightly cu128 + transformers + diffusers for FLUX.2-klein-4B on Blackwell GPUs"
LABEL org.opencontainers.image.source="https://github.com/OliverrZhu/homelab-public-images"
LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Point HF Hub cache to a stable path; Vast mounts /workspace or /root typically.
ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface

# --- System dependencies -------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python / python3
RUN update-alternatives --install /usr/bin/python  python  /usr/bin/python3.11 1 \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Upgrade pip once; all subsequent pip calls are no-cache to keep layers lean.
RUN python -m pip install --no-cache-dir --upgrade pip

# --- PyTorch nightly cu128 -----------------------------------------------------
# Nightly wheels include SM 100 / SM 120 (Blackwell) kernels absent in the
# stable 2.6+cu124 release. We omit torchvision/torchaudio — the inference
# workload does not need them and they pin an incompatible torch version.
#
# ARG lets callers override the install spec at build time, e.g.:
#   docker build --build-arg TORCH_SPEC="torch==2.7.0.dev20260501+cu128" ...
ARG TORCH_SPEC="torch --pre --index-url https://download.pytorch.org/whl/nightly/cu128"
# hadolint ignore=SC2086 -- TORCH_SPEC is intentionally word-split (multi-arg pip spec)
RUN pip install --no-cache-dir ${TORCH_SPEC}

# --- Core ML libraries ---------------------------------------------------------
ARG TRANSFORMERS_VERSION=">=4.44"
RUN pip install --no-cache-dir \
    "transformers${TRANSFORMERS_VERSION}" \
    accelerate \
    sentencepiece \
    protobuf \
    huggingface_hub

# --- diffusers (pinned git ref) ------------------------------------------------
# Flux2KleinPipeline: default is a full commit SHA so CI/local builds are
# reproducible. Override with --build-arg DIFFUSERS_REF=main for experiments.
# Bump: see images/skylab-flux-blackwell/README.md (diffusers).
ARG DIFFUSERS_REF=907c0c2c76e7a24a22e3280ac40f7f2f800a4b01
RUN pip install --no-cache-dir "git+https://github.com/huggingface/diffusers.git@${DIFFUSERS_REF}"

# --- Smoke-check (import-only; no GPU required at build time) -----------------
# Same logic as scripts/runtime_smoke.py (baked at /opt/skylab/ for post-pull checks).
COPY scripts/runtime_smoke.py /opt/skylab/runtime_smoke.py
RUN python /opt/skylab/runtime_smoke.py

# --- Runtime defaults ----------------------------------------------------------
WORKDIR /workspace
# No ENTRYPOINT — SkyPilot / Vast manage the workload lifecycle.
