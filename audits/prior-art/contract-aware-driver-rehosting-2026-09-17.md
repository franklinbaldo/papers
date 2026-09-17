---
type: "Audit Report"
title: "Prior-art audit — contract-aware driver shadow checking"
description: "Claim-level prior-art audit for contract-aware semantic checking and Windows driver rehosting, with GitHub cutoffs fixed before comparison."
tags: [prior-art, driver-rehosting, shadow-checking, windows, methodology]
timestamp: 2026-09-17T13:03:00-04:00
---

# Prior-art audit — contract-aware driver shadow checking

This audit separates the paper's concrete `METHOD_BUFFERED` sensor from the broader framing added later as **contract-aware semantic checking**. It asks what was already public before each claim appeared in this repository, rather than comparing only current publication dates.

## 1. Claim-specific cutoffs

### C1 — `SystemBuffer` declared-output-boundary sensor

The earliest public GitHub evidence located in this repository is pull request [#295](https://github.com/franklinbaldo/papers/pull/295), opened **2026-08-13 16:05:22 UTC**. Its initial paper already proposed a `SystemBuffer Shadow Checker` for synthetic `METHOD_BUFFERED` requests that distinguishes the physical allocation from `OutputBufferLength` and detects a write that remains inside `max(InputBufferLength, OutputBufferLength)` while crossing the caller-declared output boundary. The initial commit in that line is [`b64aa178`](https://github.com/franklinbaldo/papers/commit/b64aa178549fbe8ad11e1a7cd5a62280ba7e130d).

**Cutoff for C1:** 2026-08-13 16:05:22 UTC.

### C2 — generalization to “contract-aware semantic checking”

The exact framing that the scientific contribution is broader than driver rehosting and consists of detecting physically memory-safe accesses that cross a logical API-contract boundary first appears explicitly in pull request [#480](https://github.com/franklinbaldo/papers/pull/480), opened **2026-09-17 14:32:15 UTC**.

The underlying concrete mechanism is older (C1), but the broad abstraction is claim-specific and therefore gets its own later cutoff.

**Cutoff for C2:** 2026-09-17 14:32:15 UTC.

### C3 — rehosting as a cheaper experimental vehicle

The August paper already hypothesized that selected driver logic could be exercised without installation/hardware/reboot costs while leaving the host authorization boundary unchanged. That claim remains explicitly empirical and unproven in the paper.

**Cutoff for C3:** 2026-08-13 16:05:22 UTC.

## 2. Audited claims

- **C1.** A trace checker can flag writes that cross the caller-declared `OutputBufferLength` while remaining inside the larger physical `SystemBuffer` allocation used by `METHOD_BUFFERED`, and keep that raw event distinct from a confirmed output overrun.
- **C2.** “Contract-aware semantic checking” is the broader methodological idea: instrumenting logical/API boundaries that may lie inside a physically valid allocation, rather than treating allocation safety as the only relevant boundary.
- **C3.** User-mode rehosting can make this kind of instrumentation and replay cheaper or easier than a native/VM workflow, subject to calibration and matched authorization/cost measurements.

## 3. Pre-cutoff antecedents

### 3.1 AddressSanitizer container-overflow — `partial_prior_art` for C2

AddressSanitizer's documented **container-overflow** mode explicitly detects access in the interval between a container's logical `end()` and its allocated `capacity()`: the access is **inside the allocated heap region but outside the current logical container bounds**. The public sanitizer documentation was already present by 2017.

Source: [AddressSanitizerContainerOverflow](https://github.com/google/sanitizers/wiki/AddressSanitizerContainerOverflow), edited 2017-03-31; foundational shadow-memory sanitizer paper: Serebryany et al., [AddressSanitizer: A Fast Address Sanity Checker](https://www.usenix.org/conference/atc12/technical-sessions/presentation/serebryany), USENIX ATC 2012.

**Classification:** `partial_prior_art` for C2; `adjacent_prior_work` for C1.

**Why it matters:** the broad statement “conventional memory instrumentation asks only whether an access remains inside the allocation” is too strong. At least one established sanitizer family can encode and check a logical bound strictly inside an allocated region. It does not, however, derive that bound from a Windows IOCTL contract or distinguish raw boundary crossing from output intent.

### 3.2 EffectiveSan sub-object bounds — `partial_prior_art` for C2

EffectiveSan dynamically narrows bounds to C/C++ sub-objects and reports accesses that remain within the containing allocation but fall outside the selected sub-object. This is another pre-cutoff example of runtime instrumentation enforcing a semantic/logical boundary finer than allocation extent.

Source: Duck and Yap, [EffectiveSan: Type and Memory Error Detection using Dynamically Typed C/C++](https://pldi18.sigplan.org/details/pldi-2018-papers/14/EffectiveSan-Type-and-Memory-Error-Detection-using-Dynamically-Typed-C-C-), PLDI 2018.

**Classification:** `partial_prior_art` for C2; `adjacent_prior_work` for C1.

**Overlap:** logical/sub-object bounds inside a larger physical allocation, dynamic instrumentation, explicit error reporting.

**Difference:** the bound comes from effective type/sub-object layout, not from an API's request contract or operation-specific input/output semantics.

### 3.3 Windows buffered-I/O contract — `adjacent_prior_work` for C1

Microsoft has long documented that for `METHOD_BUFFERED`, one `SystemBuffer` represents both input and output, while `InputBufferLength` and `OutputBufferLength` remain distinct logical lengths and the allocated system buffer is sized to the larger of the two. Microsoft also separately documents that drivers must validate buffer sizes and that `IoStatus.Information` can exceed the output buffer if a driver fails to check it.

Sources:

- [Buffer Descriptions for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes).
- [Failure to Check the Size of Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/failure-to-check-the-size-of-buffers), public Microsoft documentation with a 2021 update date.
- [Failure to Initialize Output Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/failure-to-initialize-output-buffers), likewise documenting the overlapping buffered-I/O layout and output-length semantics.

**Classification:** `adjacent_prior_work` for C1.

These sources establish the exact Windows contract on which the checker operates, but they do not by themselves describe the paper's standalone trace sensor or its evidence ladder.

### 3.4 DDT — `adjacent_prior_work` for C3 and driver-testing architecture

Kuznetsov, Chipounov, and Candea's **DDT** automatically tested closed-source Windows binary drivers without requiring the corresponding hardware, using selective symbolic execution plus virtualization and modular dynamic checkers. The system produced executable traces and found 14 serious bugs in Microsoft-certified drivers.

Source: [Testing Closed-Source Binary Device Drivers with DDT](https://www.usenix.org/conference/usenix-atc-10/testing-closed-source-binary-device-drivers-ddt), USENIX ATC, June 2010.

**Classification:** `adjacent_prior_work` for C3.

DDT predates the current paper by sixteen years and is important against any broad novelty claim around “testing Windows binary drivers without hardware with modular dynamic checkers.” It does not use the same process-local `METHOD_BUFFERED` logical-bound sensor, and it relies on virtualization/selective symbolic execution rather than the proposed LiteBox-style vehicle.

### 3.5 SymDrive — `adjacent_prior_work` for C3

SymDrive tests Linux and FreeBSD drivers without their devices, using symbolic execution and driver-state checkers. It demonstrates the older general strategy of replacing or abstracting hardware dependencies so driver logic can be exercised and checked under an analysis harness.

Source: Renzelmann, Kadav, and Swift, [SymDrive: Testing Drivers without Devices](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/renzelmann), OSDI 2012.

**Classification:** `adjacent_prior_work` for C3.

### 3.6 Para-rehosting and rehosting for dynamic analysis — `adjacent_prior_work` for C3

Li et al. proposed **para-rehosting**, natively executing microcontroller software on commodity hardware and then applying off-the-shelf dynamic analysis such as AFL and ASan. Their 2021 work explicitly frames rehosting as a way to make mature host-side testing tools available to otherwise difficult targets.

Source: Li et al., [From Library Portability to Para-rehosting: Natively Executing Microcontroller Software on Commodity Hardware](https://arxiv.org/abs/2107.12867), arXiv v1 2021-07-04.

**Classification:** `adjacent_prior_work` for C3.

The current paper's Windows-driver target, authorization accounting, typed fixtures, and buffered-I/O checker differ, but the general “rehost to lower analysis friction and reuse instrumentation” idea is established prior work.

### 3.7 LibAFL QEMU Windows-driver case study — `adjacent_prior_work` for C3

LibAFL QEMU provides fuzzing-oriented QEMU integration in system and user modes and includes a Windows kernel-driver case study, explicitly comparing against kAFL.

Source: Malmain, Fioraldi, and Francillon, [LibAFL QEMU: A Library for Fuzzing-oriented Emulation](https://www.eurecom.fr/en/publication/7610), BAR/NDSS 2024.

**Classification:** `adjacent_prior_work` for C3.

### 3.8 LifeFuzz — `adjacent_prior_work` for Windows-driver fuzzing

LifeFuzz is a 2026 EuroSys paper on lifecycle-guided fuzzing for Windows driver cross-handler vulnerabilities. Its public bibliographic record predates C1's August cutoff.

Source: Yu et al., [LifeFuzz: Lifecycle-Guided Fuzzing for Windows Driver Cross-Handler Vulnerabilities](https://dblp.org/rec/conf/eurosys/YuLXLLBH26), EuroSys 2026.

**Classification:** `adjacent_prior_work` for C1/C3.

It narrows the space in which the current project can claim novelty for Windows-driver fuzzing generally, but no evidence located in this round shows LifeFuzz implementing the same declared-output-boundary-within-allocation sensor.

## 4. What survives this round

The broad C2 formulation is **not novel as a general principle**. Runtime systems had already demonstrated that a physically valid memory access can violate a finer logical boundary and that shadow/metadata instrumentation can detect such cases. AddressSanitizer container-overflow is especially close at the geometric level: allocated capacity is larger than the logical valid range.

The narrower C1 combination remains unresolved after this search. I did **not locate** pre-cutoff work that combines all of the following in one method:

1. the Windows `METHOD_BUFFERED` shared-allocation geometry;
2. explicit observation of `write_end > OutputBufferLength` while `write_end <= max(InputBufferLength, OutputBufferLength)`;
3. classification of that observation as a raw boundary-crossing event rather than automatically a bug;
4. promotion only after operation-specific evidence establishes output intent; and
5. independent reproduction before vulnerability confirmation.

That is a negative search result, not proof of firstness.

C3 also cannot be claimed broadly as novel: driver testing without devices, rehosting, virtualization, symbolic execution, and host-side dynamic analysis all have extensive antecedents. What remains specific is the proposed measurement of research cost under an explicitly recorded authorization tuple and the use of rehosting as a vehicle for this particular semantic sensor.

## 5. Search record

Representative searches performed in this round included:

- `"contract-aware" memory safety logical bounds allocation shadow checking API contract buffer`
- `"container-overflow" AddressSanitizer logical end allocated buffer`
- `"intra-object overflow" dynamic bounds checking memory safety EffectiveSan`
- `"SystemBuffer" "OutputBufferLength" driver verifier METHOD_BUFFERED`
- `"METHOD_BUFFERED" "OutputBufferLength" overflow driver fuzzing`
- `"device driver rehosting" user mode Windows driver fuzzing`
- `"device driver" rehosting symbolic execution user mode driver testing S2E SymDrive DDT`
- `"API contract" runtime checking memory buffer bounds shadow memory`
- `"Windows driver" "user mode" rehosting binary driver testing paper`
- `"IOCTL" fuzzing "OutputBufferLength" Windows driver paper`
- `"semantic" "buffer overflow" "API contract" sanitizer`

Sources were checked against primary venue/project pages where available: USENIX, SIGPLAN/PLDI, Microsoft Learn, arXiv, EURECOM/NDSS workshop records, and the GitHub history of this repository.

## 6. Classification update

| Claim | Previous practical reading | This audit |
|---|---|---|
| C1 exact `METHOD_BUFFERED` trace sensor + evidence ladder | apparently distinctive | **unresolved exact-combination novelty**; several adjacent antecedents, no exact pre-cutoff match located |
| C2 broad contract-aware semantic checking | framed as primary methodological contribution | **partially anticipated** by logical/container/sub-object bounds checking; broad novelty should not be implied |
| C3 rehosting lowers analysis friction | hypothesis | **established adjacent strategy, empirical local hypothesis remains open** |

## 7. Consequence for the paper

The current paper should be read narrowly. Its strongest defensible contribution claim after this audit is not “memory instrumentation usually knows only allocation bounds,” nor “rehosting makes driver analysis possible.” It is the **Windows-specific composition and evidentiary discipline**: an operation-aware `METHOD_BUFFERED` trace sensor that separates physical safety, declared output boundary, semantic output intent, and independent confirmation.

A future edit to `contract_aware_driver_rehosting.md` should add AddressSanitizer container-overflow and EffectiveSan to Related Work and narrow the sentence contrasting the proposal with “conventional memory instrumentation.” The present audit records that required correction without retroactively rewriting the claim's publication history.

## 8. Later work

No post-C1 (after 2026-08-13 16:05:22 UTC) work was located in this round that materially matches the exact C1 composition. Searches did find later/current Windows-driver security material, but nothing with enough method-level overlap to justify `later_overlap` or `later_non_citing` for the exact claim.

Absence of a located later match is provisional and should be revisited as the hourly search expands into patents, theses, code repositories, and less-indexed security tooling.
