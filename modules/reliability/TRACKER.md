# Reliability tracker — test plans + open actions (R1, 2026-10-14)
Status from RULINGS.md (latest mention), DECISIONS files and test-plan files. "open" unless a closing ruling was found. P1 = safety/T8, P2 = gate, P3 = mass/docs.

| ID | Source | Description | Owner | Status | Priority |
|---|---|---|---|---|---|
| A4/O13 | RULINGS.md; actuators/results/DECISIONS.md D58 | hip lever converged FEA ≥ SF 1.5 (G2 cap+flanks) | actuators → GB (bryan PC) | open | P1 |
| A7 | RULINGS.md | clamp proof-load 13.1 kN, witness marks, DP490 datasheet | legs | open (verify) | P1 |
| A8 | RULINGS.md R-022 | GE 12 C life → wear part 5 250 h | actuators | closed (wear part) | P2 |
| A9 | RULINGS.md | JST-GH mass; O20a/O20b plans | actuators | plans written; tests not run | P2 |
| A10/A29 | RULINGS.md | cover panel layout + fall wall/rib check | arbiter/covers | open | P2 |
| A11/A18/A24/A31 | RULINGS.md | brain parts, MCU, cold plate, ZED link, lid | arbiter/brain | open | P3 |
| A12 | RULINGS.md | itemise "all other lines" | arbiter | open (rd 13) | P3 |
| A14 | RULINGS.md R-023 | ankle_roll stop + push rerun + panels | legs | closed on paper (CAD in G2) | P2 |
| A15 | RULINGS.md R-023/24 | GB structure r2: convergence, clamp h1.5, tongue bore, foot collar, tube doubler | legs → GB (bryan PC) | open | P1 |
| A16 | RULINGS.md | tongue fault SF 1.48 → dowel or converged margin | legs | open | P1 |
| A17 | RULINGS.md | clevis pad vs knee tongue clearance; arm clocking | legs | open | P2 |
| A19 | RULINGS.md | covers CAD panel layout | arbiter | open | P3 |
| A20 | RULINGS.md R-024 | foot-collar fallback mass | legs | open | P2 |
| A21 | RULINGS.md | hip yaw/roll stop brackets sized | legs | open | P1 |
| A22 | RULINGS.md | QA1 MGF12T rating or bench plan | actuators | open | P2 |
| A23/A25/A26/A28 | RULINGS.md | head part citations, harness reconcile, sim neck, obsolete cap | robot lab/head/actuators/legs | open | P3 (A28 P2) |
| A27 | RULINGS.md R-027 | head filter | head | closed | — |
| A30 | RULINGS.md | cover cost sheet | robot lab | check R-029 | P3 |
| A32 | RULINGS.md | 7075 palm CAD | hands | open | P3 |
| O4 | TARGETS.md G3 | screw L10 at new levers | actuators | open | P2 |
| O23 | TARGETS.md G3 | GE eye wear test | actuators | open | P2 |
| TP-1 | actuators/results/BENCH_TEST_PLAN.md | one-leg actuator bench (thermal, 235 W pass line) | actuators | planned (G5) | P2 |
| TP-2 | actuators/results/PROOF_TEST_hip_lever.md | 100 % proof 5680 N/pin + qual-to-rupture | actuators | on hold until O13 | P1 |
| TP-3 | actuators/results/O20_TEST_PLANS.md O20a | power-core flex cycle test | electronics/actuators | planned | P2 |
| TP-4 | actuators/results/O20_TEST_PLANS.md O20b | EtherCAT cable SI + flex | electronics | planned | P2 |
| TP-5 | legs/BOND_SPEC.md | DP490 bond process / coupons | legs | spec only | P1 |
| G2/G3/G5 | TARGETS.md | CAD zero-clash / converged FEA / bench gates | all | NOT MET | P1 |
| RT-1 (new) | R1_FEA_REVIEW.md §1 | add walk-load fatigue criterion to hip lever G2 | actuators | new | P1 |
| RT-2 (new) | R1_FEA_REVIEW.md §2–3 | redo clevis/clamp Goodman with Se 87 MPa | legs | new | P1 |
| RT-3 (new) | R1_FEA_REVIEW.md §8 | knee twin-housing centre web stress | actuators | new | P2 |
| RT-4 (new) | R1_FMEA.md F07/F12 | battery abuse/fall test plan; HIL fall/push tests | torso/controls | new (unstaffed) | P1 |
| RT-5 (new) | R1_FMEA.md F16 | lap-shear coupons per lot + per-leg proof | legs/materials | new | P1 |

Status caveat: the box was overloaded during R1, so closure status for A-items was read by hand, not scripted; owners should correct any row.

## R2 additions (2026-10-21)
| ID | Source | Description | Owner | Status | Priority |
|---|---|---|---|---|---|
| P-046 | RULINGS.md R-031; legs/R031_FIXES.md | clevis cheek 17 / R8, clamp root 28: Goodman ≥ 1.5 at Se 87 | legs → job 9 b1/b2 | hand checks landed (1.52 / 1.50, questionable); FEA pending | P1 |
| P-047 | same | tube walls 1.6 mm (7050 femur) outside the sleeve, SF ≥ 1.5 | legs → job 9 b3 | hand 1.58 / 1.52; FEA pending | P1 |
| P-048 | same | tongue ø6 dowel + bore-opening check | legs → job 9 b4 | open | P1 |
| P-049 | same | foot collar OD R2 + taper, fretting interface | legs → job 9 b5 | open | P2 |
| P-050 | same | DP490 per-lot coupons | legs/materials | plan confirmed → TP-G5-13 | P1 |
| JOB9-b | reliability/JOB9_SPEC.md | A15 structure r2 with P-046…P-049 | T&R on the bryan PC | spec ready | P1 |
| JOB9-c | reliability/JOB9_SPEC.md | knee twin-housing centre web at 3.6 kN/screw | T&R on the bryan PC | spec ready, pending Actuators rev C confirmation | P2 |
| J1-Mx | design/fea/job1_pad_r8/REPORT.md | roll torque 566–773 N·m vs CSG-25 369 N·m | arms | open (R11/R13) | P1 |
| J10-clip | reliability/R2_VERIFY.md | clip normalized obs in job 10 train/eval | controls | recommended | P2 |
| TP-G5-01 | R-042 | EPP80 40 mm pad drop tower, 220 J, 1/10/100 drops, 0 and 40 °C | arms/materials | planned (G5) | P1 |
| TP-G5-02 | A37 | G10 sleeve creep 100 h, 34 MPa, 100 °C | materials | planned | P1 |
| TP-G5-03 | design/R069_TESTS.md T-B2 | PA12 knee cap kneel-fall | design/materials | planned | P2 |
| TP-G5-04 | T-F1 | TPU bellows flex 10⁶ cycles | design/materials | planned | P2 |
| TP-G5-05 | T-G | snap-hook retention / fall | design | planned | P2 |
| TP-G5-06 | R-076 | MR30 vibration + pull retention | electronics | planned | P2 |
| TP-G5-07 | R-079 | walking convection h, heated rev B knee, skin TCs, standoff ΔT | thermal/legs | planned | P1 |
| TP-G5-08 | R-081 | sole pad wear + impact | legs | planned | P2 |
| TP-G5-09 | R-085 | grip with encoder-cap TC | arms | planned | P2 |
| TP-G5-10 | R-077 | hot always-on load ≤ 2.4 W | electronics | planned | P2 |
| TP-G5-11 | T-029 | BiSS-C CM noise + MII timing | electronics | planned | P2 |
| TP-G5-12 | R-114 | EA 9396 lap coupons, A38 prep, 82 °C post-cure, 1000 h at 80 °C ≥ 3.3 MPa | materials | planned | P1 |
| TP-G5-14 | R-112 | 80 °C hot proof | materials/legs | planned | P1 |
| R143-TB | RULINGS.md R-143 §2b; reliability/R143_TOUCH_BURN.md rev 4d; Thermal ec7b49d/eef2728; ID P-156 | rev 4d recheck: grille 37–38.5 PASS, inlet 36 PASS, knee-housing fairing 40.6–41.5 PASS (slots must be ≤ 5 mm), **outlet webs 54–61 °C FAIL** → outlet shroud/relocation; housing low-ε vs fairing-foil conflict; standing drive base margin 1.5–3.8 K | Thermal + ID (outlet, slots, ε conflict), T&R (G5) | outlet open; rest conditional pass | P1 |
| TP-G5-15 | G5_TEST_PLAN.md | grille/fairing touch-point thermocouples, duty/carry/standstill/seated, probe B push | T&R/Thermal | planned | P1 |
| R143-OUT | R143_TOUCH_BURN.md rev 4e; Thermal 218a541; ID P-156 rev 4e | outlet shroud: no-sustained-contact class CONFIRMED at 48 °C (target 43) IF dilution slots + foil inner face (ID drawing lacks both), up/side openings ≤ 5 mm (probe B reaches 74–90 °C webs as drawn), handling map with no-hold zone + hot label | ID (drawing), Thermal, ID+Controls (handling map) | conditional; open | P1 |
| HANDLING-MAP | design/HANDLING_MAP.md draft (ID) | N1 z 755–845 covers the hood; its 48 °C no-sustained-contact class is wrong for rev 5 (hanging hand in the zone, 43 °C applies); plume above 845 and the label at z 830 sit in the jet; Controls to co-publish | ID + Controls | draft – needs fix | P1 |
| R146-PRONE | R146_PRONE_LANDING.md §1–9; r146_prone.py, r146_fc86721.json; TP-G5-16/17 | fc86721 [EST]: L1 CONDITIONAL (1.74 kN elastic, no crush; 0.30 m/s fails the 0.10 D94 gate, WBC pending); L2 368 J, crush 19–20/70 mm, pack 24–82 g, Δv 4.0, rails ≤7.1 kN PASS, head 10.4 spare → CONDITIONAL until TP-G5-17; L3 527 J 27–29/70 mm, head marginal 1.7 mm; T-031 gate head FAIL (ID/Torso); rescue proc e6dd4b0 accept with 7 changes | T&R / Controls / Torso / ID | conditional | P1 |
| R143-REV5 | R143_TOUCH_BURN.md rev 5; r143_rev5.py; ID a065aa3/0b3fab9 | outboard side exit + hood: IP2X PASS; vs 43 °C (likely contact: the hanging hand interferes 22 mm with the hood, swing crosses it): hood face PASS good mixing / FAIL poor, louvres FAIL, plume skin FAIL, robot hand in the jet FAIL, housing fairing slots PASS (41.5); REJECT as drawn, recommend Option B rear outlet via the L60 cut-out (Legs structural check, Thermal re-run) | ID / Legs / Thermal | rejected – B recommended | P1 |
| TP-G5-17 | G5_TEST_PLAN.md | pack shock 104 g / 20 ms / 5.7 m/s, 3 axes, no vent / OCV & impedance / no damage / BMS OK | T&R / Torso | planned | P1 |
| RESCUE-PROC | design/HANDLING_MAP.md e6dd4b0 | battery check first, B2 hot zone + gloves, 3-person lift, knee pinch, cartridge replacement spec, pack checks before re-enable, MO_OFF+5 s | Controls / ID | changes requested | P1 |
| L60-FALL | L60_FALL_LOAD.md rev A+B; Legs 916c57f | rev B: 7267 N is the PAIR peak (rev A doubled), DF 2.0 → rotor inertia (D97 ≤5.18 kN pair) + structural DLF 1.05 (t_r ≈51 ms vs T_n 7–10 ms) → L60 bracket 13.1 kN (was 29). Tube moment = stop + motor in parallel (stop doesn't bypass the tubes): governing 1.23 kN·m → tibia 45×1.5 SF 0.69 / femur 0.86 (393 fall) → tibia 2.3 / femur 1.8 mm, or Controls knee torque ≤50 N·m at the stop → 0.92 kN·m → tibia 1.7 mm, femur OK; stop energy ≤62.7 J (bottoming ~97 J) | Legs / Controls / Actuators | DECIDED (Robot Lab 10:01): Controls knee cap ≤50 N·m within 10° of the stop + tibia 1.7 mm → 0.92 kN·m, tibia SF ≈1.03, femur 1.14 | P1 |
| R143-B2 | R143_TOUCH_BURN.md B2; Thermal a32d341 | rear outlet: shroud 40–42 PASS, skirt foil + 15 mm gap required, 48 °C class valid with hand clearance ≥ 63 mm (≥ 30 required), notch 1320 mm² → Tb 71.3 PASS; N1 must move to the rear | Thermal / ID / Legs / Controls | conditional pass | P1 |
| B2-HAND-KEEPOUT | R143_TOUCH_BURN.md B2 hand-clearance spec; Controls 6d4c8fb | 63 mm withdrawn (bent leg → −65 mm). Spec: (a) plume/louvres keep-out 30 mm + 60 mm plume, transit ≤0.5 s/≤20 %, zero in sustained poses; (b) face 40–42 °C contact thermally OK (re-check TP-G5-15); (c) mechanical walk/carry/stand 15/10/5 mm, crouch/kneel 20/15/10 mm, shroud survives 100 N strike; source fix: shroud ≤ y150, aft-only openings, chamfer | Controls / ID / Thermal | spec issued | P1 |
| HIP-PINCH | R_HIP_PINCH.md; r_hip_pinch_check.py; TP-G5-18; ID df1e9e3 | hem↔panel FAIL (24.4 in ROM, 21.5 overtravel, ~19.5 w/ tol vs 25 finger; hand 100 FAIL w/o compliant edge); panel↔thigh ≤1 fixed PASS; L↔R FAIL (100 in-ROM bilateral pairs incl. yaw 22) → Controls keep-out ≥28 mm (warn 35/trip 28) + compliant edges ≤140 N for motors-off; hem R→~146.5; panel↔shank/floor OPEN; N7 wording wrong, add N8, H2 ≥100 mm above hem | ID / Controls / Legs | fail – fixes specified | P1 |
| CHEST-LC1 | CHEST_DESIGN_LOAD.md; Torso ff59d8f | LC1 redefined: option (b) corrected: limit 29.0 kN (22.3 lot top × 1.30 rate), ultimate 43.5 kN; LC1a normal on the land, LC1b ±25 mm offset, LC1c 25° 21.2 kN + 9.9 kN; pass σ ≤ fall allowable at 29 (no extra SF), no rupture/buckling ≥1.0 at 43.5, k_land ≥5.3 MN/m (δ ≤5.5 mm), delete the 0.05 mm gate; bottoming not credible (≥1.47 kJ); Job 3 still FAILS (SF ~0.28) → bulkhead redesign; dynamic coupon to verify the rate factor | Torso / Materials | decision issued | P1 |
| HIP-PINCH-8b | R_HIP_PINCH.md rev 8b; r_hip_pinch_check_8b.py; ID acb9bd5 | hem R144 32.6/28.3/26.3 PASS (J-channel −1 mm to confirm); L↔R full-ROM asym 1/6000 <3 mm, worst 0.77 at extension+yaw (ID swept pitch −10…45 only) → keep-out ≥28 mm rigid-to-rigid stays; foam stress basis wrong (60 kPa is the ~25 % value; 300–500 at 80 %): finger limp 45–52 N PASS, hand limp ≈165 N vs 140 marginal FAIL → measure / 40 mm foam / standoff; XLPE ≥90 °C near the plume, replace at >10 % loss or annually; N7/N8/H2 accept (2 wording fixes); panel↔shank/floor OPEN | ID / Controls / Legs | conditional | P1 |
| SIDE-FALL | SIDE_FALL_LOAD.md; TP-G5-19 | frontal tube moment is capped by the end joints: S1 foot planted 380 N·m (hip roll 204 + rotor ≤292 × DLF 1.3) → tibia 45×1.7 SF 2.50, femur 2.78 PASS if there is no rigid hip-roll stop; S2c knee-first with the foot moving: 530–1060 N·m → tibia SF 1.79–0.89 CONDITIONAL (lateral knee pad or swing-leg tuck; sim velocities needed); missing: hip-roll stop, side-fall sim velocities, lateral knee contact | Legs / Controls / Actuators | conditional | P1 |
