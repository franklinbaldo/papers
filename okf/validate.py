#!/usr/bin/env python3
"""OKF v0.1 conformance checker for this repository.

Checks (see okf/SPEC.md §9 for the spec's own conformance clause):
  1. Every non-reserved .md file has a parseable YAML frontmatter block.
  2. Every frontmatter block has a non-empty `type` field.
  3. Reserved filenames (`index.md`, `log.md`, anywhere in the tree) have
     NO frontmatter, per §3.1/§6/§7.

This repository adds one stricter rule on top of bare OKF conformance,
by design (see okf/types/okf-type-spec.md): every `type` value used
anywhere in the repository must have a corresponding spec file under
okf/types/. OKF itself is permissive about unknown `type` values
("consumers MUST tolerate unknown types gracefully") — that permissiveness
is for OKF *consumers* in general. This repository, as the *producer*,
chooses to close its own type vocabulary so it stays documented and
doesn't silently drift. If you're extending this repository with a new
kind of document, add okf/types/<slug>.md in the same change.

Usage:
    python3 okf/validate.py            # check the whole repo
    python3 okf/validate.py --list-types   # print the registered type set and exit
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


def main() -> int:
    if "--list-types" in sys.argv:
        for name in sorted(registered_types(REPO_ROOT / "okf" / "types")):
            print(name)
        return 0

    types = registered_types(REPO_ROOT / "okf" / "types")
    if not types:
        print("ERROR: no type specs found under okf/types/ — refusing to validate against an empty vocabulary", file=sys.stderr)
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
                errors.append(f"{rel}: reserved filename MUST NOT have frontmatter (OKF SPEC §6/§7)")
            checked += 1
            continue

        checked += 1
        if not m:
            errors.append(f"{rel}: missing YAML frontmatter block (OKF SPEC §9.1)")
            continue

        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            errors.append(f"{rel}: frontmatter is not parseable YAML ({e}) (OKF SPEC §9.1)")
            continue

        if not isinstance(fm, dict) or not fm.get("type"):
            errors.append(f"{rel}: frontmatter has no non-empty `type` field (OKF SPEC §9.2)")
            continue

        type_value = fm["type"]
        if type_value not in types:
            known = ", ".join(sorted(types))
            errors.append(
                f"{rel}: type {type_value!r} is not registered under okf/types/ "
                f"(known types: {known}) — add okf/types/<slug>.md or fix the typo"
            )

    if errors:
        print(f"OKF conformance: {len(errors)} error(s) across {checked} file(s) checked\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OKF conformance: OK ({checked} files checked, {len(types)} registered types)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
