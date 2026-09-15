"""State-conditioned reliability-weighted peer coupling on one seed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

import smoke_coupled_flavour_translation_gpu_v3 as v3  # noqa: F401
import smoke_coupled_flavour_translation_gpu as v1
import smoke_concept_flavour_gpu as base
import smoke_peer_reliability_grid_gpu as grid
import semantic_embedding_cache as cachelib

_CACHE: Path | None = None
_MANIFEST = None
_ORIGINAL_TRAIN = grid._original_train
_ORIGINAL_PEER_LOSS = grid._original_peer_loss


def _pop(name: str) -> str:
    i = sys.argv.index(name)
    value = sys.argv[i + 1]
    del sys.argv[i:i + 2]
    return value


def _cached_prepare(model_names, examples, scales, device):
    del device
    global _MANIFEST
    encoders, _MANIFEST = cachelib.load_cache(
        model_names=model_names, examples=examples, scales=scales, cache=_CACHE
    )
    return encoders


def _adaptive_train(*, mode, initial_state, spaces, direct_fields, train_indices,
                    val_indices, examples, encoders, translators, operator, input_weights,
                    input_indices, whole_brain, readout_projection, epochs, lr,
                    anchor_lambda, pos_weight, device):
    model = v1.FlavourBundle(
        [space["initial"] for space in spaces], readout_projection.shape[0], device=device
    )
    model.load_state_dict(initial_state)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    pos_weight_t = torch.tensor([float(pos_weight)], dtype=torch.float32, device=device)
    curve = []

    for epoch in range(epochs):
        losses, taste_losses, peer_losses, lambdas = [], [], [], []
        for example_index in train_indices:
            optimizer.zero_grad(set_to_none=True)
            fields = direct_fields[example_index]
            logits, drive = v1._reservoir_logits(
                model, fields, operator, input_weights, input_indices,
                whole_brain, readout_projection,
            )
            target = torch.as_tensor(
                examples[example_index].mask, dtype=torch.float32, device=device
            )
            taste = torch.nn.functional.binary_cross_entropy_with_logits(
                logits, target, pos_weight=pos_weight_t
            )
            peers = grid._weighted_peer_loss(model, fields, target, pos_weight_t)

            p_state = torch.sigmoid(logits.detach()[:, 0])
            if mode == "state_uncertainty":
                gate = (4.0 * p_state * (1.0 - p_state)).mean()
            elif mode == "state_reward_error":
                gate = torch.abs(target[:, 0] - p_state).mean()
            else:
                raise ValueError(mode)
            lambda_eff = 0.50 * gate.clamp(0.0, 1.0)

            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            loss = taste + lambda_eff * peers + anchor_lambda * anchor
            loss.backward()
            preclip = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            optimizer.step()

            losses.append(float(loss.detach().cpu()))
            taste_losses.append(float(taste.detach().cpu()))
            peer_losses.append(float(peers.detach().cpu()))
            lambdas.append(float(lambda_eff.detach().cpu()))

        validation = {}
        arms = ["all_direct", "no_128"]
        if len(encoders) >= 2:
            arms += ["no_encoder_0", "no_encoder_1"]
        arms += ["minilm_short_only"]
        for arm in arms:
            validation[arm] = v1._score_model(
                model, arm=arm, encoders=encoders, spaces=spaces,
                direct_fields=direct_fields, translators=translators,
                val_indices=val_indices, examples=examples, operator=operator,
                input_weights=input_weights, input_indices=input_indices,
                whole_brain=whole_brain, readout_projection=readout_projection,
                device=device,
            )

        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "taste_bce": float(np.mean(taste_losses)),
            "peer_loss": float(np.mean(peer_losses)),
            "lambda_eff_mean": float(np.mean(lambdas)),
            "lambda_eff_min": float(np.min(lambdas)),
            "lambda_eff_max": float(np.max(lambdas)),
            "preclip_grad_norm_last": preclip,
            "validation": validation,
            "flavours": v1._flavour_report(model, spaces),
        }
        print(json.dumps({"event": "epoch", "arm": mode, **row}), flush=True)
        curve.append(row)

    return {"curve": curve, "final_flavours": v1._flavour_report(model, spaces)}


def _state_train(*, peer_lambda, initial_state, spaces, direct_fields, train_indices,
                 val_indices, examples, encoders, translators, operator, input_weights,
                 input_indices, whole_brain, readout_projection, epochs, lr,
                 anchor_lambda, pos_weight, device):
    if float(peer_lambda) == 0.0:
        v1._peer_loss = _ORIGINAL_PEER_LOSS
        return _ORIGINAL_TRAIN(
            peer_lambda=0.0, initial_state=initial_state, spaces=spaces,
            direct_fields=direct_fields, train_indices=train_indices,
            val_indices=val_indices, examples=examples, encoders=encoders,
            translators=translators, operator=operator, input_weights=input_weights,
            input_indices=input_indices, whole_brain=whole_brain,
            readout_projection=readout_projection, epochs=epochs, lr=lr,
            anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
        )

    weights, report = grid._training_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, pos_weight=pos_weight, device=device,
    )
    grid._PEER_WEIGHTS = weights
    grid._PEER_REPORT = report
    v1._peer_loss = grid._weighted_peer_loss

    static = _ORIGINAL_TRAIN(
        peer_lambda=0.50, initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices,
        val_indices=val_indices, examples=examples, encoders=encoders,
        translators=translators, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, epochs=epochs, lr=lr,
        anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
    )
    uncertainty = _adaptive_train(
        mode="state_uncertainty", initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices,
        val_indices=val_indices, examples=examples, encoders=encoders,
        translators=translators, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, epochs=epochs, lr=lr,
        anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
    )
    reward_error = _adaptive_train(
        mode="state_reward_error", initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices,
        val_indices=val_indices, examples=examples, encoders=encoders,
        translators=translators, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, epochs=epochs, lr=lr,
        anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
    )
    v1._peer_loss = _ORIGINAL_PEER_LOSS
    return {
        "mode": "state_conditioned_peer_coupling",
        "fixed_training_reliability": report,
        "static_0.50": static,
        "state_uncertainty": uncertainty,
        "state_reward_error": reward_error,
    }


v1._train = _state_train


def main() -> None:
    global _CACHE
    _CACHE = Path(_pop("--embedding-cache"))
    base._prepare_encoders = _cached_prepare
    v1.main()
    out = Path(sys.argv[sys.argv.index("--output") + 1])
    payload = json.loads(out.read_text(encoding="utf-8"))
    payload["schema"] = "papers/malecns-state-conditioned-coupling-single-v1"
    payload["claim_status"] = "preregistered exploratory state-conditioned coupling; not Stage A/B"
    payload["preregistration"] = "preregistered-state-conditioned-coupling-2026-09-15.md"
    payload["embedding_cache"] = {
        "fingerprint": _MANIFEST["fingerprint"],
        "backend": _MANIFEST["backend"],
        "device": _MANIFEST["device"],
    }
    payload["encoder_forward_during_training"] = False
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
