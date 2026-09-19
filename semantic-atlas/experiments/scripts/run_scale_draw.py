from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from semantic_atlas.scale_embeddings import load_corpus, load_matrix, sha256_file
from semantic_atlas.scale_mknn import (
    analytic_null,
    calibrated,
    category_purity,
    exact_topk,
    jackknife_masks,
    mknn,
    permutation_null,
    stratified_gallery,
)


def shuffled_category_expected(categories: list[str]) -> float:
    _, counts = np.unique(np.asarray(categories, dtype=object), return_counts=True)
    probabilities = counts / counts.sum()
    return float(np.sum(probabilities**2))


def run(
    *,
    corpus_path: Path,
    embedding_dir: Path,
    manifest_path: Path,
    draw: int | None,
    output: Path,
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    corpus = load_corpus(corpus_path)
    ids = [str(row["arxiv_id"]) for row in corpus]
    categories = [str(row["primary_category"]) for row in corpus]
    qwen = load_matrix(embedding_dir, "qwen", "normalized")
    minilm = load_matrix(embedding_dir, "minilm", "normalized")
    if len(qwen) != len(corpus) or len(minilm) != len(corpus):
        raise RuntimeError("corpus and embedding row counts differ")

    ks = list(map(int, manifest["knn"]["ks"]))
    max_k = max(ks)
    sizes = list(map(int, manifest["gallery"]["Ns"]))
    seed_base = int(manifest["gallery"]["seed_base"])
    chronological = draw is None
    chronological_order = np.asarray(
        sorted(range(len(corpus)), key=lambda i: (corpus[i]["created"], ids[i])),
        dtype=np.int64,
    )
    rows = []
    for size in sizes:
        if chronological:
            gallery = chronological_order[:size]
            draw_key = -1
        else:
            gallery = stratified_gallery(
                ids, categories, size, draw=int(draw), seed=seed_base
            )
            draw_key = int(draw)
        gallery_ids = [ids[index] for index in gallery]
        gallery_categories = [categories[index] for index in gallery]
        print(json.dumps({"stage": "exact_cross", "draw": draw_key, "N": size}), flush=True)
        q_neighbors = exact_topk(qwen, gallery, k=max_k)
        m_neighbors = exact_topk(minilm, gallery, k=max_k)

        null_count = 10_000 if size <= 10_000 else 1_000
        cross_null = permutation_null(
            q_neighbors,
            m_neighbors,
            ks=ks,
            permutations=null_count,
            seed=seed_base + 1_000_003 * (draw_key + 2) + size,
        )

        anchors, mask_a, mask_b = jackknife_masks(
            gallery_ids,
            draw=draw_key,
            seed=seed_base,
            anchor_fraction=float(manifest["same_observer_ceiling"]["anchor_fraction"]),
            retention=float(manifest["same_observer_ceiling"]["nonanchor_retention"]),
        )
        print(json.dumps({"stage": "exact_jackknife", "draw": draw_key, "N": size}), flush=True)
        q_a = exact_topk(qwen, gallery, k=max_k, queries=anchors, candidate_mask=mask_a)
        q_b = exact_topk(qwen, gallery, k=max_k, queries=anchors, candidate_mask=mask_b)
        m_a = exact_topk(minilm, gallery, k=max_k, queries=anchors, candidate_mask=mask_a)
        m_b = exact_topk(minilm, gallery, k=max_k, queries=anchors, candidate_mask=mask_b)

        category_null = shuffled_category_expected(gallery_categories)
        for k in ks:
            cross_raw = mknn(q_neighbors, m_neighbors, k)
            same_null = analytic_null(size, k, query_count=len(anchors))
            q_raw = mknn(q_a, q_b, k)
            m_raw = mknn(m_a, m_b, k)
            rows.append(
                {
                    "gallery_n": size,
                    "k": k,
                    "draw": draw_key,
                    "gallery_kind": "chronological_prefix" if chronological else "stratified_random",
                    "gallery_ids_sha256": __import__("hashlib").sha256(
                        "\n".join(gallery_ids).encode("utf-8")
                    ).hexdigest(),
                    "cross_model": {
                        "raw_mknn": cross_raw,
                        "calibrated_mknn": calibrated(cross_raw, cross_null[str(k)]["q95"]),
                        "permutation_null": cross_null[str(k)],
                    },
                    "same_observer_gallery_jackknife": {
                        "anchors": len(anchors),
                        "mask_a_candidates": int(mask_a.sum()),
                        "mask_b_candidates": int(mask_b.sum()),
                        "analytic_null": same_null,
                        "qwen": {
                            "raw_mknn": q_raw,
                            "calibrated_mknn": calibrated(
                                q_raw, same_null["q95_independent_query_approx"]
                            ),
                        },
                        "minilm": {
                            "raw_mknn": m_raw,
                            "calibrated_mknn": calibrated(
                                m_raw, same_null["q95_independent_query_approx"]
                            ),
                        },
                    },
                    "category_purity": {
                        "qwen": category_purity(q_neighbors, gallery_categories, k),
                        "minilm": category_purity(m_neighbors, gallery_categories, k),
                        "shuffled_label_expected": category_null,
                    },
                }
            )
        print(json.dumps({"stage": "complete_N", "draw": draw_key, "N": size}), flush=True)

    result = {
        "schema_version": 1,
        "experiment": manifest["experiment"],
        "executed_at": datetime.now(UTC).isoformat(),
        "draw": None if chronological else int(draw),
        "gallery_kind": "chronological_prefix" if chronological else "stratified_random",
        "manifest_sha256": sha256_file(manifest_path),
        "corpus_sha256": sha256_file(corpus_path),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--embedding-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--draw", required=True, help="0-31 or chronological")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    draw = None if args.draw == "chronological" else int(args.draw)
    run(
        corpus_path=args.corpus,
        embedding_dir=args.embedding_dir,
        manifest_path=args.manifest,
        draw=draw,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
