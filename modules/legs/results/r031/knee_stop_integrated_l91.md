# L91: integrated knee PU stop concept study (replaces the D99 arms, ring and pins) [hand, EST], 2026-10-21
Gates: fault 92.5 J and design 44 J inside 25 % strain; T_STOP ≤ 830 N·m; contact 130°, top-out ≤ 143.6° (13.6° = 0.237 rad of travel); ≤ 0.49 kg per robot counting **added material only**; 262 MPa design / 393 fall (7075-T7351, single path); bearing tiers 455/381/295 MPa; 58 MPa fatigue (rare-event, Controls kneel 108.9° < 130°).

## PU sizing (PU 90A, Freelin-Wade PUR90A curve as in L81: σ25 ≈ 11.7 MPa, energy density 1.49 J/cm³ at 25 %, 2.14 at 30 %)
- Volume: 92.5 J / 1.49 = **62 cm³ per knee** (≈ 70 g PU). This is energy-bound and independent of the lever arm. 44 J uses 30 cm³, i.e. ≈ 15 % strain.
- Stack thickness for 25 % at top-out: t = 0.237·r / 0.25 = 0.95·r. Area A = V/t.
- Peak force F25 = σ25·A = 11.7 × 62 000 / (0.95 r), so **T25 = F25·r ≈ 760 N·m ≤ 830, for any r**. The arm sets only force and packaging, not torque. (×1.3 rate factor on the 44 J design case: 544 N·m, as D99.)

| | r (mm) | stack t | area per knee | F at 830 N·m |
|---|---|---|---|---|
| A: twin housing-boss stacks | 60 | 57 mm | 1090 mm² (2 × 26×21) | 13.8 kN (6.9 per side) |
| B: single central stack | 50 | 48 mm | 1305 mm² (1 × 36×36) | 16.6 kN |

## Option A: twin PU stacks in two r116b housing lower-rear bosses, striking faces machined on the tibia tongue-neck block
- **Housing:** two cast/machined bosses on the lower rear of the r116b housing, either side of the tibia (y ≈ 98–124 / 136–162). Each is a 30×25 root and 15 mm proud, with a blind PU pocket 26×21 and a ø6 guide pin. The stack reaches 57 mm along the arc, so the bosses hold the stack base and the stack sits in a pocket that runs into the housing wall.
  - Boss root bending: 6.9 kN × 20 mm = 138 N·m; Z 30·25²/6 = 3125 mm³ → 44 MPa, ×Kt 1.5 = 66 MPa. **SF 3.97 (262) design / 5.9 (393) fall.**
  - PU face bearing 6.9 kN / 546 mm² = 12.6 MPa, far below the 295 tier. No pin bores are loaded, so no bearing-tier reduction applies.
  - Housing-to-thigh path: 13.8 kN must pass through the housing mount into the L58/L60. Actuators must check the housing mount bolts and the casting ribs (open item).
- **Strike faces:** two 20×25×8 pads machined integral with the solid 7075 tongue-neck block, so there is no bond and no slip. Neck shear 13.8 kN / (36×28) = 13.7 MPa. Neck bending is the same knee moment path already passed at 17.2 kN in L78. No metal path to the femur bond (the housing is not on the femur bond).
- **Added mass per knee [EST]:** PU 70 g; shims/end plates 25 g; housing bosses 2 × 11 cm³ (pocketed) 62 g; neck pads 2 × 4 cm³ 22 g → **179 g/knee, 0.36 kg robot ≤ 0.49 PASS** (margin 0.13).

## Option B: single central PU stack in a housing underside pocket at r50, striking the tongue-neck top face
- One 36×36×48 stack, centred at y 130 under the housing between the knee screws, in a pocket cast into the housing underside (a local wall thickening, 6 mm floor). It strikes a flat face machined on the top of the tongue-neck block / tibia doubler at r50.
  - Pocket floor plate 6 mm, spanning 36 between the housing ribs: 16.6 kN as a fixed-fixed plate strip, M = F·L/8 = 75 N·m, Z = 36·6²/6 = 216 → 347 MPa, FAIL. **The floor must be 9 mm:** Z 486 → 154 MPa, ×Kt 1.3 = 200 MPa, **SF 1.31 design (262) / 1.96 fall (393)**.
  - Neck top face bearing 16.6 kN / 1296 = 12.8 MPa, OK. Neck shear 16.5 MPa, OK.
  - The force is the highest of the two options. It runs straight into the housing body, so Actuators must confirm the housing-to-thigh mount at 16.6 kN.
- **Added mass per knee [EST]:** PU 70 g; shims/plates 15 g; pocket walls and floor 9 mm (≈ 14 cm³) 39 g; neck face 3 cm³ 8 g → **132 g/knee, 0.26 kg robot ≤ 0.49 PASS** (margin 0.23).
- Risk: the central space under the housing must clear the tibia, neck and knee lever from 0 to 145° with a 48 mm stack. Not swept yet; it needs a CAD sweep.

## Recommendation
**Option B** if the central sweep passes (lightest, one part, 0.26 kg). **Option A** as the fallback (0.36 kg; lower loads, two smaller stacks beside the tibia). Both drop the 24×18 arms, tibia ring and pins, about −0.45 kg robot against the D99 r75b CAD figure of 0.871.

## What Actuators must change in the r116b housing
1. Add the PU seat: two lower-rear bosses with pockets (A) or one underside pocket with a 9 mm floor (B), including the ø6 guide-pin bores and a PU retention lip.
2. Add local ribs from the seat to the housing mount face, and re-check the housing casting stress and the mount bolts at 13.8 kN (A) / 16.6 kN (B) plus the 830 N·m couple.
3. Trim or relocate fins locally over the seat (rear fin tips already trimmed in r116b), and re-run Thermal's fin-area check.
4. Re-run the housing-to-L60 gap and the knee ROM sweep with the boss/pocket (Legs can run it on model_v4).
5. Re-run the rotor-energy/stop dynamics with the new arm (r60/r50 instead of r75); the stop torque is unchanged at ≈ 760 N·m.
6. Re-issue the STEP so Legs can measure the added CAD mass.
