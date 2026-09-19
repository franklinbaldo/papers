---
type: "Findings Record"
title: "MaleCNS Car Interface Run 23: budgeted peer Wi-Fi witness before LiDAR escalation"
description: "A cheap peer-observed speed token can resolve some common-mode OBD/GNSS conflicts before paying for LiDAR, but naive escalation burns future information budget; an exploratory conflict-score guard improves that trade-off in some regimes and exposes peer-trust as a first-class active-information problem."
tags: [malecns, driving, obd-ii, gnss, android, camera, lidar, wifi, rf, multi-agent, active-sensing, value-of-information, sensor-fusion, robustness, experiment]
timestamp: 2026-09-19T15:54:00-04:00
---

# Run 23 — buy a cheap peer token before paying for LiDAR

Run 22 established a useful failure mode for active sensing: OBD-II and GNSS can agree while being wrong together, camera ego-motion can expose the contradiction, and a fourth independent LiDAR witness can break the tie. But the Run-22 policy treated every LiDAR request as free. That is not a fair baseline for a future MaleCNS coordinator whose proposed job is to decide **when another bit of reality is worth buying**.

This run adds an explicit per-episode information budget and a cheaper multi-agent channel ahead of LiDAR. When persistent OBD/GNSS-vs-camera conflict exists, the car may first request a Wi-Fi/RF token from a nearby cooperating agent. The token contains only:

- that peer's physically observed estimate of the host car's longitudinal speed;
- the peer's declared confidence;
- token age/latency.

One realizable implementation is a nearby phone/camera agent tracking the host vehicle's relative longitudinal motion and combining it with its own GNSS/ego-motion before broadcasting the scalar estimate. The experiment does **not** assume that such a peer is always present or trustworthy; dropout, bias, confidence and age are explicit variables.

The peer token costs 1 abstract acquisition unit and LiDAR costs 5. Each active arm receives the same 150-unit cap per episode. These costs are an experimental accounting convention, **not measured market, energy, bandwidth or latency prices**; the cost ratio requires later hardware calibration and sensitivity analysis.

## Reality boundary

The deployable policy receives only signals reproducible from an ordinary car, phone and declared external/peer sensors:

- matched-time OBD-II speed;
- phone GNSS speed;
- Android camera ego-speed;
- optional peer-observed host-speed token, confidence and age delivered over local Wi-Fi/RF;
- optional low-cost external LiDAR ego-speed.

Synthetic truth, injected fault mode, common-bias state, the identity of the bad sensor, simulator pose/map and future samples exist only in the generator/scoring code. The acquisition policy never receives them.

A peer token is **not** a truth oracle. A confidently biased peer is deliberately included as an adversarial regime. Low-confidence biased peers are also tested to determine whether ordinary confidence/age gating can safely refuse a cheap but dubious corroborator.

## Policies and staged ablations

All active policies use the same Run-22 persistent primary-conflict detector. The experiment compares:

1. `pair-only`: OBD/GNSS mean, no acquisition;
2. `naive-three`: OBD/GNSS/camera mean, no acquisition;
3. `budgeted-lidar-only`: buy LiDAR on detected conflict until the common budget is exhausted;
4. `budgeted-rf-only`: buy a peer token on conflict, use it only when confidence/age and support margin are decisive, never escalate;
5. `budgeted-rf-first`: buy the peer token first; if it is unavailable/ambiguous and conflict is sufficiently strong, escalate to LiDAR.

The peer resolver discounts declared confidence exponentially with token age. A peer is decisive only when effective confidence is at least 0.55 and its distance to the pair vs camera differs by at least 0.20 m/s. A peer that supports the camera is blended with the camera; a peer that supports the OBD/GNSS pair leaves the pair unchanged.

### Important adaptive step inside this round

The first exploratory implementation escalated to LiDAR after every unavailable/ambiguous peer token. The 150-unit pilot exposed **budget cannibalization**: in the shared-static / clean-camera / clean-peer / clean-LiDAR regime it achieved MAE 1.152664, worse than RF-only 0.927902, because expensive escalations reduced later cheap-token availability.

After observing that pilot, the policy was changed to require `conflict_score >= 1.50` before LiDAR escalation. This threshold was therefore chosen **adaptively after seeing pilot behavior**. The guarded results below are exploratory engineering evidence, not an independently preregistered confirmatory test. A future confirmatory run must freeze the escalation rule on separate calibration seeds/data.

The guard improved the same static regime from 1.152664 to 1.056728, but did not uniformly improve every regime: shared-drift moved from 0.626210 to 0.648006 while shared-jump improved from 0.463947 to 0.447864. This is exactly the trade-off expected from spending fewer expensive observations.

## Executed validation

Final guarded run:

- 3 seeds;
- 20 episodes per seed per condition;
- 250 matched-time steps per episode at 10 Hz;
- 48 conditions = 4 OBD/GNSS pair regimes × 2 camera regimes × 3 peer regimes × 2 LiDAR regimes;
- 2,880 episodes / 720,000 control-time steps;
- budget cap 150 units per episode;
- peer cost 1 unit, LiDAR cost 5 units;
- peer token dropout 10%;
- peer age 40–280 ms;
- peer speed noise SD 0.50 m/s;
- clean peer declared confidence centered at 0.92;
- biased high-confidence peer uses the same confidence distribution but a persistent 1.2–2.0 m/s bias;
- low-confidence biased peer centers declared confidence at 0.38.

A second completed sensitivity run used the same 48-condition grid with a 75-unit budget cap. An attempted 300-unit ancillary run was interrupted by the execution timeout before producing a result file and is not used below.

`python -m unittest -v test_budgeted_peer_witness.py` -> **6/6 passed**.

`python -m py_compile budgeted_peer_witness.py peer_rf_budget_ablation.py test_budgeted_peer_witness.py` -> **passed**.

No CARLA asset, dataset, model, weight or package was downloaded. This run uses only the existing standard-library synthetic harness; there was **no heavyweight cache miss**.

## Primary result — clean camera, clean peer, clean LiDAR

| pair regime | pair MAE | naive 3-way | budgeted LiDAR | RF-only | RF-first guarded | RF-first spend / 150 |
|---|---:|---:|---:|---:|---:|---:|
| clean | 0.192890 | 0.193888 | 0.192890 | 0.192890 | **0.192890** | 0.0 |
| shared static | 1.589447 | 1.056814 | 1.439020 | **0.927902** | 1.056728 | 144.7 |
| shared drift | 0.903626 | **0.617080** | 0.798947 | 0.660188 | 0.648006 | 72.0 |
| shared jump | 1.004484 | 0.701228 | 0.821938 | 0.463883 | **0.447864** | 134.7 |

Under a hard budget, the cheap token is often substantially more useful than spending the budget directly on LiDAR. In shared-static failure RF-only reduces pair error by about **41.6%** and beats budgeted LiDAR by about **35.5%**. In shared-jump failure the guarded RF-first policy reduces pair error by about **55.4%** and beats budgeted LiDAR by about **45.5%**.

The static regime is also the clearest warning: **RF-first is not automatically better than RF-only**. Even after adding the conflict-score guard, it spends 33.9 units on LiDAR and loses to RF-only because those expensive escalations displace future cheap peer observations. Active sensing is therefore a sequential resource-allocation problem, not just a hierarchy of "better" sensors.

In shared drift, guarded RF-first spends only 72.0/150 units and slightly beats RF-only (`0.648006` vs `0.660188`). In shared jump it spends 134.7 units and slightly beats RF-only (`0.447864` vs `0.463883`). The marginal value of escalation depends on fault dynamics and remaining information opportunities.

## Lower-budget sensitivity

With the budget reduced from 150 to 75 units, the same clean-witness common-mode regimes produced:

| pair regime | LiDAR-only MAE | RF-only MAE | RF-first guarded MAE |
|---|---:|---:|---:|
| shared static | 1.5145 | **1.2475** | 1.3102 |
| shared drift | 0.8577 | **0.6734** | 0.6905 |
| shared jump | 0.9129 | **0.5893** | 0.6945 |

The cheap channel becomes more valuable as the budget tightens. At 75 units, guarded escalation loses to RF-only in all three common-mode regimes. This supports a concrete controller input: **remaining acquisition budget must be part of the state**, and escalation should estimate opportunity cost rather than only current conflict severity.

## Peer and sensor corruption falsifiers

The token cannot be treated as trusted merely because it arrived over the declared channel.

With shared-static OBD/GNSS bias, clean camera and clean LiDAR:

- clean high-confidence peer: RF-only `0.927902`, guarded RF-first `1.056728`;
- **biased high-confidence peer**: RF-only `1.405715`, guarded RF-first `1.418036`;
- **biased low-confidence peer**: RF-only falls back to pair-only (`1.605905`) because no token is decisive; guarded RF-first reaches `1.508813` by spending 87 LiDAR units after rejecting the peer.

Thus confidence gating is useful against honestly low-confidence peers, but a confidently wrong peer remains dangerous. Reputation/identity history or independent corroboration is required before a peer token can become more than another fallible sensor.

A biased LiDAR also cannot be a final oracle. In shared-static / clean-camera / clean-peer conditions, RF-first is `1.087193` with biased LiDAR versus `1.056728` with clean LiDAR; RF-only is nearly unchanged (`0.931874`) because it never exposes itself to that extra failure mode.

Camera identity remains a deeper ambiguity. When the OBD/GNSS pair is actually clean but the camera has persistent bias, conflict detection triggers heavily and the guarded RF-first arm worsens MAE from pair-only `0.193081` to `0.212961` while spending ~142.2/150 units. A peer token can reduce uncertainty, but the current policy still sometimes buys evidence for a conflict whose majority side was already correct.

## What this changes for MaleCNS

Run 22 asked whether a controller can decide when to buy another physical observation. Run 23 makes that question harder and more useful:

> **Which observation should be bought now, given its cost, latency, reliability, the current conflict geometry, and the opportunity cost of not saving that budget for later?**

A conventional baseline now exists for this decision. MaleCNS should not receive credit merely for requesting LiDAR on conflict. It should have to beat at least:

- the fixed conflict-triggered LiDAR policy;
- cheap-peer-only acquisition;
- the guarded RF-first heuristic;
- eventually a conventional learned/bandit value-of-information policy,

under equal observation budgets and the same reality-bounded input channels.

Candidate controller channels exposed by this run are all physically/digitally realizable:

| candidate signal | cost / availability | expected rate / latency | simulator/mock emulation | privacy / safety constraints | marginal-value ablation |
|---|---|---|---|---|---|
| `peer_speed_token` | near-zero radio bytes after peer discovery; only when a cooperating observer is present | event-driven, target 2–10 Hz; tens to hundreds of ms | peer camera/GNSS measurement + packet dropout/age/bias | broadcasts can expose location/trajectory; require consent, authentication and bounded retention | remove peer channel at same total budget |
| `peer_effective_confidence` | computed locally | per token, negligible compute | declared confidence × age decay | must not be equated with trust; sender may be confidently wrong | shuffled/miscalibrated confidence control |
| `peer_support_margin` | computed locally from observed speeds | per token | exact deterministic calculation | no added collection beyond existing values | remove margin gate while holding token stream fixed |
| `budget_remaining` | free local bookkeeping | every control step | exact | none beyond preventing unsafe resource exhaustion | hidden-budget vs explicit-budget controller |
| `acquisition_cost` | configured estimate, later hardware-calibrated | per action | fixed or measured distributions | cost must include distraction/compute/network/energy and sensor duty-cycle constraints | 1:3 / 1:5 / 1:10 cost-ratio sensitivity |
| `witness_disagreement_history` | small RAM window | control rate | deterministic state | peer identity should be pseudonymous/minimized | memoryless vs history-aware acquisition |

## Limits and next falsifiers

This remains synthetic. No real peer camera tracker, Wi-Fi Direct/Aware link, phone CSI, vehicle-to-vehicle protocol, LiDAR driver or hardware cost measurement was executed. The peer's observation model is intentionally simple and should not be interpreted as demonstrated real-car V2V accuracy.

The most important next steps are:

1. freeze a calibration/test split for the escalation rule so `conflict_score >= 1.50` is no longer adaptively chosen on the same generator family;
2. compare guarded heuristics to a conventional contextual bandit/learned value-of-information policy under the **same** budget;
3. add peer reputation learned only from delayed observable corroboration, with Sybil/correlated-bias controls;
4. replace at least camera ego-speed or the peer witness with a real, checksum-pinned artifact;
5. measure actual Android/Wi-Fi and low-cost LiDAR latency/energy so abstract acquisition units can be mapped to hardware costs;
6. only then insert MaleCNS as the acquisition controller and require improvement over those conventional controls.

## Daily research requirement

The repository already contains today's dedicated `RESEARCH_2026-09-19.md` prior-art and autonomous-driving benchmark/safety survey, including the distinction between explicit MaleCNS/connectome-derived control and generic insect-inspired robotics, plus training/offline/closed-loop/safety/external-comparison classification. This run therefore concentrated on the active-information experiment rather than duplicating the same-day survey.
