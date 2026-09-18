#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "Markdown>=3.10.3,<4",
#   "PyYAML>=6.0.3,<7",
# ]
# ///

"""Prepare one OKF paper for a Zenodo deposition.

This script never talks to Zenodo and never reads secrets. It only validates
repository metadata and produces the exact files/metadata consumed by the
zenodraft GitHub Action.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import markdown
import yaml

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
ABSTRACT_RE = re.compile(
    r"(?ims)^#{1,3}\s+Abstract\s*$\n(?P<body>.*?)(?=^#{1,3}\s+|\Z)"
)


class PrepareError(RuntimeError):
    pass


def parse_document(path: Path) -> tuple[dict[str, Any], str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise PrepareError(f"{path}: missing YAML frontmatter")
    fm = yaml.safe_load(match.group(1)) or {}
    if not isinstance(fm, dict):
        raise PrepareError(f"{path}: frontmatter must be a mapping")
    return fm, text[match.end():], text


def current_sha(repo_root: Path) -> str:
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_identifier(fm: dict[str, Any], scheme: str) -> str | None:
    for item in fm.get("identifiers", []) or []:
        if isinstance(item, dict) and item.get("scheme") == scheme and item.get("value"):
            return str(item["value"])
    return None


def creators(repo_root: Path, paper_fm: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    entries = paper_fm.get("authors")
    if not isinstance(entries, list) or not entries:
        raise PrepareError(
            "paper must have an ordered frontmatter authors list before Zenodo publication"
        )

    result: list[dict[str, str]] = []
    refs: list[str] = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("ref"):
            raise PrepareError(f"authors[{i}] must contain ref")
        ref = str(entry["ref"])
        refs.append(ref)
        author_fm, _, _ = parse_document(repo_root / ref.lstrip("/"))
        if author_fm.get("type") != "Author":
            raise PrepareError(f"{ref}: expected type Author")

        given = author_fm.get("given_names")
        family = author_fm.get("family_name")
        if not given or not family:
            raise PrepareError(f"{ref}: Author needs given_names and family_name")

        creator: dict[str, str] = {"name": f"{family}, {given}"}
        affiliations = entry.get("affiliations")
        if isinstance(affiliations, list) and affiliations:
            creator["affiliation"] = "; ".join(str(x) for x in affiliations)
        else:
            defaults = author_fm.get("affiliations") or []
            names = [
                str(x["name"])
                for x in defaults
                if isinstance(x, dict) and x.get("name")
            ]
            if names:
                creator["affiliation"] = "; ".join(names)

        orcid = get_identifier(author_fm, "orcid")
        if orcid:
            creator["orcid"] = orcid
        result.append(creator)
    return result, refs


def abstract_as_html(body: str, description: Any) -> str:
    match = ABSTRACT_RE.search(body)
    if match:
        return markdown.markdown(
            match.group("body").strip(), extensions=["tables", "fenced_code"]
        )
    if description:
        return f"<p>{html.escape(str(description))}</p>"
    raise PrepareError("paper needs an Abstract section or description")


def validate_publication(fm: dict[str, Any]) -> dict[str, Any]:
    publication = fm.get("publication")
    if not isinstance(publication, dict):
        raise PrepareError("paper has no publication mapping")
    if publication.get("status") != "ready":
        raise PrepareError(
            f"publication.status must be ready, got {publication.get('status')!r}"
        )
    if "zenodo" not in (publication.get("targets") or []):
        raise PrepareError("publication.targets must include zenodo")
    zenodo = publication.get("zenodo")
    if not isinstance(zenodo, dict):
        raise PrepareError("publication.zenodo mapping is required")
    if zenodo.get("access_right", "open") in {"open", "embargoed"} and not zenodo.get("license"):
        raise PrepareError("publication.zenodo.license must be explicit")
    return zenodo


def prepare(repo_root: Path, paper_rel: Path, out_root: Path) -> dict[str, Any]:
    paper_path = repo_root / paper_rel
    fm, body, full_text = parse_document(paper_path)
    zcfg = validate_publication(fm)
    author_rows, author_refs = creators(repo_root, fm)
    sha = current_sha(repo_root)

    out_dir = out_root / paper_rel.stem
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    source_name = paper_rel.name
    source_bytes = full_text.encode("utf-8")
    (out_dir / source_name).write_bytes(source_bytes)

    html_name = f"{paper_rel.stem}.html"
    rendered = markdown.markdown(body, extensions=["tables", "fenced_code", "toc"])
    rendered_html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(str(fm.get('title') or paper_rel.stem))}</title>"
        "</head><body>" + rendered + "</body></html>"
    )
    (out_dir / html_name).write_text(rendered_html, encoding="utf-8")

    metadata: dict[str, Any] = {
        "upload_type": "publication",
        "publication_type": str(zcfg.get("publication_type", "preprint")),
        "publication_date": str(
            zcfg.get("publication_date")
            or datetime.now(timezone.utc).date().isoformat()
        ),
        "title": str(fm.get("title") or paper_rel.stem),
        "creators": author_rows,
        "description": abstract_as_html(body, fm.get("description")),
        "access_right": str(zcfg.get("access_right", "open")),
        "license": str(zcfg["license"]),
        "keywords": [str(tag) for tag in (fm.get("tags") or [])],
        "notes": (
            f"Canonical source commit: {sha}. "
            f"https://github.com/franklinbaldo/papers/blob/{sha}/{paper_rel.as_posix()}"
        ),
    }
    for key in ("language", "version"):
        if zcfg.get(key):
            metadata[key] = str(zcfg[key])

    metadata_path = out_dir / "zenodo.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    file_hashes = {
        source_name: digest(source_bytes),
        html_name: digest(rendered_html.encode("utf-8")),
        "zenodo.json": digest(metadata_path.read_bytes()),
    }
    bundle_sha256 = digest(
        json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode()
    )
    provenance = {
        "schema": "franklinbaldo/papers-zenodo-provenance-v1",
        "repository": "https://github.com/franklinbaldo/papers",
        "paper": paper_rel.as_posix(),
        "source_commit": sha,
        "author_refs": author_refs,
        "files": file_hashes,
        "bundle_sha256": bundle_sha256,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    provenance_path = out_dir / "PROVENANCE.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    files = [str(out_dir / source_name), str(out_dir / html_name), str(provenance_path)]
    output = {
        "metadata_path": str(metadata_path),
        "filenames": " ".join(files),
        "bundle_sha256": bundle_sha256,
        "source_commit": sha,
        "paper": paper_rel.as_posix(),
    }

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            for key, value in output.items():
                fh.write(f"{key}={value}\n")

    print(json.dumps(output, indent=2))
    return output


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "authors").mkdir()
        (root / "authors/test.md").write_text(
            """---
type: Author
title: Test Author
given_names: Test
family_name: Author
identifiers:
  - scheme: orcid
    value: 0000-0000-0000-000X
affiliations:
  - name: Example Lab
---
# Test
""",
            encoding="utf-8",
        )
        (root / "paper.md").write_text(
            """---
type: Technical Paper
title: Test Paper
description: Test fallback
tags: [test]
authors:
  - ref: /authors/test.md
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-4.0
---
# Test Paper

## Abstract

Test abstract.
""",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
        out = prepare(root, Path("paper.md"), root / "dist")
        assert len(out["bundle_sha256"]) == 64
        meta = json.loads(Path(out["metadata_path"]).read_text())
        assert meta["creators"][0]["name"] == "Author, Test"
        assert meta["license"] == "cc-by-4.0"
    print("zenodo_prepare self-test: OK")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper")
    parser.add_argument("--out", default="dist/zenodo")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if not args.paper:
        parser.error("--paper is required unless --self-test is used")

    repo_root = Path(__file__).resolve().parent.parent
    prepare(repo_root, Path(args.paper), repo_root / args.out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrepareError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
