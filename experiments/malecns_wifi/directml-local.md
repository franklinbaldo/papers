# MaleCNS local hybrid backend (Windows / DirectML)

This path is deliberately separate from the CUDA/Kaggle scientific runners.
It exists to test whether the Intel UHD 630 can accelerate the small dense
trainable modules while the sparse MaleCNS recurrence remains on CPU.

## Architecture

```text
frozen MiniLM / E5        CPU (first prototype)
        |
        v
native semantic fields    CPU
        |
        +----> ChannelAdapter / flavour      DirectML or CPU
        |                |
        |                v
        |        relation features
        |                |
        +<---------------+
        |
        v
sparse MaleCNS recurrence CPU
        |
        v
readout state             CPU
        |
        v
taste head + loss         DirectML or CPU
```

CPU<->dense copies remain in the autograd graph.  A backend that cannot carry
those gradients must fail; there is no silent algorithmic fallback.

This is an operational backend experiment.  Do not treat DirectML results as
confirmatory evidence until CPU-vs-DirectML numerical parity has been checked.

## Isolated environment

`torch-directml` may require a different PyTorch version from the main repo.
Do not downgrade the main environment.  Create a separate Windows venv with
`uv` (never `uvx`):

```powershell
uv venv --python 3.11 .venv-directml
uv pip install --python .venv-directml\Scripts\python.exe `
  torch-directml numpy scipy scikit-learn sentence-transformers
```

Confirm the device:

```powershell
.venv-directml\Scripts\python.exe -c "import torch_directml; print(torch_directml.device_name(0))"
```

Expected on the target machine: an Intel UHD Graphics 630 DirectML device.

## 1. Benchmark the exact channel adapter

From `experiments/malecns_wifi`:

```powershell
.venv-directml\Scripts\python.exe scripts\benchmark_directml_adapter.py `
  --device both `
  --batch 256 `
  --steps 100 `
  --output artifacts\directml-adapter-benchmark.json
```

The JSON reports CPU and DirectML milliseconds/step plus
`directml_speedup_over_cpu`.  This exercises forward, BCE, backward and AdamW
using the real rank-16 residual `ChannelAdapter`.

Repeat at batches 32, 64, 128, 256 and 512 before deciding whether the iGPU is
worth using; tiny batches may be overhead-bound.

## 2. Run the hybrid directed-peer prototype

Use the same frozen `graph.npz` as the CUDA runs.

CPU dense control:

```powershell
.venv-directml\Scripts\python.exe scripts\smoke_directed_peer_gains_local_hybrid.py `
  --graph path\to\graph.npz `
  --output artifacts\directed-cpu-seed-20260918.json `
  --dense-device cpu `
  --seed 20260918
```

DirectML dense arm:

```powershell
.venv-directml\Scripts\python.exe scripts\smoke_directed_peer_gains_local_hybrid.py `
  --graph path\to\graph.npz `
  --output artifacts\directed-directml-seed-20260918.json `
  --dense-device directml `
  --seed 20260918
```

Before using DirectML scientifically, compare the CPU and DirectML runs for the
same seed and initialization.  Curves need not be bit-identical, but the arm
ordering and metrics should be numerically close enough that backend choice is
not changing the conclusion.

After parity, run the preregistered seeds `20260918` and `20260919`.

## Scope

The current hybrid prototype intentionally does **not**:

- change the existing CUDA/Kaggle runners;
- add inference-time channel attention;
- change `peer_lambda=0.50`, scales, models, epochs, or seeds;
- move sparse MaleCNS operations to DirectML;
- use OpenVINO yet.

A later independent optimization may run the frozen MiniLM/E5 encoder inference
through OpenVINO and cache the native semantic fields.  That is orthogonal to
this DirectML training path and should be benchmarked separately.
