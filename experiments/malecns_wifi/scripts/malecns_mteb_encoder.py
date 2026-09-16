"""Frozen MaleCNS document encoders compatible with the MTEB EncoderProtocol.

Two encoders share the same logical representation (see
``malecns_wifi.document_reservoir``):

* ``FrozenMaleCNSEncoder`` runs the frozen MiniLM/E5 semantic stage and the
  MaleCNS reservoir live, per MTEB batch. This is the path used by the first
  official run.
* ``CachedDocumentEncoder`` serves precomputed document embeddings (stage B
  output) looked up by the sha256 of the document text, so the official MTEB
  evaluator can be re-run on any variant without paying the encoders again.

Neither encoder sees benchmark labels.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from malecns_wifi.document_reservoir import (
    DocumentReservoir,
    DocumentReservoirConfig,
    load_reservoir_inputs,
    sample_windows,
    unit_rows,
)
from malecns_wifi.multieurlex_cache import model_prefix, text_key

# Backwards-compatible aliases for the first official run's module layout.
_sample_windows = sample_windows
_unit_rows = unit_rows


@dataclass(frozen=True)
class MaleCNSEncoderConfig:
    graph: Path
    models: tuple[str, ...] = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    )
    readout_width: int = 256
    seed: int = 20260915
    max_chunks: int = 4
    chunk_chars: int = 3000
    gain: float = 4.0
    leak: float = 0.4
    target_rms: float = 0.05
    batch_size: int = 16
    backend: str = "canonical"
    device: str = "cuda"

    def reservoir_config(self) -> DocumentReservoirConfig:
        return DocumentReservoirConfig(
            readout_width=self.readout_width,
            seed=self.seed,
            max_chunks=self.max_chunks,
            chunk_chars=self.chunk_chars,
            gain=self.gain,
            leak=self.leak,
            target_rms=self.target_rms,
        )


class _SimilarityMixin:
    @property
    def mteb_model_meta(self):
        # Instantiated directly by our runner, so MTEB needs no registry metadata.
        # The property is still required by the runtime-checkable EncoderProtocol.
        return None

    def similarity(self, embeddings1, embeddings2):
        left = unit_rows(np.asarray(embeddings1, dtype=np.float32))
        right = unit_rows(np.asarray(embeddings2, dtype=np.float32))
        return left @ right.T

    def similarity_pairwise(self, embeddings1, embeddings2):
        left = unit_rows(np.asarray(embeddings1, dtype=np.float32))
        right = unit_rows(np.asarray(embeddings2, dtype=np.float32))
        if left.shape != right.shape:
            raise ValueError(
                f"pairwise similarity requires equal shapes, got {left.shape} and {right.shape}"
            )
        return np.sum(left * right, axis=1)


def _iter_texts(inputs, requested: int):
    for dataloader_batch in inputs:
        texts = dataloader_batch["text"]
        if isinstance(texts, str):
            texts = [texts]
        texts = list(texts)
        for start in range(0, len(texts), requested):
            yield texts[start:start + requested]


class FrozenMaleCNSEncoder(_SimilarityMixin):
    """MTEB-compatible encoder using the frozen full MaleCNS recurrent graph."""

    def __init__(self, config: MaleCNSEncoderConfig):
        import torch
        from sentence_transformers import SentenceTransformer

        if config.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("FrozenMaleCNSEncoder requested CUDA but it is not available")
        self.config = config
        self.device = torch.device(config.device)

        matrix, input_indices = load_reservoir_inputs(config.graph)

        self.semantic_models = []
        dims = []
        for model_name in config.models:
            model = SentenceTransformer(model_name, device=config.device)
            dims.append(int(model.get_sentence_embedding_dimension()))
            self.semantic_models.append((model_name, model))
        self.semantic_dim = int(sum(dims))

        self.reservoir = DocumentReservoir(
            matrix,
            input_indices,
            semantic_dim=self.semantic_dim,
            config=config.reservoir_config(),
            device=self.device,
            backend=config.backend,
        )
        self.neurons = self.reservoir.neurons
        self.edges = self.reservoir.edges
        self.sensory_neurons = self.reservoir.sensory_neurons
        self.semantic_seconds: dict[str, float] = {name: 0.0 for name in config.models}
        self.stats: dict[str, Any] = {
            "documents": 0,
            "semantic_chunks": 0,
            "graph_neurons": self.neurons,
            "graph_edges": self.edges,
            "sensory_neurons": self.sensory_neurons,
            "semantic_dim": self.semantic_dim,
            "readout_width": config.readout_width,
            "models": list(config.models),
            "backend": config.backend,
        }

    def _embed_documents(self, texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
        """Return [batch, max_chunks, semantic_dim] and active mask."""
        import time

        windows_per_doc = [
            sample_windows(text, max_chunks=self.config.max_chunks, chunk_chars=self.config.chunk_chars)
            for text in texts
        ]
        max_steps = max(len(w) for w in windows_per_doc)
        flat: list[str] = []
        positions: list[tuple[int, int]] = []
        for doc_i, windows in enumerate(windows_per_doc):
            for step_i, value in enumerate(windows):
                flat.append(value)
                positions.append((doc_i, step_i))

        per_model = []
        for model_name, model in self.semantic_models:
            prefix = model_prefix(model_name)
            t0 = time.perf_counter()
            encoded = model.encode(
                [prefix + value for value in flat],
                batch_size=max(8, self.config.batch_size * 2),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self.semantic_seconds[model_name] += time.perf_counter() - t0
            per_model.append(unit_rows(encoded))
        fused = np.concatenate(per_model, axis=1).astype(np.float32)

        cube = np.zeros((len(texts), max_steps, self.semantic_dim), dtype=np.float32)
        active = np.zeros((len(texts), max_steps), dtype=np.bool_)
        for row, (doc_i, step_i) in enumerate(positions):
            cube[doc_i, step_i] = fused[row]
            active[doc_i, step_i] = True
        self.stats["semantic_chunks"] += len(flat)
        return cube, active

    def _reservoir_batch(self, cube: np.ndarray, active: np.ndarray) -> np.ndarray:
        return self.reservoir.forward(cube, active)

    def encode(
        self,
        inputs,
        *,
        task_metadata,
        hf_split: str,
        hf_subset: str,
        prompt_type=None,
        batch_size: int | None = None,
        **kwargs,
    ) -> np.ndarray:
        del task_metadata, hf_split, hf_subset, prompt_type, kwargs
        output = []
        requested = int(batch_size or self.config.batch_size)
        for local in _iter_texts(inputs, requested):
            cube, active = self._embed_documents(local)
            output.append(self._reservoir_batch(cube, active))
            self.stats["documents"] += len(local)
        self.stats["semantic_seconds"] = dict(self.semantic_seconds)
        self.stats["reservoir"] = self.reservoir.stats.as_dict()
        if not output:
            return np.empty((0, self.config.readout_width), dtype=np.float32)
        return np.concatenate(output, axis=0)


class CachedDocumentEncoder(_SimilarityMixin):
    """Serve stage-B document embeddings to the MTEB evaluator by text hash."""

    def __init__(self, embeddings_path: Path):
        import json

        archive = np.load(embeddings_path, allow_pickle=False)
        self.embeddings = archive["embeddings"].astype(np.float32)
        keys = archive["doc_key"].tolist()
        self.index = {str(key): i for i, key in enumerate(keys)}
        manifest_file = embeddings_path.with_suffix(".manifest.json")
        self.manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}
        self.stats: dict[str, Any] = {
            "documents": 0,
            "cached_documents": int(self.embeddings.shape[0]),
            "readout_width": int(self.embeddings.shape[1]),
            "variant": self.manifest.get("variant"),
            "backend": self.manifest.get("backend"),
            "semantic_cache_fingerprint": self.manifest.get("semantic_cache_fingerprint"),
        }

    def encode(
        self,
        inputs,
        *,
        task_metadata,
        hf_split: str,
        hf_subset: str,
        prompt_type=None,
        batch_size: int | None = None,
        **kwargs,
    ) -> np.ndarray:
        del task_metadata, hf_split, hf_subset, prompt_type, kwargs
        rows = []
        for local in _iter_texts(inputs, int(batch_size or 64)):
            for text in local:
                key = text_key(text)
                if key not in self.index:
                    raise KeyError("document missing from stage-B embeddings; rebuild the semantic cache")
                rows.append(self.index[key])
            self.stats["documents"] += len(local)
        if not rows:
            return np.empty((0, self.embeddings.shape[1]), dtype=np.float32)
        return self.embeddings[np.asarray(rows, dtype=np.int64)]
