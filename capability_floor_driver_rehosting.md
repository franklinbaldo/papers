---
type: "Technical Paper"
title: "Privilege Ceilings, Capability Floors: User-Mode Rehosting of Windows Drivers"
description: "A position and methodology paper on lowering the practical cost of driver analysis without elevating the researcher's Windows privilege token."
tags: [driver-rehosting, windows, litebox, security-research, methodology, dual-use]
timestamp: 2026-08-13T00:00:00-04:00
---

# Privilege Ceilings, Capability Floors: User-Mode Rehosting of Windows Drivers

> **Position and methodology paper.** LiteBox capability brokering and two
> read-only Windows backends have been demonstrated. Windows `.sys` loading, a
> synthetic NT ABI, shadow checking, and third-party-driver evaluation remain
> proposals. This paper reports no driver vulnerability.

## Abstract

Privilege is often modeled as a scalar: a process either gains authorization or
it does not. Program rehosting exposes a second axis. A non-administrative
Windows process that rehosts selected driver logic retains the same token, yet
may gain practical access to relocation, synthetic requests, memory tracing, and
process-local fuzzing without installing the driver, possessing its hardware,
or rebooting after every failure. We call the invariant authorization boundary
the **privilege ceiling** and the minimum routinely accessible analytical
repertoire the **capability floor**.

This paper formalizes that distinction and proposes a fail-closed methodology
for rehosting purpose-built Windows driver binaries in user mode. The design
combines a PE loader, minimal NT ABI, synthetic `METHOD_BUFFERED` requests, an
instrumented allocator, explicit IRQL state, and a SystemBuffer Shadow Checker
that detects contractual out-of-bounds writes even when they remain inside the
I/O manager's physical allocation. Calibration, abandonment, isolation, and
coordinated-disclosure gates must pass before any third-party driver is tested.
The claim is not that rehosting reproduces Windows kernel execution. It is that
a calibrated artifact may lower the cost of producing useful, qualified
evidence while leaving the Windows privilege ceiling unchanged.

## 1. Privilege and capability are different axes

Represent an actor's effective position as

\[
S=(P,C),
\]

where \(P\) is the highest host authority available and \(C\) is the set of
actions practically achievable with available tooling, knowledge, time, and
infrastructure. A rehosting workflow may preserve \(P\) while expanding \(C\):

\[
P'=P, \qquad C'=C\cup\{\text{relocation, synthetic dispatch, write tracing,
process-local fuzzing}\}.
\]

Therefore \(P'=P\) does not imply \(C'=C\). “No privilege is gained” is correct
about authorization and incomplete about practical power. The converse
overstatement is also wrong: a rehosted `.sys` has no ring-0 execution, DMA,
interrupts, physical memory, or arbitrary device handles merely because its
code can be invoked.

The distinction has a dual-use consequence. Removing installation, hardware,
recovery, and instrumentation costs can broaden defensive participation. It can
also lower the cost of finding defects whose exploitation might later attack
the unchanged privilege ceiling. Accessibility must therefore grow together
with evidentiary discipline and containment.

## 2. Demonstrated substrate versus proposed artifact

The substrate is a LiteBox fork that runs rewritten Linux ELF programs in a
Windows user-mode process. It adds a capability registry, profiles (`none`,
`safe`, `host`), explicit selection, and fail-closed rejection of unavailable
capabilities. CPU, SIMD, memory, clocks, and threads are inherent; brokered
resources require policy.

Two read-only brokers have been demonstrated: `hostinfo` returns architecture
and logical-processor data, and `power` queries AC/battery state through the
Windows power stack. An ELF toy also executed `CPUID`, `RDTSC`, and `RDRAND`
with brokered hardware set to `none`. These results demonstrate policy-controlled
brokering and direct CPU instructions. They do not demonstrate `.sys` rehosting,
device passthrough, hostile-code isolation, or vulnerability discovery.

The proposed artifact is separate:

```text
driver.sys
  -> read-only PE inspection and relocation
  -> minimal allowlisted NT ABI
  -> synthetic DRIVER_OBJECT / DEVICE_OBJECT / IRP
  -> instrumented memory and contractual shadow state
  -> captured output and trapped operations
```

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

\[
N=\max(\text{InputBufferLength},\text{OutputBufferLength}),
\]

copies bounded input into `SystemBuffer`, invokes dispatch, and models bounded
copy-back. Physical bounds and caller contract are different. With input length
64 and output length 8, a 32-byte write may remain inside the allocation while
violating the output contract. A guard page alone misses it.

The checker records every write interval

\[
W_i=[o_i,o_i+s_i)
\]

and its high-water mark \(H=\max_i(o_i+s_i)\). At dispatch return or synthetic
completion, `H > OutputBufferLength` emits `UNBOUNDED_WRITE`, independently of
page faults. `IoStatus.Information > OutputBufferLength` emits a distinct
invalid-completion event. Events include IOCTL, input/output lengths, offending
interval, high-water mark, completion length, and available write-site trace.

Contractual overflow inside \(N\), physical overflow beyond \(N\), and harness
bookkeeping error are separate evidence classes. Any compatibility exception
must be explicit, narrow, hash- and operation-bound, documented, and visible in
output—never silently suppressed.

## 5. Threat model and isolation

A `.sys` remains hostile native code outside the kernel. It may corrupt its
process, loop, jump unexpectedly, or attack the emulated ABI. It must not run in
the main launcher. The proposed boundary is a disposable child with copied and
bounded inputs, time/memory/output limits, deterministic cleanup, and structured
operation logs. Job objects, restricted tokens, process mitigations, and
AppContainer may reduce exposure without admin; they do not automatically form
a VM-strength boundary. Code still executes under an identity derived from the
current user.

The PE loader, pointer translation, integer arithmetic, object lifetimes, import
registry, and event serialization all process hostile input. `--hardware none`
requires external effects to be rejected or simulated; it does not make native
code harmless.

The initial experiment forbids driver installation, SCM registration, physical
memory, port I/O, DMA, interrupts, and arbitrary `DeviceIoControl` relay. Any
future physical effect must cross a typed, policy-checked capability backend.

## 6. Evaluation design

The empirical question is whether rehosting changes research cost while
producing calibrated evidence.

- **RQ1:** Which actions become practical under an unchanged Windows token?
- **RQ2:** How do setup, recovery, throughput, and infrastructure compare with a
  Windows VM/kernel-debugging workflow?
- **RQ3:** Does shadow checking detect every seeded buffered-I/O violation,
  including writes contained within the physical allocation?
- **RQ4:** Which false-positive and false-negative classes follow from the
  minimal ABI, fixed IRQL, and missing hardware/concurrency?
- **RQ5:** Which crash, hang, exhaustion, and forbidden-operation cases can be
  bounded without admin?

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

The positive toy corpus seeds boundary writes, contractual and physical
overflows, oversized completion, use-after-free, double-free, IRQL mismatch,
unsupported import, forbidden operation, crash, and loop. A conforming negative
corpus mirrors request shapes. Outcomes are machine-readable and classified as
expected finding, harness defect, unsupported, inconclusive, or unexpected.

## 7. Calibration and abandonment

No third-party driver executes merely because the toy runs. The proposed gate
requires 100% detection of seeded cases across repeated clean runs, zero
unexplained findings in the conforming corpus, and containment of every crash
and hang toy. These are preregistered targets, not retrospective claims.

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

Only E2/E3 may be called a confirmed vulnerability. Third-party E0/E1 evidence
remains private. Microsoft-driver findings go to MSRC; third-party findings go
to the vendor's security contact or `security.txt`; multivendor or unresponsive
cases may require MSRC/MSVR or a CERT. LiteBox findings follow its private
repository security process.

A report identifies product, binary version/signer/source/SHA-256, Windows and
token conditions, deterministic reproduction and rate, expected/observed
behavior, concrete impact without inflation, IOCTL and buffer sizes, events and
traces, negative controls, and a minimally weaponized private PoC. Restricted
binaries and private dump data are not published. Disclosure waits for vendor
coordination or an agreed timeline.

## 9. Dual use

Rehosting may remove installation, hardware, recovery, and instrumentation
costs. That helps defenders and may also broaden access to defect discovery.
Non-admin execution does not erase the latter effect; it describes another
axis. The appropriate response is to couple capability with stricter evidence:
fail-closed imports, typed effects, calibrated detectors, explicit unsupported
states, private findings, and coordinated disclosure.

“Super non-admin” would be technically misleading. No new Windows authorization
is granted. The system raises practical capacity within a constrained research
domain.

## 10. Related work

ECMO demonstrates peripheral transplantation for embedded-Linux-kernel
rehosting and downstream analysis. Agamotto uses lightweight VM checkpoints to
accelerate kernel-driver fuzzing. Drifuzz and ReUSB address hardware-dependent
driver reachability and replay. These systems motivate dependency control, but
our proposed experiment is narrower: a purpose-built Windows driver, no real
device, and a contract-level buffered-I/O sensor.

Windows Driver Verifier is the kernel-realistic baseline for memory and IRQL
checks, not something this artifact replaces. The proposed contribution is
earlier, cheaper, process-local instrumentation whose findings remain qualified
until reproduced independently.

## 11. Limitations

The model omits most Windows driver behavior and cannot establish absence of
bugs. Fixed IRQL and single-threading suppress classes of failures. Synthetic
objects may diverge from Windows. Compiler, WDK, framework, and ABI differences
may make binaries unsupported. A non-admin process sandbox is not a hypervisor.
Instrumentation can alter behavior and can itself be defective.

The capability-floor thesis remains conceptual until research costs are
measured. Current toys establish typed brokering and CPU access, not `.sys`
execution or the magnitude of cost reduction. Empirical results must revise
this paper rather than be implied retroactively.

## 12. Conclusion

Privilege and practical capability are non-identical. Driver rehosting may keep
a non-admin token unchanged while making driver logic easier to execute,
observe, and test. The proposal responds with narrow claims and strong gates:
read-only inspection, toy-first execution, fail-closed ABI, contractual shadow
checking, explicit IRQL, bounded execution, abandonment criteria, and no
vulnerability claim without independent reproduction or vendor confirmation.
If calibration fails, read-only inspection is the honest endpoint.

# Citations

[1] [Microsoft LiteBox](https://github.com/microsoft/litebox).

[2] [LiteBox fork PR #3](https://github.com/franklinbaldo/litebox/pull/3) — implementation substrate and driver-rehosting RFC.

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
