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
