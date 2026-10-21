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
