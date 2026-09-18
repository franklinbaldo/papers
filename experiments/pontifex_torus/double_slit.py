# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex double-slit experiment: two simultaneous size-1 occlusions.

Operational definition
----------------------
For encoder E and two distinct occlusion centers p,q:

    I_E(p,q) = R_E(p,q) - R_E(p) - R_E(q)

where R_E(p,q) is the response to masking both centers simultaneously.

This is called an "interference term" only operationally. No quantum-mechanical
claim is implied. The experiment asks whether joint perturbation contains
non-additive semantic information and whether that interaction transfers across
semantic spaces.

Controls
--------
1. Raw additivity residual in A and B.
2. Cross-space correlation I_A vs I_B.
3. Held-out-text prediction of B joint response from:
   - A singles only,
   - A singles + pair geometry,
   - A singles + A joint response,
   - A singles + A joint + toroidal pair geometry.
4. Held-out prediction of B interference itself.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from build_field_store import ENCODER_A, ENCODER_B, make_texts, cos_distance


def mask_pair(tokens: list[str], i: int, j: int) -> str:
    out = list(tokens)
    out[i] = "[MASK]"
    out[j] = "[MASK]"
    return " ".join(out)


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def ranks(x):
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    out = np.empty(len(x), dtype=float)
    out[order] = np.arange(len(x), dtype=float)
    return out


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def pair_geometry(p1, p2):
    # Periodic coordinates. Use ordered pair with p1 < p2 in raw sequence.
    t1 = 2.0 * math.pi * p1
    t2 = 2.0 * math.pi * p2
    d = abs(p2 - p1)
    circ = min(d, 1.0 - d)
    mid = ((p1 + p2) / 2.0) % 1.0
    tm = 2.0 * math.pi * mid
    td = 2.0 * math.pi * circ
    return [
        math.sin(t1), math.cos(t1),
        math.sin(t2), math.cos(t2),
        math.sin(tm), math.cos(tm),
        circ,
        math.sin(td), math.cos(td),
    ]


def load_single_responses(path: Path):
    d = np.load(path, allow_pickle=False)
    tid = d["text_id"].astype(int)
    pos = d["pos"].astype(float)
    size = d["size"].astype(int)
    a = d["response_a"].astype(float)
    b = d["response_b"].astype(float)
    ids = np.unique(tid)

    singles = {}
    for text_id in ids:
        mask = (tid == text_id) & (size == 1)
        pp = pos[mask]
        aa = a[mask]
        bb = b[mask]
        order = np.argsort(pp)
        singles[int(text_id)] = [
            (float(pp[k]), float(aa[k]), float(bb[k]))
            for k in order
        ]
    return d, ids, singles


def build_pair_dataset(field_store: Path, max_pairs_per_text: int, seed: int):
    d, ids, singles = load_single_responses(field_store)
    corpus = make_texts(len(ids), 17)

    pair_texts = []
    meta = []
    rng = np.random.default_rng(seed)

    for text_id in ids:
        text_id = int(text_id)
        tokens = corpus[text_id].split()
        nstarts = len(singles[text_id])
        # Dense builder enumerates starts from 0..len(tokens)-2.
        starts = list(range(nstarts))
        pairs = list(itertools.combinations(starts, 2))
        if max_pairs_per_text > 0 and len(pairs) > max_pairs_per_text:
            pick = np.sort(rng.choice(len(pairs), size=max_pairs_per_text, replace=False))
            pairs = [pairs[int(k)] for k in pick]

        for i, j in pairs:
            pair_texts.append(mask_pair(tokens, i, j))
            p1, a1, b1 = singles[text_id][i]
            p2, a2, b2 = singles[text_id][j]
            meta.append((text_id, i, j, p1, p2, a1, a2, b1, b2))

    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    pair_a = model_a.encode(pair_texts, batch_size=128, convert_to_numpy=True)
    pair_b = model_b.encode(pair_texts, batch_size=128, convert_to_numpy=True)

    orig_a_all = d["original_a"].astype(float)
    orig_b_all = d["original_b"].astype(float)
    orig_a = np.stack([orig_a_all[m[0]] for m in meta])
    orig_b = np.stack([orig_b_all[m[0]] for m in meta])

    ra12 = cos_distance(orig_a, pair_a)
    rb12 = cos_distance(orig_b, pair_b)

    rows = []
    for m, a12, b12 in zip(meta, ra12, rb12):
        text_id, i, j, p1, p2, a1, a2, b1, b2 = m
        ia = float(a12 - a1 - a2)
        ib = float(b12 - b1 - b2)
        rows.append({
            "text_id": int(text_id),
            "i": int(i),
            "j": int(j),
            "p1": float(p1),
            "p2": float(p2),
            "a1": float(a1),
            "a2": float(a2),
            "b1": float(b1),
            "b2": float(b2),
            "a12": float(a12),
            "b12": float(b12),
            "ia": ia,
            "ib": ib,
            "circ_sep": float(min(abs(p2-p1), 1.0-abs(p2-p1))),
        })
    return rows


def features(row, kind):
    a1, a2, a12 = row["a1"], row["a2"], row["a12"]
    base = [a1, a2, a1 + a2, a1 * a2]
    geom = pair_geometry(row["p1"], row["p2"])

    if kind == "a_singles":
        return base
    if kind == "a_singles_geom":
        return base + geom
    if kind == "a_joint":
        return base + [a12, row["ia"]]
    if kind == "a_joint_torus":
        return base + [a12, row["ia"]] + geom + [
            a12 * row["circ_sep"],
            row["ia"] * math.cos(2.0 * math.pi * row["circ_sep"]),
        ]
    if kind == "interference_torus":
        return [row["ia"], a1, a2, a1*a2] + geom
    raise KeyError(kind)


def summarize(vals):
    x = np.asarray(vals, dtype=float)
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
        "mean_abs": float(np.mean(np.abs(x))),
    }


def rmse(y, pred):
    return float(mean_squared_error(y, pred) ** 0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--max-pairs-per-text", type=int, default=32)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-double-slit.json"))
    args = ap.parse_args()

    rows = build_pair_dataset(args.field_store, args.max_pairs_per_text, seed=23)
    text_ids = np.asarray(sorted(set(r["text_id"] for r in rows)), dtype=int)

    ia = np.asarray([r["ia"] for r in rows])
    ib = np.asarray([r["ib"] for r in rows])
    sep = np.asarray([r["circ_sep"] for r in rows])

    global_stats = {
        "pairs": int(len(rows)),
        "texts": int(len(text_ids)),
        "A_interference": summarize(ia),
        "B_interference": summarize(ib),
        "I_A_vs_I_B_pearson": pearson(ia, ib),
        "I_A_vs_I_B_spearman": spearman(ia, ib),
        "abs_I_A_vs_separation_pearson": pearson(np.abs(ia), sep),
        "abs_I_B_vs_separation_pearson": pearson(np.abs(ib), sep),
        "B_raw_additive_rmse": rmse(
            np.asarray([r["b12"] for r in rows]),
            np.asarray([r["b1"] + r["b2"] for r in rows]),
        ),
    }

    methods = ["a_singles", "a_singles_geom", "a_joint", "a_joint_torus"]
    records = []

    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        order = text_ids.copy()
        rng.shuffle(order)
        cut = max(2, int(args.train_frac * len(order)))
        tr_ids = set(int(x) for x in order[:cut])
        te_ids = set(int(x) for x in order[cut:])
        tr = [r for r in rows if r["text_id"] in tr_ids]
        te = [r for r in rows if r["text_id"] in te_ids]

        ytr_joint = np.asarray([r["b12"] for r in tr])
        yte_joint = np.asarray([r["b12"] for r in te])
        ytr_i = np.asarray([r["ib"] for r in tr])
        yte_i = np.asarray([r["ib"] for r in te])

        # Cross-space prediction of the B joint response.
        for method in methods:
            xtr = np.asarray([features(r, method) for r in tr])
            xte = np.asarray([features(r, method) for r in te])
            model = Ridge(alpha=1.0).fit(xtr, ytr_joint)
            pred = model.predict(xte)
            records.append({
                "seed": int(seed),
                "task": "predict_B_joint_response",
                "method": method,
                "rmse": rmse(yte_joint, pred),
                "pearson": pearson(yte_joint, pred),
            })

        # Predict the actual non-additive B term from A's non-additive term.
        xtr = np.asarray([features(r, "interference_torus") for r in tr])
        xte = np.asarray([features(r, "interference_torus") for r in te])
        model = Ridge(alpha=1.0).fit(xtr, ytr_i)
        pred = model.predict(xte)
        records.append({
            "seed": int(seed),
            "task": "predict_B_interference",
            "method": "A_interference_plus_torus",
            "rmse": rmse(yte_i, pred),
            "pearson": pearson(yte_i, pred),
        })

        # Zero-interference null for B interaction prediction.
        records.append({
            "seed": int(seed),
            "task": "predict_B_interference",
            "method": "zero_interference_null",
            "rmse": rmse(yte_i, np.zeros_like(yte_i)),
            "pearson": float("nan"),
        })

    summary = {}
    groups = sorted(set((r["task"], r["method"]) for r in records))
    for task, method in groups:
        rs = [r for r in records if r["task"] == task and r["method"] == method]
        rvals = np.asarray([r["rmse"] for r in rs], dtype=float)
        pvals = np.asarray([r["pearson"] for r in rs], dtype=float)
        pvals = pvals[np.isfinite(pvals)]
        summary[f"{task}|{method}"] = {
            "rmse": {
                "mean": float(rvals.mean()),
                "median": float(np.median(rvals)),
                "std": float(rvals.std(ddof=1)) if len(rvals) > 1 else 0.0,
            },
            "pearson": {
                "mean": float(pvals.mean()) if len(pvals) else float("nan"),
                "median": float(np.median(pvals)) if len(pvals) else float("nan"),
            },
        }

    result = {
        "experiment": "Pontifex double-slit simultaneous occlusion",
        "definition": "I_E(p,q)=R_E(p,q)-R_E(p)-R_E(q)",
        "field_store": str(args.field_store),
        "max_pairs_per_text": args.max_pairs_per_text,
        "global_stats": global_stats,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "interference": "non-additive response residual only; no quantum claim",
            "a_joint_gain": "if A joint response improves held-out B joint prediction over A singles, simultaneous occlusion exposes transferable interaction information",
            "torus_gain": "if pair-periodic geometry further improves held-out prediction, pair location/separation matters beyond scalar joint response",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
