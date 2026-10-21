# G5 test plan — RL Test & Reliability additions (2026-10-21)
Procedures and pass criteria only; no hardware yet. Each item: n samples, conditioning, method, pass. Unless stated, record force/temperature at ≥ 1 kHz / 1 Hz, photograph before and after, and log to `modules/reliability/results/g5/<id>/`. Existing plans stay where they are (actuators BENCH_TEST_PLAN, PROOF_TEST_hip_lever, O20a/b, design/R069_TESTS.md).

| ID | Source | Test |
|---|---|---|
| TP-G5-01 | R-042 | EPP80 40 mm shoulder pad drop tower |
| TP-G5-02 | A37 | G10 thermal-break sleeve creep |
| TP-G5-03/04/05 | design/R069_TESTS.md | T-B2 knee cap kneel-fall, T-F1 bellows flex, T-G snap retention (procedures in that file; T&R adds witnessing + logging only) |
| TP-G5-06 | R-076 | MR30 connector vibration + pull retention |
| TP-G5-07 | R-079 | walking-convection h on a heated rev B knee |
| TP-G5-08 | R-081 | sole pad wear + impact |
| TP-G5-09 | R-085 | grip test with encoder-cap thermocouple |
| TP-G5-10 | R-077 | hot always-on converter load |
| TP-G5-11 | T-029 | BiSS-C master CM noise + MII timing |
| TP-G5-12 | R-114 | EA 9396 lap coupons, hot creep |
| TP-G5-13 | P-050 | DP490 per-lot coupons (legs/R031_FIXES.md) |
| TP-G5-14 | R-112 | 80 °C hot proof |

## TP-G5-01 EPP80 40 mm shoulder pad drop tower (R-042)
- **Samples:** n = 3 pads per temperature (production density EPP80, 40 mm, on the R-079/R-120 tray + honeycomb stack), new pads per series.
- **Conditioning:** ≥ 4 h at **0 °C** and at **40 °C**; test within 60 s of removal (or in a chamber).
- **Method:** guided drop tower, flat or ø100 hemispherical striker matching the side-fall contact, mass and height set to **220 J** (verify by h × m·g ±2 %). Load cell under the anvil (≥ 50 kHz), accelerometer on the striker. Drops 1, 10 and 100 on the same spot, 60 s apart; thickness after 1 min and after 24 h.
- **Pass:** drop-1 peak force ≤ the pad design limit used in the Arms/job 1 loads (**9.17 kN**) at both temperatures; peak force at drop 10 ≤ 1.15 × drop 1 and at drop 100 ≤ 1.30 × drop 1; thickness recovery ≥ 90 % after 24 h (drop 10) and ≥ 80 % (drop 100); no split through the pad, no bond failure.

## TP-G5-02 G10 sleeve creep (A37)
- **Samples:** n = 3 G10/FR4 sleeves (production geometry, grain/weave as built) in a motor-to-collar clamp fixture with production bolts.
- **Method:** constant compressive bearing stress **34 MPa** at **100 °C** for **100 h** (dead weight or servo hold); LVDT on the stack every 10 min; bolt preload by load washer.
- **Pass:** creep strain at 100 h ≤ 0.5 %, extrapolated (log-time) to 14 600 h ≤ 1 %; preload loss ≤ 15 %; no delamination or crack (visual + dye penetrant after test).

## TP-G5-06 MR30 vibration + pull retention (R-076)
- **Samples:** n = 5 mated Amass MR30 pairs as harnessed (strain relief as built).
- **Method:** random vibration 10–2000 Hz, 5 g rms, 1 h per axis (IEC 60068-2-64-style), carrying rated current; monitor contact resistance continuously (4-wire) and log ≥ 1 µs discontinuities. Then axial pull to separation at 10 mm/min.
- **Pass:** no discontinuity > 1 µs; Δresistance ≤ 20 % of the initial value; temperature rise at rated current ≤ 30 K; retention ≥ the datasheet value and ≥ 2 × the worst harness snag load (≥ 40 N [EST, confirm with Electronics]).

## TP-G5-07 Walking-convection h on a heated rev B knee (R-079)
- **Setup:** rev B finned knee housing with cartridge heaters or the motors at a known power (I²R measured); thermocouples on the fin root, fin tip, housing, plus the **ID skin TCs** (inner face of the shin/knee cover) and the **standoff ΔT** (both sides of each cover standoff). Mount on a leg swinging at gait kinematics, or a rotating arm/wind tunnel matching the local airspeed.
- **Method:** steady state at **0.5, 1.0, 1.5, 2.0 m/s**, plus 0 m/s natural convection; h = P / (A_fin·(T_surface − T_amb)), radiation corrected.
- **Pass:** measured h ≥ the value assumed in the thermal model (R-079/R-081) at every speed (else the carry-duty limits are re-run); cover skin ≤ 48 °C touch limit; standoff ΔT matches the model within ±20 %.

## TP-G5-08 Sole pad wear + impact (R-081)
- **Samples:** n = 3 sole pads (foot C2, production compound).
- **Method:** (1) wear: reciprocating abrader on concrete and tile at the walk contact pressure, 10⁶ cycles at 1 Hz (≈ 1 year); measure thickness and mass every 10⁵. (2) impact: heel-strike drop (66.5 kg foot-share, 1.2 m/s gait speed) × 10 000, at 0 and 40 °C.
- **Pass:** wear ≤ 30 % of the pad thickness at 10⁶ cycles; no delamination from the sole; static CoF ≥ 0.6 dry concrete before/after; peak force within ±15 % of new after the impact series.

## TP-G5-09 Grip with encoder-cap thermocouple (R-085)
- **Setup:** hand on the bench, TC bonded to the encoder cap of the hottest finger/thumb drive.
- **Method:** repeated 10 kg grip/hold at the R-085 duty (hold to thermal steady state, then the rated grip cycle).
- **Pass:** encoder cap ≤ the encoder rating minus 10 °C (cite the part), no slip of a 10 kg test object, grip force ≥ the design value at steady-state temperature.

## TP-G5-10 Hot always-on load (R-077)
- **Setup:** RP03-11012SRAW (R-076/R-077) on the production board in a **60 °C** chamber (worst internal ambient), always-on loads connected.
- **Method:** measure output power and converter case temperature at steady state over 4 h.
- **Pass:** hot always-on load ≤ **2.4 W** (80 % of rating, R-076); case ≤ maker limit after the >60 °C derate; output within regulation.

## TP-G5-11 BiSS-C master CM noise + MII timing (T-029)
- **Setup:** production drive, actuator and harness length, motor PWM running at rated current.
- **Method:** inject common-mode noise per IEC 61000-4-4/-4-6 levels on the encoder cable, scope the BiSS-C clock/data at the master; log CRC errors. Measure MII/EtherCAT timing (setup/hold) at 0, 25, 60 °C board temperature.
- **Pass:** zero CRC errors in 10⁶ frames at rated PWM; worst-case setup/hold margin ≥ 20 % of the spec; EtherCAT frame loss 0 over 1 h; drive derate ladder steps (60/80/90 °C) trip correctly.

## TP-G5-12 EA 9396 lap coupons, hot creep (R-114)
- **Samples:** n = 5 per condition, ASTM D1002 single-lap, adherends prepared per **A38** (same surface prep as the part).
- **Cure:** room-temperature cure + **82 °C post-cure** per R-114.
- **Method:** (1) static lap shear at 23 °C and 80 °C; (2) sustained **≥ 3.3 MPa** shear at **80 °C for 1000 h**, with an extensometer on the joint.
- **Pass:** no rupture in 1000 h; creep displacement ≤ 0.05 mm, flat (secondary) slope at 1000 h; residual 23 °C strength after the creep ≥ 80 % of the control.

## TP-G5-13 DP490 per-lot coupons (P-050)
Per `legs/R031_FIXES.md`: 5 ASTM D1002 coupons per lot at 23 and 60 °C, part-equivalent prep; pass ≥ 80 % of the BOND_SPEC value. A lot that fails is quarantined.

## TP-G5-14 80 °C hot proof (R-112)
- **Samples:** every production bonded joint covered by R-112 (A38 hot bond), plus 1 qualification part per lot.
- **Method:** soak the part at **80 °C** ≥ 1 h, then apply the proof load (1.25 × design, as in PROOF_TEST_hip_lever) for 30 s at temperature.
- **Pass:** no residual set > 0.02 mm, no audible or visible disbond, a tap/ultrasonic check unchanged; the qualification part then goes to rupture and must be ≥ 1.5 × design at 80 °C.
