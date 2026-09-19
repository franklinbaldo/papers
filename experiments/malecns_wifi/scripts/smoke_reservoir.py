from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_wifi import smoke_reservoir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/smoke.json"))
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    result = smoke_reservoir(args.graph, args.output, seed=args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["final_finite"] or result["activity_spread"] <= 256:
        raise SystemExit("reservoir smoke gate failed: activity did not propagate stably")


if __name__ == "__main__":
    main()
