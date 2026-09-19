---
type: "Companion Note"
title: "Driving datasets, safety benchmarks, and near-free sensor channels"
description: "First survey of datasets, closed-loop benchmarks, public Tesla/Waymo safety evidence, and inexpensive real-time scalar/vector channels that can extend the MaleCNS car-interface experiments."
tags: [malecns, autonomous-driving, datasets, benchmarks, safety, sensors, sim-to-real]
timestamp: 2026-09-18T17:05:00-04:00
---

# Driving datasets, safety benchmarks, and near-free sensor channels

This note separates four distinct evaluation needs:

1. **training / representation learning** from recorded driving;
2. **offline perception / forecasting** benchmarks;
3. **closed-loop planning and control** benchmarks;
4. **real-world safety outcome comparison**.

These must not be conflated. A perception dataset cannot by itself establish safe driving, and a company safety dashboard is not a training dataset.

## 1. Best immediate fit: comma2k19

Source: https://github.com/commaai/comma2k19

comma2k19 is unusually close to the intended physical MaleCNS retrofit stack:

- road-facing camera;
- phone-like GPS;
- 9-axis IMU;
- raw GNSS;
- CAN data;
- car speed;
- steering angle;
- wheel speeds;
- radar-derived distance fields;
- global pose estimates for evaluation.

It contains about 33 hours of driving on California I-280, split into 1-minute segments.

### Why it matters

This is the most natural first real-world dataset for validating the interface adapters before expensive closed-loop simulation.

Recommended uses:

- train/test sensor normalization and timing;
- derive phone + OBD observations from real recordings;
- test prediction of speed, steering, ego-motion and road-state proxies;
- pretrain thin adapters without modifying MaleCNS;
- construct masked-input ablations;
- validate sensor noise/dropout models before CARLA.

Ground-truth fields such as global pose or radar distance may be used for labels/evaluation but must not cross the runtime reality boundary unless an equivalent physical sensor is explicitly declared.

Cache recommendation: download only selected 1-minute segments first; use immutable chunk-level caches keyed by source URL + checksum.

## 2. Closed-loop benchmark: CARLA Leaderboard 2.1

Sources:
- https://leaderboard.carla.org/
- https://leaderboard.carla.org/evaluation_v2_1/

CARLA Leaderboard evaluates complete driving behavior, including:

- route completion;
- collision rates with vehicles, pedestrians and layout;
- red-light and stop-sign infractions;
- off-road infractions;
- route deviations;
- timeouts;
- blocked-agent events;
- minimum-speed and emergency-yield infractions.

The benchmark explicitly prohibits privileged simulator information in the sensor track, which aligns closely with this project's reality-boundary rule.

### Proposed use

Adopt a subset of CARLA Leaderboard metrics unchanged as the canonical closed-loop scorecard for MaleCNS.

Run two tracks:

- **retrofit-realistic**: only sensors reproducible by phone + OBD + declared cheap modules;
- **extended-cheap-sensors**: retrofit-realistic plus declared ultrasound / LiDAR / RF / YOLO channels.

Never feed CARLA ground truth directly to MaleCNS.

## 3. Planning benchmark: nuPlan

Source: https://www.nuscenes.org/nuplan

nuPlan provides around 1,200 hours of driving and explicitly supports open-loop and closed-loop planning evaluation. Its scenarios include lane changes, unprotected turns, pedestrian interaction and other mined events, with planning metrics for traffic-rule compliance, human-driving similarity, dynamics and goal achievement.

### Proposed use

Use nuPlan primarily as:

- a planning/control benchmark;
- a source of mined difficult scenarios;
- an external metric vocabulary for comfort, goal completion and rule compliance.

This complements CARLA: CARLA gives flexible simulation; nuPlan gives a planning-centric benchmark with real-log-derived scenario structure.

## 4. Waymo Open Dataset

Sources:
- https://waymo.com/open/
- https://waymo.com/open/challenges/
- https://waymo.com/open/faq/

Waymo Open Dataset is strong for:

- camera/LiDAR perception;
- motion forecasting;
- end-to-end vision-based driving research;
- scenario generation and simulated-agent evaluation.

Important boundary: Waymo states that its open dataset is an unlabeled mixture of manual and autonomous driving and is **not suitable for evaluating the real-world performance of Waymo vehicles**.

### Proposed use

Use WOD for perception and forecasting comparisons, not for claims about Waymo safety.

Good candidate tasks:

- camera-only object/perception evaluation;
- interaction prediction;
- vision-based end-to-end representation tests;
- scenario generation.

The dataset is free for research under a non-commercial Waymo license, not an open-source license.

## 5. Argoverse 2

Source: https://www.argoverse.org/av2.html

Argoverse 2 provides:

- Sensor Dataset: 1,000 annotated 3D scenarios;
- Motion Forecasting Dataset: 250,000 scenarios;
- large LiDAR collections;
- HD maps and map-change scenarios.

The Motion Forecasting Dataset is around 58 GB; the sensor set is approximately 1 TB.

### Proposed use

Do not download the full sensor corpus initially.

Use:

- motion scenarios for forecasting baselines;
- selected sensor subsets for camera/LiDAR ablations;
- map-change examples for robustness to stale navigation information.

Cache by immutable archive part and avoid whole-dataset downloads unless a registered experiment requires them.

## 6. Oxford RobotCar

Source: https://robotcar-dataset.robots.ox.ac.uk/

This dataset repeatedly traverses the same Oxford route across a year, with weather, traffic, construction and seasonal variation.

Sensors include:

- multiple cameras;
- 2D and 3D LiDAR;
- GPS/INS;
- reference visual odometry.

### Proposed use

Excellent for testing whether the system overfits environmental appearance.

Possible scalar channels / tasks:

- localization confidence;
- visual-change score;
- GNSS uncertainty;
- disagreement between visual odometry and GNSS;
- weather/domain-shift robustness.

## 7. Audi A2D2

Source: http://www.a2d2.audi/

A2D2 combines camera, LiDAR and vehicle-bus data. Vehicle-state information includes speed/acceleration, steering, throttle and braking.

### Proposed use

Useful second real-world validation dataset after comma2k19 because it combines exteroception and vehicle-state channels.

## 8. KITTI and BDD100K

KITTI remains a canonical perception benchmark for detection, stereo, optical flow, odometry and related tasks.

BDD100K is useful for diverse road-scene perception and semantic tasks.

These are valuable for component benchmarking but much weaker than CARLA/nuPlan for closed-loop driving quality.

## 9. Public safety evidence: Waymo

Source: https://waymo.com/safety/impact/

Through March 2026, Waymo reports 220.6 million rider-only miles. Its public safety hub exposes reproducible CSVs and compares rider-only crash outcomes against human benchmarks matched to operating geography.

Reported all-location rates include:

- serious-injury-or-worse crashes: 0.01 incidents per million miles for Waymo vs 0.23 benchmark;
- any-injury-reported crashes: 0.71 vs 3.91 incidents per million miles.

Waymo also publishes raw CSVs underlying the dashboard, including miles, SGO crash identifiers/outcome groupings and benchmark comparisons.

### Proposed use

Do not use these numbers as a training target.

Instead use their **metric structure** as an external long-horizon safety scorecard:

- collisions per million simulated/real miles;
- injury-severity proxy categories;
- vulnerable-road-user categories;
- geographically stratified comparisons;
- confidence intervals / exposure-normalized event rates.

For our simulation scale, use events per 1,000 or 10,000 km initially and report uncertainty explicitly.

## 10. Public safety evidence: Tesla

Sources:
- https://www.tesla.com/VehicleSafetyReport
- https://www.tesla.com/fsd-evidence-dashboard

Tesla currently publishes FSD (Supervised) mileage and collision-rate comparisons, stratified by control type and road class. The dashboard distinguishes major collisions (airbag / irreversible restraint deployment) and minor collisions using telemetry thresholds.

Tesla also publishes a Safety Score based on measurable driving factors such as hard braking, aggressive turning, unsafe following time and forced disengagement.

### Proposed use

Tesla's company-reported safety dashboard is useful as a source of metric ideas, but it is not directly comparable to an unsupervised system and should not be treated as an independent benchmark of our agent.

Particularly useful scalar targets for our experiment:

- hard-braking rate;
- aggressive-turning rate;
- unsafe-following-time fraction;
- forced-intervention / disengagement rate;
- major/minor collision rates;
- highway vs non-highway stratification.

These can be computed continuously in CARLA and later from real car telemetry.

## 11. Independent incident dataset: NHTSA SGO

Source: https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting

NHTSA publishes downloadable CSV incident reports for ADS and Level-2 ADAS crashes.

Current data includes reporting entity, make/model/year, incident identifiers, road/surface conditions, crash object and narratives.

The dataset has important limitations including duplicate reports, data corrections and differing reporting coverage.

### Proposed use

Use as:

- a taxonomy of real failure modes;
- a source for scenario generation;
- a source of safety-event categories;
- an external check against over-simplified company dashboards.

Do not compare raw manufacturer crash counts without exposure normalization.

# Near-free scalar/vector channels

The design criterion is broad: any signal physically or digitally realizable in a normal retrofit and useful to better driving can become a channel.

## A. Signals already available from the phone at zero extra hardware cost

### GNSS quality

Useful real-time values:

- horizontal accuracy;
- satellite count;
- fix age;
- estimated speed accuracy;
- heading accuracy.

Potential bodily meaning: localization confidence.

### Accelerometer-derived ride quality

Scalars:

- longitudinal jerk;
- lateral jerk;
- vibration RMS;
- vertical shock index.

Useful for comfort, potholes, road roughness and excessive maneuver detection.

### Gyroscope-derived turn dynamics

Scalars:

- yaw rate;
- yaw acceleration;
- yaw disagreement with steering command.

Useful for detecting oversteer/understeer-like mismatch or loss of expected motion.

### Magnetometer quality / heading disagreement

Scalar:

- difference between magnetic heading, GNSS course and integrated gyro heading.

Can act as a cheap confidence signal rather than a raw orientation source.

### Ambient light

Scalar:

- lux / image exposure proxy.

Useful to adapt camera processing and anticipate low-visibility regimes.

### Barometer

Scalars:

- pressure;
- pressure change;
- inferred grade trend only when carefully fused.

Potentially useful for slope/context but probably low marginal value; should be tested, not assumed.

### Microphone / acoustics

Derived scalars:

- horn probability;
- siren probability;
- tire/road-noise energy;
- rain-noise probability;
- engine anomaly score.

Avoid speech/content analysis by default; process locally into event scores.

## B. Zero/near-zero vehicle signals

Depending on the car and OBD/CAN availability:

- individual wheel speeds;
- steering angle;
- steering-rate;
- brake state;
- throttle;
- engine RPM/load;
- turn-signal state;
- gear;
- ABS/traction-control activation;
- yaw-rate or stability-control information where exposed;
- battery/charging state for EVs;
- wiper state.

Particularly valuable derived scalar: **wheel-slip disagreement**, e.g. normalized variance among wheel speeds.

## C. Camera-derived cheap semantic scalars

YOLO or another compact on-device detector can produce:

- pedestrian count;
- cyclist count;
- vehicle count;
- nearest-box image scale;
- object-confidence entropy;
- traffic-light state confidence;
- stop-sign confidence.

Additional tiny models can provide:

- drivable-area fraction;
- lane-line confidence;
- optical-flow magnitude;
- time-to-contact approximation from image expansion;
- rain/fog/night classifier;
- road-surface classifier.

These are all lawful because they derive only from the real camera.

## D. Ultrasound / ToF / low-cost LiDAR

Candidate scalars:

- nearest range;
- range derivative;
- echo energy;
- echo entropy;
- left-right range asymmetry;
- active-ping confidence.

Active sensing can be given an explicit cost so the agent learns when sensing is worth paying for.

## E. RF and connectivity

Wi-Fi/Bluetooth/cellular signals:

- RSSI statistics;
- number of visible access points;
- scan-set similarity to previous locations;
- channel occupancy;
- cellular signal quality;
- neighboring-agent count;
- packet loss;
- latency;
- peer confidence/reputation.

These can support context, approximate localization and multi-agent coordination.

No payload interception is needed.

## F. Free semantic services / map-derived signals

Where licensing permits and data can be cached:

- road speed limit;
- road class;
- curvature ahead;
- intersection distance;
- turn direction;
- grade;
- school-zone / pedestrian-zone flag;
- known traffic-control geometry.

These should be derived from publicly available or locally cached map/navigation sources and treated as external semantic inputs analogous to navigation instructions, not as simulator ground truth.

A key ablation is **map semantics on/off** because these signals may dominate some tasks.

## G. Weather/environment context

Free or low-cost sources can provide:

- precipitation probability/intensity;
- visibility;
- temperature;
- wind;
- sunrise/sunset / solar elevation.

For true sim-to-real fidelity, prefer locally sensed or cached forecast values with realistic update rates rather than perfect simulator weather labels.

## H. Cross-sensor disagreement channels

These may be especially valuable for MaleCNS because each is a compact scalar with direct behavioral meaning:

- camera ego-motion vs IMU motion;
- GNSS heading vs gyro heading;
- wheel speed vs GNSS speed;
- steering angle vs yaw response;
- map curvature vs observed visual curvature;
- YOLO object motion vs optical flow;
- expected brake deceleration vs measured deceleration.

Disagreement channels may encode uncertainty more usefully than feeding every raw sensor separately.

# Proposed experiment priority

## Phase 1 — cheap real-data adapter benchmark

Use a cached subset of comma2k19.

Tasks:

1. reproduce phone + CAN observations;
2. predict next-step speed/yaw/steering from the declared interface;
3. ablate camera, IMU, GPS and CAN;
4. compare raw versus derived disagreement scalars.

## Phase 2 — CARLA closed-loop canonical scorecard

Adopt CARLA Leaderboard-style:

- route completion;
- collisions/km;
- traffic-light and stop-sign violations/km;
- off-route time;
- route deviations;
- comfort/jerk;
- intervention rate.

## Phase 3 — scenario diversity

Borrow difficult scenarios from nuPlan and NHTSA crash categories.

## Phase 4 — external safety normalization

Once simulated/real mileage is large enough, report exposure-normalized event rates structurally comparable to Waymo/Tesla safety reporting, without claiming equivalence across operational design domains.

# Cache policy

Every external dataset/model must have:

- source URL;
- version/revision;
- checksum when available;
- local persistent cache path;
- manifest of downloaded shards;
- no automatic redownload when the cached checksum/version matches.

Prefer tiny registered subsets first. Full terabyte-scale downloads require a specific experiment justification.
