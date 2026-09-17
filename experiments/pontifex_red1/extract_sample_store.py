# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyserini>=2.4.0",
#   "faiss-cpu>=1.13.0",
#   "numpy>=2.0",
# ]
# ///
"""Extract a fixed MS MARCO PID sample from a Pyserini prebuilt FAISS index.

The full index is memory-mapped read-only. Only sampled vectors are copied into
RAM and persisted as a compact NPZ feature store. PID lookup is obtained by a
single streaming scan of the companion `docid` file, so no assumption is made
that internal FAISS position equals the external MS MARCO pid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import faiss
import numpy as np
from pyserini.util import download_prebuilt_index

from sample_manifest import sample_pids, SPEC_VERSION

DEFAULT_INDEX = "msmarco-v1-passage.tct_colbert-v2-hnp"


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
        raise AssertionError(f"{len(missing)} sampled PIDs absent from docid mapping: {preview}")
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--size", type=int, default=10_000)
    ap.add_argument("--output", type=Path, default=Path("sample-store.npz"))
    args = ap.parse_args()

    pids_int = sample_pids(args.size)
    pids = [str(x) for x in pids_int]
    pid_hash = hashlib.sha256("\n".join(pids).encode()).hexdigest()

    print(f"downloading/index={args.index} sample={args.size}", flush=True)
    index_dir = Path(download_prebuilt_index(args.index))
    index_path = index_dir / "index"
    docid_path = index_dir / "docid"
    if not index_path.exists() or not docid_path.exists():
        raise FileNotFoundError(f"expected index+docid in {index_dir}; found {[p.name for p in index_dir.iterdir()]}")

    print(f"index_dir={index_dir}", flush=True)
    print(f"index_bytes={index_path.stat().st_size} docid_bytes={docid_path.stat().st_size}", flush=True)

    pid_to_pos = positions_for_pids(docid_path, pids)
    positions = np.asarray([pid_to_pos[pid] for pid in pids], dtype=np.int64)

    flags = mmap_flags()
    print(f"opening mmap flags={flags}", flush=True)
    index = faiss.read_index(str(index_path), flags)
    print(f"faiss_class={type(index).__name__} ntotal={index.ntotal} dim={index.d}", flush=True)

    vectors = np.empty((args.size, int(index.d)), dtype=np.float32)
    for i, pos in enumerate(positions):
        vectors[i] = np.asarray(index.reconstruct(int(pos)), dtype=np.float32)
        if i and i % 1000 == 0:
            print(f"reconstructed={i}/{args.size}", flush=True)

    if not np.isfinite(vectors).all():
        raise AssertionError("non-finite sampled vectors")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        pids=np.asarray(pids),
        positions=positions,
        embeddings=vectors,
    )

    meta = {
        "type": "pontifex_sample_feature_store",
        "sample_spec_version": SPEC_VERSION,
        "sample_size": args.size,
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
            for i in range(min(5, args.size))
        ],
    }
    meta_path = args.output.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)


if __name__ == "__main__":
    main()
