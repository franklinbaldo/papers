"""Frozen MaleCNS document encoder compatible with the MTEB EncoderProtocol.

The encoder uses no benchmark labels. Frozen MiniLM/E5 semantic channels drive
sensory populations of the row-normalised MaleCNS connectome. Up to four text
windows are sampled across each document and integrated recurrently; a fixed
sparse whole-brain projection is returned as the document embedding.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.tagger import row_normalise, select_populations


def _csr_to_torch(matrix: sp.csr_matrix, *, device):
    import torch

    matrix = matrix.tocsr().astype(np.float32)
    return torch.sparse_csr_tensor(
        torch.as_tensor(matrix.indptr, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.indices, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.data, dtype=torch.float32, device=device),
        size=matrix.shape,
        device=device,
    )


def _fixed_sparse_projection(rows: int, cols: int, *, seed: int, device):
    import torch

    rng = np.random.default_rng(seed)
    per_row = max(1, int(round(math.sqrt(cols))))
    row = np.repeat(np.arange(rows, dtype=np.int64), per_row)
    col = np.concatenate([
        rng.choice(cols, size=per_row, replace=False).astype(np.int64)
        for _ in range(rows)
    ])
    sign = rng.choice([-1.0, 1.0], size=len(row)).astype(np.float32)
    value = sign / np.float32(math.sqrt(per_row))
    indices = torch.as_tensor(np.vstack([row, col]), dtype=torch.int64, device=device)
    values = torch.as_tensor(value, dtype=torch.float32, device=device)
    return torch.sparse_coo_tensor(indices, values, (rows, cols), device=device).coalesce()


def _sample_windows(text: str, *, max_chunks: int, chunk_chars: int) -> list[str]:
    text = str(text or "").strip()
    if not text:
        return [" "]
    if len(text) <= chunk_chars:
        return [text]
    count = min(max_chunks, max(2, math.ceil(len(text) / chunk_chars)))
    max_start = max(0, len(text) - chunk_chars)
    starts = np.linspace(0, max_start, num=count, dtype=np.int64)
    return [text[int(start): int(start) + chunk_chars] for start in starts]


def _unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    if values.ndim == 1:
        values = values[None, :]
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)


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


class FrozenMaleCNSEncoder:
    """MTEB-compatible encoder using the frozen full MaleCNS recurrent graph."""

    def __init__(self, config: MaleCNSEncoderConfig):
        import torch
        from sentence_transformers import SentenceTransformer

        if not torch.cuda.is_available():
            raise RuntimeError("FrozenMaleCNSEncoder currently requires CUDA")
        self.config = config
        self.device = torch.device("cuda")

        matrix = row_normalise(load_graph(config.graph))
        archive = np.load(config.graph, allow_pickle=False)
        populations = select_populations(archive["superclass"])
        self.operator = _csr_to_torch(matrix, device=self.device)
        self.neurons = int(matrix.shape[0])
        self.edges = int(matrix.nnz)
        self.input_indices = torch.as_tensor(
            populations.input_indices, dtype=torch.int64, device=self.device
        )
        self.sensory_neurons = int(populations.input_indices.size)

        self.semantic_models = []
        dims = []
        for model_name in config.models:
            model = SentenceTransformer(model_name, device="cuda")
            dim = int(model.get_sentence_embedding_dimension())
            self.semantic_models.append((model_name, model))
            dims.append(dim)
        self.semantic_dim = int(sum(dims))

        rng = np.random.default_rng(config.seed)
        weights = rng.normal(
            size=(self.sensory_neurons, self.semantic_dim)
        ).astype(np.float32) / np.float32(math.sqrt(self.semantic_dim))
        self.input_weights = torch.as_tensor(weights, dtype=torch.float32, device=self.device)
        self.readout_projection = _fixed_sparse_projection(
            config.readout_width,
            self.neurons,
            seed=config.seed + 17,
            device=self.device,
        )

        self.stats: dict[str, Any] = {
            "documents": 0,
            "semantic_chunks": 0,
            "graph_neurons": self.neurons,
            "graph_edges": self.edges,
            "sensory_neurons": self.sensory_neurons,
            "semantic_dim": self.semantic_dim,
            "readout_width": config.readout_width,
            "models": list(config.models),
        }

    @property
    def mteb_model_meta(self):
        # This object is instantiated directly by our runner, so MTEB does not
        # need registry metadata to construct it. The property is still required
        # by the runtime-checkable EncoderProtocol.
        return None

    def similarity(self, embeddings1, embeddings2):
        left = _unit_rows(np.asarray(embeddings1, dtype=np.float32))
        right = _unit_rows(np.asarray(embeddings2, dtype=np.float32))
        return left @ right.T

    def similarity_pairwise(self, embeddings1, embeddings2):
        left = _unit_rows(np.asarray(embeddings1, dtype=np.float32))
        right = _unit_rows(np.asarray(embeddings2, dtype=np.float32))
        if left.shape != right.shape:
            raise ValueError(
                f"pairwise similarity requires equal shapes, got {left.shape} and {right.shape}"
            )
        return np.sum(left * right, axis=1)

    def _embed_documents(self, texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
        """Return [batch, max_chunks, semantic_dim] and active mask."""
        windows_per_doc = [
            _sample_windows(
                text,
                max_chunks=self.config.max_chunks,
                chunk_chars=self.config.chunk_chars,
            )
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
            values = flat
            if "e5" in model_name.lower():
                values = ["passage: " + value for value in flat]
            encoded = model.encode(
                values,
                batch_size=max(8, self.config.batch_size * 2),
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            per_model.append(_unit_rows(encoded))
        fused = np.concatenate(per_model, axis=1).astype(np.float32)

        cube = np.zeros((len(texts), max_steps, self.semantic_dim), dtype=np.float32)
        active = np.zeros((len(texts), max_steps), dtype=np.bool_)
        for row, (doc_i, step_i) in enumerate(positions):
            cube[doc_i, step_i] = fused[row]
            active[doc_i, step_i] = True
        self.stats["semantic_chunks"] += len(flat)
        return cube, active

    def _reservoir_batch(self, cube: np.ndarray, active: np.ndarray) -> np.ndarray:
        import torch

        batch, steps, _ = cube.shape
        features = torch.as_tensor(cube, dtype=torch.float32, device=self.device)
        active_t = torch.as_tensor(active, dtype=torch.bool, device=self.device)
        state = torch.zeros((self.neurons, batch), dtype=torch.float32, device=self.device)

        for step in range(steps):
            local = features[:, step, :]
            projected = self.input_weights @ local.T
            rms = torch.sqrt(torch.mean(projected.square(), dim=0, keepdim=True)).clamp_min(1e-12)
            projected = projected * (self.config.target_rms / rms)
            drive = torch.zeros_like(state)
            drive.index_copy_(0, self.input_indices, projected)
            pre = torch.sparse.mm(self.operator, state) * self.config.gain + drive
            updated = (1.0 - self.config.leak) * state + self.config.leak * torch.tanh(pre)
            mask = active_t[:, step][None, :]
            state = torch.where(mask, updated, state)

        readout = torch.sparse.mm(self.readout_projection, state).T
        readout = readout / torch.linalg.vector_norm(readout, dim=1, keepdim=True).clamp_min(1e-12)
        return readout.detach().cpu().numpy().astype(np.float32)

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
        for dataloader_batch in inputs:
            texts = dataloader_batch["text"]
            if isinstance(texts, str):
                texts = [texts]
            texts = list(texts)
            for start in range(0, len(texts), requested):
                local = texts[start:start + requested]
                cube, active = self._embed_documents(local)
                output.append(self._reservoir_batch(cube, active))
                self.stats["documents"] += len(local)
        if not output:
            return np.empty((0, self.config.readout_width), dtype=np.float32)
        return np.concatenate(output, axis=0)
