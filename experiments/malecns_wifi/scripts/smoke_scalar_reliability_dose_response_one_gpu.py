"""Single-seed scalar-reliability dose response on fresh seeds."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import smoke_coupled_flavour_translation_gpu_v3 as v3  # noqa: F401
import smoke_coupled_flavour_translation_gpu as v1
import smoke_peer_reliability_grid_gpu as grid

_base_train = grid._original_train
_base_peer_loss = grid._original_peer_loss
LAMBDAS = (0.05, 0.10, 0.25, 0.50)


def _dose_train(*, peer_lambda, initial_state, spaces, direct_fields, train_indices,
                val_indices, examples, encoders, translators, operator, input_weights,
                input_indices, whole_brain, readout_projection, epochs, lr,
                anchor_lambda, pos_weight, device):
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

    weights, report = grid._training_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, pos_weight=pos_weight, device=device,
    )
    grid._PEER_WEIGHTS = weights
    grid._PEER_REPORT = report
    v1._peer_loss = grid._weighted_peer_loss

    arms = {}
    for value in LAMBDAS:
        arms[f"reliability_{value:.2f}"] = _base_train(
            peer_lambda=value, initial_state=initial_state, spaces=spaces,
            direct_fields=direct_fields, train_indices=train_indices,
            val_indices=val_indices, examples=examples, encoders=encoders,
            translators=translators, operator=operator, input_weights=input_weights,
            input_indices=input_indices, whole_brain=whole_brain,
            readout_projection=readout_projection, epochs=epochs, lr=lr,
            anchor_lambda=anchor_lambda, pos_weight=pos_weight, device=device,
        )

    v1._peer_loss = _base_peer_loss
    return {
        "mode": "scalar_reliability_dose_response",
        "fixed_training_reliability": report,
        **arms,
    }


v1._train = _dose_train


def _output_path() -> Path:
    try:
        return Path(sys.argv[sys.argv.index("--output") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("--output is required") from exc


def main() -> None:
    v1.main()
    path = _output_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema"] = "papers/malecns-scalar-reliability-dose-response-single-v1"
    payload["claim_status"] = "preregistered coupling-strength mapping; not Stage A/B"
    payload["dose_response_lambdas"] = list(LAMBDAS)
    payload["dose_response_arms"] = ["independent"] + [f"reliability_{x:.2f}" for x in LAMBDAS]
    payload["preregistration"] = "preregistered-scalar-reliability-dose-response-2026-09-15.md"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "scalar_reliability_dose_response_single_complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
