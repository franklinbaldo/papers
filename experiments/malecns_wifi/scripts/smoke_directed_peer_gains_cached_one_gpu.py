"""Single-seed directed peer-gain run using a frozen semantic embedding cache on CUDA.

Only encoder preparation is replaced by cache loading. All downstream directed-
teaching logic, MaleCNS recurrence, adapters, losses and validation remain the
existing CUDA implementation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import semantic_embedding_cache as cachelib
import smoke_concept_flavour_gpu as base
import smoke_directed_peer_gains_one_gpu as directed

_CACHE: Path | None = None
_CACHE_MANIFEST: dict | None = None


def _pop_arg(name: str) -> str:
    try:
        index = sys.argv.index(name)
        value = sys.argv[index + 1]
    except (ValueError, IndexError) as exc:
        raise SystemExit(f"{name} is required") from exc
    del sys.argv[index:index + 2]
    return value


def _cached_prepare_encoders(model_names, examples, scales, device):
    del device
    global _CACHE_MANIFEST
    encoders, manifest = cachelib.load_cache(
        model_names=model_names,
        examples=examples,
        scales=scales,
        cache=_CACHE,
    )
    _CACHE_MANIFEST = manifest
    print(json.dumps({
        "event": "semantic_embedding_cache_loaded",
        "cache": str(_CACHE),
        "fingerprint": manifest["fingerprint"],
        "backend": manifest["backend"],
        "device": manifest["device"],
        "seconds_original_build": manifest.get("seconds"),
    }), flush=True)
    return encoders


def _output_path() -> Path:
    try:
        return Path(sys.argv[sys.argv.index("--output") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("--output is required") from exc


def main() -> None:
    global _CACHE
    _CACHE = Path(_pop_arg("--embedding-cache"))
    base._prepare_encoders = _cached_prepare_encoders
    directed.main()

    path = _output_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["embedding_cache"] = {
        "path": str(_CACHE),
        "schema": _CACHE_MANIFEST.get("schema") if _CACHE_MANIFEST else None,
        "fingerprint": _CACHE_MANIFEST.get("fingerprint") if _CACHE_MANIFEST else None,
        "backend": _CACHE_MANIFEST.get("backend") if _CACHE_MANIFEST else None,
        "device": _CACHE_MANIFEST.get("device") if _CACHE_MANIFEST else None,
        "batch_size": _CACHE_MANIFEST.get("batch_size") if _CACHE_MANIFEST else None,
    }
    payload["encoder_forward_during_training"] = False
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
