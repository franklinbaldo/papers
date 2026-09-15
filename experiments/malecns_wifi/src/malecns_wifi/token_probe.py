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
    *, candidate_C: tuple[float, ...] = (0.03, 0.1, 0.3, 1.0, 3.0), max_iter: int = 200,
    seed: int = 20260915,
) -> tuple[Any, float]:
    from sklearn.linear_model import LogisticRegression

    best_model, best_c, best_acc = None, None, -1.0
    for c in candidate_C:
        model = LogisticRegression(C=c, max_iter=max_iter, random_state=seed)
        model.fit(train_x, train_y)
        acc = float(model.score(val_x, val_y))
        if acc > best_acc:
            best_model, best_c, best_acc = model, c, acc
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
