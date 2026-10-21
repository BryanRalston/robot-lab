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
