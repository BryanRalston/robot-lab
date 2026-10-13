# Bench test plan: net DC-bus energy per stride on a shared bus (TARGETS G5, R-009)
Owner: RL Actuators. Draft round 3, 2026-10-13. Evidence deadline (R-009): end of round 4.

## 1. Purpose and pass criteria
Measure the net DC energy drawn from a shared 20S bus while two or more leg actuators replay the walk 1.2 m/s joint trajectories. Compare it with the same replay where regen cannot be shared or stored ("no regen").

Each criterion below is tied to R-009. Results are normalised to the 12-joint robot by the per-joint energy split in `regen_core.py`.

| # | criterion | threshold | basis |
|---|---|---|---|
| P1 | measured netting, both legs equivalent: E_noregen − E_shared per stride × stride rate | **≥ 213.4 W** | R-009: realised regen ≥ 942.4 − 729.0 W |
| P2 | absolute steady robot power, measured legs + 254 W rest-of-robot | **≤ 729 W** | T7 2 h on 1620 Wh × 0.9 |
| P3 | model agreement: measured/modeled per-joint DC energy per stride | within ±10 % per joint, ±5 % summed | upgrades `regen_sim.py` to ×1.0 |
| P4 | bus safety | Vbus ≤ 90 V clamp never reached; BMS regen current ≤ 30 A; chopper energy logged | R1.3, D16 |
| P5 | thermal | winding ΔT ≤ 100 K after 30 min of continuous replay | CONTRACTS thermal rule |

Note: with iron loss now modeled (D18), the modeled regen is 245 W and the no-regen power 964 W. P1 and P2 together therefore need ≥ 96 % of modeled regen realised at 1.2 m/s. The test also yields the 1.0 m/s number (fallback, R-009): pass line P2 ≤ 729 W against a modeled 615 W full / 699 W half credit.

## 2. Hardware (minimum configuration: one leg, 5 actuators, 10 drives)
| item | spec | qty |
|---|---|---|
| hip_yaw, hip_roll rotary units | TBM2G-06008A + CSG-17-100; TBM2G-08508A + CSG-25-100 (P-005/P-006) | 1 each |
| twin-screw units | hip_pitch (2 × 07613D + RV12x4, 50 mm), knee (2 × 07613D + RV12x5, 47.5 mm), ankle (2 × 06013D + RV12x4) | 1 each |
| load: per joint | absorber/driver dynamometer on the joint output. Either (a) a rotary servo load motor (e.g. a second TBM2G-08513 + CSG-32-50, torque-controlled) or (b) for screws, the real leg linkage pinned to a ground frame with a load actuator at the foot/thigh. The load must both **drive and absorb** (four-quadrant), so it reproduces the negative-work phases | 5 |
| drives | Elmo Gold Twitter R70/100 EtherCAT | 8 (+2 load side if using Elmo) |
| bus | 20S5P P45B pack with BMS (30 A regen-charge limit) **or** a bidirectional DC supply in battery-emulation mode (OCV 72 V, 60 mΩ series R) plus a brake chopper set at 88 V | 1 |
| load-side bus | **separate** supply with its own sink, so load-motor energy never mixes with the device-under-test bus | 1 |
| master | EtherCAT master (TwinCAT or SOEM on RT Linux), 1 kHz, distributed clocks | 1 |

The full both-legs check (P1 at robot level) needs a second leg or a mirrored replay of the left-leg data with a 0.5-stride phase shift. A one-leg bench understates cross-leg netting, which is conservative.

## 3. Instrumentation
| quantity | sensor | accuracy | rate |
|---|---|---|---|
| DUT bus voltage and current (battery side) | 4-wire shunt 1 mΩ ±0.1 % + isolated 24-bit ADC, or a power analyser (e.g. Yokogawa WT1806E / ZES LMG) DC channel | energy ±0.2 % | ≥ 10 kHz, integrated |
| chopper current | Hall sensor ±1 % | | 10 kHz |
| per-drive DC input current | drive-internal DC bus current/voltage (EtherCAT PDO) cross-checked against a clamp probe on one drive | ±2 % | 1 kHz |
| joint torque | in-line torque flange (rotary) / load cell in the rod (screws), ±0.5 % FS | | 1 kHz |
| joint angle/speed | AksIM-2 output encoders (20 bit) | | 1 kHz |
| winding temperature | NTC/PT1000 in each stator + housing thermocouples | ±1 K | 1 Hz |
| ambient | thermocouple | ±0.5 K | 1 Hz |

All logs share the EtherCAT distributed-clock timestamp. The power analyser is triggered by a stride-sync digital output.

## 4. Procedure
1. **Characterise first:** run no-load speed sweeps of every motor (0–7600 rpm). These give measured iron/drag loss, replacing the D18 datasheet-derived fit. Then run locked-rotor resistance at 25 °C and hot.
2. **Transmission back-drive efficiency:** run each joint as a generator at 3 torque levels × 3 speeds. This sweep factor (eta_back) dominates the uncertainty: −15 % costs 15 % of regen.
3. **Trajectory replay:** take the Legs walk_1p2 gait-ID trajectories (`modules/legs/results/walk_1p2.npz`), or the forward-sim trace once it walks (regen_core format (b)). Each DUT joint tracks position and feed-forward torque; the load reproduces the gait torque as a disturbance profile. Run 2 min warm-up, then 20 strides.
4. Run (3) in three bus configurations:
   - **A, no regen:** each drive has its own supply and chopper (no sharing).
   - **B, shared bus without charge:** BMS charge path disabled; chopper on.
   - **C, shared bus + 30 A charge.**
5. Repeat (3)–(4) at 1.0 m/s (fallback) and at winding temperature hot (after 30 min). Do 3 repeats per configuration.
6. **Compute:** E per stride = ∫ V·I dt over each stride (stride-sync). Report mean ± 2σ over 20 strides × 3 repeats. Scale to the robot with the per-joint shares from `regen_core.py`, and report the scaled figure separately from the raw one-leg number.
7. **Model check:** feed the measured trajectories and the measured iron/back-drive data into `regen_sweep.py`. Compare against P3.

## 5. Acceptance and reporting
- P1–P5 all pass → Arbiter grants full regen credit (R-009), T7 met at 1.2 m/s.
- P1 fails but the 1.0 m/s replay passes P2 → evidence for the R-009 T6/T7 trade (cruise speed for the 2 h rating).
- Report: `modules/actuators/results/bench_<date>.md` with raw logs (CSV), the scaling sheet and photos.

## 6. Effort and risks
- Rig: one leg with 4-quadrant loads plus a battery emulator. This is the long pole for the end-of-round-4 deadline.
- The CPU-only fallback is available now (forward-sim trace through `regen_sweep.py`). It upgrades the sim to ×1.0 but does not replace the bench, per R-009.
- Risk: the load motors' torque ripple corrupts small regen phases. Mitigation: compare against the torque sensor, not the commanded torque.
