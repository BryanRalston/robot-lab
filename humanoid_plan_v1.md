# Humanoid Robot Design Specification (v1, revised: design-only, unconstrained budget)
*Prepared for Bryan Ralston · Oct 12, 2026 · Status: draft*

> Benchmark specs are cited. Everything marked **[EST]** is our engineering estimate or design target, not a published figure. Competitor numbers are vendor claims; Optimus figures are third-party reports only.

---

## 1. State of the art: benchmark (Oct 2026)

| Robot | Height | Mass | Total DoF | Hand DoF | Payload | Speed | Battery / runtime | Price | Sources |
|---|---|---|---|---|---|---|---|---|---|
| **Boston Dynamics Atlas (electric, product)** | 1.9 m | 90 kg | 56 | not published (tactile hands) | 50 kg instant / 30 kg sustained | not published | 4 h, self-swapping battery; IP67 | Enterprise only (not public) | [BD] |
| **Figure 03** | 1.73 m (5'8") | 61 kg | Not published (third parties say ~30) | Not published (third parties say ~20); palm cams, 3 g fingertip sensing | 20 kg | 1.2 m/s | 2.3 kWh, ~5 h; 2 kW wireless charging | Not public | [F03], [F03-batt], [RG] |
| **Tesla Optimus Gen 2 → Gen 3** | ~1.73 m | ~57 kg | 28 body (14 rotary + 14 linear actuators) | 11/hand (Gen 2) → 22/hand (Gen 3, reported) | ~20 kg carry (Gen 2) | ~1.3–1.6 m/s (reported) | ~2.3 kWh (reported) | $20–30k target at scale (unconfirmed) | [OPT], [HA] (no official Tesla spec sheet) |
| **Unitree H1** | ~1.80 m | ~47 kg | 19 actuated (5/leg, 4/arm + torso) | none standard | not specified | 3.3 m/s (claimed record) | 864 Wh | ~$90k (quote) | [UH1], [RZ-H1] |
| **Unitree G1** | 1.32 m | ~35 kg | 23–43 | 7 (optional Dex3-1 three-finger hand) | ~2 kg per arm | up to 2 m/s | 9 Ah, ~2 h | from $13,500 | [UG1], [UG1-doc] |
| **1X NEO** | 1.68 m | ~30 kg | 75 (per vendor tracker) | 22 finger/palm + 3 wrist, tendon-driven | 25 kg carry / 8 kg arm | 1.4 m/s walk, 6.2 m/s max run | 842 Wh, ~4 h | $20,000 or $499/mo | [TQ], [RR] |
| **Agility Digit (current) / Digit 5** | 1.75 m / 1.81 m | ~64 kg / 129 kg | 28 (current, per trackers) | grippers, not dexterous hands | 16 kg / 22.7 kg | not published here | up to 4 h (current); 90 min with 9 min charge (Digit 5) | RaaS / enterprise | [RZ], [IDT] |

**Key reference parts:** NVIDIA Jetson AGX Thor (T5000): 2,070 FP4 TFLOPS (sparse), 128 GB LPDDR5X, 14-core Arm, 40–130 W; dev kit $5,499 (raised from $3,499 in July 2026). T4000: 1,200 TFLOPS, 40–70 W. [NV], [NV-blog], [ANT]

**Takeaways**
1. The **leading benchmark is ~1.7 m, 55–65 kg, ~20 kg payload, 4–5 h runtime, 1.2–1.5 m/s walk**, plus dexterous hands with roughly 20 DoF.
2. The edge comes from **in-house actuators** (Figure, Tesla, BD), **dexterous hands with tactile sensing**, and above all **VLA autonomy and data scale** (Figure Helix, 1X Redwood, Tesla). Hardware is necessary, but autonomy is the differentiator.
3. Unitree shows the cost frontier: a full robot for $13.5k–$90k built around integrated QDD-style PMSM joints.

---

## 2. Target specs: beat every current humanoid on every axis
All targets are **[EST]** design goals. The comparison column shows the current best published figure from §1.

| Spec | Target | Current best (source) |
|---|---|---|
| Height | 1.75 m (fits human workspaces; reach 2.3 m+) | Atlas 1.9 m, reach 2.3 m [BD] |
| Mass | 68 kg | Figure 03 61 kg at 20 kg payload [F03] |
| Total DoF | **75** (body 33 + hands 2×21) | NEO 75 per vendor tracker [RR]; Atlas 56 [BD] |
| Hand DoF | 21 actuated per hand + 3 wrist (counted in body) | NEO 22 + 3 wrist [TQ]; Optimus Gen 3 22 (reported) [OPT] |
| Payload | 60 kg instant / 35 kg sustained (two-arm); 10 kg per arm at full reach | Atlas 50 / 30 kg [BD] |
| Walk / run | 2.0 m/s walk, 5 m/s run | H1 3.3 m/s [UH1]; NEO 6.2 m/s max run [TQ] |
| Runtime | 6 h mixed duty, plus self-swappable battery (unlimited uptime) | Figure 03 5 h [F03-batt]; Atlas 4 h with swap [BD] |
| Battery | 3.0 kWh, 2.5 kW wireless charge plus hot-swap | Figure 03 2.3 kWh, 2 kW [F03-batt] |
| Joint range | Continuous-rotation waist, wrist roll, and neck yaw | Atlas "continuous" [BD] |
| Ingress / temp | IP67, −20 to 45 °C | Atlas IP67, −20 to 40 °C [BD] |
| Fingertip sensing | < 1 g force threshold, plus palm cameras | Figure 03 ~3 g [F03] |
| Compute | 2× Jetson Thor T5000 (4,140 FP4 TFLOPS sparse, 260 W max) + RT controller | Thor 2,070 TFLOPS each [NV] |
| Control rates | Joint current loop 20–40 kHz, joint impedance 2 kHz, WBC 1 kHz, RL policy 200 Hz, VLA 10–50 Hz | |
| Noise | < 55 dB(A) at 1 m when walking | |

---

## 3. Body plan and joint table
Kinematic layout: legs 2×7 (hip 3, knee 1, ankle 2, toe 1), waist 3, arms 2×7 (shoulder 3, elbow 1, wrist 3), neck 2. Arm wrists are counted in the arms, so the **body total is 33**; with 2×21 hand DoF the robot has **75 actuated DoF**, which equals or exceeds every published total. All torques and speeds are peak values **[EST]**, to be validated by trajectory-optimization sweeps (sprint, jump 0.5 m, 60 kg deadlift, stairs, fall recovery).

| # | Joint | DoF | Actuator | Peak torque | Peak speed | Range |
|---|---|---|---|---|---|---|
| 1 | Hip yaw | 1 ×2 | QDD: frameless PMSM Ø100 + 1-stage planetary 9:1 | 150 N·m | 20 rad/s | ±45° |
| 2 | Hip roll | 1 ×2 | QDD Ø120, planetary 9:1 | 300 N·m | 18 rad/s | −30/+90° |
| 3 | Hip pitch | 1 ×2 | QDD Ø130, 2-stage compound planetary 12:1, liquid-cooled | 400 N·m | 18 rad/s | −160/+45° |
| 4 | Knee | 1 ×2 | Inverted planetary roller screw (Ø16, 4 mm lead) + PMSM in the thigh, via a variable-ratio linkage | 450 N·m (> H1 360 [UH1]) | 20 rad/s | 0–165° |
| 5 | Ankle pitch + roll | 2 ×2 | Parallel: 2× ball/roller-screw linear actuators in the shank (differential) | 250 N·m pitch / 120 N·m roll combined | 25 rad/s | ±50° / ±30° |
| 6 | Toe | 1 ×2 | Small QDD + belt, passive spring | 40 N·m | 20 rad/s | 0–60° |
| 7 | Waist yaw | 1 | Cycloidal 30:1 + hollow PMSM, slip ring | 250 N·m | 8 rad/s | continuous |
| 8 | Waist pitch/roll | 2 | Two linear roller screws, parallel (spine) | 400 / 250 N·m | 6 rad/s | ±60° / ±30° |
| 9 | Shoulder pitch | 1 ×2 | Strain-wave (CSG-25 class) 50:1 + frameless | 180 N·m | 10 rad/s | continuous |
| 10 | Shoulder roll | 1 ×2 | Strain-wave 50:1 | 150 N·m | 10 rad/s | −20/+190° |
| 11 | Upper-arm yaw | 1 ×2 | Strain-wave (CSG-20) | 80 N·m | 12 rad/s | ±170° |
| 12 | Elbow | 1 ×2 | Planetary roller screw linear actuator, in the upper arm | 150 N·m | 12 rad/s | 0–150° |
| 13 | Wrist roll | 1 ×2 | Strain-wave CSF-14 | 25 N·m | 15 rad/s | continuous |
| 14 | Wrist pitch/yaw | 2 ×2 | 2× micro ball-screw linear actuators in the forearm (parallel) | 30 N·m | 15 rad/s | ±80° / ±40° |
| 15 | Neck yaw / pitch | 2 | Strain-wave micro + PMSM | 10 N·m | 15 rad/s | continuous / ±50° |

**Actuator rationale.** Low-ratio quasi-direct-drive in the hips gives backdrivability, impact tolerance, and transparency for RL sim-to-real. Roller screws handle the highest-torque, high-impact points (knee, ankle, spine, elbow), following Optimus's 14 linear actuators [OPT]: they offer high force density and shock load capacity, and placing motors proximally cuts leg inertia. Strain-wave drives in the shoulders and wrists give zero-backlash precision.

**Every actuator module includes:** frameless PMSM (NdFeB N52SH, concentrated windings, segmented stator), an integrated 48–100 V GaN inverter (20–40 kHz FOC), dual absolute encoders (motor 19-bit, output 21-bit), a winding NTC plus an inverter thermistor, a strain-gauge output torque sensor on the hips, knees, and shoulders, a power-off brake on the shoulders and waist, and a hollow shaft for harnessing.

---

## 4. Mechanical design by segment
- **Head (2.5 kg):** magnesium shell with a glass visor. Holds the sensor cluster (§6) and a 4-mic array. Neck carries a continuous slip ring.
- **Torso / chest (14 kg including battery):** monocoque of carbon-fiber composite skins over a 7075-T7351 machined frame. The structural battery pack (3.0 kWh) is load-bearing between the pelvis and the shoulder girdle. Compute bay in the upper chest, with a liquid-cooling loop and radiator plus fan in the back.
- **Spine / waist:** cycloidal yaw ring (Ø200 crossed-roller bearing) plus two spine roller screws in parallel. Hollow center for the main power bus and cooling lines.
- **Pelvis:** Ti-6Al-4V additively manufactured (laser powder bed fusion) topology-optimized node housing the hip yaw/roll/pitch actuators in a compact co-located arrangement, with the hip axes intersecting for clean kinematics. Primary IMU sits here.
- **Thigh (6 kg each):** carbon-fiber tube with AM titanium end fittings. Contains the knee roller screw and motor, mounted proximally.
- **Shank (3 kg each):** CF tube carrying the 2 ankle linear actuators mounted near the knee (low distal mass) and 2-DOF parallel rods to the ankle.
- **Foot (1.2 kg each):** CF plate with an Al heel and a sprung toe joint. 6-axis F/T in the ankle plus a 16-zone pressure insole. Replaceable rubber sole; 2.5 kW wireless charging coil in each foot (an extension of Figure 03's approach [F03]).
- **Shoulder girdle:** magnesium AZ91 casting. The shoulder pitch axis is offset forward 30 mm for a larger frontal workspace.
- **Upper arm / forearm:** CF-wrapped Al shells. The forearm houses all 21 hand motors plus the 2 wrist linear actuators, so hand mass stays low (tendon routing through the wrist).
- **Covers:** replaceable TPU lattice padding plus a washable textile suit (IP67 is sealed at the module level, not the suit). Skin-level capacitive proximity and contact sensing (§6).
- **Fasteners and serviceability:** each limb segment is a field-replaceable unit with a quick connector (power plus EtherCAT plus coolant dry-break). Target: swap a limb in < 10 min.

**Materials summary:** Ti-6Al-4V AM (pelvis, joint nodes), 7075 Al (frames, actuator housings), T800 carbon fiber (long bones, shells), Mg AZ91 (head, shoulder girdle), PEEK/POM (hand links), Dyneema SK99 (hand tendons), NdFeB N52SH (magnets), 52100/440C steel (bearings, screws).

**Mass budget [EST]:** actuators 30 kg, structure 13 kg, battery 13 kg, hands 2×1.1 kg, compute/electronics 4 kg, cooling 2 kg, sensors/covers/harness 4 kg. Total ≈ 68 kg.

---

## 5. Hands (2 × 21 DoF)
- **Kinematics:** thumb 5 DoF (CMC 2, MCP 2, IP 1). Each finger 4 DoF (MCP flex and abduction, PIP, DIP). DIP is independently actuated on the index and middle fingers and coupled on the ring and little fingers. Palm arch 1 DoF. Total 21.
- **Actuation:** forearm-mounted brushless micro-motors (Ø16–22 mm) with micro ball screws driving Dyneema tendons in antagonistic pairs (flex plus extend), with series springs for compliance, as in the Optimus Gen 3 forearm approach [OPT] and the NEO tendon hand [TQ].
- **Targets [EST]:** 25 N fingertip force per finger, 60 N thumb-index pinch, 300 N power grasp, full close in < 0.25 s, 1.1 kg per hand.
- **Sensing:** tendon tension sensors, joint absolute encoders (magnetic, Hall-array), and a 3-axis tactile skin on all phalanges plus palm (> 1,000 taxels per hand, < 1 g threshold, 500 Hz). Optical-tactile (GelSight-style) fingertips on the thumb, index, and middle fingers. Palm RGB camera (Figure 03 approach [F03]) plus a ToF depth sensor.
- **Durability:** tendons field-replaceable, IP67 glove, rated for 1M grasp cycles **[EST]**.

---

## 6. Sensors
| Location | Sensors |
|---|---|
| Head | 2× stereo pairs (forward global-shutter, 2.3 MP, 90 fps, HDR), 1 wide fisheye up, 4 side/rear fisheye cameras (360° coverage like Atlas [BD]), solid-state LiDAR (forward), thermal camera, 4–6 mic array, ambient light |
| Chest | Down-facing stereo depth for footstep planning, mmWave radar for human detection |
| Pelvis | Tactical-grade IMU (fiber-optic gyro class) plus a redundant MEMS IMU |
| Joints | Dual encoders, torque sensors (major joints), current, temperature, vibration (accelerometer per actuator for predictive maintenance) |
| Feet | 6-axis F/T at the ankle, 16-zone pressure insole, contact switch |
| Wrists | 6-axis F/T |
| Hands | §5 |
| Skin | Capacitive proximity plus contact sensing on the torso and arms, for safety and whole-body contact manipulation |
| Power | Cell-level voltage and temperature, pack current, insulation monitoring |

---

## 7. Compute and electronics
- **AI compute:** 2× NVIDIA Jetson Thor T5000 [NV]. Node A runs perception, VLM reasoning, and memory. Node B runs the fast VLA action head and the RL whole-body policy. Interconnect: 25 GbE.
- **Real-time controller:** a lockstep safety-rated MCU cluster (e.g., TI Sitara AM6x / Infineon AURIX class) as EtherCAT master running joint impedance at 2 kHz and WBC at 1 kHz.
- **Bus:** EtherCAT ring (redundant), 3 branches (left/right legs+torso, arms, hands).
- **Safety:** independent SIL-2/PLd safety chain: STO on every drive, dual-channel e-stop, wireless e-stop, and safe torque/speed monitoring near humans.
- **Comms:** Wi-Fi 7 plus 5G, plus 60 GHz mmWave dock offload (Figure 03 uses 10 Gbps [F03]), and a 4 TB NVMe logger.

---

## 8. Power
- **Pack:** 3.0 kWh, 24S high-silicon-anode NMC pouch or 4680-class cells, ~88 V nominal (higher voltage, lower current). Structural, self-swappable in < 60 s via a rear dock (Atlas-style [BD]), plus a 2.5 kW wireless charge through the feet.
- **Bus:** 88 V main bus, 48 V for the hands, 12/5 V for sensors. GaN DC-DC.
- **Regeneration:** absorbed by the battery plus 200 J of supercaps on each leg bus, to handle jump/landing transients.
- **Budget [EST]:** standing ~180 W, walking 450 W, heavy lifting 1.5–3 kW peaks, compute 100–260 W. That gives ~6 h mixed duty.
- **Safety:** cell-level fusing, aerogel thermal-propagation barriers, and a BMS designed for UN38.3 + UL 2271 (Figure 03 path [F03-batt]).

---

## 9. Thermal
- **Liquid cooling loop:** glycol-water through jackets on hip pitch/roll, knee, and spine actuators, plus the compute cold plates. A pump in the torso and a radiator-fan module in the back, at 1.2 kW heat rejection **[EST]**.
- **Air cooling:** forced air for the arm actuators. Hand motors are in the forearm with ducted air.
- **Motor design:** high slot fill, Class H insulation (180 °C), stator potted in thermally conductive epoxy.
- **Control:** real-time copper-temperature observer per actuator, with torque derating and thermal awareness exposed to the planner, so the policy learns to rest hot joints.
- **Ambient range:** −20 to 45 °C, with a battery heater for cold starts.

---

## 10. Control and AI stack
1. **Actuator level (20–40 kHz / 2 kHz):** FOC with feedforward friction and cogging compensation. Joint impedance control with torque-sensor feedback.
2. **State estimation (1 kHz):** invariant EKF fusing IMU, kinematics, foot contacts, and visual-inertial odometry.
3. **Whole-body control (1 kHz):** hierarchical QP WBC as a safety and constraint layer, combined with a centroidal MPC (100 Hz) for contact planning.
4. **Learned whole-body policy (200 Hz):** a single RL policy (HOVER/ExBody-style command space covering base velocity, root pose, and upper-body keypoints) trained in Isaac Lab with thousands of parallel environments and validated in MuJoCo (sim2sim). Human motion priors come from retargeted mocap (AMP). Teacher-student distillation with privileged terrain. Domain randomization covers mass, friction, latency, motor constants, and actuator networks fit from dyno data.
5. **Dexterous manipulation:** RL in-hand manipulation policies trained in sim with tactile simulation, plus imitation from teleop.
6. **Vision-language-action (dual system, as in Figure Helix):** System 2, a VLM at 7–10 Hz (fine-tuned from GR00T N1.x or π0.5-class open models), produces latent intent. System 1, a visuomotor diffusion/flow transformer at 50–200 Hz, outputs whole-body targets (arms, hands, torso, base velocity) to the WBC.
7. **Data:** full-body VR teleop (Vision Pro hand tracking plus a mocap suit, haptic gloves with force feedback), egocentric human video pretraining, and sim-generated synthetic demonstrations (Isaac/Cosmos). Fleet learning feeds failures back into data.
8. **Safety layers:** control barrier functions for self-collision and human distance; ISO/TS 15066 speed and separation; a learned safe-fall policy (curl, protect head and hands); a watchdog falls back to a stand-in-place or crouch controller.
9. **Middleware:** RT-Linux, a deterministic shared-memory RT loop, ROS 2 for tooling, MCAP logging, and OTA updates with signed images.

---

## 11. Key design risks
- **Knee and hip thermal limits** at 60 kg payload. Mitigation: liquid cooling and torque-sensor-based efficiency maps.
- **Roller screw shock loads and backdrivability** on falls. Mitigation: series compliance and sacrificial overload clutches.
- **21-DoF tendon hand durability and calibration drift.** Mitigation: tension sensing and auto-recalibration.
- **Mass creep** above the 68 kg target. Mitigation: a hard mass budget per segment.
- **Sim-to-real for 75 DoF**, especially the hands. Mitigation: system ID, actuator nets, real-data fine-tuning.
- **Dual-Thor power and heat** in the torso. Mitigation: the shared liquid loop.
- **IP67 sealing vs. heat rejection.** Mitigation: sealed modules with external radiators.

## 12. Next design steps
1. Build the full parametric CAD skeleton plus URDF/MJCF, and run trajectory-optimization torque/speed sweeps to freeze the joint table in §3.
2. Prototype and dyno-test 3 hero actuators: hip-pitch QDD, knee roller screw, shoulder strain-wave.
3. Build a 21-DoF hand on the bench with tactile skin.
4. Train a locomotion policy on the target model in Isaac Lab, then cross-check in MuJoCo.

---

## Sources
- [BD] Boston Dynamics, Atlas product page: https://bostondynamics.com/products/atlas/
- [F03] Figure, "Introducing Figure 03": https://www.figure.ai/news/introducing-figure-03
- [F03-batt] Figure, "F.03 Battery Development": https://www.figure.ai/news/f-03-battery-development
- [RG] Robotica Guide, Figure 03 specs: https://roboticaguide.com/figure-03-specs-helix-botq-what-is-undisclosed/
- [OPT] Optimusk blog, Optimus hardware (third-party, unofficial): https://optimusk.blog/blog/tesla-optimus-hardware-specs/
- [HA] HumanoidApplications compare: https://humanoidapplications.com/compare/
- [UH1] Unitree H1: https://www.unitree.com/h1
- [RZ-H1] RoboZaps H1 review: https://blog.robozaps.com/b/unitree-h1-review
- [UG1] Unitree G1: https://www.unitree.com/g1/
- [UG1-doc] Unitree G1 developer docs: https://support.unitree.com/home/en/G1_developer/about_G1
- [TQ] TechniaHQ comparison (NEO details): https://www.techniahqservice.com/robotics-news/tesla-optimus-vs-figure-unitree-1x-neo
- [RR] RankedRobot NEO vs G1: https://rankedrobot.com/compare/1x-neo-vs-unitree-g1/
- [RZ] RoboZaps Optimus alternatives: https://blog.robozaps.com/b/tesla-optimus-alternatives-competitors
- [IDT] Inside Deep Tech 2026 guide (Digit 5): https://www.insidedeeptech.com/humanoid-robots-2026-full-guide/
- [NV] NVIDIA Jetson Thor: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/
- [NV-blog] NVIDIA technical blog, Jetson Thor: https://developer.nvidia.com/blog/introducing-nvidia-jetson-thor-the-ultimate-platform-for-physical-ai/
- [ANT] Antarum, Thor pricing: https://www.antarum.ai/parts-power/nvidia-jetson-agx-thor-dev-kit/

*Note: Component part names in §3 are candidates to evaluate. Their specs should be confirmed against current datasheets before purchase.*
