# RL Arms & Hands R13 (2026-10-21): R-120 deliverables: pad stand-off, CRBH 7013 A roll housing, e stack, clash, mass
Basis: R-120 (12f68a4); ID stand-off layout 00ff254 (`modules/design/pad_r10_standoff.json`), used as given except where Arms owns the interface.
Calcs: `pad_r13.py/.json` (hand), `clash_r13.py/.json` (sim/v3 light model). Image: `R13_standoff_7013.png` (= `media/progress/2026-10-21_arms_R13_standoff_7013.png`).
Tags: [CALC] = computed from geometry here, not measured. [EST] = unsourced. Measured masses come at G5. No 3D-printed parts: all items machined 7075-T6.

R-120 numbers reproduced (R10 core, 15° no mu credit, CRBH 7013 A, dp 85): s0 **2.31 / 2.16 / 2.04** (e0/5/10), Mx **321 N·m**, CSG-25 SF at fault **1.10**.

## 1. Stand-off (P-arms, 7075-T6 billet, machined, one setup for ribs+face)
| feature | dim | source |
|---|---|---|
| face plate | 62 × 62 × 4 (Y 23–27), rear pocketed, 2 mm floor | ID 00ff254 |
| pad interface | 4 × M4 tapped in 8 mm bosses on ±24 mm square; 0.5 mm 7075 tray + R10 core 54.8² × 75.3 unchanged; contact Y 102.3 | ID |
| pad centre | Z −20 below roll axis (±0.1 machined) | R-120 |
| ribs | 2 × 5 thk × 30 wide, Y 0–23, span Z 0 to −20 | ID |
| **roll flange (Arms change)** | **OD 70 / ID 44 × 5** (was OD 60/40 × 4) | R13 |
| **flange fastening (Arms)** | **8 × M4 12.9 on PCD 62 into roll-output hub (M4×8 tapped) + 2 × Ø4 m6 dowels** | R13 |
**Why changed:** ID's ring is narrower than the CRBH 7013 A bore (Ø70), and 6 × M4 on PCD 50 carries 321 N·m + 7 kN shear at 3.30 kN/bolt (SF 1.51 vs 5 kN): too thin. 8 × M4 on PCD 62 gives 2.17 kN/bolt (**SF 2.31**). Friction alone (5.5 kN) won't hold, so dowels take shear.
Ribs (strong axis, hand): 146 MPa vs 335 allowable, SF 2.29. Weak axis (5 mm) and the face-plate pocket go to FEA.

## 2. Roll housing, CRBH 6013 A → 7013 A (Arms geometry; Actuators books the row)
| part | 6013 (old) | 7013 A (R13) |
|---|---|---|
| bearing | 60 × 90 × 13, C0 24.3 kN, 0.33 kg | **70 × 100 × 13, C0 27.7 kN, 0.38 kg** (IKO cat. l.802) |
| seat flange | OD 98 / bore 90 × 15 | **OD 108 / bore Ø100 H7 × 15** |
| output hub | Ø60 / Ø48 × 20 [EST] | **Ø70 g6 / Ø54 × 20**, 8 × M4×8 tapped PCD 62 |
| outer clamp ring | OD 98 / 84 × 3 | OD 108 / 94 × 3 |
Envelope: housing seat flange +10 mm diameter (+5 radial). It's stator on shoulder_P, so it doesn't move with roll. Torso clearance is unchanged: housing inboard edge y 0.232 vs torso 0.17.

## 3. Tolerance stack, e ≤ 5 mm (pad force line vs design point)
| contributor | ± mm |
|---|---|
| bearing seat position (H7) | 0.05 |
| CRBH runout / width centre | 0.05 |
| hub face to bearing plane | 0.10 |
| flange thickness/flatness | 0.05 |
| dowel location (Ø4 m6/H7) | 0.03 |
| rib/face plate position (one setup) | 0.10 |
| tray M4 float (Ø4.5 holes, not doweled) | 0.25 |
| tray lip to core (bond fixture) | 0.50 |
| core cut position/squareness | 0.50 |
| elastic deflection at 7 kN [EST → FEA] | 0.50 |
| **worst case / RSS** | **2.13 / 0.92** |
As built, e ≤ 2.1 mm worst case, so 2.9 mm of the 5 mm budget is left for the impact-centroid shift on the core (FEA brackets this at e 0/5/10). **PASS.** Drawing note: bond the core in a fixture located off the tray tabs.

## 4. Clash (light model, gate ≥ 10 mm; pad + stand-off as solid boxes, pad proud +15 mm/side inherent)
| check | min gap | result |
|---|---|---|
| tuck B (+5/0/0/0) | torso 135, head 290 | ✓ |
| R5 tuck | torso 130 | ✓ |
| abduction roll −15…180 × pitch −180…60 (680 poses): head/neck | 141 / 141 | ✓ (pad never approaches the head) |
| roll 135° soft limit (pitch 0…−90) | head ≥ 171, torso 34 | ✓ |
| overhead pitch ≤ −150 with roll ≥ 170 (34 poses) | torso box **9.4** | **marginal (crude box)**: keep the 135° soft limit; CAD in Job 8 |
| own forearm/hand, elbow fold (4224 poses) | 20.3 | ✓ |
| 7013 housing (OD 100/108) vs pad/stand-off | radial overlap if co-located in x | **OPEN**: the pad x-range (±31) must sit axially outboard of the housing face, ≥ 3 mm [EST]. Light model has no housing x position; CAD check is in Job 8 |
| covers/fairings | no shoulder cover row in `cover_set_v5` (only the pad row) | no clash found; ID owns cover trims for the +15 mm pad and Ø108 flange |
Head sweep: the pad sets **no** head limit. The R7 135° soft limit can be lifted once the CAD (head shell, not the sphere) confirms it in Job 8.

## 5. Mass [CALC] (pair, vs R-120 booking)
| item | R13 calc | booked R-120 |
|---|---|---|
| stand-off 0.072/side (face 0.0194, ribs 0.0177, flange 0.0309, fasteners+dowels 0.004) net of 0.024 boss | **+0.096** | +0.052 |
| housing growth (flange, hub, clamp) | **+0.075** | +0.060 |
| CRBH 7013 A vs 6013 (cited) | +0.100 | +0.100 |
| **total** | **+0.271** | +0.212 → **+0.059 over** |
The overrun comes from the stronger flange (+0.017/side vs ID) and the larger hub. Measured masses at G5.

## FEA re-run: Job 8 add-on (spec in R7_ROUND.md §G; not launched)
