import json
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from malecns_wifi.tagger import (
    CLASSES,
    Document,
    ReservoirSpec,
    TaggerSpec,
    classify_text,
    encode,
    label_noise,
    load_corpus,
    macro_f1,
    run_experiment,
    select_populations,
)

# Wording taken from the hand-annotated resultado spans of the segmenter splits.
GOLD_WORDINGS = [
    ("RECURSO PARCIALMENTE PROVIDO", "partial"),
    ("RECURSO NÃO PROVIDO", "unfavourable"),
    ("RECURSO PROVIDO", "favourable"),
    ("EMBARGOS DE DECLARAÇÃO CONHECIDOS E PARCIALMENTE ACOLHIDOS À UNANIMIDADE", "partial"),
    ("RECURSO NÃO CONHECIDO À UNANIMIDADE", "unfavourable"),
    ("JULGO IMPROCEDENTE", "unfavourable"),
    ("JULGO PROCEDENTE", "favourable"),
    ("JULGO EXTINTO O PROCESSO", "unfavourable"),
    ("JULGO IMPROCEDENTES", "unfavourable"),
    ("JULGO PARCIALMENTE PROCEDENTES", "partial"),
    ("JULGO PROCEDENTES", "favourable"),
    ("julgo EXTINTO O PROCESSO", "unfavourable"),
    ("nego provimento ao recurso", "unfavourable"),
    ("dou parcial provimento", "partial"),
]


@pytest.mark.parametrize(("wording", "expected"), GOLD_WORDINGS)
def test_weak_labeller_matches_the_hand_annotated_wordings(wording: str, expected: str) -> None:
    assert classify_text(wording) == expected


def test_weak_labeller_returns_none_when_nothing_matches() -> None:
    assert classify_text("relatorio sem dispositivo algum") is None


def _corpus_file(path: Path) -> Path:
    rows = [
        {
            "text": "relatorio de um caso qualquer. ao final, JULGO PROCEDENTE o pedido.",
            "label": [{"category": "resultado", "start": 40, "end": 56}],
            "info": {"doc_id": "d0"},
        },
        {
            "text": "outro caso. dispositivo: JULGO IMPROCEDENTE o pedido inicial.",
            "label": [{"category": "resultado", "start": 25, "end": 43}],
            "info": {"doc_id": "d1"},
        },
    ]
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    return path


def test_masking_removes_the_outcome_phrase_but_keeps_the_gold_label(tmp_path: Path) -> None:
    source = _corpus_file(tmp_path / "corpus.jsonl")
    masked = load_corpus(source, mask_resultado=True)
    unmasked = load_corpus(source, mask_resultado=False)

    assert [d.gold for d in masked] == ["favourable", "unfavourable"]
    assert [d.gold for d in unmasked] == ["favourable", "unfavourable"]
    # The point of masking: the answer is no longer quoted in the text.
    assert all(d.weak is None for d in masked)
    assert [d.weak for d in unmasked] == ["favourable", "unfavourable"]
    assert len(masked[0].text) == len(unmasked[0].text), "masking must not shift byte offsets"


def test_label_noise_compares_weak_against_gold(tmp_path: Path) -> None:
    documents = load_corpus(_corpus_file(tmp_path / "corpus.jsonl"), mask_resultado=False)
    noise = label_noise(documents)
    assert noise["gold_documents"] == 2
    assert noise["weak_accuracy"] == 1.0


def test_encode_keeps_the_tail_when_truncating() -> None:
    document = Document(doc_id="d", text="abcdefghij", gold=None, weak=None)
    batch, lengths = encode([document], ReservoirSpec(max_bytes=4))
    assert lengths.tolist() == [4]
    assert bytes(batch[0]).decode() == "ghij"


def test_encode_pads_to_the_longest_document_and_records_true_lengths() -> None:
    documents = [
        Document(doc_id="a", text="abc", gold=None, weak=None),
        Document(doc_id="b", text="abcdef", gold=None, weak=None),
    ]
    batch, lengths = encode(documents, ReservoirSpec())
    assert lengths.tolist() == [3, 6]
    assert batch.shape == (2, 6)
    assert batch[0, 3:].tolist() == [0, 0, 0]


def test_select_populations_rejects_an_empty_selector() -> None:
    superclass = np.asarray(["cb_sensory", "descending_neuron", "cb_intrinsic"])
    chosen = select_populations(superclass)
    assert chosen.input_indices.tolist() == [0]
    assert chosen.readout_indices.tolist() == [1]
    with pytest.raises(ValueError, match="empty population"):
        select_populations(superclass, readout_selector=("no_such_class",))


def test_macro_f1_on_a_known_confusion() -> None:
    true = np.asarray([0, 0, 1, 1, 2, 2])
    predicted = np.asarray([0, 0, 1, 2, 2, 2])
    scored = macro_f1(true, predicted, CLASSES)
    assert scored["accuracy"] == pytest.approx(5 / 6)
    assert scored["per_class"][CLASSES[0]]["f1"] == pytest.approx(1.0)
    assert scored["per_class"][CLASSES[1]]["support"] == 2


def _toy_graph(path: Path, n: int = 60) -> Path:
    """A small signed operator carrying the annotations the tagger selects on."""
    rng = np.random.default_rng(0)
    dense = rng.normal(size=(n, n)).astype(np.float32)
    dense[rng.random((n, n)) > 0.1] = 0.0
    matrix = sp.csr_matrix(dense)
    superclass = np.asarray(
        ["cb_sensory"] * 10 + ["descending_neuron"] * 10 + ["cb_intrinsic"] * (n - 20), dtype="U32"
    )
    np.savez_compressed(
        path,
        data=matrix.data,
        indices=matrix.indices,
        indptr=matrix.indptr,
        shape=np.asarray(matrix.shape, dtype=np.int64),
        bodies=np.arange(n, dtype=np.int64),
        sign=np.sign(np.asarray(matrix.sum(axis=1)).ravel()).astype(np.float32),
        nt=np.full(n, "acetylcholine", dtype="U24"),
        superclass=superclass,
        cell_class=np.full(n, "unknown", dtype="U32"),
    )
    return path


def test_experiment_runs_end_to_end_and_reports_both_paired_contrasts(tmp_path: Path) -> None:
    graph = _toy_graph(tmp_path / "graph.npz")
    train = [
        Document(f"t{i}", f"caso {i} " * 20, gold=CLASSES[i % 3], weak=None) for i in range(9)
    ]
    evaluate = [Document(f"e{i}", f"outro {i} " * 20, gold=CLASSES[i % 3], weak=None) for i in range(6)]

    report = run_experiment(
        graph,
        train,
        evaluate,
        TaggerSpec(seeds=(0, 1), reservoir=ReservoirSpec(batch_size=4, max_bytes=64)),
    )

    assert {run["operator"] for run in report["runs"]} == {
        "malecns",
        "degree_null",
        "random_esn",
    }
    assert len(report["runs"]) == 6
    for null in ("degree_null", "random_esn"):
        paired = report["summary"][f"malecns_minus_{null}"]
        assert paired["seeds"] == 2
        assert len(paired["values"]) == 2
    assert 0.0 <= report["char_ngram_baseline"]["macro_f1"] <= 1.0
    for run in report["runs"]:
        assert np.isfinite(run["macro_f1"])
        assert run["diagnostics"]["eval"]["recurrent_to_input_ratio"] >= 0.0


def test_experiment_refuses_a_split_with_no_labels(tmp_path: Path) -> None:
    graph = _toy_graph(tmp_path / "graph.npz")
    train = [Document("t", "texto", gold=CLASSES[0], weak=None)]
    with pytest.raises(ValueError, match="no labelled documents"):
        run_experiment(graph, train, [Document("e", "texto", gold=None, weak=None)], TaggerSpec())
