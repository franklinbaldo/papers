from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_ROLES = (
    "calibration",
    "train",
    "interaction_test",
    "composition_test",
    "relation_holdout",
)

_ALLOWED_PURPOSES: dict[str, frozenset[str]] = {
    "calibration": frozenset({"calibrate"}),
    "train": frozenset({"fit", "tune"}),
    "interaction_test": frozenset({"confirm_gate1"}),
    "composition_test": frozenset({"confirm_gate2"}),
    "relation_holdout": frozenset({"exploratory_transfer"}),
}


def _pair(record: Mapping[str, Any]) -> tuple[Any, Any]:
    return record["a"], record["b"]


def validate_manifest(manifest: Mapping[str, Sequence[Mapping[str, Any]]]) -> None:
    missing = [role for role in REQUIRED_ROLES if role not in manifest]
    if missing:
        raise ValueError(f"manifest missing roles: {missing}")

    seen_ids: dict[str, str] = {}
    for role in REQUIRED_ROLES:
        rows = manifest[role]
        for row in rows:
            for field in ("id", "a", "b"):
                if field not in row:
                    raise ValueError(f"{role} row missing required field {field!r}")
            rid = str(row["id"])
            if rid in seen_ids:
                raise ValueError(
                    f"example id {rid!r} appears in both {seen_ids[rid]} and {role}"
                )
            seen_ids[rid] = role

    train = manifest["train"]
    composition = manifest["composition_test"]
    train_pairs = {_pair(row) for row in train}
    composition_pairs = {_pair(row) for row in composition}
    overlap = train_pairs & composition_pairs
    if overlap:
        raise ValueError(f"composition_test contains train combinations: {sorted(overlap)!r}")

    train_a = {row["a"] for row in train}
    train_b = {row["b"] for row in train}
    for role in ("interaction_test", "composition_test"):
        unknown_a = {row["a"] for row in manifest[role]} - train_a
        unknown_b = {row["b"] for row in manifest[role]} - train_b
        if unknown_a or unknown_b:
            raise ValueError(
                f"{role} contains factor identities unseen in train: "
                f"A={sorted(map(str, unknown_a))}, B={sorted(map(str, unknown_b))}"
            )


def load_manifest(path: str | Path) -> dict[str, list[dict[str, Any]]]:
    source = Path(path)
    manifest = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be an object")
    validate_manifest(manifest)
    return manifest


def manifest_sha256(manifest: Mapping[str, Sequence[Mapping[str, Any]]]) -> str:
    """Stable content hash used to freeze a manifest before a confirmatory run."""

    validate_manifest(manifest)
    payload = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class SplitRegistry:
    manifest: Mapping[str, Sequence[Mapping[str, Any]]]

    def __post_init__(self) -> None:
        validate_manifest(self.manifest)

    def rows(self, role: str, *, purpose: str) -> Sequence[Mapping[str, Any]]:
        if role not in _ALLOWED_PURPOSES:
            raise ValueError(f"unknown split role {role!r}")
        if purpose not in _ALLOWED_PURPOSES[role]:
            raise PermissionError(
                f"split {role!r} cannot be used for purpose {purpose!r}; "
                f"allowed={sorted(_ALLOWED_PURPOSES[role])}"
            )
        return self.manifest[role]
