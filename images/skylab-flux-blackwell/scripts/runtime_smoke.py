#!/usr/bin/env python3
"""Import and version checks for skylab-flux-blackwell (matches Dockerfile build smoke).

Use after pulling an image or on a GPU host:

  docker run --rm IMAGE python /opt/skylab/runtime_smoke.py
  docker run --rm --gpus all IMAGE python /opt/skylab/runtime_smoke.py --require-gpu
"""

from __future__ import annotations

import argparse
import sys


def check_imports_and_versions() -> tuple[list[str], dict[str, object]]:
    import accelerate
    import diffusers
    import google.protobuf
    import huggingface_hub
    import sentencepiece
    import torch
    import transformers
    from diffusers import Flux2KleinPipeline

    errors: list[str] = []
    if "cu128" not in torch.__version__.lower():
        errors.append(f"torch wheel must be cu128, got {torch.__version__!r}")
    if torch.version.cuda is None:
        errors.append("torch.version.cuda is None (CPU-only torch wheel?)")
    elif not str(torch.version.cuda).startswith("12.8"):
        errors.append(
            f"torch.version.cuda must be 12.8.x for this image, got {torch.version.cuda!r}"
        )
    if not isinstance(Flux2KleinPipeline, type):
        errors.append("Flux2KleinPipeline is not a class")

    versions: dict[str, object] = {
        "torch": torch.__version__,
        "torch.version.cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "transformers": transformers.__version__,
        "diffusers": diffusers.__version__,
        "accelerate": accelerate.__version__,
        "huggingface_hub": huggingface_hub.__version__,
        "protobuf": google.protobuf.__version__,
        "sentencepiece": getattr(sentencepiece, "__version__", "?"),
    }
    return errors, versions


def report_cuda_devices() -> None:
    import torch

    if not torch.cuda.is_available():
        print("CUDA: not available in this container (no GPU / no nvidia-container-toolkit).")
        return
    n = torch.cuda.device_count()
    print(f"CUDA devices visible to PyTorch: {n}")
    for i in range(n):
        props = torch.cuda.get_device_properties(i)
        cap = f"{props.major}.{props.minor}"
        gib = props.total_memory / (1024**3)
        print(f"  [{i}] {props.name} | capability {cap} | mem_GiB={gib:.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-gpu",
        action="store_true",
        help="Exit with code 1 if torch.cuda.is_available() is False.",
    )
    args = parser.parse_args()

    errors, versions = check_imports_and_versions()
    if errors:
        print("runtime_smoke FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "smoke OK —",
        ", ".join(f"{k}={v}" for k, v in versions.items()),
    )
    report_cuda_devices()

    if args.require_gpu:
        import torch

        if not torch.cuda.is_available():
            print(
                "ERROR: --require-gpu set but torch.cuda.is_available() is False",
                file=sys.stderr,
            )
            raise SystemExit(1)


if __name__ == "__main__":
    main()
