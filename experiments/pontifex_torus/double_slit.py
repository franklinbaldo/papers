# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex double-occlusion experiments.

Two related tests are reported.

1. Static simultaneous occlusion
   For encoder E and two distinct centers p,q:

       I_E(p,q) = R_E(p,q) - R_E(p) - R_E(q)

   This asks whether a joint perturbation contains transferable non-additive
   information across semantic spaces.

2. Dynamic toroidal orbit
   Two size-1 occlusions move one raw position per step with fixed circular
   separation delta:

       i(t+1) = (i(t)+1) mod N
       j(t+1) = (j(t)+1) mod N

   Therefore the leading occlusion reappears at the beginning immediately after
   reaching the last valid intervention position. The experiment tests whether
   wrap transitions are unusually discontinuous and whether periodic geometry
   predicts held-out B-space interaction better than a matched non-periodic raw
   coordinate control, especially after the leading occlusion has wrapped.

"Interference" below means only non-additive response residual. No quantum claim is
implied.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from build_field_store import ENCODER_A, ENCODER_B, cos_distance, make_texts


def mask_pair(tokens: list[str], i: int, j: int) -> str:
    if i == j:
        raise ValueError("double occlusion requires distinct centers")
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
    """Nine explicitly periodic pair-coordinate features."""
    t1 = 2.0 * math.pi * p1
    t2 = 2.0 * math.pi * p2
    d = abs(p2 - p1)
    circ = min(d, 1.0 - d)
    mid = ((p1 + p2) / 2.0) % 1.0
    tm = 2.0 * math.pi * mid
    td = 2.0 * math.pi * circ
    return [
        math.sin(t1),
        math.cos(t1),
        math.sin(t2),
        math.cos(t2),
        math.sin(tm),
        math.cos(tm),
        circ,
        math.sin(td),
        math.cos(td),
    ]


def raw_pair_geometry(p1, p2):
    """Nine non-periodic polynomial/raw-coordinate control features."""
    diff = abs(p2 - p1)
    mid = (p1 + p2) / 2.0
    return [
        p1,
        p2,
        p1 * p1,
        p2 * p2,
        p1 * p2,
        diff,
        diff * diff,
        mid,
        mid * mid,
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
            (float(pp[k]), float(aa[k]), float(bb[k])) for k in order
        ]
    return d, ids, singles


def _encode_pair_specs(d, corpus, singles, specs, model_a, model_b):
    pair_texts = []
    meta = []
    for spec in specs:
        text_id = int(spec["text_id"])
        i = int(spec["i"])
        j = int(spec["j"])
        tokens = corpus[text_id].split()
        pair_texts.append(mask_pair(tokens, i, j))
        p1, a1, b1 = singles[text_id][i]
        p2, a2, b2 = singles[text_id][j]
        meta.append((spec, p1, p2, a1, a2, b1, b2))

    pair_a = model_a.encode(pair_texts, batch_size=128, convert_to_numpy=True)
    pair_b = model_b.encode(pair_texts, batch_size=128, convert_to_numpy=True)

    orig_a_all = d["original_a"].astype(float)
    orig_b_all = d["original_b"].astype(float)
    orig_a = np.stack([orig_a_all[int(m[0]["text_id"])] for m in meta])
    orig_b = np.stack([orig_b_all[int(m[0]["text_id"])] for m in meta])

    ra12 = cos_distance(orig_a, pair_a)
    rb12 = cos_distance(orig_b, pair_b)

    rows = []
    for m, a12, b12 in zip(meta, ra12, rb12):
        spec, p1, p2, a1, a2, b1, b2 = m
        ia = float(a12 - a1 - a2)
        ib = float(b12 - b1 - b2)
        row = {
            **spec,
            "text_id": int(spec["text_id"]),
            "i": int(spec["i"]),
            "j": int(spec["j"]),
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
            "circ_sep": float(min(abs(p2 - p1), 1.0 - abs(p2 - p1))),
        }
        rows.append(row)
    return rows


def build_pair_datasets(field_store: Path, max_pairs_per_text: int, seed: int):
    d, ids, singles = load_single_responses(field_store)
    corpus = make_texts(len(ids), 17)
    rng = np.random.default_rng(seed)

    static_specs = []
    orbit_specs = []

    for text_id in ids:
        text_id = int(text_id)
        nstarts = len(singles[text_id])
        starts = list(range(nstarts))

        # Static random unordered pairs preserve the original experiment.
        pairs = list(itertools.combinations(starts, 2))
        if max_pairs_per_text > 0 and len(pairs) > max_pairs_per_text:
            pick = np.sort(
                rng.choice(len(pairs), size=max_pairs_per_text, replace=False)
            )
            pairs = [pairs[int(k)] for k in pick]
        for i, j in pairs:
            static_specs.append({"text_id": text_id, "i": i, "j": j})

        # Dynamic toroidal orbits. For each unique circular separation, advance
        # both centers by +1 and wrap modulo N. The p2/leading occlusion therefore
        # crosses N-1 -> 0 before p1 whenever delta > 0.
        for delta in range(1, nstarts // 2 + 1):
            # When N is even and delta=N/2, the mask state repeats after N/2
            # steps, but keeping the full oriented orbit is intentional: the
            # transition coordinate still makes one complete toroidal lap.
            for t in range(nstarts):
                i = t
                j = (t + delta) % nstarts
                orbit_specs.append(
                    {
                        "text_id": text_id,
                        "i": i,
                        "j": j,
                        "t": t,
                        "nstarts": nstarts,
                        "delta": delta,
                        "delta_phase": float(delta / nstarts),
                        "leading_wrapped": int(j < i),
                    }
                )

    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    static_rows = _encode_pair_specs(
        d, corpus, singles, static_specs, model_a, model_b
    )
    orbit_rows = _encode_pair_specs(
        d, corpus, singles, orbit_specs, model_a, model_b
    )
    return ids, static_rows, orbit_rows


def static_features(row, kind):
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
        return [row["ia"], a1, a2, a1 * a2] + geom
    raise KeyError(kind)


def orbit_features(row, kind):
    a1, a2 = row["a1"], row["a2"]
    base = [
        row["ia"],
        a1,
        a2,
        a1 * a2,
        row["delta_phase"],
    ]
    if kind == "scalar_only":
        return base
    if kind == "raw_geometry":
        return base + raw_pair_geometry(row["p1"], row["p2"])
    if kind == "toroidal_geometry":
        return base + pair_geometry(row["p1"], row["p2"])
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
    if len(y) == 0:
        return float("nan")
    return float(mean_squared_error(y, pred) ** 0.5)


def static_analysis(rows, text_ids, seeds, train_frac):
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

    for seed in seeds:
        rng = np.random.default_rng(seed)
        order = text_ids.copy()
        rng.shuffle(order)
        cut = max(2, int(train_frac * len(order)))
        tr_ids = set(int(x) for x in order[:cut])
        te_ids = set(int(x) for x in order[cut:])
        tr = [r for r in rows if r["text_id"] in tr_ids]
        te = [r for r in rows if r["text_id"] in te_ids]

        ytr_joint = np.asarray([r["b12"] for r in tr])
        yte_joint = np.asarray([r["b12"] for r in te])
        ytr_i = np.asarray([r["ib"] for r in tr])
        yte_i = np.asarray([r["ib"] for r in te])

        for method in methods:
            xtr = np.asarray([static_features(r, method) for r in tr])
            xte = np.asarray([static_features(r, method) for r in te])
            model = Ridge(alpha=1.0).fit(xtr, ytr_joint)
            pred = model.predict(xte)
            records.append(
                {
                    "seed": int(seed),
                    "task": "predict_B_joint_response",
                    "method": method,
                    "rmse": rmse(yte_joint, pred),
                    "pearson": pearson(yte_joint, pred),
                }
            )

        xtr = np.asarray([static_features(r, "interference_torus") for r in tr])
        xte = np.asarray([static_features(r, "interference_torus") for r in te])
        model = Ridge(alpha=1.0).fit(xtr, ytr_i)
        pred = model.predict(xte)
        records.append(
            {
                "seed": int(seed),
                "task": "predict_B_interference",
                "method": "A_interference_plus_torus",
                "rmse": rmse(yte_i, pred),
                "pearson": pearson(yte_i, pred),
            }
        )
        records.append(
            {
                "seed": int(seed),
                "task": "predict_B_interference",
                "method": "zero_interference_null",
                "rmse": rmse(yte_i, np.zeros_like(yte_i)),
                "pearson": float("nan"),
            }
        )

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
    return {"global_stats": global_stats, "records": records, "summary": summary}


def orbit_transition_stats(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["text_id"], r["delta"])].append(r)

    changes = {"A": defaultdict(list), "B": defaultdict(list)}
    per_orbit = []

    for (text_id, delta), group in groups.items():
        group = sorted(group, key=lambda r: r["t"])
        n = len(group)
        if n < 3:
            continue

        orbit_record = {"text_id": int(text_id), "delta": int(delta), "n": n}
        for label, key in (("A", "ia"), ("B", "ib")):
            wrap_vals = []
            nonwrap_vals = []
            leading_wrap_vals = []
            p1_wrap_vals = []
            for idx, cur in enumerate(group):
                nxt = group[(idx + 1) % n]
                change = abs(float(nxt[key]) - float(cur[key]))
                i_wraps = int(nxt["i"]) < int(cur["i"])
                j_wraps = int(nxt["j"]) < int(cur["j"])
                if i_wraps or j_wraps:
                    wrap_vals.append(change)
                    changes[label]["wrap"].append(change)
                else:
                    nonwrap_vals.append(change)
                    changes[label]["nonwrap"].append(change)
                if j_wraps and not i_wraps:
                    leading_wrap_vals.append(change)
                    changes[label]["leading_wrap"].append(change)
                if i_wraps and not j_wraps:
                    p1_wrap_vals.append(change)
                    changes[label]["p1_wrap"].append(change)

            mean_wrap = float(np.mean(wrap_vals)) if wrap_vals else float("nan")
            mean_nonwrap = (
                float(np.mean(nonwrap_vals)) if nonwrap_vals else float("nan")
            )
            orbit_record[f"{label}_wrap_mean_abs_step"] = mean_wrap
            orbit_record[f"{label}_nonwrap_mean_abs_step"] = mean_nonwrap
            orbit_record[f"{label}_wrap_ratio"] = float(
                mean_wrap / max(mean_nonwrap, 1e-12)
            )
            orbit_record[f"{label}_leading_wrap_mean_abs_step"] = (
                float(np.mean(leading_wrap_vals))
                if leading_wrap_vals
                else float("nan")
            )
            orbit_record[f"{label}_p1_wrap_mean_abs_step"] = (
                float(np.mean(p1_wrap_vals)) if p1_wrap_vals else float("nan")
            )
        per_orbit.append(orbit_record)

    summary = {}
    for label in ("A", "B"):
        wrap = np.asarray(changes[label]["wrap"], dtype=float)
        nonwrap = np.asarray(changes[label]["nonwrap"], dtype=float)
        lead = np.asarray(changes[label]["leading_wrap"], dtype=float)
        p1wrap = np.asarray(changes[label]["p1_wrap"], dtype=float)
        ratios = np.asarray(
            [r[f"{label}_wrap_ratio"] for r in per_orbit], dtype=float
        )
        summary[label] = {
            "wrap_abs_step": summarize(wrap),
            "nonwrap_abs_step": summarize(nonwrap),
            "leading_wrap_abs_step": summarize(lead),
            "p1_wrap_abs_step": summarize(p1wrap),
            "pooled_wrap_to_nonwrap_ratio": float(
                np.mean(wrap) / max(np.mean(nonwrap), 1e-12)
            ),
            "per_orbit_wrap_ratio": summarize(ratios),
        }
    return {"summary": summary, "per_orbit": per_orbit}


def orbit_prediction(rows, text_ids, seeds, train_frac):
    methods = ["scalar_only", "raw_geometry", "toroidal_geometry"]
    records = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        order = text_ids.copy()
        rng.shuffle(order)
        cut = max(2, int(train_frac * len(order)))
        tr_ids = set(int(x) for x in order[:cut])
        te_ids = set(int(x) for x in order[cut:])
        tr = [r for r in rows if r["text_id"] in tr_ids]
        te = [r for r in rows if r["text_id"] in te_ids]
        ytr = np.asarray([r["ib"] for r in tr])
        yte = np.asarray([r["ib"] for r in te])
        wrap_mask = np.asarray([bool(r["leading_wrapped"]) for r in te])

        for method in methods:
            xtr = np.asarray([orbit_features(r, method) for r in tr])
            xte = np.asarray([orbit_features(r, method) for r in te])
            model = Ridge(alpha=1.0).fit(xtr, ytr)
            pred = model.predict(xte)
            records.append(
                {
                    "seed": int(seed),
                    "method": method,
                    "rmse_all": rmse(yte, pred),
                    "rmse_leading_wrapped": rmse(yte[wrap_mask], pred[wrap_mask]),
                    "rmse_not_wrapped": rmse(yte[~wrap_mask], pred[~wrap_mask]),
                    "pearson_all": pearson(yte, pred),
                }
            )

    summary = {}
    for method in methods:
        rs = [r for r in records if r["method"] == method]
        summary[method] = {}
        for metric in (
            "rmse_all",
            "rmse_leading_wrapped",
            "rmse_not_wrapped",
            "pearson_all",
        ):
            vals = np.asarray([r[metric] for r in rs], dtype=float)
            vals = vals[np.isfinite(vals)]
            summary[method][metric] = {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            }

    raw = summary["raw_geometry"]
    torus = summary["toroidal_geometry"]
    summary["toroidal_vs_raw"] = {
        "rmse_all_gain": float(raw["rmse_all"]["mean"] - torus["rmse_all"]["mean"]),
        "rmse_leading_wrapped_gain": float(
            raw["rmse_leading_wrapped"]["mean"]
            - torus["rmse_leading_wrapped"]["mean"]
        ),
        "rmse_not_wrapped_gain": float(
            raw["rmse_not_wrapped"]["mean"]
            - torus["rmse_not_wrapped"]["mean"]
        ),
    }
    return {"records": records, "summary": summary}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--max-pairs-per-text", type=int, default=32)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-double-slit.json"))
    args = ap.parse_args()

    text_ids, static_rows, orbit_rows = build_pair_datasets(
        args.field_store, args.max_pairs_per_text, seed=23
    )
    text_ids = np.asarray(sorted(int(x) for x in text_ids), dtype=int)

    static = static_analysis(static_rows, text_ids, args.seeds, args.train_frac)
    transition = orbit_transition_stats(orbit_rows)
    prediction = orbit_prediction(orbit_rows, text_ids, args.seeds, args.train_frac)

    result = {
        "experiment": "Pontifex simultaneous double occlusion and toroidal orbit",
        "definition": "I_E(p,q)=R_E(p,q)-R_E(p)-R_E(q)",
        "field_store": str(args.field_store),
        "max_pairs_per_text": args.max_pairs_per_text,
        "static": static,
        "dynamic_orbit": {
            "rows": int(len(orbit_rows)),
            "texts": int(len(text_ids)),
            "motion": "i(t+1)=(i(t)+1) mod N; j(t+1)=(j(t)+1) mod N",
            "transition_continuity": transition,
            "held_out_prediction": prediction,
            "interpretation_contract": {
                "wrap_continuity": "a wrap/nonwrap step ratio near 1 means coordinate wrap is not unusually discontinuous; a ratio well above 1 is evidence that the imposed circular seam is costly",
                "periodic_geometry": "positive toroidal-vs-raw RMSE gain on held-out texts means explicit periodic coordinates help beyond matched raw-coordinate polynomial features",
                "wrapped_subset": "a larger toroidal gain after the leading occlusion has wrapped is the most direct support for toroidal handling of the boundary",
                "scope": "this tests the periodic intervention substrate, not intrinsic toroidal topology of semantic space",
            },
        },
        "interpretation_contract": {
            "interference": "non-additive response residual only; no quantum claim",
            "static_a_joint_gain": "if A joint response improves held-out B joint prediction over A singles, simultaneous occlusion exposes transferable interaction information",
            "dynamic_wrap": "the leading occlusion must wrap N-1 -> 0 on its next move while the other center continues modulo N",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
