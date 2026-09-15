from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


def _torch():
    import torch

    return torch


def build_hash_projection(neurons: int, features: int, *, seed: int, device: str):
    """Map every MaleCNS neuron into a deterministic signed feature pool.

    This is a fixed, non-trainable compression used only to make a full-screen
    decoder computationally tractable.  Every neuron contributes to exactly one
    pooled feature with a deterministic +/- sign.
    """
    if neurons < 1 or features < 1:
        raise ValueError("neurons/features must be >= 1")
    torch = _torch()
    rng = np.random.default_rng(seed)
    bins_np = rng.integers(0, features, size=neurons, dtype=np.int64)
    signs_np = rng.choice(np.asarray([-1.0, 1.0], dtype=np.float32), size=neurons)
    counts_np = np.bincount(bins_np, minlength=features).astype(np.float32)
    counts_np = np.maximum(counts_np, 1.0)
    return (
        torch.from_numpy(bins_np).to(device=device, dtype=torch.long),
        torch.from_numpy(signs_np).to(device=device, dtype=torch.float32),
        torch.from_numpy(counts_np).to(device=device, dtype=torch.float32),
    )


def project_generator_state(state, bins, signs, counts, *, gain: float = 200.0):
    """Signed hash-pool the full generator state into bounded decoder features."""
    torch = _torch()
    state = state.to(torch.float32).reshape(-1)
    pooled = torch.zeros_like(counts)
    pooled.index_add_(0, bins, state * signs)
    pooled = pooled / torch.sqrt(counts)
    return torch.tanh(float(gain) * pooled)


def normalize_frame_mean(frame, target: float, *, iterations: int = 32):
    """Constrain emitted screen luminance, not retinal energy."""
    torch = _torch()
    target = float(target)
    if not 0.0 <= target <= 1.0:
        raise ValueError("target must be in [0,1]")
    out = torch.clamp(frame.to(torch.float32), 0.0, 1.0)
    if target == 0.0:
        return torch.zeros_like(out)
    for _ in range(max(1, int(iterations))):
        current = torch.clamp(out.mean(), min=1e-12)
        out = torch.clamp(out * (target / current), 0.0, 1.0)
    return out


def project_screen_to_receptors(
    frame,
    *,
    receptor_x,
    receptor_y,
    resolved_mask,
    x,
    y,
    heading,
    physical_width: float,
    target_fov_rad: float,
    ambient: float = 0.0,
):
    """Project one physical 16:9 screen frame onto resolved retinal receptors.

    `frame` lives in physical screen coordinates.  Receiver pose determines its
    angular aperture.  Sampling is bilinear and zero outside the screen.  Room
    ambient is a uniform retinal floor applied after screen transport.
    """
    torch = _torch()
    import torch.nn.functional as F

    if frame.ndim != 2:
        raise ValueError("frame must be HxW")
    if physical_width <= 0 or target_fov_rad <= 0:
        raise ValueError("physical_width/target_fov_rad must be > 0")
    ambient = float(ambient)
    if not 0.0 <= ambient <= 1.0:
        raise ValueError("ambient must be in [0,1]")

    x = x.to(torch.float64).reshape(-1)
    y = y.to(torch.float64).reshape(-1)
    heading = heading.to(torch.float64).reshape(-1)
    flies = int(x.numel())
    distance = torch.clamp(torch.hypot(x, y), min=1e-9)
    bearing = torch.remainder(torch.atan2(-y, -x) - heading + torch.pi, 2 * torch.pi) - torch.pi
    angular_width = 2.0 * torch.atan2(
        torch.full_like(distance, float(physical_width / 2.0)),
        distance,
    )
    center_x = bearing / float(target_fov_rad)
    half_x = torch.clamp(0.5 * angular_width / float(target_fov_rad), min=1e-6)
    half_y = torch.clamp(half_x * (9.0 / 16.0), min=1e-6)

    rx = receptor_x.to(device=frame.device, dtype=torch.float64)[:, None]
    ry = receptor_y.to(device=frame.device, dtype=torch.float64)[:, None]
    u = (rx - center_x[None, :]) / half_x[None, :]
    v = ry / half_y[None, :]
    # grid_sample expects N x Hout x Wout x 2 with coordinates in [-1,1].
    grid = torch.stack((u, v), dim=-1).permute(1, 0, 2).unsqueeze(2).to(torch.float32)
    image = frame.to(torch.float32)[None, None, :, :].expand(flies, 1, -1, -1)
    sampled = F.grid_sample(
        image,
        grid,
        mode="bilinear",
        padding_mode="zeros",
        align_corners=True,
    )[:, 0, :, 0].T.contiguous()
    resolved = resolved_mask.to(device=frame.device, dtype=torch.float32)[:, None]
    screen = sampled * resolved
    return (ambient + (1.0 - ambient) * screen) * resolved


def frame_ascii(frame, *, chars: str = " .:-=+*#%@") -> str:
    arr = frame.detach().cpu().numpy() if hasattr(frame, "detach") else np.asarray(frame)
    arr = np.clip(arr, 0.0, 1.0)
    idx = np.rint(arr * (len(chars) - 1)).astype(np.int64)
    return "\n".join("".join(chars[i] for i in row) for row in idx)


@dataclass
class FullScreenPlasticDecoder:
    """Online reward-plastic decoder from pooled MaleCNS state to TV pixels."""

    weight: object
    eligibility: object
    baseline: float
    width: int
    height: int
    learning_rate: float = 0.001
    exploration_sigma: float = 0.05
    eligibility_decay: float = 0.95
    baseline_rate: float = 0.02
    weight_clip: float = 3.0

    @classmethod
    def fresh(
        cls,
        *,
        features: int,
        width: int,
        height: int,
        seed: int,
        device: str,
        init_scale: float = 0.02,
        **kwargs,
    ) -> "FullScreenPlasticDecoder":
        torch = _torch()
        rng = np.random.default_rng(seed)
        w = rng.normal(0.0, init_scale, size=(features, width * height)).astype(np.float32)
        weight = torch.from_numpy(w).to(device=device)
        return cls(
            weight=weight,
            eligibility=torch.zeros_like(weight),
            baseline=0.0,
            width=int(width),
            height=int(height),
            **kwargs,
        )

    @classmethod
    def from_weight(cls, weight, *, width: int, height: int, device: str, baseline: float = 0.0, **kwargs):
        torch = _torch()
        w = torch.as_tensor(weight, dtype=torch.float32, device=device).clone()
        if w.ndim != 2 or w.shape[1] != width * height:
            raise ValueError("weight shape does not match screen dimensions")
        return cls(
            weight=w,
            eligibility=torch.zeros_like(w),
            baseline=float(baseline),
            width=int(width),
            height=int(height),
            **kwargs,
        )

    @property
    def features(self) -> int:
        return int(self.weight.shape[0])

    @property
    def pixels(self) -> int:
        return int(self.width * self.height)

    def propose(self, features, noise):
        torch = _torch()
        features = features.to(device=self.weight.device, dtype=torch.float32).reshape(-1)
        noise = noise.to(device=self.weight.device, dtype=torch.float32).reshape(-1)
        if features.numel() != self.features or noise.numel() != self.pixels:
            raise ValueError("feature/noise shape mismatch")
        logits = features @ self.weight + float(self.exploration_sigma) * noise
        return torch.sigmoid(logits).reshape(self.height, self.width)

    def update(self, features, noise, reward: float) -> dict[str, float]:
        torch = _torch()
        features = features.to(device=self.weight.device, dtype=torch.float32).reshape(-1)
        noise = noise.to(device=self.weight.device, dtype=torch.float32).reshape(-1)
        reward = float(reward)
        advantage = reward - float(self.baseline)
        credit = torch.outer(features, noise)
        credit = credit / (float(self.exploration_sigma) * math.sqrt(max(self.features, 1)))
        self.eligibility.mul_(float(self.eligibility_decay)).add_(credit)
        self.weight.add_(float(self.learning_rate) * advantage * self.eligibility)
        self.weight.clamp_(-float(self.weight_clip), float(self.weight_clip))
        self.baseline += float(self.baseline_rate) * (reward - float(self.baseline))
        return {
            "reward": reward,
            "advantage": float(advantage),
            "baseline": float(self.baseline),
            "weight_norm": float(torch.linalg.vector_norm(self.weight).detach().cpu()),
            "eligibility_norm": float(torch.linalg.vector_norm(self.eligibility).detach().cpu()),
        }
