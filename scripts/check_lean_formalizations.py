#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Compile every Lean formalization and audit the trusted boundary.

The gate is intentionally dependency-free. It:
- discovers every formalizations/**/*.lean file;
- counts formal declarations;
- rejects executable `sorry` / `admit` tokens;
- rejects explicit `axiom` declarations;
- compiles every file with the pinned Lean toolchain;
- preserves Lean's #print axioms output in CI logs.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMALIZATIONS = ROOT / "formalizations"

DECL_RE = re.compile(
    r"(?m)^\s*(?:private\s+|protected\s+)?"
    r"(theorem|lemma|def|abbrev|structure|inductive|class|instance)\b"
)
UNSAFE_RE = re.compile(r"\b(sorry|admit)\b")
AXIOM_RE = re.compile(r"(?m)^\s*axiom\b")


def strip_comments_and_strings(source: str) -> str:
    """Remove Lean comments and string contents before token auditing.

    Lean block comments nest, so use a tiny scanner rather than a regex.
    Newlines are preserved to keep diagnostics readable.
    """
    out: list[str] = []
    i = 0
    n = len(source)
    block_depth = 0
    in_string = False

    while i < n:
        if block_depth:
            if source.startswith("/-", i):
                block_depth += 1
                out.extend("  ")
                i += 2
            elif source.startswith("-/", i):
                block_depth -= 1
                out.extend("  ")
                i += 2
            else:
                out.append("\n" if source[i] == "\n" else " ")
                i += 1
            continue

        if in_string:
            ch = source[i]
            if ch == "\\" and i + 1 < n:
                out.extend("  ")
                i += 2
            elif ch == '"':
                in_string = False
                out.append(" ")
                i += 1
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if source.startswith("--", i):
            while i < n and source[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if source.startswith("/-", i):
            block_depth = 1
            out.extend("  ")
            i += 2
            continue
        if source[i] == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue

        out.append(source[i])
        i += 1

    if block_depth:
        raise SystemExit("unterminated Lean block comment while auditing sources")
    if in_string:
        raise SystemExit("unterminated Lean string while auditing sources")
    return "".join(out)


def main() -> int:
    files = sorted(FORMALIZATIONS.rglob("*.lean"))
    if not files:
        print("ERROR: no Lean formalizations found", file=sys.stderr)
        return 2

    try:
        version = subprocess.run(
            ["lean", "--version"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: Lean is unavailable: {exc}", file=sys.stderr)
        return 2

    total_declarations = 0
    total_sorries = 0
    total_axioms = 0
    audit_rows: list[tuple[Path, int, int, int]] = []

    for path in files:
        source = path.read_text(encoding="utf-8")
        executable = strip_comments_and_strings(source)
        declarations = len(DECL_RE.findall(executable))
        sorries = len(UNSAFE_RE.findall(executable))
        axioms = len(AXIOM_RE.findall(executable))
        total_declarations += declarations
        total_sorries += sorries
        total_axioms += axioms
        audit_rows.append((path, declarations, sorries, axioms))

    print(f"Lean: {version}")
    print(
        f"Audit: files={len(files)} declarations={total_declarations} "
        f"sorry/admit={total_sorries} explicit_axioms={total_axioms}"
    )
    for path, declarations, sorries, axioms in audit_rows:
        rel = path.relative_to(ROOT)
        print(
            f"  {rel}: declarations={declarations} "
            f"sorry/admit={sorries} explicit_axioms={axioms}"
        )

    if total_sorries:
        print("ERROR: trusted boundary contains sorry/admit", file=sys.stderr)
        return 1
    if total_axioms:
        print("ERROR: trusted boundary contains explicit axiom declarations", file=sys.stderr)
        return 1

    for path in files:
        rel = path.relative_to(ROOT)
        print(f"\n==> lean {rel}", flush=True)
        proc = subprocess.run(
            ["lean", str(rel)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.returncode:
            print(f"ERROR: compilation failed for {rel}", file=sys.stderr)
            return proc.returncode

    print(
        f"\nLEAN FORMALIZATIONS OK: {len(files)} files, "
        f"{total_declarations} declarations, 0 sorry/admit, 0 explicit axioms"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
