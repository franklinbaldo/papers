from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.ipc as ipc
import scipy.sparse as sp

BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome"
WEIGHTS_NAME = "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
ANNOTATIONS_NAME = "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTERS_NAME = "body-neurotransmitters-male-cns-v1.0.feather"

FAST_SIGN = {
    "acetylcholine": 1.0,
    "gaba": -1.0,
    "glutamate": -1.0,
    "histamine": -1.0,
    "dopamine": 0.0,
    "octopamine": 0.0,
    "serotonin": 0.0,
    "unclear": 0.0,
    "unknown": 0.0,
}


@dataclass(frozen=True)
class SourceSpec:
    weights_url: str
    annotations_url: str
    neurotransmitters_url: str
    attribution_url: str = "https://male-cns.janelia.org/download/"
    release: str = "MaleCNS v1.0"
    license: str = "CC BY"


@dataclass(frozen=True)
class CompilePolicy:
    traced_only: bool = True
    exclude_glia: bool = True
    min_synapses: int = 3
    weight_scale: float = 1.0


def source_spec(mirror_base_url: str | None = None) -> SourceSpec:
    base = (mirror_base_url or BASE).rstrip("/")
    return SourceSpec(
        weights_url=f"{base}/{WEIGHTS_NAME}",
        annotations_url=f"{base}/{ANNOTATIONS_NAME}",
        neurotransmitters_url=f"{base}/{NEUROTRANSMITTERS_NAME}",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path, force: bool = False) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return destination
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "papers-malecns-wifi/0.1"})
    with urllib.request.urlopen(request) as response, temporary.open("wb") as output:
        while chunk := response.read(8 * 1024 * 1024):
            output.write(chunk)
    temporary.replace(destination)
    return destination


def _column(table: pa.Table, *names: str):
    for name in names:
        if name in table.column_names:
            return table[name]
    raise KeyError(f"none of {names!r} found; columns={table.column_names!r}")


def _strings(table: pa.Table, name: str, fallback: str = "") -> np.ndarray:
    if name not in table.column_names:
        return np.full(table.num_rows, fallback, dtype="U32")
    return np.asarray(
        [fallback if x is None or str(x) == "" else str(x) for x in table[name].to_pylist()],
        dtype="U32",
    )


def _neuron_attribute(
    table: pa.Table,
    name: str,
    body_ids: np.ndarray,
    keep: np.ndarray,
    bodies: np.ndarray,
) -> np.ndarray:
    """Annotation column reduced to one value per retained body, aligned to ``bodies``."""
    values = _strings(table, name, "unknown")
    lookup: dict[int, str] = {}
    for body, value in zip(body_ids[keep], values[keep], strict=True):
        lookup.setdefault(int(body), str(value))
    return np.asarray([lookup.get(int(body), "unknown") for body in bodies], dtype="U32")


def compile_connectome(
    *,
    output_dir: Path,
    cache_dir: Path,
    source: SourceSpec | None = None,
    policy: CompilePolicy = CompilePolicy(),
) -> dict:
    source = source or source_spec()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = cache_dir / "male-cns-v1.0"
    raw_dir.mkdir(parents=True, exist_ok=True)

    urls = {
        "weights": (source.weights_url, raw_dir / WEIGHTS_NAME),
        "annotations": (source.annotations_url, raw_dir / ANNOTATIONS_NAME),
        "neurotransmitters": (source.neurotransmitters_url, raw_dir / NEUROTRANSMITTERS_NAME),
    }
    files = {key: download(url, path) for key, (url, path) in urls.items()}

    annotations = feather.read_table(files["annotations"])
    body_ids = _column(annotations, "bodyId", "body").to_numpy(zero_copy_only=False).astype(np.int64)
    keep = np.ones(annotations.num_rows, dtype=bool)
    if policy.traced_only and "status" in annotations.column_names:
        keep &= np.asarray([x == "Traced" for x in annotations["status"].to_pylist()])
    if policy.exclude_glia and "statusLabel" in annotations.column_names:
        keep &= np.asarray([x != "Glia" for x in annotations["statusLabel"].to_pylist()])
    bodies = np.unique(body_ids[keep])
    bodies.sort()
    n = len(bodies)

    nt_table = feather.read_table(files["neurotransmitters"])
    nt_bodies = _column(nt_table, "body", "bodyId").to_numpy(zero_copy_only=False).astype(np.int64)
    nt_values = _strings(nt_table, "consensus_nt", "unknown")
    nt_lookup: dict[int, str] = {}
    for body, nt in zip(nt_bodies, nt_values, strict=True):
        nt_lookup.setdefault(int(body), str(nt).lower())
    nt = np.asarray([nt_lookup.get(int(body), "unknown") for body in bodies], dtype="U24")
    sign = np.asarray([FAST_SIGN.get(value, 0.0) for value in nt], dtype=np.float32)

    superclass = _neuron_attribute(annotations, "superclass", body_ids, keep, bodies)
    cell_class = _neuron_attribute(annotations, "class", body_ids, keep, bodies)

    reader = ipc.RecordBatchFileReader(pa.memory_map(str(files["weights"]), "r"))
    rows: list[np.ndarray] = []
    cols: list[np.ndarray] = []
    values: list[np.ndarray] = []
    raw_pairs = 0
    threshold_pairs = 0
    resolved_pairs = 0
    zero_sign_pairs = 0
    retained_signed_pairs = 0

    def locate(ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        positions = np.searchsorted(bodies, ids)
        clipped = np.minimum(positions, max(n - 1, 0))
        valid = (positions < n) & (bodies[clipped] == ids)
        indices = positions.astype(np.int32, copy=False)
        indices[~valid] = -1
        return indices, valid

    for batch_index in range(reader.num_record_batches):
        batch = reader.get_batch(batch_index)
        raw_pairs += batch.num_rows
        weight = batch["weight"].to_numpy(zero_copy_only=False).astype(np.float32)
        pre = batch["body_pre"].to_numpy(zero_copy_only=False).astype(np.int64)
        post = batch["body_post"].to_numpy(zero_copy_only=False).astype(np.int64)
        threshold = weight >= policy.min_synapses
        threshold_pairs += int(threshold.sum())
        if not threshold.any():
            continue
        pre, post, weight = pre[threshold], post[threshold], weight[threshold]
        pre_idx, pre_valid = locate(pre)
        post_idx, post_valid = locate(post)
        valid = pre_valid & post_valid
        resolved_pairs += int(valid.sum())
        if not valid.any():
            continue
        pre_idx, post_idx, weight = pre_idx[valid], post_idx[valid], weight[valid]
        signed_weight = weight * sign[pre_idx] * np.float32(policy.weight_scale)
        signed = signed_weight != 0.0
        zero_sign_pairs += int(signed.size - int(signed.sum()))
        if not signed.any():
            continue
        rows.append(post_idx[signed])
        cols.append(pre_idx[signed])
        values.append(signed_weight[signed])
        retained_signed_pairs += int(signed.sum())

    row = np.concatenate(rows) if rows else np.empty(0, dtype=np.int32)
    col = np.concatenate(cols) if cols else np.empty(0, dtype=np.int32)
    data = np.concatenate(values).astype(np.float32, copy=False) if values else np.empty(0, dtype=np.float32)
    matrix = sp.csr_matrix((data, (row, col)), shape=(n, n), dtype=np.float32)
    matrix.sum_duplicates()

    graph_path = output_dir / "graph.npz"
    np.savez_compressed(
        graph_path,
        data=matrix.data,
        indices=matrix.indices,
        indptr=matrix.indptr,
        shape=np.asarray(matrix.shape, dtype=np.int64),
        bodies=bodies,
        sign=sign,
        nt=nt,
        superclass=superclass,
        cell_class=cell_class,
    )

    manifest = {
        "format": "papers/malecns-wifi-runtime-v1",
        "release": source.release,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": asdict(source),
        "policy": asdict(policy),
        "raw_files": {
            key: {"url": urls[key][0], "bytes": path.stat().st_size, "sha256": sha256(path)}
            for key, path in files.items()
        },
        "runtime": {
            "neurons": int(n),
            "edges": int(matrix.nnz),
            "raw_edge_pairs": int(raw_pairs),
            "threshold_edge_pairs": int(threshold_pairs),
            "resolved_edge_pairs": int(resolved_pairs),
            "zero_sign_edge_pairs": int(zero_sign_pairs),
            "signed_edge_pairs_before_dedup": int(retained_signed_pairs),
            "excitatory_edges": int((matrix.data > 0).sum()),
            "inhibitory_edges": int((matrix.data < 0).sum()),
            "neurons_by_sign": {
                "excitatory": int((sign > 0).sum()),
                "inhibitory": int((sign < 0).sum()),
                # "zero_sign" is a transmitter-policy fact (DA/OA/5-HT/unclear/unknown),
                # not a wiring fact: these neurons still receive edges. Wiring silence is
                # counted separately below.
                "zero_sign": int((sign == 0).sum()),
            },
            "neurons_by_connectivity": {
                "no_incoming": int((np.diff(matrix.indptr) == 0).sum()),
                "no_outgoing": int(n - np.unique(matrix.indices).size),
                "isolated": int(
                    np.setdiff1d(
                        np.flatnonzero(np.diff(matrix.indptr) == 0),
                        np.unique(matrix.indices),
                        assume_unique=False,
                    ).size
                ),
                "note": (
                    "Counted on the compiled operator. Disconnected neurons are kept so that "
                    "row indices stay stable against bodies/sign/superclass."
                ),
            },
            "orientation": "W[post, pre]",
            "dtype": "float32",
        },
        "modeling": {
            "fast_sign": FAST_SIGN,
            "note": "Computational reservoir artifact; not a biophysical simulation.",
            "edge_accounting": (
                "raw -> threshold (weight >= min_synapses) -> resolved (both endpoints retained) "
                "-> signed (presynaptic fast-transmitter sign != 0). zero_sign_edge_pairs counts "
                "the edges dropped because FAST_SIGN maps the presynaptic transmitter to 0."
            ),
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
