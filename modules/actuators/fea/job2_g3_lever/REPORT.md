# Job 2 report — G3 hip-pitch lever FEA

Release candidate `modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step`, 
solved with `hp_lever_fea_v2.mesh` / `hp_lever_fea_v2.solve` (bore cosine pressure, 
yoke face fixed at |y| = 13.5, pin traction). Design load 4542 N/pin. 
Walk amplitude is that von Mises times 2030/4542, fully reversed.

## Mass from the STEP

Two valid solids, volume 155055.4 mm³. 
Mass rule (V − 2·π·6²·25) × 2.81e-6 plus the two ø12×25 stubs as steel at 7.85 g/cm³: 
**0.4642 kg per lever** (7075 0.4198 + pins 0.0444).

## Material and allowables

7075-T6, E 71.7 GPa, ν 0.33, Sy 503 MPa, Su 572 MPa. 
Design pass: converged peak ≤ 335.3 MPa (Sy/1.5). 
Fatigue pass: hot-spot von Mises amplitude ≤ 58.0 MPa (Se 87/1.5) at 2030 N/pin, R = −1.

## Model

The v2 selectors land on this STEP: yoke facets at |y| = 13.5, bore facets at r = 21 and 
|y| 13.5…33.5, pin facets at |y| > 62.5. Checked elements exclude the 2.5 mm next to the 
fixed yoke face and the steel pin stubs, same mask as `hp_lever_fea_v2.run`.

The STEP bore lip is the sharp circle r = 21 at |y| = 33.5. There is no 1×45 chamfer and no R1 edge. 
R8 curvature (about 8.0–8.3 mm) is on the lower web/arm blends near z ≈ −27 and on the short 
side fillets. The upper web/arm edge, where the fine-mesh peak sits, is a straight edge 
(no fillet radius) across the arm at |y| = 38.5.

Ball radius in `hp_lever_fea_v2.mesh` is hardcoded at 7 mm with an 8 mm transition. 
On this STEP that support at local 0.6 mm was 661k tets (about 3.0M P2 dofs) and does not fit 
the 15 GB available to WSL on this PC. Radius 5 mm was still 343k tets. 
The runs use the same Ball field with radius 4 mm and thickness 4 mm (235k tets, 1.03M dofs at the finest RC level).

Ball centres: the upper arm/web corners, the R8 blends, the lower bore-lip arc, and the ear roots. 
Listed in each level JSON.

## RC results

| level | h (mm) | hloc (mm) | tets | P2 dofs | governing | peak (MPa) | at (mm) | amplitude (MPa) | p99.9 (MPa) |
|---|---:|---:|---:|---:|---|---:|---|---:|---:|
| 1 | 4 | 1.5 | 25042 | 124185 | sym_phi+60 | 168.9 | (-15.4, 38.8, -10.4) | 75.5 | 104.6 |
| 2 | 3 | 1 | 64249 | 298242 | sym_phi-30 | 221.0 | (-12.8, -50.6, -51.9) | 98.8 | 109.6 |
| 3 | 2 | 0.6 | 235354 | 1030179 | sym_phi+60 | 246.6 | (-15.7, 38.6, -10.0) | 110.2 | 120.6 |

Same case `sym_phi+60` (the fine-mesh governing case) at the three levels: 168.9 MPa at (-15.4, 38.8, -10.4) → 198.3 MPa at (-15.5, 38.7, -10.2) → 246.6 MPa at (-15.7, 38.6, -10.0).
That corner rose 17.4% then 24.3%.

Global peak change over the last two levels: 11.6% 
(221.0 MPa at [-12.81, -50.62, -51.85] → 246.6 MPa at [-15.65, 38.61, -10.03]).

**Singularity.** The peak changed by 11.6% over the last two levels, above 5%. 
Location on the finest mesh: (-15.65, 38.61, -10.03) mm, 
case `sym_phi+60`. This is the upper arm/web corner, the end of the straight edge at |y| = 38.5. 
The 99.9th percentile on that mesh is 120.6 MPa, about half the element max, 
which is the same pattern as a re-entrant corner: one element keeps rising while the bulk of the field does not. 
The R8 blends at z ≈ −27 are not this hot spot.

Pin displacement at |y| ≈ 69 on the finest mesh: sym_phi+60 0.090 mm, sym_phi-60 0.090 mm, sym_phi+0 0.110 mm.

Plot: `governing_vm.png`, sym_phi+60, finest mesh. The cyan ring is the peak element centroid.

## RC verdict

FAIL. There is no converged peak. The finest element max is 246.6 MPa 
(under the 335 MPa yield screen) but it is still climbing, and the amplitude at that element is 
110.2 MPa, above 58. The yield screen cannot be closed on an unbounded corner.

## Fallback b35/d40

Geometry `modules/legs/cad/hip_pitch_lever_r031_mw_b35_d40.step` (Legs L47 merged-web fallback, 
the file whose mass was booked at +0.242 kg robot against the old baseline). 
The actuators tree also has `hip_pitch_lever_r031_b35_d40.step` without the merged web. 
The merged-web solid is the one that matches the RC construction. 
Same solver, Balls moved out to the b=35 upper edge at x = ±17.95, z = −7.92 and to the R8 at |x| ≈ 17.7. 
The ear is still ø26, so the ear-flank balls stay near |x| = 13.

Volume 177206.7 mm³. Mass by the same rule: **0.5265 kg per lever**.

| level | h (mm) | hloc (mm) | tets | P2 dofs | governing | peak (MPa) | at (mm) | amplitude (MPa) | p99.9 (MPa) |
|---|---:|---:|---:|---:|---|---:|---|---:|---:|
| 1 | 4 | 1.5 | 26020 | 129837 | sym_phi+60 | 144.2 | (-3.2, 60.9, -42.4) | 64.5 | 97.7 |
| 2 | 3 | 1 | 65607 | 308157 | sym_phi+30 | 187.1 | (12.5, -50.2, -52.4) | 83.6 | 91.8 |
| 3 | 2 | 0.6 | 236235 | 1043064 | sym_phi-60 | 228.4 | (-12.6, -50.1, -52.3) | 102.1 | 97.9 |

Same case `sym_phi-60` across the three levels: 139.0 MPa at (3.0, 60.7, -42.5) → 176.8 MPa at (-12.5, 50.2, -52.4) → 228.4 MPa at (-12.6, -50.1, -52.3).

Global peak change over the last two levels: 22.1% 
(187.1 → 228.4 MPa at [-12.64, -50.13, -52.33]).

**Singularity on b35 as well**, at (-12.64, -50.13, -52.33) mm. 
p99.9 on the finest mesh is 97.9 MPa against an element max of 228.4.

b35 FAIL. Finest peak 228.4 MPa, amplitude 102.1 MPa, not converged.

Plot: `governing_vm_b35.png`.

## 17-4PH H1025

R-031 §6 holds 17-4PH H1025 if the b35/d40 7075 section still fails. 
The family script's endurance is 0.75×0.9×0.814×0.5×Su with Su 1070 MPa, so Se = 294 MPa 
and the amplitude allowable is Se/1.5 = 196 MPa. 
ASTM A564 H1025 minima are Sy 1000 MPa and Su 1070 MPa, so the yield screen is 667 MPa. 
Density 7.80 g/cm³ on the aluminium body, pins left at 7.85: 
**1.210 kg** on the RC solid (+1.491 kg robot versus 7075) and 
**1.382 kg** on the b35 solid.

This load is force-driven. Von Mises does not depend on E, and moving ν from 0.33 to about 0.27 
changes the stress by only a few percent, so a steel re-solve reproduces the same spike. 
The spike is geometric. On the RC it is the straight upper web/arm edge at |y| = 38.5. 
On b35 the finest-mesh location is the one in the table above. 
A material change does not give that element a converged value. 
Finest b35 element max 228 MPa, amplitude 102 MPa. 
Finest RC element max 247 MPa, amplitude 110 MPa. 
Both amplitudes sit under the 17-4 screen of 196 MPa only at these mesh sizes, and both rose on the last refinement. 
17-4PH H1025 is not a converged pass. The unfilleted corner has to be blended before either alloy can be released.

## Verdict

**FAIL**
