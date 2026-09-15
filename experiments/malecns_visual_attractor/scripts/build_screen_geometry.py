from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


def optic_columns(path: Path) -> dict[int, tuple[str, int, int]]:
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
                    cells[column] = strings[int(value.text)] if cell.get("t") == "s" else str(value.text)
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


def build(interface_path: Path, optic_path: Path, output_path: Path, manifest_path: Path) -> dict:
    interface = np.load(interface_path, allow_pickle=False)
    bodies = interface["visual_bodies"].astype(np.int64)
    azimuth = interface["visual_azimuth"].astype(np.float32)
    columns = optic_columns(optic_path)
    if not columns:
        raise RuntimeError("optic column table parsed zero assignments")

    h1_max = max(h1 for _, h1, _ in columns.values())
    h2_max = max(h2 for _, _, h2 in columns.values())
    x = azimuth.copy()
    y = np.zeros(len(bodies), dtype=np.float32)
    resolved = np.zeros(len(bodies), dtype=bool)
    eye = np.zeros(len(bodies), dtype=np.int8)
    h1_values = np.full(len(bodies), -1, dtype=np.int16)
    h2_values = np.full(len(bodies), -1, dtype=np.int16)

    for i, body in enumerate(bodies):
        loc = columns.get(int(body))
        if loc is None:
            eye[i] = -1 if x[i] < 0 else 1 if x[i] > 0 else 0
            continue
        side, h1, h2 = loc
        resolved[i] = True
        eye[i] = -1 if side == "L" else 1
        h1_values[i] = h1
        h2_values[i] = h2
        frac1 = (h1 - 1) / max(h1_max - 1, 1)
        x[i] = -(0.06 + 0.94 * frac1) if side == "L" else (0.06 + 0.94 * frac1)
        frac2 = (h2 - 1) / max(h2_max - 1, 1)
        y[i] = np.float32(2.0 * frac2 - 1.0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        visual_bodies=bodies,
        visual_x=x.astype(np.float32),
        visual_y=y.astype(np.float32),
        visual_resolved=resolved,
        visual_eye=eye,
        visual_h1=h1_values,
        visual_h2=h2_values,
    )
    manifest = {
        "format": "papers/malecns-screen-geometry-v1",
        "visual_receptors": int(len(bodies)),
        "optic_column_resolved": int(resolved.sum()),
        "optic_column_fallback": int((~resolved).sum()),
        "h1_max": int(h1_max),
        "h2_max": int(h2_max),
        "policy": {
            "x": "same normalized eye azimuth as visual-interface v1",
            "y": "optic-column h2 normalized to [-1,1]",
            "fallback": "unresolved receptors retain interface x and y=0; they remain in telemetry and stimulation",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--optic-columns", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.interface, args.optic_columns, args.output, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
