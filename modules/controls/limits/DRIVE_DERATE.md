# Drive thermal derate (R-141)

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
