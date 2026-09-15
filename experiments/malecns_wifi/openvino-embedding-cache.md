# OpenVINO frozen-embedding cache for local MaleCNS runs

This path turns the frozen semantic encoders into one-time preprocessing.
The scientific experiment still trains flavours/adapters/readout against the
MaleCNS dynamics; MiniLM/E5 do **zero forward passes during training**.

## Why this is separate

The existing CUDA/Kaggle runners are untouched.  This local path changes only
how frozen semantic fields are materialized.  Cache provenance is checked against:

- exact model ids;
- exact train/validation text, phrases, labels and groups;
- scales;
- positive/negative/held-out anchor banks.

A mismatch fails instead of silently reusing stale vectors.

## Environment

Use `uv`; never `uvx`.

```powershell
uv venv .venv-openvino --python 3.11
.venv-openvino\Scripts\activate
uv pip install "sentence-transformers[openvino]" numpy scipy torch scikit-learn
```

Confirm OpenVINO sees the Intel GPU:

```powershell
python -c "import openvino as ov; print(ov.Core().available_devices)"
```

Expected on the target machine: a list containing `GPU`.

## 1. Build the cache once on UHD 630

```powershell
uv run python experiments/malecns_wifi/scripts/build_semantic_embedding_cache.py `
  --output .cache/malecns/recurso-semantic-fields.npz `
  --backend openvino `
  --device GPU `
  --batch-size 64
```

The first OpenVINO load may export/compile the model and therefore be slower.
The resulting files are:

- `recurso-semantic-fields.npz` — byte-aligned frozen vectors;
- `recurso-semantic-fields.manifest.json` — provenance, backend/device and timings.

The cache is generated from the exact same windowing, E5 prefixes and byte-axis
alignment as the existing smoke.

## 2. Train from cache

CPU-only dense modules:

```powershell
uv run python experiments/malecns_wifi/scripts/smoke_directed_peer_gains_cached_hybrid.py `
  --embedding-cache .cache/malecns/recurso-semantic-fields.npz `
  --graph path\to\graph.npz `
  --output local-directed-cpu.json `
  --dense-device cpu `
  --seed 20260918
```

If the isolated DirectML environment from PR #455 is available, the same cached
fields can be reused with:

```powershell
uv run python experiments/malecns_wifi/scripts/smoke_directed_peer_gains_cached_hybrid.py `
  --embedding-cache .cache/malecns/recurso-semantic-fields.npz `
  --graph path\to\graph.npz `
  --output local-directed-dml.json `
  --dense-device directml `
  --seed 20260918
```

No encoder inference occurs in either training run.

## Parity gate before scientific use

Run the same seed with CPU and DirectML dense modules.  Do not use DirectML
results as scientific evidence until the arm metrics and learned parameters are
numerically compatible within an explicitly reported tolerance.

The embedding cache itself should be treated as deterministic input data.  When
comparing Torch-vs-OpenVINO embedding generation, report cosine/error statistics
before treating caches from the two backends as interchangeable.

## What this does not do

- no model fine-tuning;
- no LoRA in MiniLM/E5;
- no new attention/router;
- no changed lambda, seeds, scales, epochs or gates;
- no repeated encoder forward per epoch.
