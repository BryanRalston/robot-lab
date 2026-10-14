# A37 rev B: hip_pitch motor-to-collar thermal break (RL Materials, 2026-10-14)
**Rev B replaces rev A** (G10, f7d4230). RL Thermal (6cf74d2) requires a total thermal resistance R_break ≥ 20 K/W, counting every path in parallel. Rev A's full-face washers sat in parallel with the pin path, which gave about 4.6 K/W, so **rev A is withdrawn**. Data is in `MATERIALS_DB.md` (PEI1000). [EST] marks an estimate. Numbering clash: R-030 calls this P-027, but P-027 is already the Arms wrist item. The Arbiter should renumber.

## Basis
- Loads: 4 542 N per body when walking (clamp_review.py), 6 550 N per body at fault/proof (BOND_SPEC §5).
- Case temperature: checked at 98 °C, the worst case.
- Geometry: Ø12 pin through 2 tines, 8 mm each.
- **The axial load on the eye is unknown (Legs L4).**

## PEI Ultem 1000 (ULTEM_PP, ULTEM_PL)
- Compressive strength 152 MPa (10 % deformation), compressive modulus 3.31 GPa, shear strength 103 MPa.
- Thermal: k 0.12 W/m·K, CTE 56 µm/m·K, Tg 215 °C.
- Creep: SABIC publishes only tensile creep curves, up to 120 h, at 80 °C/41 MPa and 121 °C/14–28 MPa. There is no compressive creep data at 98 °C.
- **Rule used:** sustained or cyclic stress ≤ 28 MPa (the highest level SABIC characterised at 121 °C); short fault stress ≤ 76 MPa (0.5 × 152 [EST]). Confirm both with a G5 creep test.

## Option A (recommended): PEI tine sleeve OD20/ID12 × 8 mm + 2 mm flange with 15 % contact lands
- **Pin bearing on the sleeve bore** (96 mm² per tine):
  - walking 23.7 MPa, within the 28 MPa creep rule;
  - fault 34.1 MPa, **SF 2.2 hot** (4.5 at room temperature).
- **4 mm wall:** bearing on the 7075 at OD20 is 20.5 MPa. OK.
- **CTE:** PEI grows about 48 µm more than the 7075 bore on diameter from 25 to 98 °C. Use a line-to-line/slip fit with a DP490 film; no press fit.
- **Lands** (15 % of the OD20/ID12 face = 30 mm² per face):
  - capacity: 0.84 kN sustained, 2.3 kN fault;
  - if the axial load is ≤ 10 % of radial, SF is 1.9 sustained / 3.5 fault. **This depends on L4.**
  - Use 3 × 120° pads, a ≥ 0.3 mm air gap elsewhere, and a ±0.05 mm land tolerance.
  - PEI sliding on the steel inner-ring face has no wear data; bench-test it in G5.
- **Mass for 8 sleeves:**
  - PEI +20.9 g;
  - bore growing from 12 to 20 mm removes 7075, −36.2 g;
  - tines widened +8 mm, +34.5 g [EST];
  - rev A washers dropped, −2 g;
  - **net ≈ +17 g [EST].**

## Option B (not recommended): insulated bearing outer ring, PEI 22/26 × 7 mm
- Bearing on one sleeve (154 mm²) is 29.5 MPa walking, **above the 28 MPa creep rule**, and 42.5 MPa at fault (SF 1.8).
- The 2 mm polymer seat would let the spherical plain bearing's outer ring ovalise, so SKF liner-life data no longer applies.
- Thermal resistance ≈ 19 K/W, which misses 20.
- **Ceramic coating:** 0.2–0.3 mm gives < 1 K/W. Rejected.
- Mass ≈ +21 g [EST].

## Lever-cheek bolts (if bolted, L1): ≥ 60 K/W each
- A PEI washer in the preload path would see 10.4 kN on 81 mm² = 128 MPa. It would creep and lose preload. **Not allowed.**
- **Fix:** a Ti-6Al-4V compression limiter OD8.5/ID6.4 carries the preload (433 MPa vs 910 MPa yield, SF 2.1).
  - Each mm of length adds 6.1 K/W, so it needs L ≥ 10 mm.
  - PEI is used only as an unloaded spacer beside it, with a ≥ 0.3 mm air gap at the faces.
  - ≈ +1 g per bolt [EST].

## Recommendation
**Option A.**
- Margins: SF 2.2 on pin bearing at fault/98 °C; walking stress within the creep rule; land SF 1.9/3.5 subject to L4.
- Mass ≈ +17 g for both legs, plus ≈ 1 g per cheek bolt [EST].
- Gates: Legs FEA of the Ø20 tine; G5 PEI compressive creep at 25 MPa/100 °C for 100 h; land wear; J-T1.

## Asks for Legs (A38)
- **L1:** Are the cheeks bolted to the collar? Bolt count and size?
- **L2:** Recheck the Ø20 tine bore: edge distance, the +8 mm tine clearance over the full hip ROM, and FEA at 6.55 kN per body.
- **L3:** Pin retention with the flanged sleeve, and flange clearance to the GE 12 E inner ring.
- **L4:** Axial load on the eye at walking and at fault.

---
# Rev C (2026-10-14): Legs A38 reply (985200d) accepted with one correction
- **L1, parallel path:** the hip lever cheeks bolt to the hip-roll output bracket (pelvis side), not to the collar.
  - **The cheek Ti limiters are dropped (0 g).** The limiter rule still applies to any future bolt from the body/motor to the clamp arm or collar.
  - **Open for Thermal:** the rod → lever-end eye → lever pin → hip lever → needles → ø35 shaft → femur path is unbroken metal. Legs estimates ≈ 40 K/W, which in parallel with ≥ 20 K/W gives ≈ 13 K/W total. Its heat source is screw/nut friction, not the motor case. Thermal must decide whether it counts against the 20 K/W.
  - Harness/encoder P-clips that land on the thigh must be polymer or PEI-lined (note for Electronics).
- **Flange pads vs the GE 12 C, cited from the SKF product page (GE 12 C):**
  - Inner-ring raceway (sphere) **dk = 18 mm**; B 10 / C 7; tilt 10°.
  - **Shaft abutment diameter d_a = 13.5 min / 15 max mm.**
  - dk is the sphere diameter, not the flat side-face diameter. SKF's shaft abutment limit is **d_a ≤ 15 mm**. **Correction: the pads must sit within ø12.6–15** (bore chamfer r1 0.3), not ø12–17.
  - Annulus ø12.6–15 is 52 mm². **3 × 120° pads totalling 30 mm² (58 %) still fit.** Above ø15 the pad could touch the sphere or the outer ring at tilt.
- **Pad stress (30 mm², per the rule ≤ 28 MPa sustained / ≤ 76 MPa fault):**
  - Walking lateral ≈ 20 N: 0.7 MPa.
  - Misalignment friction 0.33 kN: 11 MPa (transient).
  - **Combined fault 0.82 kN: 27.3 MPa.** SF 2.8 vs 76, and 5.6 vs PEI compressive 152 MPa (MIFPEI/ULTEM). This **confirms the Legs SF ≥ 2.5**.
  - The sustained case is below 28 MPa even if the full 0.82 kN were sustained.
  - Caveat: if 2.3 kN ever reaches the pads alone, that is 77 MPa, which exceeds the 76 fault limit. Keep the pads at **≥ 30 mm² and preferably 36 mm²** (2.3 kN → 64 MPa, SF 1.2). The G5 bench test must confirm the 0.82 kN combined bound.
- **Pin retention on PEI only:** the head/ring carries only the axial ≤ 0.82 kN, with 0.3 mm play and **no clamp preload**.
  - On the sleeve end (≈ ø12–16 contact, ≈ 88 mm²) that is ≤ 9.3 MPa fault, and ≈ 0 sustained.
  - Creep is OK because there is no preload to relax. **Rule: the retaining ring must not be shimmed to zero play** (that would create creep preload). A 1 mm PEI washer is also OK.
  - Keep the ≥ 0.3 mm air gap to 7075.
- **Tines e20 rounded:** a Legs item, accepted as is.
- **Mass: net +10.6 g robot, accepted** (+0.011 vs the +0.017 booked, 0.006 to return to reserve).

---
# Rev D (2026-10-14): Thermal A38 (bee2448). The rod path counts (55–60 K/W, total ≈ 15 K/W, FAIL)
**Material:** PEI Ultem 1000 is confirmed for both items, on the same basis as rev B (MIFPEI/ULTEM_PP/ULTEM_PL).
- Rules: ≤ 28 MPa sustained, ≤ 76 MPa fault at ≈ 98 °C, G5 creep test.
- k ≈ 0.22 W/m·K.

## Item 1: lever-end GE12 eye, PEI sleeve 20/12 with flange lands, ≥ 0.3 mm face air gap
- **Load:** the RV12 screw is a two-force member with spherical eyes at both ends (Legs A38 L4). The lever-end pin carries the **same axial screw force as the clamp eye: 4 542 N walking, 6 550 N fault per body** (clamp_review.py / BOND_SPEC §5).
- **Bearing on PEI** (pin ø12, projected area = 12 × total PEI length in the lever cheeks):
  - With 2 × 8 mm (as at the tines): 192 mm² → **23.7 MPa walking (≤ 28 OK), 34.1 MPa fault (SF 2.2 vs 76)**.
  - **Requirement: total cheek/eye PEI bearing length ≥ 16 mm.**
  - At 2 × 6 mm it would be 31.5 MPa walking, which **fails the creep rule**. Then use OD 20 with longer bosses, or an ID 14 pin.
- Outer bearing on 7075 at ø20 × 16: 14.2 MPa walking, trivial.
- **Flange lands:** same rule as rev C. Pads within the SKF shaft abutment d_a ≤ 15 (ø12.6–15), ≥ 30 mm² (36 preferred), axial ≤ 0.82 kN → 27 MPa. The retaining ring must not be shimmed to zero play.
- **Mass [EST]:** 2 sleeves × 2.6 g (rev B 20.9 g / 8) − 7075 removed (ø12→20 bore, 16 mm) 0.9 g = **+4.3 g per lever eye**. Thermal's estimate was +3 g.
  - **One hip lever eye per leg → +8.6 g robot.**
  - Legs: if the knee lever eye also has an unbroken path to the femur bond, add it too.
- The alternative (a liner on the TLA3520 shaft seat) is **rejected**. It sits in the needle load path and creep there would cost bearing preload.

## Item 2: tine sleeve OD 22 / ID 12 (5 mm wall), tine bore ø22
- Pin bearing on PEI is unchanged (ID 12, 16 mm): **23.7 / 34.1 MPa**, SF 2.2 at fault, walking within 28.
- PEI wall 5 mm: hoop/compression across the wall is lower than with the 4 mm wall (the load spreads to ø22). Outer bearing on 7075 is 4 542 / (22 × 16) = **12.9 MPa** walking, 18.6 MPa fault.
- Lands as in rev C, unchanged.
- **Sleeve mass:** 20.9 × (22² − 12²)/(20² − 12²) = 27.8 g → **+6.9 g robot** (8 sleeves).
- **Tines at ø22 [EST, Legs to confirm in CAD/FEA]:** keep e/D 1.0, so **e = 22, rounded end R16**.
  - Bore removal −1.2 g; +2 mm tine length × 30 mm × 8 mm × 8 tines ≈ +2.7 g → **+1.5 g robot**.
  - The ligament and peak stress should match the e20/ø20 result (185 MPa fault) if e/D is kept. That has not been verified.
- **Item 2 can be dropped if J-T1/G5 measures R_col ≤ 8 K/W** (Thermal A38). Then the sleeves revert to 20/12 and the tines to e20/ø20.

## Legs must recheck
1. ø22 bore: edge distance e22/R16 (2D FEA as in tine_fea_a38.py at 3 275 N/tine fault), and clearance to the eye-stub flange (rev C clearance was 4.0 mm at R20; at R22 it drops to ≈ 2 mm [EST]).
2. Lever eye: cheek/boss thickness gives ≥ 16 mm total PEI bearing; edge distance at a ø20 bore in the hip lever; the RV12 sweep clearance (≥ 1.0 mm, l47 brief, today 1.94 mm) with any boss growth; retention per rev C.
3. Whether the knee lever eye is a second parallel path.

## Mass vs the +11 g (rev C, +10.6 g)
| item | g robot |
|---|---|
| rev C net | +10.6 |
| item 1: lever-eye PEI sleeves, 2 eyes | +8.6 |
| item 2: sleeves 22/12 | +6.9 |
| item 2: tines e22/ø22 | +1.5 |
| **rev D net** | **+27.6 g (+17.0 g over rev C; +10.6 over R-053's +17 booking)** |
| if item 2 is dropped (R_col ≤ 8 measured) | +19.2 g |
