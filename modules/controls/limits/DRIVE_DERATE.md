# Drive thermal derate (R-141)

> **R-146(a) INTERIM, in force (21d1738). NOT valid for G4 sign-off.** Latch at a reading ≥ **82 °C**. Safe stop =
> CROUCH (2.0 s derated) → **HOLD_DERATED** (hold the derated crouch, MO on) → first drive trip → **TUCK** (fall config),
> logged as a **fall event** (`fall_events`, `on_fall` hook → Test fall budget). This is acceptable only as a fault path:
> R-140 keeps the duty below the 75 °C derate start. The kneel/prone path (R-145, R-146b, D94 MO=0 interlocks) stays in
> code behind `kneel_enabled = false`. Rows below that mention 83 °C or MO_OFF describe that disabled path or earlier rulings.

Sources: Arbiter **R-141** (e8b74e7, modules/RULINGS.md), **R-142** (00b3268: stop latch at a reading ≥83 °C, final); Electronics R1_ARCHITECTURE §18.5 **P-055** (23f6992) and the
**P-055 addendum** (430684c, citing Elmo *EtherCAT Application Manual* G-ETHERCATAM v1.403 [EAM]).
Code: `drive_thermal_derate.py`. Tests: `test_drive_thermal_derate.py`. Config: `controller_config.json` → `drive_thermal_derate`.

## Behaviour (every 1 kHz cycle, every drive)
| drive temp T | action |
|---|---|
| ≤ 75 °C | scale 1.0 |
| 75–82 °C | linear 1.0 → 0.5 |
| 82–83 °C | 0.5 |
| reading ≥ 83 °C on **any** drive (R-142; R-141 had 84) | latch whole-robot controlled stop: `request_safe_sit()` (WBC/fall-mode safe posture or sit), drives stay on and derated during the sit; on `sit_done()` (or `sit_timeout_s` 3 s) MO=0 on **all** drives |
| drive fault MF 0xD000 / EMCY 0x4310 (own trip 85 °C) | same latch (fault input) |
| resume | only `re_enable()`, only if every drive has a fresh reading < 78 °C and no over-temp fault; nominals restored, then the curve applies |

Limit write: **0x6072 Max torque** (RxPDO 0x160D / 0x1605) = round(scale × nominal) in per-mille of 0x6075, written
every cycle. Config alternative `limit_object: "0x6073"` (Max current, RxPDO 0x160E). **CL[1]/PL[1] are never written
and SV is never issued**: they stay at the commissioned values (no CoE index, [EAM] pp.62–64).

WBC: `torque_limits()` = scale × τ_nominal (τ_nominal = Kt·ratio·I_nominal; default from gains.npz `tau_lim`, i.e.
CONTRACTS R1.2 peaks, **[EST until commissioning]**). `combine_min(drive, pick, carry, knee_winding, …)` takes the element-wise min.

Temperature source (`temp_source`): primary **0x22A2:00** (UINT16 °C, RO, mappable) in the 1 kHz TxPDO; candidate
`0x22A3:1..4`; fallback `sdo` = SDO at 10 Hz per drive, round-robin.
Stale handling: no accepted reading for 20 ms (PDO) / 0.5 s (SDO) → fail-safe scale 0.5; 5 s → controlled stop.
Jumps: a step larger than max(2 K, 3 K/s × age) is rejected unless repeated 3 consecutive reads (plate ≤ 0.3 K/s, 10× margin).

## Sit timing check (R-142: reading 83 → trip 85 °C; worst case with truncation = 1.0 K true band)
| basis | dT/dt | time 84→85 | sit + latency | margin |
|---|---|---|---|---|
| plate lumped, knee worst (430684c: τ ≥ 185 s, 12 W / 40.3 J/K) | 0.30 K/s | 3.33 s | 1.2 s [EST, = sit-to-stand] + 0.05 s | **+2.1 s PASS** |
| drive-only, no plate (adiabatic bound, from DRIVE_HEAT_PLATES / R131 data), 1 K worst band | 1.19 K/s | 0.84 s | 1.25 s | **−0.41 s** (bound, not expected); with a 2 K band (rounding) +0.43 s |

**Flag: 1 °C quantisation.** 0x22A2 is integer °C. If the drive truncates, a reading of 84 can be a true 84.99 °C, so the
real band before the 85 °C trip can be ~0 K. At 0.3 K/s the sit needs ≥ 0.38 K of band.
**Adopted by R-142 (00b3268), final even if the bench shows rounding:** latch the stop on a reading ≥ 83 °C, i.e. a true temperature of ≥ 83.0 °C. That gives
≥ 1 K, which is 3.3 s at the plate slope (margin +2.1 s) and covers the quantisation. Keep resume at < 78 °C.
Above 82 °C the limit is already 0.5, so I²R losses during the sit are ≤ ~¼ of the losses at peak. That makes the plate
slope conservative. The sit duration itself is an estimate: measure stand-to-sit on the bench.

## Bench-verify (UNCONFIRMED, Electronics owns the indices)
1. 0x22A2/0x22A3 mappable: p.63 says yes. p.64 (and Table 5 versus p.64 for 0x6072/0x6073) contradict each other. Confirm the TxPDO mapping is accepted.
2. Which 0x22A3 sub equals TI[1]: compare with TI[1] via EAS, then switch `temp_source`.
3. 0x6072/0x6073 units: per-mille of 0x6075 (CiA 402) is not stated in [EAM].
4. CL[1]/PL[1] interaction: verify that 0x6072/0x6073 cap the current **below** the commissioned CL/PL (effective = min?).
5. Binary Interpreter fallback 0x2013 (rPDO2) / 0x2012 (tPDO2), UINT64: the frame format isn't in [EAM], and the RO/WO attributes look swapped. Use it only if (4) fails.
6. Integer truncation versus rounding of 0x22A2 (informational only; R-142 keeps 83 °C either way).

## Open items
- MuJoCo heat-up/sit smoke not added: the PD-only stand on the box isn't stable without the policy/WBC, so it can't validate the sit. Run it with the WBC sit once that path exists.
- The WBC/fall-mode `request_safe_sit` hook and `sit_done` signal must be wired by the WBC owner. τ_nominal must come from the commissioned limits.

## Safe-sit time in sim (R-142 follow-up), `safe_sit_wbc.py`
Setup: sim/v3 4115f6e at 68 kg (LEGS_MASS=68), CPU MuJoCo, 1 kHz. Legs WBC (`modules/legs/wbc/controller.py`) in stand mode
(QP + ZMP-in-support), with every leg drive limited to 0.5 × the R1.2 limit. The CoM height reference and the joint
posture follow a minimum-jerk profile from standing (CoM 0.909 m) to a crouch. A 0.45 m chair is drawn but has no contact.
Pass: no fall, 0 QP failures, final CoM within 3 cm of the target, |τ| ≤ derated limit, measured CoP margin ≥ 0.
Raw output: `safe_sit_wbc_results.txt`.

| descent T | result (crouch: pelvis 0.85 m, CoM 0.909 → 0.765 m, −0.144 m) |
|---|---|
| 1.0 s | **falls** at 2.59 s (CoP 25 mm outside the sole, torque saturated) |
| 1.5 s | stable, but leg torque hits the 0.5 derate limit (clipped) |
| 2.0 s | stable, peak 0.95 of the derated limit |
| 2.5 s | stable, peak 0.95 |

**Fastest stable: 1.5 s; fastest without torque saturation: 2.0 s. Both ≤ 2.5 s.** At 0.3 K/s, 2.0 s + 0.05 s uses 0.62 K
of the ≥1.0 K band (R-142), so the margin is about 1.6×. Full torque gives the same shape: 1.5 s ok, 1.0 s not.

Limits of this result (do not over-read):
- **It is a crouch, not a seated sit.** With an upright pelvis the IK pose needs the ankle past its −0.79 rad dorsiflexion
  stop below a pelvis height of about 0.94 m. Deeper poses run the shank into the stop, and the stand-mode WBC diverges
  (this happens at full torque too, so it is not a derate effect). With 0.4 rad of pelvis pitch, a CoM of 0.725 m was
  stable once at T = 2.5 s, but it is not robust: it fell with nearby gains. Reaching a 0.45 m seat (CoM about 0.59 m) needs
  a trunk-lean sit mode in the WBC: pelvis pitch reference, stiffer stand-mode CoM-x loop (gain 2.5 s⁻² now), and a joint-limit-aware posture.
  That belongs to Legs/WBC.
- The measured CoP touches the sole edge briefly (minimum margin 0 mm; < 5 mm for 1.8 % of the time at T = 2.0 s), so the ZMP
  margin is thin. The contact points are the 4 box corners per foot.
- The script patches the WBC at runtime (pelvis pitch reference, leg posture gains); both stay at their stock values for this
  table. `controller.py` is not edited.

## R-145 (5f5bd1d) stop sequence and Actuators D94 (7d22c91) torque-free end pose
State machine in `drive_thermal_derate.py`: **CROUCH** (2.0 s derated, WBC) → **KNEEL** (fall-mode) → **CONTACT_CONFIRMED** → **MO_OFF**.
Fallback: **HOLD_DERATED** (kneel timeout 1.2 s [EST], crouch timeout 2.6 s, or `kneel_impossible()`), then **TUCK** on the
first drive trip. MO is never commanded off in HOLD_DERATED or TUCK.
`supported()` needs all four flags together: knee contact, CoM inside the knee+toe polygon, CoM speed < 0.1 m/s, and
`torque_ok`. `torque_ok` comes from `static_hold_ok()`: the static holding torque must be below the D94 friction hold at
every joint (hip 7, knee 7, ankle 8, all other joints 7 N·m). The flags must hold for 50 ms. `_mo_off()` raises
`UnsupportedMoOff` otherwise. Tests cover every transition, both timeouts, contact flicker, and the MO guard over all
flag combinations, including the torque flag.

### Sim: crouch then kneel (`safe_sit_wbc.run_kneel`), sim/v3 4115f6e, 68 kg, legs at 0.5 derate, CPU
- Knee pads: sim/v3 has no knee contact geom, so `<s>_knee_pad` boxes **[EST]** (50×100×80 mm) are added on the front of
  each shank at the knee, for this sim only.
- The repo has no fall-mode controller. The kneel is a joint PD (gains.npz) along minimum-jerk waypoints
  (`fall_mode_kneel` in controller_config, **EST**), with the supervisor driving the states.
- **Result: the kneel is not achieved. Total time to supported contact: not reached → gate (≤ 2.8 s) FAIL / not measurable.**
  - The crouch works: 2.0 s, peak 0.95 of the derated limit.
  - Every kneel variant tried (≈15: trunk/hip lean, arms forward, WBC CoM lean to x 0.14–0.18 m before the drop,
    0.6–1.6 s, at both 0.5 and 1.0 torque) sits back and falls onto the pelvis/torso. No knee or pad contact occurs, so
    the peak knee impact force is not available.
  - Mechanism: in the crouch the ankle is already at its −0.79 rad dorsiflexion stop. The knees can only travel forward
    if the heels lift, which needs the CoM ahead of the toe line, and neither the PD nor the stand-mode WBC moves it there.
  - The supervisor correctly ended in HOLD_DERATED with MO on (no MO=0 was sent).
- GIF: `media/progress/2026-10-21_controls_r145_crouch_kneel_attempt.gif`.
- **Latch:** left at 83 °C. R-145 drops it to 82 only if the sim *shows* > 2.8 s, and the kneel time could not be
  measured at all. Arbiter call.

### End-pose holding (`kneel_hold.py`, results `kneel_hold_results.json`)
Each candidate pose is settled under a PD hold. Then MO=0, with joint friction set to the D94 holds.
"PD hold" is the mean PD torque at rest, an upper bound because the pose target fights the contacts.
"MO=0" shows whether the pose actually stays with friction alone.

| pose (target → actual contacts) | PD hold max (N·m) | MO=0: CoM drop / max drift / joints at friction limit |
|---|---|---|
| B kneel, sitting back (knees 135° stop): pads + feet | 16.5 (hips, shoulders, waist > 7) | **274 mm / 83° / hips, knees, waist, shoulders: collapses** |
| C hands + knees: hands + feet | 40.8 (knees) | **199 mm / 107°: collapses** |
| E child's pose: pads + feet + hands | 29.2 (hips) | 47 mm / 49° (elbows, knees at limit): slumps |
| A upright kneel: ends face-down on chest pad + thighs + hands | 38.3 | 5.5 mm / 5.5°, hips and shoulders at friction limit |
| D forearms + knees: ends on head + knee pads | 98.9 | **5.6 mm / 6.2°, no joint at the limit** |
| F prone: chest pad + feet + hands | 69.3 | **22.5 mm / 9.7°, no joint at the limit** |

**No kneel pose meets the D94 rule.** Every pose with the trunk held up on knees, feet or hands needs 11–41 N·m at the
hips, knees, waist or shoulders, and collapses with MO=0. The only poses that stay put with MO=0 (no joint at its
friction limit) are **lying on the floor**: forehead/chest down on the knee pads, or prone on the chest pad. That is the
lowest-torque settled state. Open item for the Arbiter: R-145 + D94 together imply the MO=0 end state is a controlled
lowering to prone/chest-pad (or the robot keeps derated torque, i.e. HOLD_DERATED → drive trip → tuck), not a kneel.

## R-146(b) G4 toe-pivot kneel — status 2026-10-21 (sim, NOT passing)
| Run | P1a CoM shift | CoM x reached (target 0.14) | P1b toe pivot |
|---|---|---|---|
| ZMP_K (12,7), T1A 0.6 | 0.6 s | 0.089 m | falls backward |
| ZMP_K (40,12), T1A 0.8 (kneel/safe-stop mode only, `safe_stop_zmp_k` in controller_config; global WBC unchanged) | 0.8 s (target reached ~1.0 s) | 0.136 m | ankle hits −0.79 stop at t≈1.5 s, CoM falls back to −0.01 m, unstable |
| same, FOOT_PITCH 0.3 / 0.15 | 0.8 s | 0.136 m | same failure |
| same, ANKLE_MIN −1.1 (diagnostic only) | 0.8 s | 0.136 m | CoM stays forward (0.11 m) but knee hits its limit and the feet bounce: unstable |

P2–P4 are never reached, so no phase times are valid against the ≤3.3 s gate. The ankle dorsiflexion stop is the binding constraint (Legs check needed).

## R-146(b) WBC chest-supported lower, standalone (chest_lower_wbc.py, 2026-10-21, sim/v3 68 kg, legs + arms ×0.5)
**Prone stays FORBIDDEN as a routine safe-sit** until the full G4 chain (kneel → pads → hands → this lower) passes in
sim and on the bench. This result covers the lower phase only, started from a supported hands-and-knees pose.

Controller: task-space WBC (damped weighted least squares on the floating-base Jacobian, 1 kHz). It holds the hands
and knee pads in place, keeps each elbow over its hand (gradually), and tracks the chest-pad descent velocity at
0.9 × ProneLowerGuard.speed_limit(gap), with a reference governor (lead ≤ 10 mm) and measured-speed feedback. The
trunk pitch is slaved to the gap, and only the pitch-plane joints move. Joint PD plus a contact-consistent
gravity feed-forward. Sequence: contact → hold until settled (|vz| < 5 mm/s for 0.2 s) → torque relax over 0.8 s
→ D94 flag (all |τ| < friction hold, chest still) → MO=0.

| Case | Contact speed m/s (≤ 0.10) | Peak chest N (≤ 8800) | Lower time s | MO=0 at s | Elbow peak N·m | Shoulder pitch peak N·m |
|---|---|---|---|---|---|---|
| nominal 68 kg, pad tc 0.02 | **0.081** | 271 | 3.02 | 3.95 | 25.0 | 55.9 |
| DR 65–68.5 kg × pad tc 0.005/0.02/0.04 (6 runs) | **≤ 0.082** | ≤ 430 | 3.00–3.02 | 3.90–4.00 | ≤ 25.2 | ≤ 56.0 |

- The descent speed stayed under the guard limit throughout (max speed − limit = −0.016 m/s).
- **Torque caps:**
  - Elbow cap in force: 38 N·m (0.5 × 76). That is below the 69 N·m hard cap and below the 40 N·m / 180 s thermal
    limit. The 25 N·m peak is under the 28 N·m continuous limit too.
  - Shoulder pitch: 83.5 cap. Hip pitch: 34.6 of 175.
- **Open issue (end pose):** the knee pads roll off and the robot rests on the thigh fronts about 27 mm above the
  knee joint (pads [EST]). At MO=0 the split is chest 271 N, thighs 275 N, hands 121 N, knee pads 0 N.
  - Holding the shank orientation keeps the pads loaded, but then the elbows hit the 38 N·m cap and the lower
    stalls at a 50–60 mm gap.
  - Adding a CoM-share task lands on the pads (chest 292 / pads 233 / hands 94 / feet 48 N) but overshoots the
    speed limit (contact 0.11–0.41 m/s).
  - Needs: a longer pad up the thigh front (ID), or more elbow budget, or a better arm-load schedule.
- The trunk ends about 0.2 rad head-down (pitch 1.78) with no head contact.
- GIF: media/progress/2026-10-21_controls_r146b_chest_lower_wbc.gif

## D96 PU knee stop at 135° — knee speed at stop contact (knee_stop_impact.py, sim/v3 + pads [EST], MO=0, D94 friction)
The stop is modelled as the joint-limit contact at 2.356 rad, with PU timeconst 0.005 / 0.01 / 0.02 s [EST].
DR: mass 65 / 68 / 68.5 kg × timeconst × lean (99 runs).

| Case | Knee speed at stop, nominal (rad/s) | DR max (rad/s) | Peak stop torque, DR max (N·m) [EST] |
|---|---|---|---|
| crouch collapse (HOLD_DERATED → drive trip / TUCK) | 5.36–5.40 | 5.41 | 5520 |
| forward fall from stance | 5.99–6.18 | **6.18** | 6825 |
| kneel tip back (sits onto heels) | 2.40–2.49 | 2.50 | 2066 |
| kneel tip forward | stop not reached (knee ≤ 90°) | – | – |

- **Design input for STOP_IMPACT_N: 6.2 rad/s per knee** (forward fall, MO=0).
- The stop torque scales about 1/timeconst: worst case 6825 / 3333 / 1665 N·m at 0.005 / 0.01 / 0.02 s, so it needs
  the real PU stiffness and stroke.
- The kneel retry does not reach the pads yet (R-146(b) P1b), so kneel_tip stands in for it.

## P-157 / D96 ankle update and kneel retry (2026-10-21)
- **Soft limit with roll coupling** (`ankle_pitch_min`, `check_ankles`; config `drive_thermal_derate.ankle_*`):
  - −0.916 rad (−52.5°) at any roll.
  - Down to −0.955 rad only with |ankle roll| ≤ 10°; the −0.960 rad (−55°) mechanical stop is never commanded.
  - A violation in KNEEL → HOLD_DERATED. Tests added.
- **sim/v3 XML not changed** (ankle range still −45°). job 10's brief stops if the sim/v3 hash ≠ 4115f6e or if
  `git diff d786dff HEAD -- sim/v3` is non-empty, and the ankle range feeds make_model (a training input). The kneel
  applies −0.955 at runtime instead (`kneel_prone_wbc.ANKLE_MIN`). Regenerating sim/v3 (gen_v3.py LIM and the XML)
  needs a decision on job 10.
- **Kneel retry with ANKLE_MIN −0.955, safe-stop ZMP_K (40,12):** still FAILS in P1b.
  - The CoM reaches 0.136 m (target 0.14) and the ankle now reaches −0.96.
  - At t≈1.4–1.5 s the feet unload (fz 15 N), the foot never pitches onto the toes, and the CoM falls from 0.87 to
    0.76 m in 0.2 s, then bounces.
  - The knee pads are never reached, so there is no knee-pad contact speed yet. Phase times: P1a 0.8 s; P1b–P4 not
    valid against the 3.3 s total.
  - The stance QP is flat-foot only; a toe-support task-space controller (as in chest_lower_wbc.py) is the next step.
