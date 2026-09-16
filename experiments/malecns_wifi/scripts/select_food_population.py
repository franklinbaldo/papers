from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pyarrow.feather as feather


DEFAULT_PATTERN = r"(?:sugar|sweet|gr5a|gr64)"
SEARCH_COLUMNS = (
    "type",
    "instance",
    "superclass",
    "class",
    "subclass",
    "receptorType",
    "flywireType",
    "mancType",
    "entryNerve",
)


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Find anatomically annotated appetitive/sugar gustatory candidates in the "
            "MaleCNS annotation table and map their body IDs onto graph.npz indices. "
            "This produces a candidate report for provenance; it never silently "
            "labels neurons from graph structure."
        )
    )
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    args = parser.parse_args()

    table = feather.read_table(args.annotations)
    available = [column for column in SEARCH_COLUMNS if column in table.column_names]
    if not available:
        raise SystemExit(f"none of the expected annotation columns found: {table.column_names}")

    body_column = "bodyId" if "bodyId" in table.column_names else "body"
    bodies = table[body_column].to_numpy(zero_copy_only=False).astype(np.int64)
    pattern = re.compile(args.pattern, re.IGNORECASE)

    rows: list[dict] = []
    columns = {name: table[name].to_pylist() for name in available}
    for row_index, body in enumerate(bodies):
        values = {name: _text(columns[name][row_index]) for name in available}
        matched = [name for name, value in values.items() if pattern.search(value)]
        if matched:
            rows.append(
                {
                    "body_id": int(body),
                    "matched_columns": matched,
                    "annotations": values,
                }
            )

    graph = np.load(args.graph, allow_pickle=False)
    graph_bodies = graph["bodies"].astype(np.int64, copy=False)
    body_to_index = {int(body): index for index, body in enumerate(graph_bodies)}
    retained = []
    missing = []
    for row in rows:
        body = row["body_id"]
        if body in body_to_index:
            retained.append({**row, "graph_index": int(body_to_index[body])})
        else:
            missing.append(row)

    report = {
        "format": "papers/malecns-food-population-candidates-v1",
        "selection": {
            "pattern": args.pattern,
            "columns_searched": available,
            "note": (
                "Candidate discovery only. A scientific run must freeze an explicitly reviewed "
                "body_id list in its run manifest before training. Graph degree/connectivity is "
                "never used to infer gustatory identity."
            ),
        },
        "candidates_in_graph": retained,
        "candidates_not_in_graph": missing,
        "counts": {
            "annotation_matches": len(rows),
            "retained_in_compiled_graph": len(retained),
            "missing_from_compiled_graph": len(missing),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report["counts"], sort_keys=True))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
