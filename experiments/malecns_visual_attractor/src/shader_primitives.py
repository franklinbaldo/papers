from __future__ import annotations

import math


def _torch():
    import torch
    return torch


PRIMITIVES = (
    "blob",
    "ring",
    "horizontal_wave",
    "vertical_wave",
    "diagonal_wave",
    "checker",
    "radial_rings",
    "spokes",
    "looming_disk",
    "swirl",
    "global_pulse",
    "oscilloscope",
)
PARAMS_PER_PRIMITIVE = 5
CONTROL_DIM = len(PRIMITIVES) * (1 + PARAMS_PER_PRIMITIVE)


def _grid(width: int, height: int, *, device: str):
    torch = _torch()
    yy = torch.linspace(-1.0, 1.0, height, device=device)
    xx = torch.linspace(-1.0, 1.0, width, device=device)
    y, x = torch.meshgrid(yy, xx, indexing="ij")
    return x, y


def render_visual_primitives(controls, *, width: int = 64, height: int = 36, time_s: float = 0.0):
    """Render a weighted bank of general visual primitives from continuous controls.

    Each primitive receives one signed mixture weight and five bounded parameters.
    The renderer intentionally supplies structure but no hand-coded lure: evolution/
    plasticity must discover which primitives, weights, scales, phases and motion help.
    Output is grayscale in [0,1]; emitted-energy matching happens outside this module.
    """
    torch = _torch()
    c = torch.as_tensor(controls, dtype=torch.float32).reshape(-1)
    if c.numel() != CONTROL_DIM:
        raise ValueError(f"controls must have {CONTROL_DIM} entries")
    device = str(c.device)
    x, y = _grid(width, height, device=device)
    rows = c.reshape(len(PRIMITIVES), 1 + PARAMS_PER_PRIMITIVE)
    weights = torch.tanh(rows[:, 0])
    p = torch.tanh(rows[:, 1:])
    accum = torch.zeros((height, width), device=c.device, dtype=torch.float32)
    total = torch.zeros((), device=c.device, dtype=torch.float32)

    for i, name in enumerate(PRIMITIVES):
        a, b, d, e, f = p[i]
        phase = math.pi * float(time_s) * (0.4 + 2.6 * (d + 1.0) * 0.5) + math.pi * f
        cx, cy = 0.75 * a, 0.75 * b
        scale = 0.12 + 0.70 * (e + 1.0) * 0.5
        freq = 1.0 + 7.0 * (d + 1.0) * 0.5
        dx, dy = x - cx, y - cy
        r = torch.sqrt(dx * dx + dy * dy + 1e-8)
        theta = torch.atan2(dy, dx)

        if name == "blob":
            v = torch.exp(-0.5 * (r / scale) ** 2)
        elif name == "ring":
            radius = 0.15 + 0.65 * (d + 1.0) * 0.5
            v = torch.exp(-0.5 * ((r - radius) / (0.04 + 0.16 * scale)) ** 2)
        elif name == "horizontal_wave":
            v = 0.5 + 0.5 * torch.sin(freq * math.pi * y + phase)
        elif name == "vertical_wave":
            v = 0.5 + 0.5 * torch.sin(freq * math.pi * x + phase)
        elif name == "diagonal_wave":
            angle = math.pi * a
            axis = torch.cos(angle) * x + torch.sin(angle) * y
            v = 0.5 + 0.5 * torch.sin(freq * math.pi * axis + phase)
        elif name == "checker":
            v = 0.5 + 0.5 * torch.tanh(3.0 * torch.sin(freq * math.pi * x + phase) * torch.sin(freq * math.pi * y + phase))
        elif name == "radial_rings":
            v = 0.5 + 0.5 * torch.sin(freq * math.pi * r + phase)
        elif name == "spokes":
            v = 0.5 + 0.5 * torch.sin(freq * theta + phase)
        elif name == "looming_disk":
            radius = torch.clamp(torch.tensor(0.08 + 0.75 * ((math.sin(phase) + 1.0) * 0.5), device=c.device), 0.04, 0.9)
            v = torch.sigmoid((radius - r) * (12.0 + 25.0 * scale))
        elif name == "swirl":
            v = 0.5 + 0.5 * torch.sin(freq * theta + (2.0 + 7.0 * scale) * r + phase)
        elif name == "global_pulse":
            v = torch.full_like(x, 0.5 + 0.5 * math.sin(phase))
        elif name == "oscilloscope":
            trace = 0.45 * torch.sin(freq * math.pi * x + phase) + cy
            thickness = 0.025 + 0.10 * scale
            v = torch.exp(-0.5 * ((y - trace) / thickness) ** 2)
        else:
            raise AssertionError(name)

        w = weights[i]
        accum = accum + w * (2.0 * v - 1.0)
        total = total + torch.abs(w)

    normalized = accum / torch.clamp(total, min=1.0)
    return torch.clamp(0.5 + 0.5 * normalized, 0.0, 1.0)


def primitive_manifest() -> dict:
    return {
        "primitives": list(PRIMITIVES),
        "params_per_primitive": PARAMS_PER_PRIMITIVE,
        "control_dim": CONTROL_DIM,
        "composition": "learned signed weights; continuous position/scale/frequency/phase parameters",
        "output": "grayscale shader frame before equal-energy normalization",
    }
