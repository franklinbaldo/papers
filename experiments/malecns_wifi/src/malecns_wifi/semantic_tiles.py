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
    """A frozen set of token-scale channels.

    Tokenization itself is intentionally external: callers pass a sequence of
    already-tokenized string units so changing a tokenizer cannot silently change
    the experiment under the same plan.
    """

    specs: tuple[TileSpec, ...]

    def __post_init__(self) -> None:
        scales = [item.scale for item in self.specs]
        if len(scales) != len(set(scales)):
            raise ValueError("one TileSpec per scale in a PyramidPlan")
        if tuple(sorted(scales, reverse=True)) != tuple(scales):
            raise ValueError("specs must be ordered largest to smallest")


def tile_cache_key(text: str, spec: TileSpec) -> str:
    """Stable content-addressed identity for one encoder input."""
    payload = "\0".join(
        [
            spec.encoder_id,
            spec.encoder_revision,
            spec.normalisation_version,
            text,
        ]
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def overlapping_tiles(tokens: list[str], spec: TileSpec) -> list[Tile]:
    """Generate deterministic overlapping tiles, including the final short tail.

    The span coordinates are in caller-provided token units. Joining uses a single
    space because the protocol's cache identity must depend on the exact text sent
    to the encoder; callers needing byte-exact reconstruction should pass units and
    a normalisation version that encode that policy explicitly.
    """
    if not tokens:
        return []
    result: list[Tile] = []
    seen: set[tuple[int, int]] = set()
    starts = list(range(0, len(tokens), spec.stride))
    for start in starts:
        end = min(start + spec.scale, len(tokens))
        if start >= end:
            continue
        span = (start, end)
        if span in seen:
            continue
        seen.add(span)
        text = " ".join(tokens[start:end])
        result.append(
            Tile(
                start=start,
                end=end,
                text=text,
                spec=spec,
                cache_key=tile_cache_key(text, spec),
            )
        )
        if end == len(tokens):
            break
    return result


def build_pyramid(tokens: list[str], plan: PyramidPlan) -> dict[int, list[Tile]]:
    return {spec.scale: overlapping_tiles(tokens, spec) for spec in plan.specs}


def containing_tiles(child: Tile, parents: Iterable[Tile]) -> list[Tile]:
    """All larger tiles that fully contain ``child``, nearest parent first."""
    matches = [item for item in parents if item.start <= child.start and item.end >= child.end]
    return sorted(matches, key=lambda item: (item.width, item.start))


def relation_pairs(pyramid: dict[int, list[Tile]]) -> list[tuple[Tile, Tile]]:
    """Enumerate child->ancestor relations across all declared scales.

    This deliberately permits redundant ancestors: a 64-token tile may be related
    both to its containing 128 and 256 tiles. Each pair remains within the child's
    encoder family only when the two TileSpecs share encoder id/revision; cross-
    encoder relations are excluded rather than projected into a fake common space.
    """
    scales = sorted(pyramid, reverse=True)
    pairs: list[tuple[Tile, Tile]] = []
    for child_scale in reversed(scales):
        for child in pyramid[child_scale]:
            for parent_scale in scales:
                if parent_scale <= child_scale:
                    continue
                for parent in containing_tiles(child, pyramid[parent_scale]):
                    if (
                        parent.spec.encoder_id == child.spec.encoder_id
                        and parent.spec.encoder_revision == child.spec.encoder_revision
                    ):
                        pairs.append((child, parent))
    return pairs


def cache_ledger(pyramids: Iterable[dict[int, list[Tile]]]) -> dict:
    """Count total/unique encoder inputs and exact reuse by scale and globally."""
    all_tiles: list[Tile] = []
    for pyramid in pyramids:
        for tiles in pyramid.values():
            all_tiles.extend(tiles)

    by_scale: dict[int, dict] = {}
    for scale in sorted({tile.spec.scale for tile in all_tiles}, reverse=True):
        rows = [tile for tile in all_tiles if tile.spec.scale == scale]
        unique = len({tile.cache_key for tile in rows})
        total = len(rows)
        by_scale[scale] = {
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
        "by_scale": by_scale,
    }


def flavourizer_scales(mode: str, scales: Iterable[int]) -> tuple[int, ...]:
    """Freeze the four confirmatory flavour-placement arms."""
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
