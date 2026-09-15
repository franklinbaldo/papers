"""Per-(encoder, scale) trainable-adapter entrypoint for coupled flavour smoke.

Builds on v2 (device-safe) while keeping v1/v2 intact for provenance.
Every semantic channel owns an independent low-rank residual adapter, even when
another channel has the same dimensionality.  Cross-channel communication stays
at the evidence level; adapter weights are never shared across embedding models
or context scales.

The adapter is identity at initialization:
    A(x) = unit(x + scale * up(tanh(down(unit(x)))))
with `up` zero-initialized.  This lets the run start from the exact frozen
embedding geometry and then specialize each (encoder, scale) channel online.
"""

from __future__ import annotations

import torch

# Importing v2 first installs the device-safe flavour bundle and forward invariant
# into the v1 module.  We then extend that patched module with per-channel adapters.
import smoke_coupled_flavour_translation_gpu_v2 as v2  # noqa: F401
import smoke_coupled_flavour_translation_gpu as v1


class ChannelAdapter(torch.nn.Module):
    def __init__(self, dim: int, *, rank: int = 16, residual_scale: float = 0.1, device):
        super().__init__()
        rank = min(int(rank), int(dim))
        self.down = torch.nn.Linear(dim, rank, bias=False, device=device)
        self.up = torch.nn.Linear(rank, dim, bias=False, device=device)
        self.residual_scale = float(residual_scale)
        torch.nn.init.normal_(self.down.weight, mean=0.0, std=1.0 / max(dim, 1) ** 0.5)
        torch.nn.init.zeros_(self.up.weight)

    def forward(self, values):
        unit = values / torch.linalg.vector_norm(values, dim=1, keepdim=True).clamp_min(1e-12)
        residual = self.up(torch.tanh(self.down(unit)))
        adapted = unit + self.residual_scale * residual
        return adapted / torch.linalg.vector_norm(adapted, dim=1, keepdim=True).clamp_min(1e-12)


class PerChannelAdapterFlavourBundle(v1.FlavourBundle):
    def __init__(self, initial_flavours, readout_width, *, device):
        super().__init__(initial_flavours, readout_width, device=device)
        self.channel_adapters = torch.nn.ModuleList([
            ChannelAdapter(len(value), rank=16, residual_scale=0.1, device=device)
            for value in initial_flavours
        ])
        # `super()` is device-safe through v2, but make the invariant explicit for
        # newly added modules too.
        self.to(device)

    def adapt(self, index: int, field):
        return self.channel_adapters[index](field)


_base_reservoir_logits = v1._reservoir_logits


def _adapted_reservoir_logits(
    model,
    fields,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    *,
    target_rms=0.05,
):
    if len(fields) != len(model.channel_adapters):
        raise RuntimeError(
            f"adapter/channel invariant failed: fields={len(fields)} "
            f"adapters={len(model.channel_adapters)}"
        )
    adapted_fields = [model.adapt(index, field) for index, field in enumerate(fields)]
    return _base_reservoir_logits(
        model,
        adapted_fields,
        operator,
        input_weights,
        input_indices,
        whole_brain,
        readout_projection,
        target_rms=target_rms,
    )


def _adapted_local_logits(model, fields):
    rows = []
    for index, field in enumerate(fields):
        adapted = model.adapt(index, field)
        rows.append(6.0 * (adapted @ model.flavour(index)))
    return torch.stack(rows, dim=1)


v1.FlavourBundle = PerChannelAdapterFlavourBundle
v1._reservoir_logits = _adapted_reservoir_logits
v1._local_logits = _adapted_local_logits


if __name__ == "__main__":
    v1.main()
