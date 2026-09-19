from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_wifi import CompilePolicy, compile_connectome, source_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1"))
    parser.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "malecns-wifi")
    parser.add_argument("--mirror-base-url", default=None)
    parser.add_argument("--min-synapses", type=int, default=3)
    args = parser.parse_args()

    manifest = compile_connectome(
        output_dir=args.output,
        cache_dir=args.cache,
        source=source_spec(args.mirror_base_url),
        policy=CompilePolicy(min_synapses=args.min_synapses),
    )
    print(json.dumps(manifest["runtime"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
