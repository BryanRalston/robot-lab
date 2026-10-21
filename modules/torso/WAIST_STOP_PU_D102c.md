# Waist pitch PU end stops + limiter keep-out (Actuators D102c eb5520f)
Stack (+y): motor -> CSG-25 -> friction limiter (0.394 kg, ø90/ø66, L 23, slip 170 N·m) -> yoke.
- Keep-out: ø90 (r_clear 47) × 23 mm on the pitch axis, y 55–78 (was Mayr ø95 × 67, 2.88 kg; rejected).
- Absolute encoder ring: YOKE side of the limiter (y 78–84, ø66 bore), so it reads true torso pitch after slip.
- PU stops: torso-side of limiter (torso cheek lugs, r_lug 100 mm, |y| 72–100, two per cheek: one per range end).
## Sizing (PUR90A layered stack, curve and data from actuators/results/KNEE_STOP_PU_D99.md, ASTM D575 quasi-static)
D99 basis: 25 % strain -> 1.40 J/cm³ PU, 10.9 MPa, shape factor 0.50, curve efficiency η = E/(F·δ) = 0.51.
- 356 J shared by 2 lugs (one per cheek) = 178 J/lug. Travel 0.30 rad × 100 mm = 30 mm = 25 % of 120 mm PU length.
- PU per lug: 127 cm³ = 2 columns 24 × 22 mm (A 1060 mm²) × 12 layers × 10 mm + 1 mm 7075 shims, stack ≈ 135 mm.
- Peak at 356 J (25 %): 11.6 kN/lug -> **2.32 kN·m > 1.7 kN·m target: FAIL**.
- Physics floor: T_peak ≥ E/(η·θ) = 356/(0.51·0.30) = 2.33 kN·m for any PU/TUBUS-type progressive elastomer
  (ACE TUBUS TA is also progressive). Meeting ≤1.7 kN·m needs η ≥ 0.70 (hydraulic/constant-force) or travel ≥ 0.41 rad (23.5°).
- 25 % at exactly 356 J = zero bottoming margin; 22 % variant = 161 cm³/lug, stack ≈ 170 mm.
- Mass: PU 0.15 + shims/plates/pin 0.09 = 0.24 kg/lug, ×4 = **0.97 kg**.
## Travel / clearance
Contact at range ends (−30°, +60°, sim v3), overtravel to −47° / +77°. Stack is tangential, 135 mm at r 100 -> spans ~77° of arc
per lug; both range-end lugs per cheek fit in the 360−90 = 270° free arc only if the stacks sit on the strike wings, not the cheek.
The pitch range itself is untouched (stops beyond it). The overtravel to −47/+77 has NOT been swept against hip/pelvis
geometry (the earlier sweep covered −30/+60 only): OPEN.

## Round 2 (T&R 65c95eb/0acbe03), hand calcs, 2026-10-21
### Layout change: 2 diametral pairs per range end (one pair per cheek at r ±100), so the load is a pure couple
8 stacks in total, 4 engage per end. Per stack (356 J): 89 J, 63.6 cm³ = 24 × 22 mm × 120 mm PUR90A (+shims ≈ 135 mm).
Mass 8 × (0.076 PU + 0.06 hw) = **1.09 kg**. Peak is unchanged at 2.32 kN·m (η floor).
Lug force F = T/(4r): 4.25 kN at 1.7 kN·m (17 kN couple), 5.8 kN at 2.32 kN·m.
### Structure (7075 single-path, allowable 257 MPa, R-128; SF = 257/σ_limit, target ≥1.5)
| item | size | σ at 1.7 kN·m | SF | σ at 2.32 kN·m | SF |
|---|---|---|---|---|---|
| torso lug, cantilever 21 mm | 25 radial × 16 thick, 2× M6 12.9 | 84 | 3.1 | 114 | 2.25 |
| waistY strike wing (same section) | 25 × 16 | 84 | 3.1 | 114 | 2.25 |
| stop face plate, bearing 10.9 MPa | 3 mm 7075 | 11 | >10 | 11 | >10 |
| yoke cheek, in-plane couple/cheek | 8 × 120 | 44 | 5.8 | 60 | 4.3 |
| cheek local, lug moment, no pad | 8 mm, 60 wide | 140 | 1.84 | 191 | **1.35 FAIL** |
| cheek local + 4 mm pad (+0.03 kg) | 12 mm | 62 | 4.1 | 85 | 3.0 |
### CRBH 6013 A tilt (≤0.61 kN·m, R-161a); lug y 86 vs bearing plane y ≈ 60–68 (e ≈ 26 mm, assumed from the stack y 55–84)
- Paired couple, 20 % contact mismatch, 2.32 kN·m: net 1.16 kN × 26 = **0.03 kN·m PASS**.
- Worst case, one lug of the pair only: 11.6 kN × 26 = **0.30 kN·m PASS** (radial 11.6 vs C0 24.3 kN).
- P-162 brake (R-161a: ≥204 flexion, ≤600 extension sweep, cap 2.5 kN·m): single anti-rotation pin at r 60, e 15:
  600 N·m -> 10 kN -> **0.15 PASS**; 2.5 kN·m -> 41.7 kN -> **0.63 FAIL**. Requirement: react the brake through a bolt circle
  (pure couple, ≈0) or keep a pin within 14 mm of the bearing plane.
### Alternate at 183 J (1.5 × 122 J T&R upper-body max)
- (a) Same 17° travel: peak 2.32 × 183/356 = **1.19 kN·m**. Stack 120 PU (≈135 mm), A 272 mm² (16 × 17). Mass **0.71 kg** (8 stacks).
- (b) Shortest stack at the 1.7 kN·m cap: θ = 183/(0.51 × 1700) = 0.21 rad (12°). PU 84 mm (≈95 mm stack), A 390 mm². **0.67 kg**.
### Overtravel sweep −47° / +77° (pitch axis global 1349.6 = deck +143)
- Lugs at r ≤ 121: lowest z = deck +22 at any angle. Hip-yaw housings, L39 bumpers and hip ROM are all below the deck: CLEAR.
- Box front-lower corner (x 108.5, z +60) at +77°: z = deck +51. Rear-lower corner (x −107, +60) at −47°: deck +105. Cheek corners r 67: deck +76. Min **51 mm CLEAR**.
### Fit on the strike wings
- Stack 135 mm straight, tangent at r 100: ends at r 121, inner face r 89, outside the limiter ø90 (r 45), the CRBH OD 90 and the ø100 spacers (r 50); y 72–100 is outside waistY |y| ≤ 70.
- Arc per cheek: 2 stacks (pair) ≈ 2 × 78° + lug sweep 124° + lug 15° ≈ 295° < 360°. Pairs are diametral, so both ends together need 4 stacks/cheek: **does NOT fit at 135 mm** (≈450°). Fits with the 183 J (b) 95 mm stacks (4 × 57° + 139° = 367°, marginal) or by splitting by y (inner band y 72–86 for one end, outer y 86–100 for the other: 2 × 295° in separate planes, FITS, wing width 28 -> 2 × 14 mm, stack width 22 -> 14: A 336 mm², needs L 190 for 356 J -> FAIL; OK for 183 J (a)).
