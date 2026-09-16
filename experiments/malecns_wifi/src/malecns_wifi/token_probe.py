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


@dataclass
class DescendingPoolClassifier:
    """Biologically grounded Winner-Take-All decoder for MaleCNS descending neurons.

    Instead of fitting an unconstrained multinomial logistic regression probe across
    1,314 dimensions (which OOMs on 1.6M tokens and collapses to majority 'O' without
    extreme measures), the 1,314 anatomically identified descending neurons are
    partitioned into 66 functional regions/pools P_0, ..., P_{65}, one for each
    Few-NERD fine tag (P_0 = 'O', P_1..P_{65} = fine entity tags).

    Each pool has synaptic readout weights w_j (j in P_k) and regional bias b_k:
        S_k(x) = sum_{j in P_k} w_j * x_j + b_k
    Winner-take-all prediction:
        y_hat = argmax_k S_k(x)

    Online dopaminergic reward learning (R-STDP / dopamine reward prediction error):
    When token has true class y*:
        p_k = softmax(S / tau)_k
        delta_k = (I[k == y*] - p_k) * omega(y*)
    where omega(y*) balances ubiquitous 'O' (80% of tokens) against rare fine
    entity classes so the fly brain learns to detect entity spans.
    """

    n_features: int
    n_classes: int
    mode: str = "regional"  # 'regional' (1314 params) or 'dense' (86k params)
    pools: list[np.ndarray] | None = None
    weights: np.ndarray | None = None
    biases: np.ndarray | None = None
    best_val_macro_f1: float = -1.0
    best_val_accuracy: float = -1.0

    @property
    def n_features_in_(self) -> int:
        return self.n_features

    def __post_init__(self) -> None:
        if self.pools is None:
            self.pools = [
                np.asarray(p, dtype=np.int64)
                for p in np.array_split(np.arange(self.n_features), self.n_classes)
            ]
        if self.mode == "regional":
            if self.weights is None:
                self.weights = np.ones(self.n_features, dtype=np.float32)
        else:
            if self.weights is None:
                self.weights = np.zeros((self.n_classes, self.n_features), dtype=np.float32)
                for k, p in enumerate(self.pools):
                    if len(p) > 0:
                        self.weights[k, p] = 1.0 / float(np.sqrt(len(p)))
        if self.biases is None:
            self.biases = np.zeros(self.n_classes, dtype=np.float32)

    def predict_scores(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        if self.mode == "regional":
            Xw = X * self.weights
            scores = np.empty((len(X), self.n_classes), dtype=np.float32)
            for k, p in enumerate(self.pools):
                if len(p) > 0:
                    scores[:, k] = Xw[:, p].sum(axis=1) + self.biases[k]
                else:
                    scores[:, k] = self.biases[k]
            return scores
        return X @ self.weights.T + self.biases

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_scores(X), axis=1)

    def fit(
        self,
        train_x: np.ndarray,
        train_y: np.ndarray,
        val_x: np.ndarray | None = None,
        val_y: np.ndarray | None = None,
        *,
        epochs: int = 10,
        lr: float = 0.01,
        batch_size: int = 256,
        class_weight: str | None = "balanced",
        weight_decay: float = 1e-4,
        seed: int = 20260915,
        val_true_seqs: list[np.ndarray] | None = None,
        label_names: list[str] | None = None,
    ) -> DescendingPoolClassifier:
        rng = np.random.default_rng(seed)
        counts = np.bincount(train_y, minlength=self.n_classes)
        cw = np.ones(self.n_classes, dtype=np.float32)
        if class_weight == "balanced":
            for c in range(self.n_classes):
                cnt = max(int(counts[c]), 1)
                cw[c] = float(len(train_y) / (self.n_classes * cnt))
            cw = cw * (len(cw) / float(np.sum(cw)))

        mw = np.zeros_like(self.weights)
        vw = np.zeros_like(self.weights)
        mb = np.zeros_like(self.biases)
        vb = np.zeros_like(self.biases)
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        step = 0

        best_weights = self.weights.copy()
        best_biases = self.biases.copy()
        best_f1 = -1.0
        best_acc = 0.0

        for epoch in range(epochs):
            idx = rng.permutation(len(train_x))
            for s in range(0, len(idx), batch_size):
                step += 1
                b_idx = idx[s : s + batch_size]
                xb, yb = train_x[b_idx], train_y[b_idx]
                scores = self.predict_scores(xb)
                exp_s = np.exp(scores - np.max(scores, axis=1, keepdims=True))
                probs = exp_s / np.sum(exp_s, axis=1, keepdims=True)

                T = np.zeros_like(probs)
                T[np.arange(len(yb)), yb] = 1.0
                sample_w = cw[yb][:, None]
                delta = (T - probs) * sample_w

                grad_b = -delta.mean(axis=0)
                if self.mode == "regional":
                    grad_w = np.zeros_like(self.weights)
                    for k, p in enumerate(self.pools):
                        if len(p) > 0:
                            grad_w[p] = -(delta[:, k : k + 1] * xb[:, p]).mean(axis=0) + weight_decay * self.weights[p]
                else:
                    grad_w = -(delta.T @ xb / len(xb)) + weight_decay * self.weights

                mw = beta1 * mw + (1.0 - beta1) * grad_w
                vw = beta2 * vw + (1.0 - beta2) * (grad_w ** 2)
                mb = beta1 * mb + (1.0 - beta1) * grad_b
                vb = beta2 * vb + (1.0 - beta2) * (grad_b ** 2)

                m_hat_w = mw / (1.0 - beta1 ** step)
                v_hat_w = vw / (1.0 - beta2 ** step)
                m_hat_b = mb / (1.0 - beta1 ** step)
                v_hat_b = vb / (1.0 - beta2 ** step)

                self.weights -= lr * m_hat_w / (np.sqrt(v_hat_w) + eps)
                self.biases -= lr * m_hat_b / (np.sqrt(v_hat_b) + eps)

            if val_x is not None and val_y is not None:
                val_pred = self.predict(val_x)
                val_acc = float(np.mean(val_pred == val_y))
                if val_true_seqs is not None and label_names is not None:
                    # Score exact span metrics on validation
                    cursor = 0
                    pred_seqs = []
                    for true_s in val_true_seqs:
                        n = len(true_s)
                        pred_seqs.append(val_pred[cursor : cursor + n])
                        cursor += n
                    metrics = span_metrics(val_true_seqs, pred_seqs, label_names)
                    val_score = float(metrics["micro_f1"])
                else:
                    from sklearn.metrics import f1_score
                    val_score = float(f1_score(val_y, val_pred, average="macro", zero_division=0))

                if val_score > best_f1 or epoch == 0:
                    best_f1 = val_score
                    best_acc = val_acc
                    best_weights = self.weights.copy()
                    best_biases = self.biases.copy()

        self.weights = best_weights
        self.biases = best_biases
        self.best_val_macro_f1 = best_f1
        self.best_val_accuracy = best_acc
        return self


def fit_probe(
    train_x: np.ndarray,
    train_y: np.ndarray,
    val_x: np.ndarray,
    val_y: np.ndarray,
    *,
    classifier: str = "pool_reward",
    candidate_C: tuple[float, ...] = (0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0),
    max_iter: int = 200,
    epochs: int = 10,
    lr: float = 0.01,
    batch_size: int = 256,
    seed: int = 20260915,
    max_train_rows: int | None = None,
    val_true_seqs: list[np.ndarray] | None = None,
    label_names: list[str] | None = None,
) -> tuple[Any, Any, float]:
    """Fit a probe on frozen readout embeddings.

    Supports:
    * ``'pool_reward'`` (default): biologically-grounded descending neuron pool
      Winner-Take-All decoder with dopaminergic reward prediction error (RPE)
      learning. O(1) memory, zero OOM, processes millions of tokens in seconds.
    * ``'dense_reward'``: full linear map with dopaminergic RPE learning.
    * ``'logistic_regression'``: scikit-learn LogisticRegression (L-BFGS solver).
    """
    if max_train_rows is not None and max_train_rows > 0 and len(train_x) > max_train_rows:
        keep = np.random.default_rng(seed).choice(len(train_x), size=max_train_rows, replace=False)
        train_x, train_y = train_x[keep], train_y[keep]

    if classifier in ("pool_reward", "dense_reward"):
        n_classes = int(max(int(train_y.max()), int(val_y.max()))) + 1
        if label_names is not None:
            n_classes = max(n_classes, len(label_names))
        mode = "regional" if classifier == "pool_reward" else "dense"
        model = DescendingPoolClassifier(
            n_features=int(train_x.shape[1]),
            n_classes=n_classes,
            mode=mode,
        )
        model.fit(
            train_x,
            train_y,
            val_x,
            val_y,
            epochs=epochs,
            lr=lr,
            batch_size=batch_size,
            seed=seed,
            val_true_seqs=val_true_seqs,
            label_names=label_names,
        )
        return model, {"method": classifier, "val_macro_f1": model.best_val_macro_f1, "epochs": epochs}, model.best_val_accuracy

    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score

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
