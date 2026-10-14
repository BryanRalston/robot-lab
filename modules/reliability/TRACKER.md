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
