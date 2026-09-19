#!/usr/bin/env python3
"""Validate every paper currently marked ready for Zenodo.

This is a repository-local dry run only: it prepares bundles under dist/ and
never calls Zenodo or reads credentials.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from zenodo_prepare import PrepareError, parse_document, prepare


def is_ready_zenodo_paper(fm: dict[str, Any]) -> bool:
    paper_type = str(fm.get("type") or "").lower()
    if "paper" not in paper_type:
        return False
    publication = fm.get("publication")
    if not isinstance(publication, dict):
        return False
    return (
        publication.get("status") == "ready"
        and "zenodo" in (publication.get("targets") or [])
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    out_root = repo_root / "dist" / "zenodo-check"
    candidates: list[Path] = []

    for path in sorted(repo_root.rglob("*.md")):
        if any(part in {".git", "dist"} for part in path.parts):
            continue
        try:
            fm, _, _ = parse_document(path)
        except (PrepareError, OSError):
            continue
        if is_ready_zenodo_paper(fm):
            candidates.append(path.relative_to(repo_root))

    if not candidates:
        print("No papers currently marked ready for Zenodo.")
        return 0

    print(f"Validating {len(candidates)} Zenodo-ready paper(s):")
    for paper in candidates:
        print(f"- {paper.as_posix()}")
        prepare(repo_root, paper, out_root)

    print(f"Validated {len(candidates)} Zenodo-ready paper(s) without external publication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
