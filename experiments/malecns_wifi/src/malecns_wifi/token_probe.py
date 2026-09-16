"""Stage C helper: fit a linear probe on frozen readout embeddings, score spans.

The connectome, its input weights and its readout projection are frozen and
never see labels (see ``token_reservoir.py``). The *only* supervised
component in this benchmark is a linear probe from the 256-d per-token
readout to the label space, fit on the official train split and scored on the
official test split -- analogous to the k-NN classifier MTEB fits on top of a
frozen sentence encoder for document classification. Regularisation strength
is selected on the validation split only; test labels never influence probe
fitting, selection, or the connectome itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ProbeResult:
    C: float
    val_accuracy: float
    test_predictions: np.ndarray


def fit_probe(
    train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, val_y: np.ndarray,
    *, candidate_C: tuple[float, ...] = (0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0), max_iter: int = 200,
    seed: int = 20260915, max_train_rows: int | None = 100_000,
) -> tuple[Any, float, float]:
    """Fit a multinomial probe, selecting ``C`` by validation macro-F1, not accuracy.

    Few-NERD's label space is heavily skewed (``O`` is ~80% of bytes across 66
    classes): plain accuracy is maximised by a model that predicts ``O``
    everywhere, which recovers zero entity spans. This was found empirically --
    accuracy-based selection collapsed to all-``O`` predictions (span F1
    exactly 0) even with 4,000 training sentences. ``class_weight='balanced'``
    plus macro-F1 selection lets minority entity types actually influence which
    regularisation strength wins. Selection still uses only train/validation;
    test labels never enter this function.

    ``max_train_rows`` uniformly subsamples the TRAINING rows only (seeded,
    label-blind -- a random row subset, not filtered by label value) before
    fitting, purely to bound memory: LogisticRegression's solver OOM'd fitting
    ~1.6M rows x 1,314 dims (the descending-neuron readout) on a standard
    Colab instance. This mirrors the MTEB classification evaluator's own
    ``samples_per_label`` undersampling convention rather than inventing a new
    one. ``validation``/``test`` are never subsampled -- only prediction
    (cheap) happens on them, not fitting.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score

    if max_train_rows is not None and len(train_x) > max_train_rows:
        keep = np.random.default_rng(seed).choice(len(train_x), size=max_train_rows, replace=False)
        train_x, train_y = train_x[keep], train_y[keep]

    best_model, best_c, best_f1, best_acc = None, None, -1.0, -1.0
    for c in candidate_C:
        model = LogisticRegression(C=c, max_iter=max_iter, random_state=seed, class_weight="balanced")
        model.fit(train_x, train_y)
        val_pred = model.predict(val_x)
        macro_f1 = float(f1_score(val_y, val_pred, average="macro", zero_division=0))
        if macro_f1 > best_f1:
            best_model, best_c, best_f1 = model, c, macro_f1
            best_acc = float(np.mean(val_pred == val_y))
    return best_model, best_c, best_acc


def bio_tags(label_ids: np.ndarray, label_names: list[str]) -> list[str]:
    """Contiguous same-label token runs -> BIO, so seqeval can score entities.

    Few-NERD's own tags are IO (no B-/I- prefix): a run of identical non-`O`
    ids is one entity. This conversion only affects span *bookkeeping* -- it
    changes no label, no token, no prediction.
    """
    tags: list[str] = []
    previous = None
    for label_id in label_ids:
        name = label_names[label_id]
        if name == "O":
            tags.append("O")
        elif name == previous:
            tags.append(f"I-{name}")
        else:
            tags.append(f"B-{name}")
        previous = name if name != "O" else None
    return tags


def span_metrics(
    true_ids: list[np.ndarray], pred_ids: list[np.ndarray], label_names: list[str]
) -> dict[str, Any]:
    """Entity-level micro/macro F1 via seqeval, following the Few-NERD paper's protocol."""
    from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

    true_bio = [bio_tags(seq, label_names) for seq in true_ids]
    pred_bio = [bio_tags(seq, label_names) for seq in pred_ids]
    report = classification_report(true_bio, pred_bio, output_dict=True, zero_division=0)
    return {
        "micro_f1": f1_score(true_bio, pred_bio, average="micro", zero_division=0),
        "macro_f1": f1_score(true_bio, pred_bio, average="macro", zero_division=0),
        "micro_precision": precision_score(true_bio, pred_bio, average="micro", zero_division=0),
        "micro_recall": recall_score(true_bio, pred_bio, average="micro", zero_division=0),
        "per_entity": {k: v for k, v in report.items() if k not in ("micro avg", "macro avg", "weighted avg")},
    }


def token_accuracy(true_ids: np.ndarray, pred_ids: np.ndarray) -> float:
    return float(np.mean(true_ids == pred_ids)) if len(true_ids) else 0.0
