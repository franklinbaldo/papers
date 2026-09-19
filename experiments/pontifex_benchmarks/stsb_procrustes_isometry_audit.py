# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "datasets>=3.0",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "scipy>=1.14",
#   "sentence-transformers>=5.0",
# ]
# ///
"""Post-hoc STS-B diagnostic: is Procrustes transporting B, or preserving A?

This experiment was designed after observing the first STS-B transport test result.
It is therefore an exploratory mechanism audit, not a fresh confirmatory benchmark.

The motivating algebra is simple.  For the rectangular Procrustes map W returned by
``fit_procrustes`` when d_A <= d_B, W W^T = I (up to floating-point error).  A pure
map x -> xW is consequently an isometry of A: dot products, norms and cosines are
preserved even if W contains no useful information about B.  High STS score after
such a map is not by itself evidence of cross-space transport.

The audit separates these claims with three endpoints:

1. numerical isometry: verify that pure xW preserves A pair cosines;
2. task retention: STS-B Spearman after the centered/translated map (secondary and
   explicitly post-hoc because this test set has already been inspected);
3. B-specific transport: sentencewise mapped-A/B cosine plus pair-geometry RMSE and
   Spearman against untouched B test embeddings.  These endpoints use no task label
   for fitting or selection.

Controls at each K:
- correctly paired Procrustes;
- shuffled-correspondence Procrustes (same A anchors, same B anchors and means);
- random Stiefel isometries with the same centering/target-mean translation.

Leakage contract:
- map fitting uses only leakage-filtered STS-B train correspondences;
- validation and test sentences are excluded from the anchor pool;
- no validation/test label fits or selects any map or control;
- B test embeddings are evaluation-only diagnostics;
- the control count, seeds and budgets are fixed by CLI/defaults before evaluation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import stsb_transport as st


def rmse(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.asarray(x) - np.asarray(y)) ** 2)))


def point_cosine(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.sum(st.l2norm(x) * st.l2norm(y), axis=1)


def qsummary(xs: list[float]) -> dict[str, float]:
    a = np.asarray(xs, dtype=np.float64)
    return {
        "min": float(np.min(a)),
        "q25": float(np.quantile(a, 0.25)),
        "median": float(np.median(a)),
        "q75": float(np.quantile(a, 0.75)),
        "max": float(np.max(a)),
    }


def transport_metrics(
    mapped_pairs_1: np.ndarray,
    mapped_pairs_2: np.ndarray,
    mapped_unique: np.ndarray,
    b_pairs_1: np.ndarray,
    b_pairs_2: np.ndarray,
    b_unique: np.ndarray,
    gold: np.ndarray,
) -> dict[str, object]:
    mapped_pair_cos = st.cosine_pairs(mapped_pairs_1, mapped_pairs_2)
    b_pair_cos = st.cosine_pairs(b_pairs_1, b_pairs_2)
    task = st.correlations(mapped_pair_cos, gold)
    geom_s = spearmanr(mapped_pair_cos, b_pair_cos).statistic
    aligned = point_cosine(mapped_unique, b_unique)
    return {
        "task": task,
        "b_pair_geometry": {
            "cosine_rmse": rmse(mapped_pair_cos, b_pair_cos),
            "cosine_spearman": float(geom_s),
        },
        "b_point_alignment": {
            "mean_cosine": float(np.mean(aligned)),
            "median_cosine": float(np.median(aligned)),
        },
    }


def random_stiefel(d_a: int, d_b: int, rng: np.random.Generator) -> np.ndarray:
    if d_a > d_b:
        raise ValueError("this audit assumes d_A <= d_B")
    # Q has orthonormal columns in R^(d_B x d_A); W = Q^T therefore W W^T = I.
    g = rng.normal(size=(d_b, d_a))
    q, _ = np.linalg.qr(g, mode="reduced")
    return q.T.astype(np.float32)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", nargs="+", type=int, default=[8, 16, 32, 64, 128, 256])
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--controls", type=int, default=16)
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-stsb-procrustes-isometry-audit.json"),
    )
    args = ap.parse_args()
    if args.controls < 4:
        raise ValueError("use at least four negative-control replicates")

    ds = st.load_dataset(st.DATASET)
    train1, train2, _ = st.split_sentences(ds["train"])
    val1, val2, _ = st.split_sentences(ds["validation"])
    test1, test2, test_gold = st.split_sentences(ds["test"])

    eval_sentence_set = set(val1) | set(val2) | set(test1) | set(test2)
    raw_train_candidates = st.unique_in_order(train1 + train2)
    anchor_candidates = [s for s in raw_train_candidates if s not in eval_sentence_set]
    excluded_exact_overlap = len(raw_train_candidates) - len(anchor_candidates)

    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(anchor_candidates))
    anchor_candidates = [anchor_candidates[i] for i in order]
    budgets = sorted({int(k) for k in args.budgets if 1 < int(k) <= len(anchor_candidates)})
    if not budgets:
        raise RuntimeError("no valid budgets")

    # Match the exact union/order from the first benchmark so its embedding cache is reusable.
    all_texts = st.unique_in_order(
        anchor_candidates[: max(budgets)] + val1 + val2 + test1 + test2
    )
    emb = st.encode_all(all_texts, args.cache)
    idx = emb.lookup()

    test_a1, test_a2 = st.gather(emb.a, idx, test1), st.gather(emb.a, idx, test2)
    test_b1, test_b2 = st.gather(emb.b, idx, test1), st.gather(emb.b, idx, test2)
    test_unique = st.unique_in_order(test1 + test2)
    test_au = st.gather(emb.a, idx, test_unique)
    test_bu = st.gather(emb.b, idx, test_unique)
    a_pair_cos = st.cosine_pairs(test_a1, test_a2)
    b_pair_cos = st.cosine_pairs(test_b1, test_b2)
    a_task = st.correlations(a_pair_cos, test_gold)
    b_task = st.correlations(b_pair_cos, test_gold)

    rows: list[dict[str, object]] = []
    for k in budgets:
        anchors = anchor_candidates[:k]
        a_anchor = st.gather(emb.a, idx, anchors)
        b_anchor = st.gather(emb.b, idx, anchors)

        w = st.fit_procrustes(a_anchor, b_anchor)
        eye = np.eye(w.shape[0], dtype=np.float64)
        wwt_error = float(
            np.linalg.norm(w.astype(np.float64) @ w.astype(np.float64).T - eye, ord="fro")
            / math.sqrt(w.shape[0])
        )

        # Pure isometry endpoint: no centering and no target-space translation.
        pure1 = test_a1 @ w
        pure2 = test_a2 @ w
        pure_cos = st.cosine_pairs(pure1, pure2)
        pure_delta = np.abs(pure_cos - a_pair_cos)

        paired1 = st.apply_centered_map(test_a1, a_anchor, b_anchor, w)
        paired2 = st.apply_centered_map(test_a2, a_anchor, b_anchor, w)
        pairedu = st.apply_centered_map(test_au, a_anchor, b_anchor, w)
        paired_metrics = transport_metrics(
            paired1, paired2, pairedu, test_b1, test_b2, test_bu, test_gold
        )

        shuffled_metrics: list[dict[str, object]] = []
        random_metrics: list[dict[str, object]] = []
        for i in range(args.controls):
            rng_i = np.random.default_rng(args.seed + 100_000 * k + i)

            perm = rng_i.permutation(k)
            w_shuf = st.fit_procrustes(a_anchor, b_anchor[perm])
            sh1 = st.apply_centered_map(test_a1, a_anchor, b_anchor, w_shuf)
            sh2 = st.apply_centered_map(test_a2, a_anchor, b_anchor, w_shuf)
            shu = st.apply_centered_map(test_au, a_anchor, b_anchor, w_shuf)
            shuffled_metrics.append(
                transport_metrics(sh1, sh2, shu, test_b1, test_b2, test_bu, test_gold)
            )

            w_rand = random_stiefel(a_anchor.shape[1], b_anchor.shape[1], rng_i)
            ra1 = st.apply_centered_map(test_a1, a_anchor, b_anchor, w_rand)
            ra2 = st.apply_centered_map(test_a2, a_anchor, b_anchor, w_rand)
            rau = st.apply_centered_map(test_au, a_anchor, b_anchor, w_rand)
            random_metrics.append(
                transport_metrics(ra1, ra2, rau, test_b1, test_b2, test_bu, test_gold)
            )

        def collect(ms: list[dict[str, object]], *path: str) -> list[float]:
            out: list[float] = []
            for m in ms:
                cur: object = m
                for key in path:
                    cur = cur[key]  # type: ignore[index]
                out.append(float(cur))
            return out

        shuffled_summary = {
            "task_spearman": qsummary(collect(shuffled_metrics, "task", "spearman")),
            "b_pair_geometry_spearman": qsummary(
                collect(shuffled_metrics, "b_pair_geometry", "cosine_spearman")
            ),
            "b_pair_geometry_rmse": qsummary(
                collect(shuffled_metrics, "b_pair_geometry", "cosine_rmse")
            ),
            "b_point_alignment_mean_cosine": qsummary(
                collect(shuffled_metrics, "b_point_alignment", "mean_cosine")
            ),
        }
        random_summary = {
            "task_spearman": qsummary(collect(random_metrics, "task", "spearman")),
            "b_pair_geometry_spearman": qsummary(
                collect(random_metrics, "b_pair_geometry", "cosine_spearman")
            ),
            "b_pair_geometry_rmse": qsummary(
                collect(random_metrics, "b_pair_geometry", "cosine_rmse")
            ),
            "b_point_alignment_mean_cosine": qsummary(
                collect(random_metrics, "b_point_alignment", "mean_cosine")
            ),
        }

        paired_geom_s = float(paired_metrics["b_pair_geometry"]["cosine_spearman"])  # type: ignore[index]
        paired_geom_rmse = float(paired_metrics["b_pair_geometry"]["cosine_rmse"])  # type: ignore[index]
        paired_point = float(paired_metrics["b_point_alignment"]["mean_cosine"])  # type: ignore[index]
        rows.append(
            {
                "shared_correspondences_k": k,
                "anchors_sha256": st.sha256_lines(anchors),
                "paired_procrustes": paired_metrics,
                "algebraic_isometry_audit": {
                    "relative_frobenius_WWT_minus_I": wwt_error,
                    "pure_map_max_abs_pair_cosine_change": float(np.max(pure_delta)),
                    "pure_map_mean_abs_pair_cosine_change": float(np.mean(pure_delta)),
                },
                "shuffled_correspondence_controls": shuffled_summary,
                "random_stiefel_controls": random_summary,
                "paired_position_vs_controls": {
                    "paired_b_pair_geometry_spearman_gt_all_shuffled": bool(
                        paired_geom_s
                        > max(collect(shuffled_metrics, "b_pair_geometry", "cosine_spearman"))
                    ),
                    "paired_b_pair_geometry_rmse_lt_all_shuffled": bool(
                        paired_geom_rmse
                        < min(collect(shuffled_metrics, "b_pair_geometry", "cosine_rmse"))
                    ),
                    "paired_b_point_alignment_gt_all_shuffled": bool(
                        paired_point
                        > max(collect(shuffled_metrics, "b_point_alignment", "mean_cosine"))
                    ),
                    "paired_b_pair_geometry_spearman_gt_all_random": bool(
                        paired_geom_s
                        > max(collect(random_metrics, "b_pair_geometry", "cosine_spearman"))
                    ),
                    "paired_b_pair_geometry_rmse_lt_all_random": bool(
                        paired_geom_rmse
                        < min(collect(random_metrics, "b_pair_geometry", "cosine_rmse"))
                    ),
                    "paired_b_point_alignment_gt_all_random": bool(
                        paired_point
                        > max(collect(random_metrics, "b_point_alignment", "mean_cosine"))
                    ),
                },
            }
        )

    payload = {
        "experiment": "Pontifex STS-B Procrustes isometry audit",
        "status": "post-hoc mechanism diagnostic; not a fresh confirmatory benchmark",
        "seed": args.seed,
        "negative_control_replicates_per_family": args.controls,
        "models": {"A": st.MODEL_A, "B": st.MODEL_B},
        "split_contract": {
            "assembly": "benchmark/model choice and this diagnostic were motivated by already-inspected prior STS-B results",
            "student": "leakage-filtered STS-B train sentence correspondences only",
            "validation": "unused by this parameter-free audit",
            "test": "evaluation only; labels appear only in the secondary task-retention diagnostic",
            "test_labels_used_for_any_fit_or_selection": False,
            "b_test_embeddings_used_for_any_fit_or_selection": False,
        },
        "leakage_audit": {
            "raw_unique_train_candidates": len(raw_train_candidates),
            "excluded_exact_overlap_with_validation_or_test": excluded_exact_overlap,
            "eligible_train_candidates": len(anchor_candidates),
            "test_unique_sentences": len(test_unique),
        },
        "reference": {
            "A_only_test": a_task,
            "B_oracle_test": b_task,
            "A_vs_B_pair_geometry_spearman": float(spearmanr(a_pair_cos, b_pair_cos).statistic),
            "A_vs_B_pair_geometry_rmse": rmse(a_pair_cos, b_pair_cos),
        },
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
