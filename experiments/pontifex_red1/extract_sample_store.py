# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyserini>=2.4.0",
#   "faiss-cpu>=1.13.0",
#   "numpy>=2.0",
# ]
# ///
"""Extract selected MS MARCO passage vectors from a Pyserini prebuilt FAISS index.

The full index is memory-mapped read-only. Only selected vectors are copied into
RAM and persisted as a compact NPZ feature store. PID lookup is obtained by a
single streaming scan of the companion ``docid`` file, so no assumption is made
that internal FAISS position equals the external MS MARCO pid.

By default the selector is the deterministic modular sample from ``sample_manifest``.
For benchmark candidate pools, ``--pid-file`` accepts an explicit ordered PID manifest
without changing the extraction path. This is the bridge needed to extract exactly the
same frozen candidate IDs from two different prebuilt representation spaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from pyserini.util import download_prebuilt_index

from sample_manifest import SPEC_VERSION, sample_pids

DEFAULT_INDEX = "msmarco-v1-passage.tct_colbert-v2-hnp"
EXPLICIT_PID_SPEC_VERSION = "explicit_pid_manifest_v1"


def mmap_flags() -> int:
    flags = int(getattr(faiss, "IO_FLAG_READ_ONLY", 0))
    if hasattr(faiss, "IO_FLAG_MMAP_IFC"):
        flags |= int(faiss.IO_FLAG_MMAP_IFC)
    else:
        flags |= int(getattr(faiss, "IO_FLAG_MMAP", 0))
    return flags


def positions_for_pids(docid_path: Path, wanted: list[str]) -> dict[str, int]:
    targets = set(wanted)
    found: dict[str, int] = {}
    with docid_path.open("r", encoding="utf-8") as fh:
        for pos, line in enumerate(fh):
            pid = line.rstrip("\n\r")
            if pid in targets:
                found[pid] = pos
                if len(found) == len(targets):
                    break
    missing = targets - found.keys()
    if missing:
        preview = sorted(missing)[:10]
        raise AssertionError(f"{len(missing)} selected PIDs absent from docid mapping: {preview}")
    return found


def _json_pids(payload: Any) -> list[str] | None:
    if isinstance(payload, list):
        return [str(value) for value in payload]
    if isinstance(payload, dict):
        for key in ("pids", "docids", "ids"):
            value = payload.get(key)
            if isinstance(value, list):
                return [str(item) for item in value]
    return None


def load_explicit_pids(path: Path) -> list[str]:
    """Load an ordered candidate PID manifest from JSON or one-PID-per-line text."""

    raw = path.read_text(encoding="utf-8")
    pids: list[str] | None = None
    try:
        pids = _json_pids(json.loads(raw))
    except json.JSONDecodeError:
        pass

    if pids is None:
        pids = [line.strip() for line in raw.splitlines() if line.strip()]

    if not pids:
        raise ValueError(f"explicit PID manifest is empty: {path}")
    if any(not pid for pid in pids):
        raise ValueError("explicit PID manifest contains an empty PID")
    if len(set(pids)) != len(pids):
        raise ValueError("explicit PID manifest contains duplicate PIDs")
    return pids


def resolve_pids(size: int, pid_file: Path | None) -> tuple[list[str], dict[str, Any]]:
    if pid_file is not None:
        pids = load_explicit_pids(pid_file)
        source_bytes = pid_file.read_bytes()
        return pids, {
            "selection_mode": "explicit_pid_manifest",
            "selection_spec_version": EXPLICIT_PID_SPEC_VERSION,
            "pid_manifest_source": str(pid_file),
            "pid_manifest_file_sha256": hashlib.sha256(source_bytes).hexdigest(),
        }

    pids = [str(value) for value in sample_pids(size)]
    return pids, {
        "selection_mode": "deterministic_modular_sample",
        "selection_spec_version": SPEC_VERSION,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--size", type=int, default=10_000)
    ap.add_argument(
        "--pid-file",
        type=Path,
        help="Ordered explicit PID manifest: JSON list/object with pids/docids/ids, or one PID per line.",
    )
    ap.add_argument("--output", type=Path, default=Path("sample-store.npz"))
    args = ap.parse_args()

    pids, selection = resolve_pids(args.size, args.pid_file)
    pid_hash = hashlib.sha256("\n".join(pids).encode()).hexdigest()
    n_selected = len(pids)

    print(
        f"downloading/index={args.index} selected={n_selected} mode={selection['selection_mode']}",
        flush=True,
    )
    index_dir = Path(download_prebuilt_index(args.index))
    index_path = index_dir / "index"
    docid_path = index_dir / "docid"
    if not index_path.exists() or not docid_path.exists():
        raise FileNotFoundError(
            f"expected index+docid in {index_dir}; found {[p.name for p in index_dir.iterdir()]}"
        )

    print(f"index_dir={index_dir}", flush=True)
    print(
        f"index_bytes={index_path.stat().st_size} docid_bytes={docid_path.stat().st_size}",
        flush=True,
    )

    pid_to_pos = positions_for_pids(docid_path, pids)
    positions = np.asarray([pid_to_pos[pid] for pid in pids], dtype=np.int64)

    flags = mmap_flags()
    print(f"opening mmap flags={flags}", flush=True)
    index = faiss.read_index(str(index_path), flags)
    print(f"faiss_class={type(index).__name__} ntotal={index.ntotal} dim={index.d}", flush=True)

    vectors = np.empty((n_selected, int(index.d)), dtype=np.float32)
    for i, pos in enumerate(positions):
        vectors[i] = np.asarray(index.reconstruct(int(pos)), dtype=np.float32)
        if i and i % 1000 == 0:
            print(f"reconstructed={i}/{n_selected}", flush=True)

    if not np.isfinite(vectors).all():
        raise AssertionError("non-finite selected vectors")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        pids=np.asarray(pids),
        positions=positions,
        embeddings=vectors,
    )

    meta = {
        "type": "pontifex_sample_feature_store",
        **selection,
        "sample_size": n_selected,
        "pid_sequence_sha256": pid_hash,
        "index_alias": args.index,
        "index_dir_name": index_dir.name,
        "faiss_class": type(index).__name__,
        "ntotal": int(index.ntotal),
        "dimension": int(index.d),
        "dtype": "float32",
        "index_bytes": index_path.stat().st_size,
        "feature_store_bytes": args.output.stat().st_size,
        "first_rows": [
            {
                "pid": pids[i],
                "internal_position": int(positions[i]),
                "norm": float(np.linalg.norm(vectors[i])),
            }
            for i in range(min(5, n_selected))
        ],
    }
    meta_path = args.output.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)


if __name__ == "__main__":
    main()
