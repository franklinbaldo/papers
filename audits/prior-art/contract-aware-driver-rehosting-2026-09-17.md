---
type: "Audit Report"
title: "Contract-aware shadow checking prior-art audit — 2026-09-17"
description: "Claim-specific prior-art audit of Windows driver rehosting and semantic sub-allocation boundary checking, with separate GitHub-derived cutoffs for the original SystemBuffer detector and the later generalized contract-aware framing."
tags: [driver-rehosting, windows, shadow-checking, prior-art, addresssanitizer, memory-safety, speakeasy, method-buffered]
timestamp: 2026-09-17T17:58:01-04:00
---

# Contract-aware shadow checking prior-art audit — 2026-09-17

> **Status:** first reproducible prior-art audit focused on [`contract_aware_driver_rehosting.md`](../../contract_aware_driver_rehosting.md). The main correction is that two component ideas have substantially older antecedents than the paper's current Related Work makes explicit: Windows kernel-driver execution/emulation outside the real kernel, and instrumentation of a logical sub-boundary that lies inside a physically allocated region. This audit does **not** establish exhaustive novelty, patent novelty, or causal dependence between projects.

## 1. Audited claims and claim-specific cutoffs

The paper currently combines two separable propositions:

1. **Windows/SystemBuffer-specific detector:** in a synthetic `METHOD_BUFFERED` request, instrument writes against both `N = max(InputBufferLength, OutputBufferLength)` and the narrower caller-declared `OutputBufferLength`; a write may be physically in-bounds yet cross the declared output boundary. Such a crossing remains a raw event until output intent is established.
2. **Generalized methodological framing:** **contract-aware semantic checking** observes accesses that remain physically memory-safe but cross a narrower logical boundary declared by an API/calling contract; user-mode driver rehosting is the experimental vehicle rather than the scientific endpoint.

These claims did not become public at the same time, so this audit uses two cutoffs.

### 1.1 SystemBuffer detector cutoff — 2026-08-13 16:05:22 UTC

Pull request [`#295`](https://github.com/franklinbaldo/papers/pull/295), **“Add contract-aware Windows driver rehosting paper,”** was publicly opened at **2026-08-13 16:05:22 UTC**. Its public body already states that the proposed checker:

- treats `H > OutputBufferLength` as a raw boundary-crossing event rather than automatically as a Windows-contract violation;
- separates logical boundary crossing, physical overflow, and invalid completion length;
- requires evidence of output intent before semantic promotion;
- keeps the M5 checker independently exercisable over typed trace fixtures; and
- includes benign shared-buffer scratch/input-tail negative controls.

The PR head was `b413d10a2ab6a295e11f3f5151cba08b5a4887f1`; the paper was later merged by `6599de44643c220289e0d4457e6c5c62a0cb85a8`.

For the concrete SystemBuffer detector combination, the conservative public cutoff is therefore **2026-08-13 16:05:22 UTC**.

### 1.2 Generalized contract-aware semantic-checking cutoff — 2026-09-17 14:32:15 UTC

Pull request [`#480`](https://github.com/franklinbaldo/papers/pull/480), **“Clarify contract-aware shadow checking contribution,”** was publicly opened at **2026-09-17 14:32:15 UTC**. Its body explicitly says that the revision makes **contract-aware semantic checking** the primary methodological contribution, treats rehosting as the experimental vehicle, renames the raw event to `DECLARED_OUTPUT_BOUNDARY_CROSSING`, and reserves `OUTPUT_OVERRUN` for cases with output-intent evidence.

That framing was not stated with the same generality in the original August paper. For claims about the broad abstraction “physical allocation permits the access, but a narrower semantic/API contract forbids it,” the conservative public cutoff is therefore **2026-09-17 14:32:15 UTC**.

## 2. Search protocol

The search deliberately decomposed the current contribution into older vocabularies instead of searching only for the paper's names. Representative queries included:

- `AddressSanitizer container overflow inside allocated heap region outside current container bounds`
- `annotate_contiguous_container capacity size shadow memory`
- `subobject bounds sanitizer physically in bounds allocation`
- `EffectiveSan sub-object bounds overflow`
- `Windows kernel driver user mode emulation`
- `kernel driver unpacking user mode fake ntoskrnl`
- `Speakeasy kernel mode Windows binaries DriverEntry IRP`
- `METHOD_BUFFERED SystemBuffer InputBufferLength OutputBufferLength larger of two`
- `SystemBuffer shadow checker OutputBufferLength`
- `declared output boundary crossing driver`
- `contract-aware memory safety API boundary`
- post-cutoff variants of `Windows driver user-mode emulation 2026`, `OutputBufferLength shadow`, and the exact event name `DECLARED_OUTPUT_BOUNDARY_CROSSING`.

Sources checked included GitHub history for our cutoff, LLVM/AddressSanitizer historical material, the EffectiveSan preprint, x64dbg's original driver-unpacking write-up, Mandiant's Speakeasy documentation, Microsoft Windows-driver documentation, and targeted recent web searches. Primary/project sources were preferred; recent searches were used only to identify possible post-cutoff overlap.

## 3. Findings before the relevant cutoffs

### 3.1 AddressSanitizer container-overflow already checks a logical used-range boundary inside a larger valid allocation

**Classification:** `prior_art` for the broad abstraction “instrument a narrower logical bound that lies inside a physically allocated region”; strong `partial_prior_art` for the current contract-aware methodology as a whole.

LLVM's libc++ added AddressSanitizer support to `std::vector` in revision `r208319`; the LLVM commit discussion is dated **2014-05-12**:

- <https://lists.llvm.org/pipermail/cfe-commits/Week-of-Mon-20140512/105270.html>

The sanitizer interface distinguishes a container's full owned region `[beg, end)` from its currently used region `[beg, mid)`, allowing `[mid, end)` to be poisoned even though it remains part of the same underlying allocation. Historical AddressSanitizer documentation describes a **container-overflow** precisely as an access inside `[v.end(), v.begin() + v.capacity())`: **inside the allocated heap region but outside current container bounds**.

- <https://github.com/google/sanitizers/wiki/AddressSanitizerContainerOverflow>

That is a direct antecedent to the generalized logical-versus-physical-boundary idea added in PR #480. The present paper cannot defensibly assign component-level novelty to the proposition that shadow metadata may make a stricter semantic/used extent observable inside a larger physically valid allocation.

**Difference:** the ASan container annotation receives the logical container extent directly and reports access to the reserved region. It does not model Windows I/O contracts, a shared input/output `SystemBuffer`, ambiguity about whether a crossing is semantically output, or an evidentiary promotion ladder from raw event to vulnerability.

### 3.2 EffectiveSan and earlier bounds-safety work establish sub-object boundaries below the enclosing allocation

**Classification:** `partial_prior_art`.

Duck & Yap, **“EffectiveSan: Type and Memory Error Detection using Dynamically Typed C/C++,”** arXiv v1 **2017-10-17**, explicitly targets **(sub-)object bounds overflows** and instruments dynamic type/bounds checks:

- <https://arxiv.org/abs/1710.06125>

This strengthens the historical point beyond `std::vector`: memory-safety tooling can attach bounds to an object or sub-object that are stricter than the containing storage allocation. SoftBound and related pointer-bounds systems provide an even older adjacent line for metadata-backed spatial bounds, although their ordinary object-bound formulation is less semantically close to an API-declared output role than ASan's annotated container extent or EffectiveSan's sub-object checks.

**Difference:** these tools infer or propagate language/object bounds. The current paper's proposed boundary is an operation-specific **contract field** (`OutputBufferLength`) that may be smaller than the physical `SystemBuffer`, and a crossing is deliberately *not* called a violation until output intent is independently supported.

### 3.3 Windows already documents the exact physical/logical size mismatch that motivates the detector

**Classification:** `partial_prior_art` for the Windows contract facts; not prior art for the proposed checker itself.

Microsoft's documentation for `METHOD_BUFFERED` states that `Irp->AssociatedIrp.SystemBuffer` represents both the input and output buffers, that input and output have separate `InputBufferLength` / `OutputBufferLength` fields, and that the system allocates one buffer whose physical size is the **larger** of the two lengths:

- <https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes>

Microsoft also documented by at least **2021-12-14** that buffered-request input and output overlap and that `IoStatus.Information` controls how much data is returned, with incorrect initialization/length handling creating disclosure risk:

- <https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/failure-to-initialize-output-buffers>

Thus the underlying Windows contract facts are established prior work. What remains to be evaluated is the proposed instrumentation and evidence taxonomy built on top of those facts.

### 3.4 User-mode execution/emulation of Windows kernel drivers predates the paper by years

**Classification:** `prior_art` for the narrow proposition “execute/rehost Windows kernel-driver binaries in user mode or an emulated non-kernel environment for analysis”; `partial_prior_art` for the complete paper.

#### x64dbg / mrexodia driver_unpacking — 2017

The x64dbg post **“Kernel driver unpacking”**, dated **2017-06-08**, describes converting a Windows driver so it can be loaded/debugged as a user-mode executable and faking kernel imports. The associated `mrexodia/driver_unpacking` repository describes itself as **“user mode emulation of Windows kernel drivers”** and provides `MakeUsermode`, with a fake `ntoskrnl.exe` acting as the emulator.

- <https://x64dbg.com/blog/2017/06/08/kernel-driver-unpacking.html>
- <https://github.com/mrexodia/driver_unpacking>

This is directly relevant prior art to any broad driver-rehosting claim.

#### Mandiant Speakeasy — 2021

Mandiant's **“Emulation of Kernel Mode Rootkits With Speakeasy”**, published **2021-01-20**, documents emulation of kernel-mode Windows binaries/device drivers. Speakeasy emulates `DriverEntry`, discovers and directly invokes IRP handlers with synthetic/dummy IRPs, models kernel structures, and can log all memory reads and writes made by the emulated sample.

- <https://cloud.google.com/blog/topics/threat-intelligence/emulation-of-kernel-mode-rootkits-with-speakeasy>
- <https://github.com/mandiant/speakeasy>

Speakeasy is therefore a particularly important antecedent missing from the current Related Work: it combines Windows-driver emulation, synthetic IRP execution, kernel-object modeling, and memory tracing years before our August 2026 cutoff.

**Difference:** neither the x64dbg approach nor the located Speakeasy material describes the paper's exact `METHOD_BUFFERED` dual-bound detector, the raw-crossing/output-intent distinction, or the E0→semantic finding→independent reproduction evidence discipline.

### 3.5 Driver-analysis systems without this exact rehosting shape remain adjacent rather than anticipatory

**Classification:** `adjacent_prior_work`.

Full-system and symbolic driver-analysis systems such as S2E/SymDrive, kAFL, BSOD, USBFuzz, Drifuzz and more recent QEMU/LibAFL workflows establish extensive prior work on analyzing or fuzzing drivers without requiring the proposed LiteBox architecture. They materially constrain claims of workflow novelty but do not, based on the sources inspected in this round, anticipate the exact contract-aware SystemBuffer sensor.

Several of these works are already cited by the paper. The important correction from this audit is that the **direct Windows user-mode/emulation lineage** (mrexodia and especially Speakeasy) belongs beside them.

## 4. Revised novelty boundary

The current contribution should be decomposed more narrowly than the phrase “contract-aware semantic checking” may suggest.

The following components are established before our cutoffs:

1. **Logical extent inside physical capacity:** ASan container annotations detect accesses within the owned allocation but outside the current logical container extent.
2. **Sub-object spatial bounds:** EffectiveSan and related work enforce bounds below the enclosing storage object.
3. **Windows `METHOD_BUFFERED` dual lengths:** Microsoft documents the shared `SystemBuffer`, distinct input/output lengths, max-sized allocation, and `Information`-controlled copy-back behavior.
4. **Windows driver rehosting/emulation:** x64dbg/mrexodia and Speakeasy execute or emulate Windows kernel drivers outside ordinary kernel loading; Speakeasy also exercises IRP entry points and records memory accesses.

After accounting for those antecedents, this search **did not locate** a pre-**2026-08-13 16:05:22 UTC** system that combines all of the following:

1. synthetic `METHOD_BUFFERED` execution with separate knowledge of the physical `max(InputBufferLength, OutputBufferLength)` allocation and caller-declared `OutputBufferLength`;
2. an explicit shadow event for a write that crosses the latter while remaining inside the former;
3. deliberate refusal to classify that crossing as an output overrun until IOCTL-specific schema, source-known fixture, phase/taint, or equivalent evidence establishes output intent;
4. a mandatory benign shared-buffer scratch/input-tail negative control;
5. fixture-level calibration independent of broad `.sys` compatibility; and
6. a separate evidence ladder requiring independent authorized reproduction before a vulnerability is called confirmed.

This is a **negative search result**, not proof that no antecedent exists. The defensible candidate novelty is therefore the **specific Windows I/O contract + ambiguity-aware promotion protocol + calibrated trace-checking combination**, not either driver rehosting or semantic/sub-allocation bounds in isolation.

For the generalized PR #480 framing, the audit is stricter: **“physically in-bounds but outside a narrower logical boundary” is already prior art as a general instrumentation idea**. The paper's stronger differentiation lies in where the logical boundary comes from (an external API/IOCTL contract), how ambiguous crossings are treated epistemically, and how that sensor is made independently testable inside a driver-rehosting methodology.

## 5. Post-cutoff search

Targeted searches after the August cutoff used the exact event name plus combinations of `OutputBufferLength`, `SystemBuffer`, `shadow`, `driver fuzzing`, `contract-aware`, `user-mode emulation`, and `Windows driver rehosting`. The recent results located in this pass were either ordinary user-mode-driver/virtual-device work, general contract checking, or unrelated driver/security material.

No post-**2026-08-13** work located in this round was close enough to the complete combination to classify as `later_independent`, `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative`.

That statement is deliberately bounded to these searches. It does not establish that no later overlapping work exists.

## 6. Candidate register

| Candidate | Earliest public date verified here | Venue/status | Claim compared | Classification | Why |
|---|---:|---|---|---|---|
| AddressSanitizer contiguous-container annotations / libc++ `std::vector` support | 2014-05-12 | LLVM implementation/discussion | logical used extent inside larger physical allocation | `prior_art` for broad abstraction; `partial_prior_art` overall | Explicitly poisons/reports the capacity tail while it remains inside the allocation. |
| EffectiveSan — Duck & Yap | 2017-10-17 | arXiv preprint / later research paper | sub-object bounds below enclosing object | `partial_prior_art` | Dynamic bounds/type instrumentation catches sub-object overflows; not an API-role contract. |
| x64dbg / `driver_unpacking` | 2017-06-08 | project/blog | Windows kernel driver in user mode with fake kernel imports | `prior_art` for rehosting subclaim | Direct user-mode Windows-driver execution/research antecedent. |
| Mandiant Speakeasy kernel-mode emulation | 2021-01-20 | project/blog | Windows driver emulation + synthetic IRPs + memory tracing | `prior_art` for emulation subclaim; strong `partial_prior_art` overall | Very close rehosting substrate, but no located dual SystemBuffer contract sensor. |
| Microsoft buffered-I/O contract documentation | public by 2021-12-14 for the inspected output-buffer guidance | platform documentation | shared SystemBuffer, distinct input/output lengths, completion length | `partial_prior_art` | Establishes the exact Windows contract facts the proposed checker operationalizes. |

## 7. Queries with negative or non-promoting results

The following searches were retained because they constrain, but do not prove, the remaining novelty boundary:

- `"DECLARED_OUTPUT_BOUNDARY_CROSSING" driver` — no independently published implementation using the paper's event/taxonomy was located.
- `"OutputBufferLength" "shadow" driver fuzzing` — no located result combined dual physical/logical SystemBuffer bounds with the paper's ambiguity-aware promotion rule.
- `"SystemBuffer" "container overflow" driver` — no direct Windows analogue of ASan's container annotation was located.
- `"contract-aware" memory safety sanitizer API boundary` — broad contract/interface-checking results appeared, but no source was promoted merely on terminology.
- recent `"Windows driver" "user-mode emulation" 2026` searches — results were not materially close to the complete claim.

“Not located” means only that the stated search did not produce a sufficiently close, verifiable candidate.

## 8. Epistemic update

This round changes the prior-art picture materially:

- **Driver rehosting itself is firmly anteceded.** Speakeasy and the 2017 x64dbg/mrexodia workflow should be treated as direct prior art, not merely distant related work.
- **The generalized logical-versus-physical-boundary idea is also anteceded.** AddressSanitizer container-overflow is a clear counterexample to any broad originality reading of that abstraction.
- **The possible contribution survives only at the combination level:** an external Windows I/O contract supplies the inner bound; the same physical allocation has dual input/output semantics; crossing is observed but not semantically promoted without intent evidence; calibration includes an ambiguity-matched negative control; and the trace checker is decoupled from broad driver compatibility and from the vulnerability claim.

Accordingly, future paper revisions should avoid suggesting novelty for “semantic checking inside a physical allocation” or “user-mode Windows driver rehosting” as standalone ideas. The stronger, still-unresolved question is whether the **specific `METHOD_BUFFERED` contract-aware, ambiguity-aware evidence protocol** provides useful detection beyond existing Windows baselines such as Driver Verifier while remaining calibratable in the proposed rehosting harness.
