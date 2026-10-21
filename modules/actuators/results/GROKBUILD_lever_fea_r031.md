# Grok Build brief G3: hip_pitch lever R-031 merged web b30/d36 R8 (release candidate). Run on the bryan PC / Grok Build, NOT the box
**Why not on the box:**
- gmsh can't load on the box (libGLU.so.1 missing).
- A converged local study needs more than 300k P2 dofs, about 4 GB or more (GROKBUILD_lever_fea_v2 §0). The box has about 4 GB free out of 15 GB, shared with other agents.

**Geometry:** `modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step`. This is a byte copy of Legs L47 `legs/cad/hip_pitch_lever_r031_mw_b30_d36.step`: 2 valid solids, 155,055 mm³.

**Material and mass:** 7075-T6 (E 70 GPa, ν 0.33, Sy 480, Su 560; R-123(a): MATERIALS_DB typical (MIF), not A/B-basis; was 71.7/503/572). Mass by the hp_lever_fea_v2 rule: (V − 2 × π6² × 25) × 2.81e-6 + steel pins 0.0444 = **0.464 kg per lever**.

**Setup:** as GROKBUILD_lever_fea_v2. That means a pressure-loaded ø42 bore, yoke-face support, and pin loads on the ear pins, using `hp_lever_fea_v2.py` mesh/solve functions with the STEP imported in place of geom().

**Cases:**
1. **Design:** 4542 N per pin (454.2 N·m / 0.050 / 2). Pass: von Mises peak ≤ 480/1.5 = **320 MPa** (R-123; peaks 320–335 FAIL) at the converged level.
2. **Fatigue (Amendment 1, R-031 §6):** 2030 N per pin, fully reversed (R = −1). Pass: **hot-spot von Mises amplitude ≤ 58 MPa** (Se 87/1.5).

**Convergence:**
- Global h 4 → 3 → 2, with gmsh Ball refinement at the web/arm R8 blends, the bore lip (1×45 chamfer + R1) and the ear roots, down to local 1.5 → 1.0 → 0.6 mm.
- The peak must change by < 5 % over the last two levels, or a singularity is declared and reported with its location.

**Report:**
- Peak and amplitude per level, with locations, plus a plot of the governing case.
- **Mass from the STEP.**

**If it fails:**
- Go to the b35/d40 fallback (Legs L47 mass +0.242 robot).
- If that fails, use 17-4PH H1025, per R-031 §6.

---
# Re-run brief G3-R2 (D92, after job2 334e848 FAIL) — supersedes the geometry, allowable and convergence sections above
**Geometry:** `modules/actuators/cad/hip_pitch_lever_g3_b34_d40_e26.step` (made by `lever_g3_fillet.py`, B=34 D0=40 D1=21 ED=26 RU=8 RE=5 XE=12.9). It is the Legs L47 merged web resized b30/d36 → **b34/d40**, with these blends:
- the lower web/arm R8, as before;
- **R8 on the upper web/arm edge** (|x| 17, |y| 38.5, z −24…−6; this was the job2 singular point at (−15.7, 38.6, −10.0)), on both sides;
- **R5 on the ear/arm root** (|x| 12.9, |y| 50, z −60…−40; the job2 L2 and b35 hot spot), on both sides.

It is 2 valid solids, 175,164 mm³, **0.5207 kg per lever** by the same mass rule. RV12 rod sweep min 1.18 mm (≥1.0 OK). For comparison: `hip_pitch_lever_g3_b30_d36_e26.step` is the RC with the blends only, 0.4672 kg, rod 1.94. Run it as case B so we can see what the fillet alone does.

**Material / allowables (L70):** 7075-T651 plate, 2.5 in (each solid 60 × 61.5 × 93; 63 mm with stock ≤ 63.5). Plate thickness runs along x (= ST); the arm y–z plane is L/LT. The part is single-path, so the static pass is the R-128 band value **≤ 271 MPa** (ST, 2.001–2.5 in), which replaces the 320 multi-path value. If Materials moves it to T7351, use 239. Fatigue: hot-spot von Mises amplitude **≤ 58 MPa** at 2030 N/pin, R = −1 (unchanged).

**Mesh for the 15 GB WSL cap:** gmsh Ball fields **radius 4 mm, thickness 4 mm** (the job2 setting, 235k tets / 1.03M dofs at the finest level), centred on these points only (no others):
- the 4 upper R8 blends, at (±17+…, ±38.5±4, −14)
- the 4 ear-root R5 blends, at (±13, ±48, −52)
- the 4 lower R8 blends
- the 2 bore lips

Levels:
| level | h | hloc |
|---|---|---|
| 1 | 4 | 1.5 |
| 2 | 3 | 1.0 |
| 3 | 2.5 | 0.6 |

At 0.6 there are ≥13 elements across the R8 and ≥8 across the R5. If a level goes over about 300k tets, drop to Ball radius 3 mm rather than coarsen hloc.

**Convergence criterion:** at the governing hot spot, the peak must change by **< 5 % between levels 2 and 3**. Also:
- the p99.9 must be ≥ 0.75 × the element max, otherwise it is still singular;
- the same hot-spot location must govern at levels 2 and 3, within 2 mm.

Also report the von Mises at 2 mm and 4 mm from the hot spot, normal to the surface, for the hand-Kt cross-check.

If it isn't converged, report it as singular with its location. Don't extrapolate.

**Hand estimate (D92) to beat:**
- **upper R8:** nominal ≈ 88 MPa design / 39 MPa amplitude, Kt 1.35, giving **peak ≈ 119 MPa, amplitude ≈ 53 MPa**;
- **ear R5:** amplitude ≈ 48–64 MPa [EST], which is the at-risk spot.

**If it fails:** report the hot spot. The next step is ear Ø26 → 28 with R5 (the rod sweep needs re-checking: Ø32 gave 0.5 mm), not 17-4PH.
