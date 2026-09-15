from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from compound_eye_artifacts import write_rgb_png


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frame = np.asarray(np.load(args.frame), dtype=np.float32)
    if frame.ndim != 2:
        raise RuntimeError(f"expected HxW frame, got {frame.shape}")
    pixels = np.rint(np.clip(frame, 0.0, 1.0) * 255.0).astype(np.uint8)
    rgb = np.repeat(pixels[:, :, None], 3, axis=2)
    write_rgb_png(args.output, rgb)


if __name__ == "__main__":
    main()
