"""Frozen MaleCNS positional reservoir for byte-synchronised token tasks (NER first).

Unlike the MultiEURLEX document encoder, which pools a handful of text chunks
into one embedding, this reservoir runs over the sentence's canonical UTF-8
byte axis: every byte is a time step, driven by the same multiscale
byte-synchronised semantic channels already established in
``text_axis_channels.py`` and used by the flavour/food experiments -- window
embeddings at several character scales, linearly interpolated to every byte
position (not per-token hidden states from a tokenizer, which has no fixed
place in this programme's channel convention). A readout is emitted at *every*
byte, not just the last, so labels can be scored at the same resolution the
channels are defined on. The only place a non-frozen parameter appears is a
linear probe fit afterwards on the readout embeddings (``token_probe.py``) --
the connectome, its input weights and its readout projection are exactly as
frozen as in the document encoder.

    text -> UTF-8 byte axis -> multiscale window embeddings (frozen MiniLM/E5)
         -> interpolated to every byte, unit-normalised per (model, scale),
            concatenated -> fixed Gaussian sensory projection (RMS-normalised
            per byte) -> row-normalised MaleCNS recurrent step (gain, leak,
            tanh) -> fixed sparse whole-brain readout at EVERY byte position
         -> [sentence, byte, readout_width]
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from malecns_wifi.document_reservoir import (
    ReservoirStats,
    csr_to_torch,
    fixed_sparse_projection,
    sensory_input_weights,
)


@dataclass(frozen=True)
class TokenReservoirConfig:
    readout_width: int = 256
    seed: int = 20260915
    gain: float = 4.0
    leak: float = 0.4
    target_rms: float = 0.05

    def as_dict(self) -> dict[str, Any]:
        return {
            "readout_width": self.readout_width,
            "seed": self.seed,
            "gain": self.gain,
            "leak": self.leak,
            "target_rms": self.target_rms,
        }


class PositionalReservoir:
    """Frozen MaleCNS recurrent encoder emitting one readout per byte position."""

    def __init__(
        self,
        matrix,
        input_indices: np.ndarray,
        *,
        semantic_dim: int,
        config: TokenReservoirConfig,
        device,
        index_dtype: str = "int64",
    ):
        import torch

        self.config = config
        self.device = torch.device(device)
        self.neurons = int(matrix.shape[0])
        self.edges = int(matrix.nnz)
        self.semantic_dim = int(semantic_dim)
        torch_index = {"int64": torch.int64, "int32": torch.int32}[index_dtype]
        self.operator = csr_to_torch(matrix, device=self.device, index_dtype=torch_index)
        self.input_indices = torch.as_tensor(
            np.asarray(input_indices, dtype=np.int64), dtype=torch.int64, device=self.device
        )
        self.sensory_neurons = int(self.input_indices.numel())
        self.input_weights = torch.as_tensor(
            sensory_input_weights(self.sensory_neurons, self.semantic_dim, seed=config.seed),
            dtype=torch.float32,
            device=self.device,
        )
        self.readout_projection = fixed_sparse_projection(
            config.readout_width, self.neurons, seed=config.seed + 17, device=self.device
        )
        self.stats = ReservoirStats()

    def _sync(self) -> None:
        import torch

        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)

    def forward(self, cube: np.ndarray, active: np.ndarray) -> np.ndarray:
        """``cube``: [batch, steps, semantic_dim] byte-synchronised channels;
        ``active``: [batch, steps] padding mask (steps = bytes here).

        Returns ``[batch, steps, readout_width]`` -- one embedding per byte
        position, not just the sentence-final state.
        """
        import torch

        gain, leak, target_rms = self.config.gain, self.config.leak, self.config.target_rms
        batch, steps, _ = cube.shape
        active = np.asarray(active, dtype=np.bool_)
        self._sync()
        t0 = time.perf_counter()

        features = torch.as_tensor(cube, dtype=torch.float32, device=self.device)
        active_t = torch.as_tensor(active, dtype=torch.bool, device=self.device)
        state = torch.zeros((self.neurons, batch), dtype=torch.float32, device=self.device)
        outputs = torch.zeros((steps, batch, self.config.readout_width), dtype=torch.float32, device=self.device)

        for step in range(steps):
            local = features[:, step, :]
            projected = self.input_weights @ local.T
            rms = torch.sqrt(torch.mean(projected.square(), dim=0, keepdim=True)).clamp_min(1e-12)
            projected = projected * (target_rms / rms)

            if step == 0:
                pre = torch.zeros_like(state)
                pre.index_copy_(0, self.input_indices, projected)
            else:
                self._sync()
                t_spmm = time.perf_counter()
                pre = torch.sparse.mm(self.operator, state) * gain
                self._sync()
                self.stats.spmm_seconds += time.perf_counter() - t_spmm
                self.stats.spmm_calls += 1
                self.stats.spmm_columns += batch
                pre.index_add_(0, self.input_indices, projected)

            updated = (1.0 - leak) * state + leak * torch.tanh(pre)
            mask = active_t[:, step][None, :]
            state = torch.where(mask, updated, state)

            readout = torch.sparse.mm(self.readout_projection, state).T
            readout = readout / torch.linalg.vector_norm(readout, dim=1, keepdim=True).clamp_min(1e-12)
            outputs[step] = readout

        result = outputs.permute(1, 0, 2).detach().cpu().numpy().astype(np.float32)
        self._sync()
        self.stats.forward_seconds += time.perf_counter() - t0
        self.stats.documents += batch
        self.stats.chunks += int(active.sum())
        self.stats.batches += 1
        return result
