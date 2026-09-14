"""Document-level outcome classification with the whole brain as a frozen reservoir.

The whole compiled operator reads a judicial decision byte by byte; only a ridge
readout over the descending neurons is fitted. Nothing else is trained -- no
epochs, no checkpoint selection, no early stopping -- so there is nothing to
select on and the comparison against the two nulls is the entire result.

Input and readout are anchored by cell type, not by degree: bytes enter through
the sensory populations and the readout pools the descending neurons.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from .characterize import degree_preserving_null, random_esn, spectral_radius

# Outcome classes. Appeals speak of provimento, first-instance rulings of
# procedencia; both collapse onto the same three-way outcome.
FAVOURABLE, UNFAVOURABLE, PARTIAL = "favourable", "unfavourable", "partial"
CLASSES = (FAVOURABLE, UNFAVOURABLE, PARTIAL)

# Ordered: the first pattern that matches wins, so the more specific form has to
# come first. Two orderings are load-bearing and were wrong in the first draft:
#
#   * "parcial" precedes the bare forms it contains, or every partial outcome
#     reads as a full one.
#   * extinction comes *last* and only in its "sem resolucao do merito" form.
#     "JULGO PROCEDENTE o pedido, extinguindo o feito nos termos do art. 487, I"
#     is the standard wording of a merits judgment; a bare /extin(to|gu)/ rule
#     placed early labels it a procedural dismissal, which is the opposite
#     outcome. Art. 485 is the dismissal; art. 487 is the ruling.
WEAK_LABEL_RULES: tuple[tuple[str, str], ...] = (
    (PARTIAL, r"parcial(?:mente)?\s+(?:proced|provid|acolh|defer)"),
    (PARTIAL, r"(?:d[oê]u?|dar|dando)\s+parcial\s+provimento"),
    (PARTIAL, r"proced[êe]ncia\s+parcial"),
    (UNFAVOURABLE, r"improceden"),
    (FAVOURABLE, r"julgo\s+proceden"),
    (UNFAVOURABLE, r"n[ãa]o\s+prov(?:ido|imento|eu)"),
    (UNFAVOURABLE, r"neg(?:o|ar|ou|am|a-se)\s+(?:\w+\s+){0,3}provimento"),
    (UNFAVOURABLE, r"n[ãa]o\s+conhec"),
    (FAVOURABLE, r"\bproceden"),
    (FAVOURABLE, r"(?:d[oê]u?|dar|dado|dando)\s+provimento"),
    (FAVOURABLE, r"recurso\s+provido"),
    (FAVOURABLE, r"acolh(?:o|i|e|id)"),
    (FAVOURABLE, r"defiro\s+(?:o\s+)?(?:pedido|requerimento)"),
    (UNFAVOURABLE, r"indefiro"),
    (UNFAVOURABLE, r"extin\w*\s+(?:o\s+)?(?:feito|processo|a\s+a[çc][ãa]o)?\s*,?\s*sem\s+"
     r"(?:resolu|julgamento|an[áa]lise|aprecia)"),
    (UNFAVOURABLE, r"art(?:igo)?\.?\s*485"),
    # Bare "julgo extinto o processo" appears as a resultado span in the hand
    # annotation. It is genuinely ambiguous between art. 485 and art. 487, so it
    # sits last: any explicit merits wording earlier in the list wins over it.
    (UNFAVOURABLE, r"julgo\s+extint"),
)
_COMPILED_RULES = tuple((label, re.compile(pattern)) for label, pattern in WEAK_LABEL_RULES)

PAD_BYTE = 0


@dataclass
class Document:
    doc_id: str
    text: str
    gold: str | None
    weak: str | None
    resultado_spans: tuple[tuple[int, int], ...] = ()

    @property
    def label(self) -> str | None:
        return self.gold if self.gold is not None else self.weak


def classify_text(text: str) -> str | None:
    """Weak outcome label from the dispositivo wording; ``None`` when nothing matches.

    Rule order carries the meaning: the most specific wording that appears anywhere
    in the document wins, regardless of where it appears.

    A "read the last cue instead, because the dispositivo is at the end" variant
    was tried and measured worse on the TJRO/TJBA/TJRJ/TJMG/TJSP benchmark (0.64
    vs 0.70 agreement on sentencas), so it is not used: once the rules are ordered
    by specificity, a late incidental mention does more damage than an early quote
    of somebody else's outcome.
    """
    lowered = text.lower()
    for label, pattern in _COMPILED_RULES:
        if pattern.search(lowered):
            return label
    return None


def load_corpus(path: Path, *, mask_resultado: bool = True) -> list[Document]:
    """Read one segmenter-split JSONL file into documents.

    When the file carries hand-annotated ``resultado`` spans they become the gold
    label. ``mask_resultado`` then blanks those spans in the text, because the
    outcome phrase is quoted verbatim in the document: left in place, every model
    -- including a character n-gram -- reads the answer off the page and the task
    measures nothing. Masked, the outcome has to be inferred from the report and
    the reasoning, which is the task worth running a reservoir on.
    """
    documents: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        text = record["text"]
        spans = tuple(
            (int(span["start"]), int(span["end"]))
            for span in record.get("label", [])
            if span.get("category") == "resultado"
        )
        gold = classify_text(" ".join(text[start:end] for start, end in spans)) if spans else None
        if mask_resultado and spans:
            characters = list(text)
            for start, end in spans:
                characters[start:end] = " " * (end - start)
            text = "".join(characters)
        documents.append(
            Document(
                doc_id=record.get("info", {}).get("doc_id", f"doc{len(documents)}"),
                text=text,
                gold=gold,
                weak=classify_text(text),
                resultado_spans=spans,
            )
        )
    return documents


def label_noise(documents: list[Document]) -> dict:
    """Agreement between the regex weak label and the hand-annotated gold label."""
    paired = [d for d in documents if d.gold is not None]
    matched = sum(1 for d in paired if d.weak == d.gold)
    missing = sum(1 for d in paired if d.weak is None)
    return {
        "gold_documents": len(paired),
        "weak_agrees_with_gold": matched,
        "weak_accuracy": matched / len(paired) if paired else 0.0,
        "weak_label_missing": missing,
        "note": "measured on masked text, so it reflects the weak labeller without the dispositivo",
    }


# --- populations and operators ---------------------------------------------


@dataclass(frozen=True)
class Populations:
    input_indices: np.ndarray
    readout_indices: np.ndarray
    input_selector: tuple[str, ...]
    readout_selector: tuple[str, ...]


def select_populations(
    superclass: np.ndarray,
    *,
    input_selector: tuple[str, ...] = ("cb_sensory", "ol_sensory"),
    readout_selector: tuple[str, ...] = ("descending_neuron",),
) -> Populations:
    """Input and readout neuron indices chosen by annotated cell type."""
    inputs = np.flatnonzero(np.isin(superclass, input_selector))
    readout = np.flatnonzero(np.isin(superclass, readout_selector))
    if inputs.size == 0 or readout.size == 0:
        raise ValueError(
            f"empty population: {inputs.size} input, {readout.size} readout neurons; "
            f"available superclasses include {sorted(set(superclass.tolist()))[:10]}"
        )
    return Populations(inputs, readout, input_selector, readout_selector)


def iter_operators(
    matrix: sp.csr_matrix,
    *,
    seed: int,
    target_radius: float = 0.95,
    radius: float | None = None,
):
    """Yield the real operator and both nulls, one at a time, each at ``target_radius``.

    A generator rather than a dict on purpose: three 10M-edge operators plus the
    source matrix do not comfortably coexist in memory, and only one is needed at
    a time. Each null is rescaled by *its own* spectral radius, not by the real
    one, so that a difference in dynamic range cannot be mistaken for a difference
    in wiring.
    """
    if radius is None:
        radius = spectral_radius(matrix, seed=seed)["estimate"]

    def make(name: str):
        if name == "malecns":
            return matrix, radius, {}
        if name == "degree_null":
            null, stats = degree_preserving_null(matrix, seed=seed + 101)
            return null, spectral_radius(null, seed=seed)["estimate"], stats
        esn, stats = random_esn(matrix, seed=seed + 202)
        return esn, spectral_radius(esn, seed=seed)["estimate"], stats

    for name in ("malecns", "degree_null", "random_esn"):
        candidate, own, stats = make(name)
        scaled = sp.csr_matrix(
            (
                (candidate.data * np.float32(target_radius / own)).astype(np.float32),
                candidate.indices,
                candidate.indptr,
            ),
            shape=candidate.shape,
        )
        del candidate
        yield name, scaled, {"spectral_radius": own, "target_radius": target_radius, **stats}
        del scaled


# --- reservoir pass ---------------------------------------------------------


@dataclass(frozen=True)
class ReservoirSpec:
    leak: float = 0.4
    embedding_dim: int = 64
    input_scale: float = 1.0
    batch_size: int = 64
    max_bytes: int = 0  # 0 = whole document
    seed: int = 0


def encode(documents: list[Document], spec: ReservoirSpec) -> tuple[np.ndarray, np.ndarray]:
    """Right-padded byte matrix plus true lengths.

    Truncation keeps the *tail* of a document: the dispositivo sits at the end,
    so cutting from the front would remove the evidence and cutting from the back
    would remove it too -- the tail is the half worth keeping.
    """
    encoded = []
    for document in documents:
        raw = document.text.encode("utf-8")
        if spec.max_bytes and len(raw) > spec.max_bytes:
            raw = raw[-spec.max_bytes :]
        encoded.append(np.frombuffer(raw, dtype=np.uint8))
    lengths = np.asarray([array.size for array in encoded], dtype=np.int64)
    width = int(lengths.max())
    batch = np.full((len(encoded), width), PAD_BYTE, dtype=np.uint8)
    for row, array in enumerate(encoded):
        batch[row, : array.size] = array
    return batch, lengths


def reservoir_features(
    operator: sp.csr_matrix,
    byte_batch: np.ndarray,
    lengths: np.ndarray,
    populations: Populations,
    embedding: np.ndarray,
    projection: np.ndarray,
    spec: ReservoirSpec,
) -> tuple[np.ndarray, dict]:
    """Run one batch of documents and pool the readout population.

    Returns ``[final_state, temporal_mean]`` over the readout neurons. A document
    that has ended stops updating, so its final state is the state at its own last
    byte rather than at the end of the longest document in the batch.
    """
    n = operator.shape[0]
    count, width = byte_batch.shape
    readout = populations.readout_indices
    inputs = populations.input_indices

    state = np.zeros((n, count), dtype=np.float32)
    accumulated = np.zeros((readout.size, count), dtype=np.float64)
    final = np.zeros((readout.size, count), dtype=np.float32)
    # Buffers live outside the loop: at 165k x batch these are megabytes per step
    # and reallocating them for every byte is what makes the pass swap.
    drive = np.zeros((n, count), dtype=np.float32)
    decayed = np.empty((n, count), dtype=np.float32)
    recurrent_energy = 0.0
    input_energy = 0.0

    for step in range(width):
        active = lengths > step
        if not active.any():
            break
        drive[inputs] = projection @ embedding[byte_batch[:, step]].T
        pre = operator @ state
        recurrent_energy += float(np.mean(pre[:, active] ** 2))
        input_energy += float(np.mean(drive[:, active] ** 2))
        pre += drive
        np.tanh(pre, out=pre)
        pre *= spec.leak
        np.multiply(state, np.float32(1.0 - spec.leak), out=decayed)
        pre += decayed
        state[:, active] = pre[:, active]

        probed = state[readout]
        accumulated[:, active] += probed[:, active]
        ending = lengths == step + 1
        if ending.any():
            final[:, ending] = probed[:, ending]

    pooled_mean = (accumulated / np.maximum(lengths, 1)[None, :]).astype(np.float32)
    features = np.vstack([final, pooled_mean]).T
    steps = max(int(width), 1)
    diagnostics = {
        "recurrent_drive_rms": float(np.sqrt(recurrent_energy / steps)),
        "input_drive_rms": float(np.sqrt(input_energy / steps)),
        "saturated_fraction": float(np.mean(np.abs(final) > 0.99)),
    }
    diagnostics["recurrent_to_input_ratio"] = diagnostics["recurrent_drive_rms"] / max(
        diagnostics["input_drive_rms"], 1e-12
    )
    return features, diagnostics


def run_operator(
    operator: sp.csr_matrix,
    documents: list[Document],
    populations: Populations,
    embedding: np.ndarray,
    projection: np.ndarray,
    spec: ReservoirSpec,
) -> tuple[np.ndarray, dict]:
    """Features for every document, in batches, with pooled diagnostics."""
    blocks: list[np.ndarray] = []
    diagnostics: list[dict] = []
    for start in range(0, len(documents), spec.batch_size):
        chunk = documents[start : start + spec.batch_size]
        byte_batch, lengths = encode(chunk, spec)
        features, stats = reservoir_features(
            operator, byte_batch, lengths, populations, embedding, projection, spec
        )
        blocks.append(features)
        diagnostics.append(stats)
    merged = {
        key: float(np.mean([d[key] for d in diagnostics]))
        for key in ("recurrent_drive_rms", "input_drive_rms", "recurrent_to_input_ratio",
                    "saturated_fraction")
    }
    return np.vstack(blocks), merged


# --- readout ----------------------------------------------------------------


def ridge_fit(features: np.ndarray, targets: np.ndarray, penalty: float) -> np.ndarray:
    """Ridge in whichever form is cheaper for the shape at hand."""
    samples, dimensions = features.shape
    design = np.hstack([features, np.ones((samples, 1))]).astype(np.float64)
    if dimensions + 1 <= samples:
        gram = design.T @ design
        scale = penalty * float(np.trace(gram)) / gram.shape[0]
        return np.linalg.solve(gram + scale * np.eye(gram.shape[0]), design.T @ targets)
    gram = design @ design.T
    scale = penalty * float(np.trace(gram)) / gram.shape[0]
    return design.T @ np.linalg.solve(gram + scale * np.eye(samples), targets)


def macro_f1(true: np.ndarray, predicted: np.ndarray, classes: tuple[str, ...]) -> dict:
    """Macro-F1 plus the per-class counts behind it."""
    scores, per_class = [], {}
    for index, name in enumerate(classes):
        tp = int(np.sum((predicted == index) & (true == index)))
        fp = int(np.sum((predicted == index) & (true != index)))
        fn = int(np.sum((predicted != index) & (true == index)))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        scores.append(f1)
        per_class[name] = {"tp": tp, "fp": fp, "fn": fn, "f1": f1, "support": tp + fn}
    return {
        "macro_f1": float(np.mean(scores)),
        "accuracy": float(np.mean(true == predicted)),
        "per_class": per_class,
    }


def char_ngram_baseline(
    train: list[Document], evaluate: list[Document], *, penalty: float, orders: tuple[int, ...]
) -> dict:
    """Hashed character n-grams plus a ridge readout -- the honest text baseline."""
    buckets = 2**15

    def featurise(documents: list[Document]) -> np.ndarray:
        matrix = np.zeros((len(documents), buckets), dtype=np.float32)
        for row, document in enumerate(documents):
            lowered = document.text.lower()
            for order in orders:
                for position in range(len(lowered) - order + 1):
                    matrix[row, hash(lowered[position : position + order]) % buckets] += 1.0
            norm = np.linalg.norm(matrix[row])
            if norm > 0:
                matrix[row] /= norm
        return matrix

    x_train, x_eval = featurise(train), featurise(evaluate)
    y_train = one_hot([d.label for d in train])
    weights = ridge_fit(x_train, y_train, penalty)
    predictions = np.hstack([x_eval, np.ones((len(evaluate), 1))]) @ weights
    truth = np.asarray([CLASSES.index(d.label) for d in evaluate])
    return macro_f1(truth, predictions.argmax(axis=1), CLASSES)


def one_hot(labels: list[str | None]) -> np.ndarray:
    matrix = np.zeros((len(labels), len(CLASSES)), dtype=np.float64)
    for row, label in enumerate(labels):
        matrix[row, CLASSES.index(label)] = 1.0
    return matrix


# --- experiment -------------------------------------------------------------


@dataclass(frozen=True)
class TaggerSpec:
    seeds: tuple[int, ...] = tuple(range(10))
    ridge: float = 1e-3
    target_radius: float = 0.95
    ngram_orders: tuple[int, ...] = (3, 4, 5)
    reservoir: ReservoirSpec = field(default_factory=ReservoirSpec)


def run_experiment(
    graph_path: Path,
    train: list[Document],
    evaluate: list[Document],
    spec: TaggerSpec,
) -> dict:
    """Fit a ridge readout per operator per seed and score every one on held-out data."""
    archive = np.load(graph_path, allow_pickle=False)
    shape = tuple(int(x) for x in archive["shape"])
    matrix = sp.csr_matrix(
        (archive["data"], archive["indices"], archive["indptr"]), shape=shape, dtype=np.float32
    )
    populations = select_populations(archive["superclass"])

    usable_train = [d for d in train if d.label in CLASSES]
    usable_eval = [d for d in evaluate if d.label in CLASSES]
    if not usable_train or not usable_eval:
        raise ValueError("no labelled documents on one side of the split")

    y_train = one_hot([d.label for d in usable_train])
    truth = np.asarray([CLASSES.index(d.label) for d in usable_eval])

    radius = spectral_radius(matrix, seed=spec.seeds[0])
    runs: list[dict] = []
    for seed in spec.seeds:
        started = time.perf_counter()
        rng = np.random.default_rng(seed)
        reservoir = ReservoirSpec(**{**spec.reservoir.__dict__, "seed": seed})
        embedding = rng.normal(size=(256, reservoir.embedding_dim)).astype(np.float32)
        projection = (
            rng.normal(size=(populations.input_indices.size, reservoir.embedding_dim))
            * reservoir.input_scale
            / np.sqrt(reservoir.embedding_dim)
        ).astype(np.float32)

        for name, operator, operator_stats in iter_operators(
            matrix, seed=seed, target_radius=spec.target_radius, radius=radius["estimate"]
        ):
            train_features, train_diag = run_operator(
                operator, usable_train, populations, embedding, projection, reservoir
            )
            eval_features, eval_diag = run_operator(
                operator, usable_eval, populations, embedding, projection, reservoir
            )
            centre = train_features.mean(axis=0)
            scale = train_features.std(axis=0) + 1e-8
            weights = ridge_fit((train_features - centre) / scale, y_train, spec.ridge)
            standardised = (eval_features - centre) / scale
            predictions = np.hstack([standardised, np.ones((standardised.shape[0], 1))]) @ weights
            runs.append(
                {
                    "seed": seed,
                    "operator": name,
                    **macro_f1(truth, predictions.argmax(axis=1), CLASSES),
                    "diagnostics": {"train": train_diag, "eval": eval_diag},
                    "operator_stats": operator_stats,
                    "seconds": round(time.perf_counter() - started, 1),
                }
            )

    baseline = char_ngram_baseline(
        usable_train, usable_eval, penalty=spec.ridge, orders=spec.ngram_orders
    )
    return {
        "format": "papers/malecns-tagger-v3",
        "graph": str(graph_path),
        "spectral_radius": radius,
        "populations": {
            "input_selector": list(populations.input_selector),
            "input_neurons": int(populations.input_indices.size),
            "readout_selector": list(populations.readout_selector),
            "readout_neurons": int(populations.readout_indices.size),
        },
        "data": {
            "train_documents": len(usable_train),
            "eval_documents": len(usable_eval),
            "train_label_counts": {
                name: sum(1 for d in usable_train if d.label == name) for name in CLASSES
            },
            "eval_label_counts": {
                name: sum(1 for d in usable_eval if d.label == name) for name in CLASSES
            },
        },
        "char_ngram_baseline": baseline,
        "runs": runs,
        "summary": summarise(runs),
        "claim_boundary": (
            "Only the ridge readout is fitted; recurrent weights and the input projection are "
            "frozen. A MaleCNS advantage requires beating BOTH nulls on held-out documents."
        ),
    }


def summarise(runs: list[dict]) -> dict:
    """Per-operator means and the paired per-seed differences against each null."""
    operators = sorted({run["operator"] for run in runs})
    by_operator = {
        name: {run["seed"]: run["macro_f1"] for run in runs if run["operator"] == name}
        for name in operators
    }
    summary: dict = {
        name: {
            "macro_f1_mean": float(np.mean(list(scores.values()))),
            "macro_f1_stdev": float(np.std(list(scores.values()), ddof=1))
            if len(scores) > 1
            else 0.0,
            "per_seed": {str(seed): value for seed, value in sorted(scores.items())},
        }
        for name, scores in by_operator.items()
    }
    for null in ("degree_null", "random_esn"):
        if "malecns" in by_operator and null in by_operator:
            seeds = sorted(set(by_operator["malecns"]) & set(by_operator[null]))
            differences = [by_operator["malecns"][s] - by_operator[null][s] for s in seeds]
            summary[f"malecns_minus_{null}"] = {
                "values": differences,
                "mean": float(np.mean(differences)) if differences else 0.0,
                "stdev": float(np.std(differences, ddof=1)) if len(differences) > 1 else 0.0,
                "malecns_wins": int(sum(1 for d in differences if d > 0)),
                "seeds": len(differences),
            }
    return summary
