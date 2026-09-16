"""Collect public MTEB MultiEURLEX-21 Portuguese scores without rerunning models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TASK_NAME = "MultiEURLEXMultilabelClassification"
SUBSET = "pt"
SPLIT = "test"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args()

    import mteb

    task = mteb.get_task(TASK_NAME, hf_subsets=[SUBSET], eval_splits=[SPLIT])
    cache = mteb.ResultCache()
    cache.download_from_remote()
    results = cache.load_results(tasks=[task], include_remote=True)

    rows = []
    for model_result in results.model_results:
        for task_result in model_result.task_results:
            if getattr(task_result, "task_name", None) != TASK_NAME:
                continue
            scores = getattr(task_result, "scores", {})
            for score_row in scores.get(SPLIT, []):
                if score_row.get("hf_subset") != SUBSET:
                    continue
                main = score_row.get("main_score", score_row.get("accuracy"))
                if main is None:
                    continue
                rows.append({
                    "model_name": model_result.model_name,
                    "model_revision": model_result.model_revision,
                    "task_name": TASK_NAME,
                    "split": SPLIT,
                    "hf_subset": SUBSET,
                    "language": score_row.get("languages", ["por-Latn"]),
                    "main_score_name": task.metadata.main_score,
                    "main_score": float(main),
                    "accuracy": float(score_row.get("accuracy", main)),
                    "lrap": score_row.get("lrap"),
                    "f1": score_row.get("f1"),
                    "hamming": score_row.get("hamming"),
                    "trained_on": score_row.get("trained_on"),
                    "comparable": True,
                    "source": "MTEB public ResultCache / embeddings-benchmark/results",
                })

    # Keep one row per model+revision, highest score when duplicate historical files exist.
    unique = {}
    for row in rows:
        key = (row["model_name"], str(row["model_revision"]))
        previous = unique.get(key)
        if previous is None or row["main_score"] > previous["main_score"]:
            unique[key] = row
    ordered = sorted(unique.values(), key=lambda row: row["main_score"], reverse=True)
    payload = {
        "schema": "papers/mteb-public-multieurlex21-pt-v1",
        "task": TASK_NAME,
        "split": SPLIT,
        "hf_subset": SUBSET,
        "language": "por-Latn",
        "main_score": task.metadata.main_score,
        "source": "https://github.com/embeddings-benchmark/results",
        "rows_found": len(ordered),
        "rows": ordered[: args.top],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"event": "public_mteb_scores_collected", "rows": len(ordered)}), flush=True)


if __name__ == "__main__":
    main()
