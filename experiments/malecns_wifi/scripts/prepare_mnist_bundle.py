"""Extract and save the canonical MNIST features bundle for connectome reservoir experiments."""
from __future__ import annotations

import argparse
import io
import urllib.request
from pathlib import Path

import numpy as np

MNIST_URL = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz"


def fetch_mnist_npz() -> dict[str, np.ndarray]:
    print(f"Fetching canonical MNIST from {MNIST_URL}...")
    req = urllib.request.Request(
        MNIST_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    npz = np.load(io.BytesIO(data))
    return {k: npz[k] for k in npz.files}


def prepare_mnist_bundle(
    n_samples: int = 1000,
    n_classes: int = 10,
    seed: int = 42,
    output_path: Path = Path("artifacts/runtime-v1/mnist-1000-features.npz"),
) -> None:
    data = fetch_mnist_npz()
    x_train, y_train = data["x_train"], data["y_train"]
    x_test, y_test = data["x_test"], data["y_test"]

    # Combine train and test to sample from full population
    x_all = np.concatenate([x_train, x_test], axis=0)
    y_all = np.concatenate([y_train, y_test], axis=0)

    # Flatten images to (N, 784) and normalize pixels to [0.0, 1.0]
    x_flat = x_all.reshape(x_all.shape[0], -1).astype(np.float32) / 255.0

    # Compute prototype/centroid embedding for each digit class (0..9)
    prototypes = np.zeros((n_classes, x_flat.shape[1]), dtype=np.float32)
    for c in range(n_classes):
        class_samples = x_flat[y_all == c]
        centroid = class_samples.mean(axis=0)
        norm = np.linalg.norm(centroid)
        prototypes[c] = centroid / max(norm, 1e-12)

    # Stratified balanced sampling across classes
    rng = np.random.default_rng(seed)
    samples_per_class = n_samples // n_classes
    selected_indices = []

    for c in range(n_classes):
        c_indices = np.where(y_all == c)[0]
        chosen = rng.choice(c_indices, size=samples_per_class, replace=False)
        selected_indices.append(chosen)

    # Interleave classes so sequential batches and folds remain balanced
    interleaved = []
    for i in range(samples_per_class):
        for c in range(n_classes):
            interleaved.append(selected_indices[c][i])

    idx = np.array(interleaved)
    x_selected = x_flat[idx]
    y_selected = y_all[idx]

    # One-hot tag masks: (N, 10)
    tag_masks = (y_selected[:, None] == np.arange(n_classes)).astype(np.float32)

    # Groups: each sample is an independent instance with group ID
    groups = np.arange(len(x_selected), dtype=np.int64)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        absolute=x_selected,
        tag_masks=tag_masks,
        groups=groups,
        tag_embeddings=prototypes,
        labels=y_selected,
        unique_docs=groups,
    )
    print(f"Saved MNIST bundle to {output_path}:")
    print(f"  Samples: {x_selected.shape[0]}")
    print(f"  Features: {x_selected.shape[1]}")
    print(f"  Classes: {tag_masks.shape[1]}")
    print(f"  Tag Embeddings: {prototypes.shape}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare canonical MNIST bundle.")
    parser.add_argument("--n-samples", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/mnist-1000-features.npz"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    prepare_mnist_bundle(n_samples=args.n_samples, seed=args.seed, output_path=args.output)


if __name__ == "__main__":
    main()
