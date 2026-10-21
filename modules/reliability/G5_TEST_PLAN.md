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

## TP-G5-15 Knee venting touch temperature, IP2X and standing drive base (R-143 §2b; rev 4d, P-156; R143_TOUCH_BURN.md)
- **Setup:** D94 knee plate in the L71 pocket with the P-156 thigh fairing: grille 8 × 4.5 mm slots with Al liner, fin-tip baffle (Al tape fin side), inlet z 643–681, outlet z 799–837 routed aft/up (with the outlet shroud if adopted), duct insert, foil under the fairing over the knee twin housing with ≥ 10 mm vented gap. Full robot leg (or a heated rig at plate power 7.2 W duty / 2 × 6.0 W carry, plus the knee housing at its case temperature).
- **Thermocouples** (type T, ≤ 0.13 mm bead, thin epoxy or spring-contact probe; ≤ ±2 K at ≥ 50 °C per ISO 13732-1 measurement guidance), IR camera calibrated against them:
  - **Touch points:** grille centre, grille top and bottom slot webs, grille frame; **inlet** webs and frame; **outlet** webs (centre and the downstream edge), frame and the skin 20 mm downstream; **fairing over the knee housing** (centre, top and bottom slot edges); fairing within 20 mm of each opening.
  - **Drive base (inside the closed fairing):** TC on each drive's heat-sink face / plate base under the drive (2 per knee), fin tip, baffle, pocket air at the outlet, knee housing case.
- **Cases:** at 25 °C and **35 °C** ambient: (1) standing at R-096 duty to steady state (the governing thermal case); (2) walking 0.5–2 m/s at duty; (3) continuous carry until the derate holds; (4) 30 min standstill heat soak after (3); (5) seated/kneeling 10 min (openings partly blocked).
- **IP2X / probe:** IEC 61032 probe B (ø12 mm, 80 mm reach, 30 N) applied to every slot of the grille, inlet, outlet and knee-housing fairing: no contact with any surface > 48 °C or with the baffle, fins or housing. The 50 mm sphere must not enter. Slot widths measured on 5 production parts: ≤ 5.0 mm max (4.5 nominal).
- **Rev 4e additions (outlet shroud):** touch TCs on the shroud outer face (centre, top and upper-side opening edges, the skin 20 mm downstream of the jet) and on the outlet webs (reference, inside). Probe B through the top/side openings: no contact with any surface > 48 °C. **Pass for the shroud zone (no-sustained-contact class): ≤ 48 °C at 35 °C ambient standing hot (target ≤ 43)**, other touch points unchanged. Run once with the dilution slots taped shut (poor-mixing sensitivity). **Cool-down:** after case (4), command the R-146 safe-sit prone fallback (MO = 0) and record the time for every touch point to reach ≤ 43 °C (sets the rescue/handling wait in the handling map).
- **B2 additions (built option):** TCs on the rear shroud outer face (centre, opening edges), louvre edges, **skirt inner face over the plume (centre and edges) plus a check of the skirt-to-shroud gap ≥ 15 mm through hip ROM** and that the foil is present, the W017 label site, and the skin 20/50/80 mm downstream of the plume. Standing hot at 25/35 °C with dilution taped (poor mixing). Drive base ≤ 80 °C (Thermal 70.6, T&R 71.3 at the 1320 mm² notch). Probe B and the sphere on the louvres and the notch. **Hand clearance ≥ 30 mm** from the shroud/plume measured in the stand, walk (arm swing), carry and prone poses. Prone cool-down time to ≤ 43 °C at the shroud and skirt (for the rescue procedure). **Pass: ≤ 48 °C at the shroud and skirt (no-sustained-contact class, valid only with the hand clearance met), ≤ 43 °C at 25 °C ambient.**
- **Rev 5 additions (side exit/hood, superseded by B2):** TCs on the hood outer face, louvre blade edges (top and aft), skin 20/50/80 mm above the hood (plume), the W017 label site, and a dummy hand cover (silicone skin with TC) at the hanging-hand position and in the swing path. Run with dilution slots taped shut (poor mixing). Probe B and the IP2X sphere on the louvres. Arm-at-side hand-to-hood clearance measured in the stand and walk modes. **Pass for rev 5: ≤ 43 °C at every touch point, all cases, both ambients (likely contact);** hand ≥ 30 mm from the hood. If Option B is built: the rear outlet uses the 48 °C class below.
- **Pass:**
  - every touch point ≤ **48 °C** at 35 °C ambient and ≤ **43 °C** at 25 °C ambient, in all cases (the outlet is included; it fails on the current estimate unless fixed);
  - **drive base ≤ 80 °C in case (1) at 35 °C ambient** (Thermal predicts 76.2–78.5, margin 1.5–3.8 K; if the measurement exceeds 78.5, Thermal re-runs the duty limit);
  - derate behaves per R-136 (75 °C start, 50 % at 85, off at 90);
  - IP2X as above.


## TP-G5-16 Chest-pad prone landing (R-146b; R146_PRONE_LANDING.md)
- Setup: full robot at 68.4 kg ±1 %, force plate under the pad zone (≥20 kHz), triaxial accelerometers on the pack rail and the bulkhead (≥10 kHz, CFC1000), high-speed video ≥1000 fps, new certified cartridge (lot plateau 19.5–22.3 kN).
- (a) L1: run the R-146b kneel-to-prone sequence ×20 from the thermal latch. Pass: peak pad force ≤8.8 kN, contact speed ≤0.1 m/s (≥95 %), ≤0.2 m/s worst case, face indentation ≤0.5 mm, MO=0 only after the D94 flags.
- (b) L2: from a held upright kneel, MO=0 tip forward ×3 (new cartridge each), arms passive. Pass: crush ≤50 mm, force ≤22.35 kN, pack-rail accel ≤ the pack rating (provisional 50 g), no structural damage.
- (c) After each L2 run: pack OCV, isolation, BMS log, visual of the cell gap; bulkhead dye-penetrant after the final run.
- Ballast-dummy alternative for (b) before a full robot is risked: a rigid-link dummy with matched mass/CoM/I about the knee.

## TP-G5-17 Pack shock at the fall pulse (R-146; R146_PRONE_LANDING.md §7; Torso c974f54)
- **Item:** flight-standard 20S5P pack (8.75 kg) with cells, holders, BMS, enclosure, rails and the rail stop shoulder, mounted on flight-standard rails on a rigid fixture. 100 % SOC (worst), 25 °C.
- **Pulse:** half-sine **104 g peak, 20 ms, Δv ≈ 5.7 m/s** (drop table or pneumatic shock machine, tolerance per IEC 60068-2-27). **3 axes, both directions (6 orientations), 3 shocks each**, plus the forward axis (pad direction) at +15 % (120 g) as a margin shot on a separate sample.
- **Instrumentation:** control accel on the table plus response accels on the pack rail and an internal cell module (CFC 1000); BMS log; cell-group voltages; video.
- **Pass:**
  - **no venting, leak, smoke, fire or rupture** (observe 1 h after the shock)
  - **OCV change ≤ 0.1 % and per-group voltage unchanged within ±5 mV; AC impedance (1 kHz) per group unchanged within ±5 %**
  - **no mechanical damage:** no cracked holders, no cell displacement into the ≥ 5 mm gap, no rail/latch/stop yield, fasteners torque-checked
  - **BMS OK:** no fault latched, isolation ≥ spec, comms intact
  - then a full charge/discharge cycle at 1C with capacity within 2 % and no thermal anomaly
- **Until it passes, R-146 L2 (tip from kneel) stays CONDITIONAL.**
