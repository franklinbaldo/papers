---
type: "Technical Paper"
title: "Contract-Aware Shadow Checking for User-Mode Windows Driver Rehosting"
description: "A methodology for observing declared-output-boundary crossings and invalid completions in a calibrated driver-rehosting harness, framed by privilege ceilings and researcher affordance floors."
tags: [driver-rehosting, windows, litebox, shadow-checking, security-research, methodology, dual-use]
timestamp: 2026-08-13T00:00:00-04:00
---

# Contract-Aware Shadow Checking for User-Mode Windows Driver Rehosting

> **Position and methodology paper.** LiteBox capability brokering and two
> read-only Windows backends have been demonstrated on unmerged draft commit
> [`a74e5e2`](https://github.com/franklinbaldo/litebox/commit/a74e5e2d132a1981c6a5934e722000f07692526c).
> Windows `.sys` loading, a synthetic NT ABI, shadow checking, and third-party
> evaluation remain specifications or incomplete scaffolds. The current M1–M7
> scaffold has not passed this paper's calibration or containment gates. This
> paper reports no driver vulnerability. Empirical results must revise it rather
> than be implied retroactively.

## Abstract

Privilege is often modeled as a scalar: a process either gains authorization or
it does not. Program rehosting exposes a second axis. A non-administrative
Windows process that rehosts selected driver logic retains the same host token,
yet may lower the cost of relocation, synthetic requests, memory tracing, and
process-local fuzzing. We call the invariant authorization boundary the
**privilege ceiling** and the set of research actions affordable under an
explicit resource budget the **researcher affordance floor**. This usage follows
the repository's [affordance-restriction framework](affordance_restriction.md);
it is intentionally distinct from LiteBox's capability-based access registry.

The primary technical proposal is a fixture-driven SystemBuffer Shadow Checker
for synthetic `METHOD_BUFFERED` requests. It records writes that cross the
declared output boundary while remaining inside the shared physical allocation.
Because that allocation also contains input, such a crossing is an E0 shadow
event, not automatically a Windows-contract violation. Promotion to a confirmed
output overrun requires an IOCTL-specific schema, source-known toy, or execution
phase that establishes output intent. By contrast,
`IoStatus.Information > OutputBufferLength` is a distinct invalid-completion
event. The trace checker is demonstrable without loading or executing a `.sys`;
typed serializable fixtures decouple it from the PE loader and synthetic NT ABI.

A PE loader, minimal NT ABI, instrumented allocator, explicit IRQL state,
isolation, calibration, abandonment, and coordinated-disclosure gates support
that sensor. The paper does not claim that rehosting reproduces Windows or
eliminates VMs for hostile targets. Toys written by the researcher may support
local iteration; third-party native code requires a disposable VM unless a
stronger boundary is demonstrated.

## 1. Privilege ceiling and affordance cost

Let `A` be a preregistered set of research actions, such as relocating a PE,
dispatching one request, recovering from a fault, and reproducing a finding.
For workflow `w`, measure each action with the cost vector
`cost_w(a) = (operator time, machine time, privileged steps, resets, hardware,
uncontained failures)`. Given an explicit budget vector `B`, define
`F_w(B) = {a in A | cost_w(a) <= B}`, where comparison is componentwise and the
units and normalization of every component are frozen before measurement. The
**researcher affordance floor** is this measured set, not a mathematical minimum
and not an authorization primitive.

Authorization is not collapsed into one workflow scalar. Each run records
`P_w = (host token, guest token, privileged setup steps, kernel execution)`.
The rehosting claim is that the host token is not expanded by loading the
harness or selecting a broker. It does **not** assume
`P_rehost = P_baseline`: a native VM baseline may require guest administration
and kernel execution even when the host identity is unchanged. The falsifiable
cost hypothesis is narrower: conditional on the recorded authorization tuple,
`F_rehost(B)` strictly contains `F_baseline(B)` for at least one preregistered
budget. Failure to observe that difference rejects the affordability claim.

Invoking `.sys` code grants no ring-0 execution, DMA, interrupts, physical
memory, or arbitrary device handles. Removing installation, hardware, recovery,
and instrumentation costs can nevertheless broaden defensive participation. It
can also lower the cost of finding defects whose exploitation might later
attack an unchanged privilege ceiling. Affordance must therefore grow together
with evidentiary discipline and containment.

## 2. Demonstrated substrate versus proposed artifact

The substrate is an unmerged LiteBox fork draft that runs rewritten Linux ELF
programs in a Windows user-mode process. It adds a capability registry, profiles
(`none`, `safe`, `host`), explicit selection, and fail-closed rejection of
unavailable capabilities. CPU, SIMD, memory, clocks, and threads are inherent;
brokered resources require policy.

Two read-only brokers have been demonstrated on draft commit `a74e5e2`:
`hostinfo` returns architecture and logical-processor data, and `power` queries
AC/battery state through the Windows power stack. An ELF toy also executed
`CPUID`, `RDTSC`, and `RDRAND` with brokered hardware set to `none`. These
results demonstrate policy-controlled brokering and direct CPU instructions.
They do not demonstrate `.sys` rehosting, device passthrough, hostile-code
isolation, or vulnerability discovery.

The proposed execution pipeline is:

```text
driver.sys
  -> read-only PE inspection and relocation
  -> minimal allowlisted NT ABI
  -> synthetic DRIVER_OBJECT / DEVICE_OBJECT / IRP
  -> instrumented memory and declared-boundary shadow state
  -> captured output and trapped operations
```

That pipeline does not impose a demonstration dependency. Every boundary has a
typed, serializable fixture so that each module can be exercised without the
previous stage:

| Module | Fixture | Sole evidence authority |
|---|---|---|
| M1 PE loader | raw `.sys` bytes | parsed/relocated image or structural rejection |
| M2 import resolver | import-table record | resolved, unsupported, or trapped import |
| M3 synthetic NT | `DriverEntry` plus one IOCTL fixture | deterministic status and output |
| M4 allocator | allocation/free/access trace | spatial or temporal memory event |
| M5 shadow checker | lengths, write intervals, completion record | declared-boundary, physical-overflow, and completion events |
| M6 IRQL model | transition and access sequence | IRQL contract event |
| M7 isolation | payload plus resource policy | contained exit and structured log |

M5 is therefore a standalone pure sensor over a trace. Its seeded and negative
cases execute no PE and no hostile code. M7 gates any module that executes real
native code; M1–M6 can still be reviewed against synthetic fixtures. This
decomposition is tracked by LiteBox issue #16 and children #17–#23 [21]. The
current implementation PR #24 is an unvalidated scaffold, not evidence that
these contracts have been met [22].

Unresolved imports and external effects fail closed. The first executable
target is written specifically for calibration. Third-party binaries remain
excluded until the gate in Section 7 passes.

## 3. Minimal synthetic NT model

This is not an NT-kernel emulator. It freezes one small, single-threaded toy
contract:

- PE relocation and an allowlisted entry point;
- synthetic driver and device objects;
- `DriverEntry` and one device-control dispatch routine;
- bounded allocation, free, logging, creation, and completion stubs;
- one buffered IOCTL;
- no PnP, WMI, cancellation, DPC, DMA, interrupts, direct I/O, or
  `METHOD_NEITHER`.

Unknown behavior produces `UNSUPPORTED` or `TRAPPED_OPERATION`; it is never
approximated silently.

### 3.1 Explicit IRQL state

The toy keeps an emulated current IRQL, starts supported dispatch at a documented
fixed level, and records modeled transitions. Paged-pool access at an
incompatible level becomes a contract event rather than succeeding because
user-mode memory happens to be resident. This does not reproduce scheduling,
interrupts, cancellation, or multiprocessor interleavings. Findings depending
on them are out of scope; paths requiring them create known false negatives.

### 3.2 Instrumented allocation

Pool stubs track address, requested size, tag, state, and available call site.
Redzones and guard pages detect spatial errors where practical. Distinct poison
patterns expose uninitialized and stale accesses. A bounded free quarantine
makes use-after-free and double-free observable. This instrumentation is a
sensor, not containment; crashes and loops require a separate process boundary.

## 4. The SystemBuffer Shadow Checker

For a synthetic `METHOD_BUFFERED` request, the modeled I/O manager allocates
`N = max(InputBufferLength, OutputBufferLength)`, copies bounded input into
`SystemBuffer`, invokes dispatch, and models bounded copy-back. Physical bounds
and the declared caller-output boundary are different. With input length 64 and
output length 8, a 32-byte write may remain inside the allocation while crossing
the declared output boundary. A trailing guard page alone cannot observe that
crossing.

The checker records every write interval `W_i = [o_i, o_i + s_i)` using checked
arithmetic and computes `H = max_i(o_i + s_i)`. It emits three distinct raw
events:

- `WRITE_PAST_DECLARED_OUTPUT` when `H > OutputBufferLength` but `H <= N`;
- `PHYSICAL_OVERFLOW` when any interval exceeds `N`; and
- `INVALID_COMPLETION_LENGTH` when
  `IoStatus.Information > OutputBufferLength`.

The first event is intentionally E0. Microsoft documents that `SystemBuffer`
represents both input and output and is allocated to the larger length; those
facts do not by themselves prove that every write in the consumed-input tail is
an output overrun. Promotion to `UNBOUNDED_WRITE` requires an IOCTL-specific
output schema, a source-known seeded toy, or phase/taint evidence that the write
was intended as output. A benign scratch/input-tail fixture is a mandatory
negative control. `INVALID_COMPLETION_LENGTH` remains an objective completion
contract event because the I/O manager trusts `Information` when copying back.

Events include IOCTL, input/output lengths, every offending interval, physical
bound, high-water mark, completion length, operation phase, and available
write-site trace. Harness bookkeeping failures are a fourth, internal evidence
class. Any operation-specific policy must be explicit, narrow, hash- and
IOCTL-bound, documented, and visible in output—never silently suppressed.

Microsoft's current Driver Verifier configuration exposes I/O Verification;
Enhanced I/O Verification has been subsumed into it since Windows 7 [19]. The
documentation does not guarantee classification of this exact
declared-boundary-within-allocation signal. Whether Driver Verifier reports the
same seeded, output-intent-confirmed violation is therefore a controlled
baseline question, not an assumed advantage of this checker.

## 5. Threat model and isolation

A `.sys` remains hostile native code outside the kernel. It may corrupt its
process, loop, jump unexpectedly, or attack the emulated ABI. It must not run in
the main launcher. A disposable child is the first candidate boundary, but
subprocess, translated execution, or another mechanism remains an explicit
design decision in M7. Whatever boundary is selected must enforce copied and
bounded inputs, process-tree termination, time/memory/output limits,
deterministic cleanup, and structured operation logs. Job objects, restricted
tokens, process mitigations, and AppContainer may reduce exposure without
admin; they do not automatically form a VM-strength boundary. Unsupported
platform limits fail closed. Code still executes under an identity derived from
the current user.

The PE loader, pointer translation, integer arithmetic, object lifetimes, import
registry, and event serialization all process hostile input. `--hardware none`
requires external effects to be rejected or simulated; it does not make native
code harmless.

Two execution regimes keep the cost claim honest. A purpose-built toy, whose
source and build are controlled by the researchers, may run locally in the
disposable child after ordinary review. Any third-party `.sys` runs only in a
disposable VM without personal credentials or unrelated user data, with network
access disabled unless the protocol requires it. Rehosting may remove repeated
guest crash/reboot cycles; it does not remove the VM requirement for hostile
native code.

The initial experiment forbids driver installation, SCM registration, physical
memory, port I/O, DMA, interrupts, and arbitrary `DeviceIoControl` relay. Any
future physical effect must cross a typed, policy-checked capability backend.

## 6. Evaluation design

The empirical question is whether rehosting changes research cost while
producing calibrated evidence.

- **RQ1:** Conditional on the recorded host/guest authorization tuple, which
  actions become affordable, and how do setup, recovery, throughput, privileged
  steps, resets, and uncontained failures compare across local-toy and
  disposable-VM workflows?
- **RQ2:** What sensitivity and false-positive rate does shadow checking achieve
  on preregistered, mutation-generated, and held-out buffered-I/O cases after
  raw events are separated from confirmed violations?
- **RQ2b:** Does Driver Verifier report the same output-intent-confirmed
  declared-boundary violations under an otherwise matched native execution?
- **RQ3:** Which false-positive and false-negative classes follow from the
  shared input/output buffer, minimal ABI, fixed IRQL, and missing
  hardware/concurrency?
- **RQ4:** Which crash, hang, exhaustion, descendant-process, output-flood, and
  forbidden-operation cases can be bounded without admin?

| Dimension | Native/VM workflow | Proposed rehosting |
|---|---|---|
| Privilege token | recorded | recorded |
| Driver installation | kernel execution requires it | forbidden |
| Physical device | target-dependent | absent in toy phase |
| Setup/recovery time | measured | measured |
| Executions per second | measured | measured |
| Write observability | verifier/debugger | interval shadow state |
| Fidelity | Windows baseline | partial and bounded |
| Host-crash exposure | possible | target: process-local failure |

Before implementation, the study records task definitions, corpus and mutation
seeds, repository commits, image hashes, Windows/WDK/WinDbg/Verifier versions,
snapshot state, hardware, and start/stop rules. Wall-clock time begins when an
operator starts target setup and ends at classified evidence or a declared
inconclusive result. Recovery time begins at fault detection and ends when the
next clean trial can start. Raw per-run data records operator and machine time,
privileged steps, resets, executions, failures, and exclusions.

The same machine and VM image are used where possible. Task order is
counterbalanced (`AB`/`BA`) to reduce learning effects. Multiple operators are
preferred; an author-only run is labeled a pilot or anecdotal cost report, not
general evidence. Third-party targets are compared inside disposable VMs in
both workflows; an unsafe local third-party run is never used to improve the
rehosting result.

The positive toy corpus seeds declared-boundary writes with known output intent,
physical overflows, oversized completion, use-after-free, double-free, IRQL
mismatch, unsupported import, forbidden operation, crash, loop, descendant
escape, and output flooding. The conforming negative corpus mirrors request
shapes and includes writes into a consumed input/scratch tail with
`IoStatus.Information <= OutputBufferLength`. At least one corpus commit
predates detector implementation, mutations are generated independently of
detector branches, and a held-out set is disclosed only after the checker is
frozen. HEVD is a prospective GPL-licensed community baseline after all safety gates pass; its
supported IOCTL paths and expected outcomes must be selected in advance, and a
partial result must not be described as broad HEVD support. Outcomes are
machine-readable and classified as expected finding, harness defect,
unsupported, inconclusive, or unexpected.

## 7. Calibration and abandonment

No third-party driver executes merely because the toy runs. The calibration
protocol is tracked in LiteBox issue #15 [23]. The proposed gate requires 100%
detection and correct classification of preregistered seeded cases across
repeated clean runs, zero unexplained findings in the conforming corpus,
successful evaluation of the frozen held-out set, and containment of every crash and hang toy. These
are calibration criteria, not a claim of general sensitivity.

The experiment stops at read-only PE inspection if:

- the toy requires an unbounded or rapidly growing import set;
- crash/hang containment is unreliable without admin;
- the conforming corpus produces unexplained findings;
- results vary across clean repetitions;
- meaningful paths primarily require unmodeled concurrency, PnP, DMA,
  interrupts, or hardware; or
- licensing prevents lawful inspection or reproducible reporting.

Passing this gate permits one selected candidate, not universal validation.
Every new import family or execution model reopens calibration.

## 8. Evidence and coordinated disclosure

An emulator event is not a vulnerability. Evidence levels are:

- **E0:** harness event;
- **E1:** calibrated, repeated emulator finding;
- **E2:** independent authorized reproduction outside the emulator;
- **E3:** vendor-confirmed security defect.

Only E2/E3 may be called a confirmed vulnerability. A raw
`WRITE_PAST_DECLARED_OUTPUT` remains E0 until output intent is independently
established. Third-party E0/E1 evidence remains private. The repository-level
disclosure workflow is tracked in LiteBox issue #11 [24]. Microsoft-driver
findings go to MSRC; third-party findings go
to the vendor's security contact or `security.txt`; multivendor or unresponsive
cases may require MSRC/MSVR or a CERT. LiteBox findings follow its private
repository security process.

A report identifies product, binary version/signer/source/SHA-256, Windows and
token conditions, deterministic reproduction and rate, expected/observed
behavior, concrete impact without inflation, IOCTL and buffer sizes, events and
traces, negative controls, and a minimally weaponized private PoC. Restricted
binaries and private dump data are not published. Disclosure waits for vendor
coordination or an agreed timeline.

## 9. Dual use and artifact release

Rehosting may remove installation, hardware, recovery, and instrumentation
costs. That helps defenders and may also broaden access to defect discovery.
Non-admin execution does not erase the latter effect; it describes another
axis. The appropriate response is to couple affordance with stricter evidence:
fail-closed imports, typed effects, calibrated detectors, explicit unsupported
states, private findings, and coordinated disclosure.

“Super non-admin” would be technically misleading. No new Windows authorization
is granted. The system raises practical affordance within a constrained research
domain.

Release is staged. Documentation and read-only PE inspection may be public.
The toy ABI, checker, and non-weaponized synthetic corpus may be released only
after calibration, with fail-closed defaults and no third-party trigger inputs.
Third-party adapters, corpora, or reproductions require a separate security and
licensing review; material tied to an undisclosed finding remains private until
coordination permits release. Arbitrary host-effect bridges are neither bundled
nor enabled by a hardware profile.

Publication cannot force downstream users to preserve these controls. That
residual dual-use risk must be reassessed at every release gate and documented
alongside which components, targets, and evidence were withheld.

## 10. Related work

ECMO demonstrates peripheral transplantation for embedded-Linux-kernel
rehosting and downstream analysis. Agamotto uses lightweight VM checkpoints to
accelerate kernel-driver fuzzing. Drifuzz and ReUSB address hardware-dependent
driver reachability and replay. These systems motivate dependency control, but
our proposed experiment is narrower: a purpose-built Windows driver, no real
device, and a declared-boundary buffered-I/O sensor.

kAFL established hardware-assisted OS fuzzing and has a documented
Windows-driver workflow; syzkaller now lists Windows as a supported platform.
BSOD directly studies binary-only driver fuzzing across Windows, Linux, and
FreeBSD. USBFuzz performs coverage-guided fuzzing on Linux and carries generated
seeds into Windows dumb fuzzing, demonstrating cross-platform portability rather
than an equivalent Windows coverage-guided workflow. HEVD provides a public
vulnerable-driver training corpus. These are baselines and candidate corpora,
not evidence that the proposed checker is superior.

Windows Driver Verifier is the kernel-realistic baseline for memory and IRQL
checks, not something this artifact replaces. The proposed contribution is a
contract-aware, process-local sensor. Claims that it is earlier or cheaper are
pending RQ1/RQ2b measurements and remain qualified until independent
reproduction.

## 11. Limitations

The model omits most Windows driver behavior and cannot establish absence of
bugs. Fixed IRQL and single-threading suppress classes of failures. Synthetic
objects may diverge from Windows. Compiler, WDK, framework, and ABI differences
may make binaries unsupported. A non-admin process sandbox is not a hypervisor.
Instrumentation can alter behavior and can itself be defective.

The affordance-floor thesis remains conceptual until research costs are
measured. Current unmerged draft experiments establish typed brokering and CPU
access, not calibrated `.sys` execution or the magnitude of cost reduction.
Empirical results must revise this paper rather than be implied retroactively.

## 12. Validation roadmap

- **August–September 2026:** reconcile the RFC with the M1–M7 typed-fixture
  decomposition, freeze the threat model, read-only PE inspector, raw-event
  taxonomy, task protocol, corpus commit, mutation method, and VM baseline.
- **October–November 2026:** resolve the M7 boundary choice, implement the toy
  ABI and process-tree/time/memory/output containment, and stop if containment
  or import bounds fail.
- **December 2026–January 2027:** freeze the checker, execute positive,
  negative, mutation-generated, and held-out toy trials, and publish raw data.
- **February–March 2027:** run the counterbalanced VM/WinDbg/Driver Verifier
  comparison; label a single-operator result as a pilot.
- **After all gates pass:** preregister and evaluate narrowly selected HEVD
  paths in a credential-free disposable VM. No date overrides a failed gate.

## 13. Conclusion

Privilege and practical affordance are non-identical. Driver rehosting may keep
a non-admin host token unchanged while making selected driver logic easier to
execute, observe, and test, even though the matched native baseline may use
different guest privileges. The proposal responds with narrow claims and strong
gates: read-only inspection, fixture-independent modules, toy-first execution,
fail-closed ABI, declared-boundary shadow events, explicit confirmation before
calling an event a violation, bounded execution, abandonment criteria, and no
vulnerability claim without independent reproduction or vendor confirmation.
If calibration fails, read-only inspection is the honest endpoint.

# Citations

[1] [Microsoft LiteBox](https://github.com/microsoft/litebox).

[2] [LiteBox fork draft commit `a74e5e2`](https://github.com/franklinbaldo/litebox/commit/a74e5e2d132a1981c6a5934e722000f07692526c) and [PR #3](https://github.com/franklinbaldo/litebox/pull/3) — unmerged implementation substrate and initial driver-rehosting RFC.

[3] [Microsoft Learn: Buffer Descriptions for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes).

[4] [Microsoft Learn: Using Buffered I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-buffered-i-o).

[5] [Microsoft Learn: POOL_TYPE](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_pool_type).

[6] [Microsoft Learn: Force IRQL Checking](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/force-irql-checking).

[7] [Microsoft Learn: Automatic Checks](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/automatic-checks).

[8] Feng et al., [ECMO: Peripheral Transplantation to Rehost Embedded Linux Kernels](https://arxiv.org/abs/2105.14295), 2021.

[9] Song et al., [Agamotto](https://www.usenix.org/system/files/sec20-song.pdf), USENIX Security 2020.

[10] Shen et al., [Drifuzz](https://www.usenix.org/system/files/sec22-shen-zekun.pdf), USENIX Security 2022.

[11] Jang et al., [ReUSB](https://www.usenix.org/system/files/usenixsecurity23-jang.pdf), USENIX Security 2023.

[12] [Microsoft Coordinated Vulnerability Disclosure](https://www.microsoft.com/en-us/msrc/cvd) and [MSRC Researcher Portal](https://msrc.microsoft.com/report/vulnerability/new).

[13] Schumilo et al., [kAFL: Hardware-Assisted Feedback Fuzzing for OS Kernels](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/schumilo), USENIX Security 2017.

[14] Intel Labs, [Fuzzing a Windows Kernel Driver with kAFL](https://intellabs.github.io/kAFL/tutorials/windows/driver/index.html).

[15] Google, [syzkaller: Supported OSes](https://github.com/google/syzkaller/blob/master/README.md).

[16] Maier and Toepfer, [BSOD: Binary-only Scalable fuzzing Of device Drivers](https://dmnk.co/raid21-bsod.pdf), RAID 2021.

[17] Peng and Payer, [USBFuzz: A Framework for Fuzzing USB Drivers by Device Emulation](https://www.usenix.org/system/files/sec20-peng_0.pdf), USENIX Security 2020.

[18] HackSys Team, [HackSys Extreme Vulnerable Driver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver), GPL-3.0.

[19] Microsoft Learn, [Driver Verifier options and I/O Verification](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/driver-verifier-options).

[20] Microsoft Learn, [Failure to Check the Size of Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/failure-to-check-the-size-of-buffers).

[21] LiteBox, [Driver-rehosting module decomposition issue #16](https://github.com/franklinbaldo/litebox/issues/16) and child issues #17–#23.

[22] LiteBox, [M1–M7 implementation scaffold PR #24](https://github.com/franklinbaldo/litebox/pull/24).

[23] LiteBox, [calibration gate issue #15](https://github.com/franklinbaldo/litebox/issues/15).

[24] LiteBox, [coordinated-disclosure process issue #11](https://github.com/franklinbaldo/litebox/issues/11).
