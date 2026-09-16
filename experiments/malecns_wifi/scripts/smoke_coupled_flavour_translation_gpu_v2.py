"""Device-safe entrypoint for the coupled flavour translation smoke.

Keeps the v1 experiment intact for provenance, fixes the taste-head device bug,
and adds a pre-forward device invariant so a CPU/CUDA split fails immediately.
"""

from __future__ import annotations

import smoke_coupled_flavour_translation_gpu as v1


class DeviceSafeFlavourBundle(v1.FlavourBundle):
    def __init__(self, initial_flavours, readout_width, *, device):
        super().__init__(initial_flavours, readout_width, device=device)
        self.taste_head = self.taste_head.to(device)


_original_reservoir_logits = v1._reservoir_logits


def _device_checked_reservoir_logits(
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
    field_device = fields[0].device
    parameter_devices = {parameter.device for parameter in model.parameters()}
    if parameter_devices != {field_device}:
        raise RuntimeError(
            f"coupled smoke device invariant failed: fields={field_device}, "
            f"model_parameters={sorted(map(str, parameter_devices))}"
        )
    return _original_reservoir_logits(
        model,
        fields,
        operator,
        input_weights,
        input_indices,
        whole_brain,
        readout_projection,
        target_rms=target_rms,
    )


v1.FlavourBundle = DeviceSafeFlavourBundle
v1._reservoir_logits = _device_checked_reservoir_logits


if __name__ == "__main__":
    v1.main()
