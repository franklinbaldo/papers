"""Reliability-weighted peer-coupling grid on per-(encoder, scale) adapters.

Builds on the successful v3 adapter smoke.  Each (encoder, scale) keeps its own
adapter and flavour.  Cross-channel teaching is evidence-only and weighted by a
fixed reliability score estimated *only on training bytes before learning*.
Validation never changes peer weights.

The expensive semantic fields, graph, translators and projections are built once.
The second training arm is expanded into a grid over peer_lambda values so all
candidates share the same cached inputs and initialization.

Exploratory curriculum smoke only; not Stage A/B confirmatory evidence.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

# v3 installs the device-safe per-(encoder, scale) adapter bundle into v1.
import smoke_coupled_flavour_translation_gpu_v3 as v3  # noqa: F401
import smoke_coupled_flavour_translation_gpu as v1


GRID = (0.05, 0.10, 0.25, 0.50)
_PEER_WEIGHTS: torch.Tensor | None = None
_PEER_REPORT: list[dict] | None = None


def _training_reliability(*, spaces, direct_fields, train_indices, examples, pos_weight, device):
    """Fixed per-channel reliability from pre-learning training bytes only.

    We score each initial local flavour with balanced BCE.  Reliability is
    exp(-balanced_bce), then normalized to mean 1.0.  This is intentionally
    simple, deterministic and label-grounded; no validation bytes are consulted.
    """
    raw = []
    details = []
    pos_weight_t = torch.tensor([float(pos_weight)], dtype=torch.float32, device=device)
    for channel_index, space in enumerate(spaces):
        logits_all = []
        targets_all = []
        flavour = torch.as_tensor(space["initial"], dtype=torch.float32, device=device)
        flavour = flavour / torch.linalg.vector_norm(flavour).clamp_min(1e-12)
        with torch.no_grad():
            for example_index in train_indices:
                field = direct_fields[example_index][channel_index]
                unit = field / torch.linalg.vector_norm(field, dim=1, keepdim=True).clamp_min(1e-12)
                logits_all.append(6.0 * (unit @ flavour))
                targets_all.append(torch.as_tensor(
                    examples[example_index].mask[:, 0], dtype=torch.float32, device=device
                ))
            logits = torch.cat(logits_all)[:, None]
            target = torch.cat(targets_all)[:, None]
            bce = torch.nn.functional.binary_cross_entropy_with_logits(
                logits, target, pos_weight=pos_weight_t
            )
        bce_value = float(bce.detach().cpu())
        quality = math.exp(-bce_value)
        raw.append(quality)
        details.append({
            "encoder": space["encoder"],
            "scale": int(space["scale"]),
            "pretrain_balanced_bce": bce_value,
            "raw_reliability": quality,
        })

    mean = max(float(np.mean(raw)), 1e-12)
    normalized = [value / mean for value in raw]
    for row, value in zip(details, normalized, strict=True):
        row["normalized_weight"] = float(value)
    return torch.tensor(normalized, dtype=torch.float32, device=device), details


def _weighted_peer_loss(model, fields, target, pos_weight):
    if _PEER_WEIGHTS is None:
        raise RuntimeError("peer reliability weights not initialized")
    logits = v1._local_logits(model, fields)
    probs = torch.sigmoid(logits.detach())
    count = logits.shape[1]
    losses = []
    for index in range(count):
        if count == 1:
            teacher = target[:, 0]
        else:
            keep = torch.tensor([j for j in range(count) if j != index], device=logits.device)
            weights = _PEER_WEIGHTS[keep]
            peer = (probs[:, keep] * weights[None, :]).sum(dim=1) / weights.sum().clamp_min(1e-12)
            # Reward stays primary. Peer evidence is a secondary soft teacher.
            teacher = 0.65 * target[:, 0] + 0.35 * peer
        soft = torch.nn.functional.binary_cross_entropy_with_logits(logits[:, index], teacher)
        hard = torch.nn.functional.binary_cross_entropy_with_logits(
            logits[:, index:index + 1], target, pos_weight=pos_weight
        )
        losses.append(0.5 * soft + 0.5 * hard)
    return torch.stack(losses).mean()


_original_train = v1._train
_original_peer_loss = v1._peer_loss


def _grid_train(*, peer_lambda, initial_state, spaces, direct_fields, train_indices,
                val_indices, examples, encoders, translators, operator, input_weights,
                input_indices, whole_brain, readout_projection, epochs, lr,
                anchor_lambda, pos_weight, device):
    global _PEER_WEIGHTS, _PEER_REPORT

    # First call from v1.main is the independent control. Keep it byte-for-byte
    # equivalent to v3 except for the corrected output schema below.
    if float(peer_lambda) == 0.0:
        return _original_train(
            peer_lambda=0.0, initial_state=initial_state, spaces=spaces,
            direct_fields=direct_fields, train_indices=train_indices,
            val_indices=val_indices, examples=examples, encoders=encoders,
            translators=translators, operator=operator, input_weights=input_weights,
            input_indices=input_indices, whole_brain=whole_brain,
            readout_projection=readout_projection, epochs=epochs, lr=lr,
            anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
        )

    _PEER_WEIGHTS, _PEER_REPORT = _training_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, pos_weight=pos_weight, device=device,
    )
    v1._peer_loss = _weighted_peer_loss

    runs = {}
    for value in GRID:
        print(json.dumps({
            "event": "peer_grid_start",
            "peer_lambda": value,
            "peer_weights": _PEER_REPORT,
        }), flush=True)
        runs[f"{value:.2f}"] = _original_train(
            peer_lambda=float(value), initial_state=initial_state, spaces=spaces,
            direct_fields=direct_fields, train_indices=train_indices,
            val_indices=val_indices, examples=examples, encoders=encoders,
            translators=translators, operator=operator, input_weights=input_weights,
            input_indices=input_indices, whole_brain=whole_brain,
            readout_projection=readout_projection, epochs=epochs, lr=lr,
            anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
        )

    # Restore for hygiene in case this module is imported interactively.
    v1._peer_loss = _original_peer_loss
    return {
        "mode": "reliability_weighted_peer_grid",
        "peer_lambdas": list(GRID),
        "fixed_training_reliability": _PEER_REPORT,
        "by_lambda": runs,
    }


v1._train = _grid_train


def _output_path() -> Path:
    try:
        return Path(sys.argv[sys.argv.index("--output") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("--output is required for reliability-grid wrapper") from exc


def main() -> None:
    v1.main()
    path = _output_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema"] = "papers/malecns-peer-reliability-grid-smoke-v1"
    payload["claim_status"] = "exploratory peer-reliability grid; not Stage A/B evidence"
    payload["coupling_rule"] = (
        "leave-one-channel-out evidence weighted by fixed pre-learning training reliability; "
        "no validation leakage; no cross-space vector arithmetic"
    )
    payload["peer_grid"] = list(GRID)
    payload["provenance_note"] = (
        "supersedes the mislabeled v3 output schema only for new grid runs; prior v3 artifact remains immutable"
    )
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "reliability_grid_complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
