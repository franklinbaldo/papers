#!/usr/bin/env python3
"""OKF v0.1 conformance checker for this repository.

Checks (see okf/SPEC.md §9 for the spec's own conformance clause):
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block has a non-empty `type` field.
  3. Reserved filenames (`index.md`, `log.md`, anywhere in the tree) have
     NO frontmatter, per §3.1/§6/§7.

Repository-local producer rules:
  4. Every `type` value used in the repository has a corresponding spec
     under okf/types/.
  5. When optional `publication` metadata is present, it follows the state
     contract documented in okf/publication.md.

Usage:
    python3 okf/validate.py
    python3 okf/validate.py --list-types
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("okf/validate.py requires PyYAML (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESERVED_FILENAMES = {"index.md", "log.md"}
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

PUBLICATION_STATUSES = {"draft", "ready", "submitted", "announced"}
PUBLICATION_RECORD_STATUSES = {"submitted", "announced"}
GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def registered_types(types_dir: Path) -> dict[str, Path]:
    """Read okf/types/*.md and return {type_name: spec_file_path}."""
    registry: dict[str, Path] = {}
    for spec_path in sorted(types_dir.glob("*.md")):
        text = spec_path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            print(f"ERROR: type spec {spec_path} itself has no frontmatter", file=sys.stderr)
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        title = fm.get("title")
        if not title:
            print(f"ERROR: type spec {spec_path} has no `title` to register as a type name", file=sys.stderr)
            continue
        registry[title] = spec_path
    return registry


def iter_markdown_files(root: Path):
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        yield path


def validate_publication(rel: Path, fm: dict, errors: list[str]) -> None:
    """Validate the repository-local optional publication frontmatter extension."""
    publication = fm.get("publication")
    if publication is None:
        return

    if not isinstance(publication, dict):
        errors.append(f"{rel}: `publication` must be a YAML mapping (see okf/publication.md)")
        return

    status = publication.get("status")
    if status not in PUBLICATION_STATUSES:
        allowed = ", ".join(sorted(PUBLICATION_STATUSES))
        errors.append(
            f"{rel}: publication.status must be one of {allowed}; got {status!r}"
        )

    targets = publication.get("targets")
    if targets is not None:
        if not isinstance(targets, list) or not all(
            isinstance(target, str) and target.strip() for target in targets
        ):
            errors.append(
                f"{rel}: publication.targets must be a list of non-empty strings"
            )

    records = publication.get("records")
    if records is None:
        return
    if not isinstance(records, list):
        errors.append(f"{rel}: publication.records must be a YAML list")
        return

    for index, record in enumerate(records):
        prefix = f"{rel}: publication.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be a YAML mapping")
            continue

        venue = record.get("venue")
        if not isinstance(venue, str) or not venue.strip():
            errors.append(f"{prefix}.venue must be a non-empty string")

        record_status = record.get("status")
        if record_status not in PUBLICATION_RECORD_STATUSES:
            allowed = ", ".join(sorted(PUBLICATION_RECORD_STATUSES))
            errors.append(
                f"{prefix}.status must be one of {allowed}; got {record_status!r}"
            )

        source_commit = record.get("source_commit")
        if source_commit is not None and (
            not isinstance(source_commit, str) or not GIT_SHA_RE.fullmatch(source_commit)
        ):
            errors.append(f"{prefix}.source_commit must be a full 40-hex Git SHA")

        bundle_sha256 = record.get("bundle_sha256")
        if bundle_sha256 is not None and (
            not isinstance(bundle_sha256, str) or not SHA256_RE.fullmatch(bundle_sha256)
        ):
            errors.append(f"{prefix}.bundle_sha256 must be a 64-hex SHA-256 digest")

        if record_status == "announced":
            for field in ("identifier", "url"):
                value = record.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"{prefix}.{field} is required for an announced record"
                    )


def main() -> int:
    if "--list-types" in sys.argv:
        for name in sorted(registered_types(REPO_ROOT / "okf" / "types")):
            print(name)
        return 0

    types = registered_types(REPO_ROOT / "okf" / "types")
    if not types:
        print(
            "ERROR: no type specs found under okf/types/ — refusing to validate against an empty vocabulary",
            file=sys.stderr,
        )
        return 2

    errors: list[str] = []
    checked = 0

    for path in iter_markdown_files(REPO_ROOT):
        rel = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        is_reserved = path.name in RESERVED_FILENAMES

        m = FRONTMATTER_RE.match(text)

        if is_reserved:
            if m:
                errors.append(
                    f"{rel}: reserved filename MUST NOT have frontmatter (OKF SPEC §6/§7)"
                )
            checked += 1
            continue

        checked += 1
        if not m:
            errors.append(f"{rel}: missing YAML frontmatter block (OKF SPEC §9.1)")
            continue

        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            errors.append(
                f"{rel}: frontmatter is not parseable YAML ({e}) (OKF SPEC §9.1)"
            )
            continue

        if not isinstance(fm, dict) or not fm.get("type"):
            errors.append(
                f"{rel}: frontmatter has no non-empty `type` field (OKF SPEC §9.2)"
            )
            continue

        type_value = fm["type"]
        if type_value not in types:
            known = ", ".join(sorted(types))
            errors.append(
                f"{rel}: type {type_value!r} is not registered under okf/types/ "
                f"(known types: {known}) — add okf/types/<slug>.md or fix the typo"
            )

        validate_publication(rel, fm, errors)

    if errors:
        print(
            f"OKF conformance: {len(errors)} error(s) across {checked} file(s) checked\n",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"OKF conformance: OK ({checked} files checked, {len(types)} registered types)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
