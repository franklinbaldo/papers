"""Train low-rank channel flavorizer on cached Few-NERD multi-scale channels.

Fits low-rank adapters V, U (rank 8) to align the multi-scale semantic channels
with Few-NERD fine entity distinctions before recurrent propagation through
the 8,982 sensory neurons of MaleCNS.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from malecns_wifi.channel_flavorizer import train_flavorizer
from malecns_wifi.fewnerd_cache import load_cache
from malecns_wifi.telemetry import Telemetry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-cache", type=Path, required=True, help="path to byte-cache directory")
    parser.add_argument("--output", type=Path, required=True, help="path to output flavorizer .npz")
    parser.add_argument("--rank", type=int, default=8, help="low-rank dimension")
    parser.add_argument("--epochs", type=int, default=5, help="training epochs")
    parser.add_argument("--learning-rate", type=float, default=0.005, help="learning rate")
    parser.add_argument("--max-sentences", type=int, default=500, help="max training sentences to sample")
    parser.add_argument("--batch-size", type=int, default=512, help="training batch size")
    parser.add_argument("--device", default="cpu", help="device ('cpu' or 'cuda')")
    parser.add_argument("--seed", type=int, default=20260915, help="random seed")
    args = parser.parse_args()

    cache = load_cache(args.token_cache)
    model_names = tuple(cache.manifest.get("encoder_order") or list(cache.encoders))
    semantic_dim = sum(cache.encoders[m].base_dim for m in model_names) * len(cache.scales)

    sentences = cache.sentences
    texts = sentences.column("text").to_pylist()
    fine_lists = sentences.column("fine_label").to_pylist()
    splits = sentences.column("split").to_pylist()

    train_indices = [i for i, s in enumerate(splits) if s == "train"]
    if args.max_sentences and len(train_indices) > args.max_sentences:
        rng = np.random.default_rng(args.seed)
        train_indices = rng.choice(train_indices, size=args.max_sentences, replace=False).tolist()

    print(f"Extracting multi-scale channel features for {len(train_indices)} training sentences...", flush=True)
    all_features = []
    all_labels = []
    for idx in train_indices:
        ch = cache.assemble_channel(model_names, texts[idx])
        labs = np.asarray(fine_lists[idx], dtype=np.int64)
        all_features.append(ch)
        all_labels.append(labs)

    X = np.concatenate(all_features, axis=0)
    y = np.concatenate(all_labels, axis=0)

    # Subsample majority 'O' class to balance training if needed
    entity_mask = y > 0
    o_indices = np.flatnonzero(~entity_mask)
    entity_indices = np.flatnonzero(entity_mask)

    rng = np.random.default_rng(args.seed)
    # Keep all entity tokens, sample 2x 'O' tokens
    n_o = min(len(o_indices), max(len(entity_indices) * 2, 2000))
    if len(o_indices) > n_o:
        sampled_o = rng.choice(o_indices, size=n_o, replace=False)
        selected = np.concatenate([entity_indices, sampled_o])
        rng.shuffle(selected)
        X = X[selected]
        y = y[selected]

    print(f"Training low-rank ChannelFlavorizer (rank={args.rank}, dim={semantic_dim}) on {len(y)} tokens...", flush=True)
    t0 = time.perf_counter()
    flav = train_flavorizer(
        X,
        y,
        semantic_dim=semantic_dim,
        rank=args.rank,
        epochs=args.epochs,
        lr=args.learning_rate,
        batch_size=args.batch_size,
        seed=args.seed,
        device=args.device,
    )
    elapsed = time.perf_counter() - t0
    print(f"Trained in {elapsed:.2f}s. Saving to {args.output}...", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    flav.save(args.output)

    manifest = {
        "schema": "papers/malecns-channel-flavorizer-v1",
        "semantic_dim": semantic_dim,
        "rank": args.rank,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "training_tokens": len(y),
        "elapsed_seconds": elapsed,
        "seed": args.seed,
    }
    args.output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"event": "channel_flavorizer_trained", **manifest}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
