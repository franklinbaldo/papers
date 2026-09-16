"""Frozen embedding pairs for representation translation, with provenance.

One text, two encoders, two vectors. The translation task is to recover the
second vector from the first without ever running the second encoder.

The encoders are run once and cached because they are frozen: re-encoding per
epoch would burn CPU to recompute a constant, and worse, it would make it easy to
accidentally fine-tune an encoder and then report the result as a frozen-substrate
finding. The cache also carries its provenance -- model repo *and* resolved Hub
revision, the prompt convention applied, and a SHA-256 over the exact texts -- so a
result JSON can name the bytes it was computed from.

E5 checkpoints are asymmetric: they expect ``query:`` / ``passage:`` prefixes and
score differently without them. The prefix used is recorded rather than assumed.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

SCHEMA = "papers/malecns-translation-pairs-v1"


def text_fingerprint(texts: list[str]) -> str:
    digest = hashlib.sha256()
    for text in texts:
        digest.update(text.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


def cache_fingerprint(*, texts: list[str], source_model: str, target_model: str) -> str:
    payload = {
        "texts": text_fingerprint(texts),
        "count": len(texts),
        "source_model": source_model,
        "target_model": target_model,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def e5_prefix(model_name: str, *, kind: str = "query") -> str:
    """The prefix an E5 checkpoint expects, or the empty string for others."""
    return f"{kind}: " if "e5" in model_name.lower() else ""


def _resolved_revision(model_name: str) -> str | None:
    try:
        from huggingface_hub import HfApi

        return HfApi().model_info(model_name).sha
    except Exception:  # pragma: no cover - offline or private repo
        return None


def encode_texts(
    model_name: str,
    texts: list[str],
    *,
    device: str = "cpu",
    batch_size: int = 32,
    prefix_kind: str = "query",
) -> tuple[np.ndarray, dict]:
    """Encode with a frozen sentence encoder and report what was actually run."""
    from sentence_transformers import SentenceTransformer

    started = time.perf_counter()
    prefix = e5_prefix(model_name, kind=prefix_kind)
    model = SentenceTransformer(model_name, device=device)
    model.eval()
    values = model.encode(
        [prefix + text for text in texts],
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)
    report = {
        "model": model_name,
        "revision": _resolved_revision(model_name),
        "dim": int(values.shape[1]),
        "prefix": prefix,
        "normalized": True,
        "device": device,
        "seconds": time.perf_counter() - started,
    }
    del model
    return values, report


def build_cache(
    *,
    texts: list[str],
    source_model: str,
    target_model: str,
    output: Path,
    corpus: dict,
    groups: list[int] | None = None,
    device: str = "cpu",
    batch_size: int = 32,
) -> dict:
    if len(texts) != len(set(texts)):
        raise ValueError("texts must be unique; duplicates make retrieval metrics meaningless")
    source, source_report = encode_texts(
        source_model, texts, device=device, batch_size=batch_size
    )
    target, target_report = encode_texts(
        target_model, texts, device=device, batch_size=batch_size, prefix_kind="passage"
    )
    group_ids = (
        np.arange(len(texts), dtype=np.int64)
        if groups is None
        else np.asarray(groups, dtype=np.int64)
    )
    if group_ids.shape[0] != len(texts):
        raise ValueError("groups must align with texts")
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, source=source, target=target, groups=group_ids)
    manifest = {
        "schema": SCHEMA,
        "fingerprint": cache_fingerprint(
            texts=texts, source_model=source_model, target_model=target_model
        ),
        "text_sha256": text_fingerprint(texts),
        "count": len(texts),
        "groups": int(np.unique(group_ids).size),
        "group_note": (
            "Texts sharing a group are near-duplicates of each other (e.g. the two "
            "sentences of an STS-B pair). Splits are group-disjoint so a paraphrase of a "
            "test item cannot sit in the training set."
        ),
        "corpus": corpus,
        "source": source_report,
        "target": target_report,
        "npz": output.name,
        "encoders_frozen": True,
        "note": (
            "Both encoders are frozen and run exactly once. Nothing downstream may "
            "update them; the translation task never calls the target encoder."
        ),
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    texts_path = output.with_suffix(".texts.json")
    texts_path.write_text(json.dumps(texts, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def load_cache(cache: Path) -> tuple[np.ndarray, np.ndarray, list[str], np.ndarray, dict]:
    """Load embeddings and re-verify the fingerprint against the stored texts."""
    manifest = json.loads(cache.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise RuntimeError(f"unexpected translation cache schema: {manifest.get('schema')}")
    texts = json.loads(cache.with_suffix(".texts.json").read_text(encoding="utf-8"))
    expected = cache_fingerprint(
        texts=texts,
        source_model=manifest["source"]["model"],
        target_model=manifest["target"]["model"],
    )
    if manifest["fingerprint"] != expected:
        raise RuntimeError("translation cache fingerprint mismatch: texts and manifest disagree")
    archive = np.load(cache, allow_pickle=False)
    source = archive["source"].astype(np.float32)
    target = archive["target"].astype(np.float32)
    if source.shape[0] != target.shape[0] or source.shape[0] != len(texts):
        raise RuntimeError("translation cache row counts disagree")
    groups = (
        archive["groups"].astype(np.int64)
        if "groups" in archive.files
        else np.arange(len(texts), dtype=np.int64)
    )
    return source, target, texts, groups, manifest


def split_indices(
    count: int, *, seed: int, train: float = 0.7, val: float = 0.15,
    groups: np.ndarray | None = None,
):
    """Group-disjoint train/val/test indices. Test is touched once, at the end.

    Splitting by item rather than by group would be a quiet leak on any corpus of
    paraphrase pairs: STS-B contributes both sentences of each pair, so an
    item-level shuffle trains on a near-duplicate of half the test set and every
    arm's score comes out inflated. Grouping costs nothing and removes the doubt.
    """
    if not 0.0 < train < 1.0 or not 0.0 < val < 1.0 or train + val >= 1.0:
        raise ValueError("train and val fractions must be positive and leave a test split")
    groups = np.arange(count) if groups is None else np.asarray(groups)
    if groups.shape[0] != count:
        raise ValueError("groups must align with the item count")
    unique = np.unique(groups)
    order = np.random.default_rng(seed).permutation(unique)
    n_train = int(round(len(unique) * train))
    n_val = int(round(len(unique) * val))
    chosen = (order[:n_train], order[n_train:n_train + n_val], order[n_train + n_val:])
    return tuple(np.sort(np.flatnonzero(np.isin(groups, part))) for part in chosen)
