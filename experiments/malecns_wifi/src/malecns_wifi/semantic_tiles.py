"""Reusable multiresolution semantic tiles for the flavour-pyramid experiment.

This module is deliberately encoder-agnostic. It decides *what* text spans should
be embedded, gives each span a stable content-addressed cache key, and records
how much encoder work can be reused. Actual encoders live elsewhere.

The key design constraint is that flavourizers operate downstream of this cache:
retraining flavourizers must not call an embedding model again.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

ChannelKey = tuple[int, str, str]


@dataclass(frozen=True)
class TileSpec:
    scale: int
    stride: int
    encoder_id: str
    encoder_revision: str
    normalisation_version: str = "v1"

    def __post_init__(self) -> None:
        if self.scale < 1:
            raise ValueError("scale must be >= 1")
        if self.stride < 1:
            raise ValueError("stride must be >= 1")
        if not self.encoder_id or not self.encoder_revision:
            raise ValueError("encoder_id and encoder_revision are required")

    @property
    def channel_key(self) -> ChannelKey:
        return (self.scale, self.encoder_id, self.encoder_revision)


@dataclass(frozen=True)
class Tile:
    start: int
    end: int
    text: str
    spec: TileSpec
    cache_key: str

    @property
    def width(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class PyramidPlan:
    """A frozen set of token-scale/encoder channels.

    The same scale may be observed by multiple encoders. That is intentional: Jina
    and MiniLM can both supply a 64-token channel, but relations are only formed
    inside one encoder/revision pair.
    """

    specs: tuple[TileSpec, ...]

    def __post_init__(self) -> None:
        keys = [item.channel_key for item in self.specs]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate scale/encoder/revision channel")
        scales = [item.scale for item in self.specs]
        if tuple(sorted(scales, reverse=True)) != tuple(scales):
            raise ValueError("specs must be ordered largest to smallest")


def tile_cache_key(text: str, spec: TileSpec) -> str:
    payload = "\0".join(
        [spec.encoder_id, spec.encoder_revision, spec.normalisation_version, text]
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def overlapping_tiles(tokens: list[str], spec: TileSpec) -> list[Tile]:
    if not tokens:
        return []
    result: list[Tile] = []
    for start in range(0, len(tokens), spec.stride):
        end = min(start + spec.scale, len(tokens))
        if start >= end:
            continue
        text = " ".join(tokens[start:end])
        result.append(
            Tile(start, end, text, spec, tile_cache_key(text, spec))
        )
        if end == len(tokens):
            break
    return result


def build_pyramid(tokens: list[str], plan: PyramidPlan) -> dict[ChannelKey, list[Tile]]:
    return {spec.channel_key: overlapping_tiles(tokens, spec) for spec in plan.specs}


def containing_tiles(child: Tile, parents: Iterable[Tile]) -> list[Tile]:
    matches = [item for item in parents if item.start <= child.start and item.end >= child.end]
    return sorted(matches, key=lambda item: (item.width, item.start))


def relation_pairs(pyramid: dict[ChannelKey, list[Tile]]) -> list[tuple[Tile, Tile]]:
    """Enumerate child->ancestor relations without ever crossing encoder spaces."""
    pairs: list[tuple[Tile, Tile]] = []
    channels = list(pyramid.items())
    for _, children in channels:
        for child in children:
            for _, parents in channels:
                if not parents:
                    continue
                parent_spec = parents[0].spec
                if parent_spec.scale <= child.spec.scale:
                    continue
                if (
                    parent_spec.encoder_id != child.spec.encoder_id
                    or parent_spec.encoder_revision != child.spec.encoder_revision
                ):
                    continue
                for parent in containing_tiles(child, parents):
                    pairs.append((child, parent))
    return pairs


def cache_ledger(pyramids: Iterable[dict[ChannelKey, list[Tile]]]) -> dict:
    all_tiles: list[Tile] = []
    for pyramid in pyramids:
        for tiles in pyramid.values():
            all_tiles.extend(tiles)

    by_channel: dict[str, dict] = {}
    for channel in sorted(
        {tile.spec.channel_key for tile in all_tiles}, reverse=True
    ):
        rows = [tile for tile in all_tiles if tile.spec.channel_key == channel]
        unique = len({tile.cache_key for tile in rows})
        total = len(rows)
        scale, encoder, revision = channel
        name = f"{scale}:{encoder}@{revision}"
        by_channel[name] = {
            "scale": scale,
            "encoder": encoder,
            "revision": revision,
            "total": total,
            "unique": unique,
            "reused": total - unique,
            "reuse_fraction": (total - unique) / total if total else 0.0,
        }

    unique_all = len({tile.cache_key for tile in all_tiles})
    total_all = len(all_tiles)
    return {
        "total": total_all,
        "unique": unique_all,
        "reused": total_all - unique_all,
        "reuse_fraction": (total_all - unique_all) / total_all if total_all else 0.0,
        "by_channel": by_channel,
    }


def flavourizer_scales(mode: str, scales: Iterable[int]) -> tuple[int, ...]:
    ordered = tuple(sorted(set(scales), reverse=True))
    if mode == "none":
        return ()
    if mode == "high_only":
        return tuple(scale for scale in ordered if scale >= 128)
    if mode == "low_only":
        return tuple(scale for scale in ordered if scale <= 32)
    if mode == "all_scales":
        return ordered
    raise ValueError(f"unknown flavourizer mode {mode!r}")
