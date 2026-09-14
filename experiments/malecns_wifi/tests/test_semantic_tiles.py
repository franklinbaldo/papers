from malecns_wifi.semantic_tiles import (
    PyramidPlan,
    TileSpec,
    build_pyramid,
    cache_ledger,
    flavourizer_scales,
    relation_pairs,
    tile_cache_key,
)


def _spec(scale: int, encoder: str = "enc", revision: str = "r1") -> TileSpec:
    return TileSpec(
        scale=scale,
        stride=max(1, scale // 2),
        encoder_id=encoder,
        encoder_revision=revision,
    )


def test_cache_key_depends_on_encoder_revision_and_text() -> None:
    base = _spec(8)
    assert tile_cache_key("a b", base) == tile_cache_key("a b", base)
    assert tile_cache_key("a b", base) != tile_cache_key("a c", base)
    assert tile_cache_key("a b", base) != tile_cache_key("a b", _spec(8, revision="r2"))


def test_pyramid_uses_overlapping_half_stride_tiles() -> None:
    tokens = [f"t{i}" for i in range(20)]
    plan = PyramidPlan((_spec(16), _spec(8), _spec(4)))
    pyramid = build_pyramid(tokens, plan)

    assert [(t.start, t.end) for t in pyramid[8]] == [(0, 8), (4, 12), (8, 16), (12, 20)]
    assert pyramid[4][1].start == 2
    assert pyramid[4][1].end == 6


def test_identical_tiles_are_reused_across_documents() -> None:
    plan = PyramidPlan((_spec(4),))
    doc = ["the", "same", "four", "tokens"]
    ledger = cache_ledger([build_pyramid(doc, plan), build_pyramid(doc, plan)])

    assert ledger["total"] == 2
    assert ledger["unique"] == 1
    assert ledger["reused"] == 1
    assert ledger["reuse_fraction"] == 0.5


def test_relations_never_cross_encoder_spaces() -> None:
    tokens = [f"t{i}" for i in range(16)]
    mixed = PyramidPlan((_spec(16, "jina"), _spec(8, "jina"), _spec(4, "mini")))
    pairs = relation_pairs(build_pyramid(tokens, mixed))

    assert pairs
    assert all(child.spec.encoder_id == parent.spec.encoder_id for child, parent in pairs)
    assert any(child.spec.scale == 8 and parent.spec.scale == 16 for child, parent in pairs)
    assert not any(child.spec.scale == 4 for child, _ in pairs)


def test_redundant_ancestors_are_allowed() -> None:
    tokens = [f"t{i}" for i in range(32)]
    plan = PyramidPlan((_spec(32), _spec(16), _spec(8)))
    pairs = relation_pairs(build_pyramid(tokens, plan))
    child0_parents = [parent.spec.scale for child, parent in pairs if child.spec.scale == 8 and child.start == 0]

    assert 16 in child0_parents
    assert 32 in child0_parents


def test_confirmatory_flavourizer_modes_are_frozen() -> None:
    scales = (1024, 512, 256, 128, 64, 32, 16, 8, 4)
    assert flavourizer_scales("none", scales) == ()
    assert flavourizer_scales("high_only", scales) == (1024, 512, 256, 128)
    assert flavourizer_scales("low_only", scales) == (32, 16, 8, 4)
    assert flavourizer_scales("all_scales", scales) == scales
