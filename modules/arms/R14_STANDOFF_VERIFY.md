# RL Arms & Hands R14 (2026-10-21): verification of ID stand-off R11 (ec12542) after the Job 8 add-on FAIL (e02c34b, bc6ad91)
Calcs: `pad_r14.py/.json`. CAD: `cad/r14/r14_cad.py` (CadQuery 2.8 runs on the RL box) → `standoff_r14.step`, `housing_7013_r14.step`, `pad_envelope_r14.step`, `r14_cad.json`. Fasteners: `fastener_bom.py` → `FASTENER_BOM.csv`, `fastener_bom.json`. Image: `R14_standoff_verify.png`.
Gate: SF ≥ 1.5 vs 7075-T6 yield 503. Tags: [CALC] = computed here (not measured); [EST] = unsourced. Measured masses come at G5. No 3D printing.

## BLOCKER: the R-120 / ID geometry intersects the roll bearing
- The roll axis is **X** in sim/v3 (`l_shoulder_roll` axis 1 0 0), in R-120 (Mx = Fn·Z + Fs·Y), in s0 (e = axial offset from the bearing plane) and in the FEA frame.
- ID's CAD draws the CRBH 7013 A and the OD108 flange **coaxial with Y**. That's the only reason no clash shows.
- With the 7013 A coaxial with X at the bearing plane (r 35–50 bearing, r ≤ 54 seat flange, x ±7.5), the stand-off and pad (Y 0–102, Z −51…+11, |X| ≤ 31) overlap it. CadQuery booleans: **stand-off ∩ housing 2.16 cm³; pad ∩ housing 12.38 cm³**.
- e ≤ 5 can't be met with ≥ 3 mm clearance. Clearing the housing axially needs e ≈ 40.5 mm, which drops s0 to **1.5** (fail).
- **My R13 error:** R13 reported "housing axial gap OPEN, assumed outboard". That assumption contradicts e ≤ 5. R-121's "clash passes" therefore rests on a wrong premise.

**Buildable options (pad outside the housing at the bearing plane, wrap carrier on the roll output, 3 mm gap; for the Arbiter):**
| option | contact Y | s0 e0 / e5 | Mx N·m | CSG-25 SF (fault) | pad extra proud | mass [EST] |
|---|---|---|---|---|---|---|
| W2 wrap carrier, 7013, pad on axis (Z0) | 138.8 | 2.06 / 1.94 | 251 | 1.4 | +36.5 | carrier ~+0.14 pair [EST] |
| W3 wrap carrier, 8016, Z0 | 144.8 | 3.39 / 3.22 | 262 | 1.34 | +42.5 | +0.72 bearing (cited) + housing ~+0.2 + carrier ~+0.14 [EST] (= R11 B, rejected for mass) |
| W1 wrap carrier, 7013, Z-20 | 138.8 | 2.05 / 1.93 | 387 | 0.91 | +36.5 | — |
- No option is cheap:
  - **W2** (7013, pad on the roll axis) passes the gear but misses s0 at e5 by 3% (1.94); it would pass at e ≤ 3 (≈ 1.99–2.0, marginal). It adds +36 mm proud per side, against the provisional +15 accepted in R-120.
  - **W3** passes everything but is R11 option B (+~1.1 kg, rejected).
  - **W1** fails the gear.
- Other levers outside Arms: ID shortens the core at a higher plateau (R-119 energy), or μ measured (G5), or a T2/mass ruling.
- **The Arbiter must rule before any stand-off is booked or Job 8b runs.**

## Verification of ID R11 as a part (it stands if a valid placement is found)
| item | value | SF / result |
|---|---|---|
| box 44×44×2.5 (Z −15) | Arms hand 62.8 MPa ×2.86 = 180; ID 215 governs | **2.34** vs yield, 1.57 vs 337 FEA limit: PASS |
| plate 62×62×4 solid | 149 MPa (ID) | 3.38: PASS |
| flange OD70 ligament, M4 Ø4.5 / dowel Ø6 at PCD62 | outer **1.75 / 1.0 mm** (0.89 d / 0.67 d) | **FAIL** (≥ 1.5 d [EST]) |
| fix: flange + hub shoulder **OD76** (= 7013 inner-ring shoulder 76), dowels to **PCD57** between bolts | M4 4.75 mm (1.56 d); dowel 3.5 / 6.5 mm; τ 249 MPa | dowel SF **2.41**, bearing SF ≥ 2.2: PASS |
| bolt access | 2–3 of 8 M4 heads sit under the closed box / solid plate | **FAIL** → 3 × Ø8 wrench holes through the plate (tray covers them; pad fitted after) |
| box root on ring | box walls X ±22 coincide with the ring bore Ø44, so the root lands on the ring over only part of the perimeter. The FE fixed root is non-conservative. | fix: ring bore **Ø36** under the box |
| machinability | 7075-T6 billet 76 × 88 × 32. Two 3-axis setups; box 39² pocketed through the bore with a Ø8 end mill (R4 inner corners, L/D 3.5); R3 fillets. | OK |
| e stack with 0.69 mm deflection | worst **2.32**, RSS 1.03 mm vs 5 | PASS (moot until the blocker is resolved) |
| ≥ 3 mm to OD108 (in ID's own frame) | stand-off flange y −5..0 sits against the housing flange face y −5 | **0 mm: FAIL** |
| cover window 68×68 R6, relief OD114 (COVER_TRIMS_R120) | box margins 12/7/17 mm; plate 3 mm/side; OD114 vs 108: 3 mm radial | PASS (ID frame) |
| head shell, torso cover, abduction ROM | no CAD exists | not run; R13 light-model results stand (head ≥ 141 mm; overhead roll ≥ 170 at 9.4 mm, so keep the 135° soft limit) |

**Interface changes ID must adopt** (Arms owns the roll interface):
- flange OD 70 → **76**
- ring bore **Ø36**
- dowels **2 × Ø6 m6 on PCD57** (not PCD62)
- **3 × Ø8 access holes** in the plate
- the housing modelled coaxial with **X**
- 8 × M4 12.9 PCD62 is **kept**

## Mass [CALC]
- Stand-off with the R14 fixes, from the CadQuery model: 0.1178 kg + bosses/fasteners → **0.124 kg/side**, vs R13 0.072 → **+0.103 kg pair vs R-121 (+0.271 → 0.374)**.
- This is an addition > 0.005, so the R-066 freeze applies and it needs a ruling. **It is not booked**, because the placement is invalid (the blocker above).

## Fastener BOM (Robot Lab request): `FASTENER_BOM.csv`
- Arm-structure fasteners only. Actuator-unit internals are in Actuators `FASTENER_BOM.md`; pad tray M4 is in ID `FASTENERS_BOM.json`. ID also lists the stand-off flange M4 and dowels, which are Arms-owned: count them here only and ID should drop them.
- **290 pcs/robot, steel ≈ 0.500 kg** [CALC/EST]. **Non-structural (Ti candidates): 140 pcs, 51.6 g steel → 29.1 g Ti64 (−22.5 g)**. Structural parts stay 12.9 steel.
- Thermal must accept Ti on the flexor end-cap clamps.
- Flag: most counts are [EST]. The ~0.5 kg arm fastener mass isn't visibly booked in the arm rows; it needs checking at the Arbiter regen.

## R-123 confirmation items (Robot Lab)
| item | Arms finding |
|---|---|
| one-piece vs bolted | **One-piece machined 7075-T6, confirmed.** A bolted box/plate would put a joint at the highest-moment section. Condition: 3 × Ø8 plate access holes, because 2–3 flange M4 heads are otherwise unreachable. |
| R3 root fillets | **Confirmed as a minimum.** Box SF 2.34 uses ID's ×2.86 FE calibration, which already contains the root concentration. The inside corners come out R4 with a Ø8 cutter. |
| Ø6 m6 dowels, ring ligament on PCD62 | **Not confirmed at PCD62:** the Ø6 outer ligament is 1.0 mm (0.67 d) and the M4 ligament 1.75 mm on OD70. **Confirmed with the fix:** OD76 flange, dowels on PCD57 (SF 2.41), M4 kept on PCD62. |
| e ≤ 5 stack incl. 0.69 mm | worst 2.32 / RSS 1.03 mm: **PASS** |
| clash with the OD108 housing flange | **FAIL.** With the real housing (coaxial with the roll axis X; `cad/r14/housing_7013_real_coaxX.stl` replaces ID's Y-axis placeholder in the same frame), the stand-off cuts 2.16 cm³ and the pad 12.38 cm³ of the bearing/flange. In ID's frame the axial gap is 0 mm. |
| real housing for the ID CAD | supplied as `cad/r14/housing_7013_real_coaxX.stl` / `.step` (Arms dir; ID's files are not edited) |

**Fastener booked vs counted (arms):**
- No explicit arm-structure fastener line exists in CONTRACTS or the Arms rows, so booked = 0 [the §3 0.80 kg/side structure lump is unitemised].
- Counted 0.500 kg/robot [CALC/EST], so the delta is **up to +0.50 kg** if the lump excludes hardware. Arbiter to confirm at the regen.
- Waist: **the Arms BOM does not touch the waist** (waist units are in the Actuators BOM).

**Verdict for FEA routing: NOT CONFIRMED.** The part design is OK with the R14 fixes, but its placement intersects the CRBH 7013 A. Job 8b waits for an Arbiter ruling on placement (W2 / W3 / other).
