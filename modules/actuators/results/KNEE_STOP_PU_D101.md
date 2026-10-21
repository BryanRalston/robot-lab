# D101 — integrated knee PU stop (Legs L91 Option B / A): HARD CONFLICT, NO-GO (2026-10-21, ~11:10 ET)
Script: knee_stop_pu_d101.py → knee_stop_pu_d101.json (model_v4 + cad/knee_twin_housing_release_r116b.step, CAD distances).

## Conflict check first (as asked)
Neither B nor A reaches the point where a motor/encoder/screw/drive conflict could arise. **The pocket location does not exist on the r116b housing:**
- The r116b housing (143.0 cm³ CAD) sits at the trunnion end of the screws. Its **lowest face is 185 mm above the knee axis** at every knee angle.
- CAD minimum distances from the housing:

| knee | to tongue-neck | to knee lever | to tibia tube |
|---|---|---|---|
| 0° | 178.5 mm | 206.4 mm | 259.6 mm |
| 130° | 178.8 mm | 163.4 mm | 66.2 mm |
| 143.6° | 178.2 mm | 161.6 mm | 8.1 mm |

- So there is **no housing underside at r50 (B) or lower-rear bosses at r60 (A)**. The tongue-neck block is ~179 mm from the housing throughout. A strike there needs a ~160–180 mm arm, which the brief excludes.
- L91 appears to place the housing at the knee pivot. In model_v4 the knee pin and clevis carry the lever; the housing hangs from the thigh trunnion (x −130, z +270).
- Because of this I did not assess the internal motor/encoder/screw layout for a pocket: the location conflict decides it first.

## Could any housing-mounted stop work?
- The only shank part that reaches the housing is the **tibia tube at r ≈ 200–280**. Its gap closes from 66 mm at 130° to 8 mm at 143.6°.
- The housing pivots about the trunnion with the screw (φ −68.6° → −66.3°). The shank's travel relative to the housing over the stop is therefore:

| r on tibia | 50 | 60 | 100 | 150 | 200 | 250 | 280 |
|---|---|---|---|---|---|---|---|
| travel 130→143.6 (mm) | 11 | 14 | 16 | 30 | 44 | 58 | 66 |
| PU thickness for 25 % | 44 | 56 | 65 | 120 | 176 | 231 | 264 |

At the tibia/housing gap (r ~250), 231 mm of PU would be needed against 66 mm of space.
- **Load path:** the housing is held only by the trunnion pin and the two screws (spherical rod ends). A strike reaction on it bends the RV12 screws (ø12 rods) unless its line passes through the trunnion. That needs contact at r ≈ 273 with face normal ∥ u_t(130°), which is the 231 mm-PU case above.
- **Verdict: D101 integrated-in-housing is NO-GO.** No STEP was issued: there is no feasible pocket to model. Items (1)–(5) of L91's Actuators list are moot. Mount-bolt, rib, fin-trim and thermal checks were not run.

## What remains (for Robot Lab)
- The PU volume (62 cm³ for 92.5 J at 25 %) and the T25 ≈ 760–790 N·m stop moment hold for any location. The mass driver is the shank-side strike hardware that reaches the PU.
- **The only metal near the knee on both segments** is the clevis (thigh) and the tongue/neck (shank), at r 40–55. L78 found no room inside the clevis: tongue 28 mm in a 42 mm gap. A clevis-bridge pocket struck by the neck top would need a 44–56 mm stack at r50–60, which doesn't fit between bridge and neck. **It needs Legs CAD to confirm or kill.**
- Options that actually cut mass, both needing a gate change:
  - (a) Accept fault-case bottoming above the drives-on energy: size E25 at 1.4 × 44.1 = 62 J. PU 41 cm³, and strike hardware loads −33 %.
  - (b) Keep D99 r75b outboard (CAD 0.871 kg, Legs 211d031) with tapered/pocketed arms (−0.08 to −0.10 [EST]).
- **Legs collar boss: none required for D101** (no feasible location). If Robot Lab picks (a) with the D99 placement, the interface loads become 0.67× the D99 values: 7.3 → 4.9 kN design, 10.5 → 7.0 kN bottoming [EST].
