"""Hierarchical semantic channels for feeding several notions of context at once.

A semantic channel is not an absolute embedding. It is a relation measured *within
one encoder space* between a smaller span and a containing larger span. Different
channels may use different encoders and different scale pairs; their raw axes never
need to be compared.

Example channel bundle::

    qwen:    R(256 | 1024)
    minilm:  R(64  | 256)
    tiny:    R(byte-window | 64)

A finer scale may also have several ancestors at once, e.g. R(256|512) and
R(256|1024). Each pair is a separate sensory channel. This is the operational
version of "every level tastes like its relation to the levels above it".

The channels are energy-normalised independently and can be projected into
separate sensory sub-populations or summed through independent projections. The
combined drive is finally re-scaled to a fixed total RMS, so adding another
semantic channel cannot win merely by injecting more current.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .semantic_hierarchy import parent_relation


@dataclass(frozen=True)
class RelationChannel:
    """One aligned child/ancestor relation measured inside one encoder space."""

    name: str
    encoder: str
    child_scale: int
    parent_scale: int
    values: np.ndarray

    @property
    def width(self) -> int:
        return int(self.values.shape[1])


@dataclass(frozen=True)
class ChannelBundle:
    """Several heterogeneous relation channels aligned to the same fine positions."""

    channels: tuple[RelationChannel, ...]
    rows: int

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(channel.name for channel in self.channels)


def relation_channel(
    *,
    name: str,
    encoder: str,
    child_scale: int,
    parent_scale: int,
    child_embeddings: np.ndarray,
    parent_embeddings: np.ndarray,
) -> RelationChannel:
    """Build one relation channel.

    The two embedding arrays must come from the *same encoder*. Across channels,
    dimensions and encoder families may differ freely. This keeps every geometric
    relation meaningful without requiring MiniLM axes to line up with Qwen axes.
    """
    if child_scale >= parent_scale:
        raise ValueError("child_scale must be smaller than parent_scale")
    child = np.asarray(child_embeddings, dtype=np.float32)
    parent = np.asarray(parent_embeddings, dtype=np.float32)
    if child.shape != parent.shape:
        raise ValueError(
            "within one relation channel child and parent must be aligned embeddings "
            "from the same encoder"
        )
    values = parent_relation(child, parent).vector.astype(np.float32, copy=False)
    return RelationChannel(
        name=name,
        encoder=encoder,
        child_scale=int(child_scale),
        parent_scale=int(parent_scale),
        values=values,
    )


def bundle_channels(*channels: RelationChannel) -> ChannelBundle:
    """Align heterogeneous channels without forcing them into a shared embedding space."""
    if not channels:
        raise ValueError("at least one semantic channel is required")
    rows = channels[0].values.shape[0]
    if any(channel.values.shape[0] != rows for channel in channels):
        raise ValueError("all channels must be aligned to the same fine positions")
    names = [channel.name for channel in channels]
    if len(set(names)) != len(names):
        raise ValueError("channel names must be unique")
    return ChannelBundle(channels=tuple(channels), rows=int(rows))


def unit_channel(values: np.ndarray) -> np.ndarray:
    """Give each semantic channel unit row energy before sensory projection."""
    array = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return array / np.maximum(norms, 1e-12)


def concatenated_view(bundle: ChannelBundle) -> tuple[np.ndarray, tuple[tuple[int, int], ...]]:
    """Convenience view for direct probes; preserves channel boundaries.

    This does *not* assert that encoder coordinates are comparable. It merely places
    independently normalised channel coordinates side-by-side for a downstream
    model, exactly as concatenating image/audio feature channels does.
    """
    pieces = []
    slices = []
    offset = 0
    for channel in bundle.channels:
        values = unit_channel(channel.values)
        pieces.append(values)
        end = offset + values.shape[1]
        slices.append((offset, end))
        offset = end
    return np.concatenate(pieces, axis=1), tuple(slices)


def project_channels(
    bundle: ChannelBundle,
    projections: dict[str, np.ndarray],
    *,
    target_total_rms: float = 0.05,
    channel_weights: dict[str, float] | None = None,
) -> tuple[np.ndarray, dict]:
    """Mix all semantic channels into one simultaneous sensory drive.

    Each projection has shape ``[sensory_neurons, channel_width]``. Channels are
    independently projected and weighted, then summed. The final matrix is scaled
    to ``target_total_rms`` across rows and time, so more channels do not mean more
    electrical energy.

    The returned diagnostics expose each channel's pre-mix RMS and final total RMS.
    A future learned mixer may train ``channel_weights``; the first controlled run
    should keep them fixed (normally equal) so the substrate, not a powerful mixer,
    gets the opportunity to combine the channels.
    """
    if target_total_rms <= 0:
        raise ValueError("target_total_rms must be positive")
    weights = channel_weights or {channel.name: 1.0 for channel in bundle.channels}
    mixed = None
    per_channel = {}
    for channel in bundle.channels:
        if channel.name not in projections:
            raise ValueError(f"missing projection for channel {channel.name!r}")
        projection = np.asarray(projections[channel.name], dtype=np.float32)
        values = unit_channel(channel.values)
        if projection.ndim != 2 or projection.shape[1] != values.shape[1]:
            raise ValueError(
                f"projection for {channel.name!r} has shape {projection.shape}, "
                f"expected [sensory, {values.shape[1]}]"
            )
        drive = projection @ values.T
        weight = float(weights.get(channel.name, 1.0))
        drive = drive * np.float32(weight)
        per_channel[channel.name] = float(np.sqrt(np.mean(drive * drive)))
        mixed = drive if mixed is None else mixed + drive

    total_rms = float(np.sqrt(np.mean(mixed * mixed)))
    scale = target_total_rms / max(total_rms, 1e-12)
    mixed = (mixed * np.float32(scale)).astype(np.float32, copy=False)
    return mixed, {
        "channel_rms_before_mix": per_channel,
        "pre_scale_total_rms": total_rms,
        "scale": float(scale),
        "realised_total_rms": float(np.sqrt(np.mean(mixed * mixed))),
        "target_total_rms": float(target_total_rms),
    }
