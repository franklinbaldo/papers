from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pyarrow.feather as feather


OPTIC_COLUMNS_COMMIT = "67767d2233657983993ff6c2be48e836a935863c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def optic_columns(path: Path) -> dict[int, tuple[str, int, int]]:
    """Parse MaleCNS optic-column assignments from the pinned supplemental xlsx."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    result: dict[int, tuple[str, int, int]] = {}
    with zipfile.ZipFile(path) as archive:
        strings_xml = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(node.itertext()) for node in strings_xml]
        for sheet_number in (1, 2):
            root = ET.fromstring(archive.read(f"xl/worksheets/sheet{sheet_number}.xml"))
            rows = root.findall("s:sheetData/s:row", ns)
            for row in rows[1:]:
                cells: dict[str, str] = {}
                for cell in row:
                    value = cell.find("s:v", ns)
                    if value is None:
                        continue
                    column = re.sub(r"\d", "", cell.attrib["r"])
                    cells[column] = (
                        strings[int(value.text)]
                        if cell.get("t") == "s"
                        else str(value.text)
                    )
                match = re.fullmatch(r"ME_([LR])_col_(\d+)_(\d+)", cells.get("A", ""))
                if not match:
                    continue
                side, h1, h2 = match.groups()
                for column in ("B", "C", "E"):
                    try:
                        body = int(cells.get(column, "-1"))
                    except ValueError:
                        continue
                    if body > 0:
                        result[body] = (side, int(h1), int(h2))
    return result


def annotation_string(frame, primary: str, fallback: str | None = None) -> np.ndarray:
    if primary in frame.columns:
        values = frame[primary]
        if fallback and fallback in frame.columns:
            values = values.fillna(frame[fallback])
        return values.fillna("").astype(str).to_numpy()
    if fallback and fallback in frame.columns:
        return frame[fallback].fillna("").astype(str).to_numpy()
    return np.full(len(frame), "", dtype=object)


def build_interface(
    graph_path: Path,
    annotations_path: Path,
    optic_columns_path: Path,
    output_path: Path,
    manifest_path: Path,
) -> dict:
    graph = np.load(graph_path, allow_pickle=False)
    bodies = graph["bodies"].astype(np.int64)
    n = len(bodies)
    body_to_index = {int(body): i for i, body in enumerate(bodies)}

    frame = feather.read_table(annotations_path).to_pandas()
    frame = frame.drop_duplicates("bodyId").copy()
    frame["bodyId"] = frame["bodyId"].astype(np.int64)
    frame = frame[frame["bodyId"].isin(body_to_index)]

    body = frame["bodyId"].to_numpy(np.int64)
    cell_type = annotation_string(frame, "flywireType", "type")
    superclass = annotation_string(frame, "superclass")
    side = annotation_string(frame, "somaSide", "rootSide")
    side = np.char.upper(side.astype(str))

    graph_index = np.asarray(
        [body_to_index[int(value)] for value in body], dtype=np.int32
    )

    visual_mask = np.isin(cell_type, ["R1-6", "R7", "R8"])
    visual_indices = graph_index[visual_mask]
    visual_bodies = body[visual_mask]
    visual_side = side[visual_mask]
    if visual_indices.size == 0:
        raise RuntimeError("no R1-6/R7/R8 photoreceptors resolved into graph")

    columns = optic_columns(optic_columns_path)
    if not columns:
        raise RuntimeError("optic column table parsed zero assignments")
    h1_max = max(h1 for _, h1, _ in columns.values())
    azimuth = np.full(visual_indices.size, np.nan, dtype=np.float32)
    resolved = np.zeros(visual_indices.size, dtype=bool)

    for i, body_id in enumerate(visual_bodies):
        location = columns.get(int(body_id))
        if location is None:
            continue
        eye_side, h1, _ = location
        frac = (h1 - 1) / max(h1_max - 1, 1)
        azimuth[i] = (
            -(0.06 + 0.94 * frac)
            if eye_side == "L"
            else (0.06 + 0.94 * frac)
        )
        resolved[i] = True

    # Unplaced cells are retained at a conservative mid-eye location rather than
    # silently dropped. The manifest makes the approximation visible.
    missing = ~resolved
    azimuth[missing] = np.where(visual_side[missing] == "L", -0.5, 0.5)

    descending_mask = (
        np.char.find(np.char.lower(superclass.astype(str)), "descending") >= 0
    )
    desc_indices = graph_index[descending_mask]
    desc_side = side[descending_mask]
    descending_left = desc_indices[desc_side == "L"]
    descending_right = desc_indices[desc_side == "R"]
    if descending_left.size == 0 or descending_right.size == 0:
        raise RuntimeError("descending neurons did not resolve on both sides")

    def typed_side_indices(type_name: str, wanted_side: str) -> np.ndarray:
        mask = (cell_type == type_name) & (side == wanted_side)
        return graph_index[mask].astype(np.int32)

    # Identified descending readouts used as the registered Run 1 decoder.
    steer_left = typed_side_indices("DNa02", "L")
    steer_right = typed_side_indices("DNa02", "R")
    forward_left = typed_side_indices("DNg100", "L")
    forward_right = typed_side_indices("DNg100", "R")

    # MaleCNS annotations use pC1* names for the male courtship-command family
    # (for example pC1a, pC1b, pC1_4b, pC1_7b and pC1_11b). The earlier P1_*
    # spelling was literature terminology, not the dataset's cell-type prefix.
    courtship_mask = np.char.startswith(cell_type.astype(str), "pC1")
    courtship_indices = graph_index[courtship_mask]

    required_run1 = {
        "DNa02 left": steer_left,
        "DNa02 right": steer_right,
        "DNg100 left": forward_left,
        "DNg100 right": forward_right,
        "pC1* courtship-prime": courtship_indices,
    }
    missing_run1 = [name for name, values in required_run1.items() if values.size == 0]
    if missing_run1:
        raise RuntimeError(
            "registered Run 1 interface groups missing: " + ", ".join(missing_run1)
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        visual_indices=visual_indices.astype(np.int32),
        visual_azimuth=azimuth.astype(np.float32),
        visual_bodies=visual_bodies.astype(np.int64),
        descending_left=descending_left.astype(np.int32),
        descending_right=descending_right.astype(np.int32),
        steer_left=steer_left.astype(np.int32),
        steer_right=steer_right.astype(np.int32),
        forward_left=forward_left.astype(np.int32),
        forward_right=forward_right.astype(np.int32),
        courtship_indices=courtship_indices.astype(np.int32),
    )

    manifest = {
        "format": "papers/malecns-visual-interface-v1",
        "graph": {
            "path": graph_path.name,
            "sha256": sha256(graph_path),
            "neurons": int(n),
        },
        "annotations": {
            "path": annotations_path.name,
            "sha256": sha256(annotations_path),
        },
        "optic_columns": {
            "path": optic_columns_path.name,
            "sha256": sha256(optic_columns_path),
            "source_commit": OPTIC_COLUMNS_COMMIT,
        },
        "policy": {
            "visual_types": ["R1-6", "R7", "R8"],
            "azimuth": "optic column h1 mapped to [-1,-0.06] left / [0.06,1] right",
            "unplaced_visual": "retain at side-specific mid-eye +/-0.5",
            "descending": "superclass contains 'descending', split by soma/root side",
            "steering_readout": "DNa02 split by soma/root side",
            "forward_readout": "DNg100 split by soma/root side",
            "courtship_prime": "cell type starts with 'pC1'",
            "run1_required_groups": sorted(required_run1),
        },
        "counts": {
            "visual": int(visual_indices.size),
            "visual_column_resolved": int(resolved.sum()),
            "visual_column_fallback": int(missing.sum()),
            "descending_left": int(descending_left.size),
            "descending_right": int(descending_right.size),
            "steer_dna02_left": int(steer_left.size),
            "steer_dna02_right": int(steer_right.size),
            "forward_dng100_left": int(forward_left.size),
            "forward_dng100_right": int(forward_right.size),
            "courtship_p1": int(courtship_indices.size),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--optic-columns", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = build_interface(
        args.graph,
        args.annotations,
        args.optic_columns,
        args.output,
        args.manifest,
    )
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
