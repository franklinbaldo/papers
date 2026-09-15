"""Single-seed directed peer-gain comparison.

Compares independent learning, scalar per-channel reliability, and a fixed
training-only directed sender->receiver teaching matrix.  No inference-time
attention/router is added; MaleCNS remains the multimodal integrator.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

import smoke_coupled_flavour_translation_gpu_v3 as v3  # noqa: F401
import smoke_coupled_flavour_translation_gpu as v1
import smoke_peer_reliability_grid_gpu as grid


_base_train = grid._original_train
_base_peer_loss = grid._original_peer_loss
_DIRECTED_WEIGHTS: torch.Tensor | None = None
_DIRECTED_REPORT: list[dict] | None = None


def _training_directed_reliability(*, spaces, direct_fields, train_indices, examples, device):
    """Estimate fixed receiver-by-sender teaching gains from training bytes only."""
    targets = []
    channel_probs = [[] for _ in spaces]

    with torch.no_grad():
        for example_index in train_indices:
            target = torch.as_tensor(
                examples[example_index].mask[:, 0], dtype=torch.float32, device=device
            )
            targets.append(target)
            for channel_index, space in enumerate(spaces):
                field = direct_fields[example_index][channel_index]
                unit = field / torch.linalg.vector_norm(
                    field, dim=1, keepdim=True
                ).clamp_min(1e-12)
                flavour = torch.as_tensor(
                    space["initial"], dtype=torch.float32, device=device
                )
                flavour = flavour / torch.linalg.vector_norm(flavour).clamp_min(1e-12)
                channel_probs[channel_index].append(torch.sigmoid(6.0 * (unit @ flavour)))

        y = torch.cat(targets)[:, None]
        probs = torch.stack([torch.cat(parts) for parts in channel_probs], dim=1)
        error = (y - probs).abs().clamp(0.0, 1.0)
        need = error
        competence = 1.0 - error

        count = len(spaces)
        matrix = torch.zeros((count, count), dtype=torch.float32, device=device)
        report = []
        for receiver in range(count):
            raw = []
            senders = []
            for sender in range(count):
                if sender == receiver:
                    continue
                usefulness = (need[:, receiver] * competence[:, sender]).mean().clamp_min(1e-8)
                raw.append(usefulness)
                senders.append(sender)
            raw_t = torch.stack(raw)
            normalized = raw_t / raw_t.mean().clamp_min(1e-12)
            for sender, raw_value, normalized_value in zip(
                senders, raw_t, normalized, strict=True
            ):
                matrix[receiver, sender] = normalized_value
                report.append({
                    "receiver_encoder": spaces[receiver]["encoder"],
                    "receiver_scale": int(spaces[receiver]["scale"]),
                    "sender_encoder": spaces[sender]["encoder"],
                    "sender_scale": int(spaces[sender]["scale"]),
                    "raw_usefulness": float(raw_value.cpu()),
                    "normalized_weight": float(normalized_value.cpu()),
                })

    return matrix, report


def _directed_peer_loss(model, fields, target, pos_weight):
    if _DIRECTED_WEIGHTS is None:
        raise RuntimeError("directed peer weights not initialized")
    logits = v1._local_logits(model, fields)
    probs = torch.sigmoid(logits.detach())
    count = logits.shape[1]
    losses = []
    for receiver in range(count):
        if count == 1:
            teacher = target[:, 0]
        else:
            keep = torch.tensor(
                [sender for sender in range(count) if sender != receiver],
                dtype=torch.long,
                device=logits.device,
            )
            weights = _DIRECTED_WEIGHTS[receiver, keep]
            peer = (probs[:, keep] * weights[None, :]).sum(dim=1) / weights.sum().clamp_min(1e-12)
            teacher = 0.65 * target[:, 0] + 0.35 * peer
        soft = torch.nn.functional.binary_cross_entropy_with_logits(
            logits[:, receiver], teacher
        )
        hard = torch.nn.functional.binary_cross_entropy_with_logits(
            logits[:, receiver:receiver + 1], target, pos_weight=pos_weight
        )
        losses.append(0.5 * soft + 0.5 * hard)
    return torch.stack(losses).mean()


def _directed_train(*, peer_lambda, initial_state, spaces, direct_fields, train_indices,
                    val_indices, examples, encoders, translators, operator, input_weights,
                    input_indices, whole_brain, readout_projection, epochs, lr,
                    anchor_lambda, pos_weight, device):
    global _DIRECTED_WEIGHTS, _DIRECTED_REPORT

    if float(peer_lambda) == 0.0:
        v1._peer_loss = _base_peer_loss
        return _base_train(
            peer_lambda=0.0, initial_state=initial_state, spaces=spaces,
            direct_fields=direct_fields, train_indices=train_indices,
            val_indices=val_indices, examples=examples, encoders=encoders,
            translators=translators, operator=operator, input_weights=input_weights,
            input_indices=input_indices, whole_brain=whole_brain,
            readout_projection=readout_projection, epochs=epochs, lr=lr,
            anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
        )

    if abs(float(peer_lambda) - 0.50) > 1e-9:
        raise RuntimeError(f"directed-gain protocol requires peer_lambda=0.50, got {peer_lambda}")

    scalar_weights, scalar_report = grid._training_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, pos_weight=pos_weight, device=device,
    )
    grid._PEER_WEIGHTS = scalar_weights
    grid._PEER_REPORT = scalar_report
    v1._peer_loss = grid._weighted_peer_loss
    scalar = _base_train(
        peer_lambda=0.50, initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices,
        val_indices=val_indices, examples=examples, encoders=encoders,
        translators=translators, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, epochs=epochs, lr=lr,
        anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
    )

    _DIRECTED_WEIGHTS, _DIRECTED_REPORT = _training_directed_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, device=device,
    )
    v1._peer_loss = _directed_peer_loss
    directed = _base_train(
        peer_lambda=0.50, initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices,
        val_indices=val_indices, examples=examples, encoders=encoders,
        translators=translators, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, epochs=epochs, lr=lr,
        anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
    )

    v1._peer_loss = _base_peer_loss
    return {
        "mode": "directed_peer_gain_comparison_lambda_0.50",
        "scalar_training_reliability": scalar_report,
        "directed_training_matrix": _DIRECTED_REPORT,
        "scalar_reliability_0.50": scalar,
        "directed_reliability_0.50": directed,
    }


v1._train = _directed_train


def _output_path() -> Path:
    try:
        return Path(sys.argv[sys.argv.index("--output") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("--output is required") from exc


def main() -> None:
    v1.main()
    path = _output_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema"] = "papers/malecns-directed-peer-gains-single-v1"
    payload["claim_status"] = "preregistered directed-teaching curriculum evidence; not Stage A/B"
    payload["replication_lambda"] = 0.50
    payload["comparison_arms"] = [
        "independent", "scalar_reliability_0.50", "directed_reliability_0.50"
    ]
    payload["preregistration"] = "preregistered-directed-peer-gains-2026-09-15.md"
    payload["coupling_rule"] = (
        "training-only cross-channel teaching; scalar reliability versus fixed directed "
        "sender->receiver usefulness matrix; no inference-time attention/router"
    )
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "directed_peer_gain_single_complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
