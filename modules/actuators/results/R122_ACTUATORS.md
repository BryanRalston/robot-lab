# R-122 mass-down: RL Actuators rows (D82, 2026-10-21)
Script `r122_actuators.py` → `results/R122_ACTUATORS.json`. Geometry: `cad_mass.py` parametric housings (authoritative per G4 brief §1); regions: G4 brief §5 candidates only (2.0 mm walls, seats, bolt circles kept). Fractions removed are [EST] until G4 FEA.

## Row 3: hip/ankle housing pocketing
**Correction to the R-122 basis:** "~0.78 kg housings" is one of each type. The robot carries **2.221 kg** (2 hip yaw 0.429, 2 hip roll 0.453, 4 hip-pitch bodies 0.570, 4 ankle bodies 0.769; G4 brief §1, CAD-measured). 20 % of 0.78 = 0.16 is therefore not the right figure; I give it from the candidate regions instead.

| region (per unit, kg) | hip yaw ×2 | hip roll ×2 | hip-pitch body ×4 | ankle body ×4 | assumption |
|---|---:|---:|---:|---:|---|
| rear-cap spoke windows | 0.022 | 0.022 | 0.016 | 0.011 | 50 % of cap annulus [EST] |
| output-flange scallops | 0.011 | 0.011 | — | — | 50 % of ring D+2…D+14 [EST] |
| screw-body cone windows | — | — | 0.007 | 0.004 | 30 % of cone [EST] |
| ankle eye-lug trim | — | — | — | 0.008 | 25 % of lug profile [EST] |
| **subtotal, no Thermal items** | **0.033** | **0.033** | **0.023** | **0.023** | |
| rotary tube windows (Thermal/contamination) | 0.009 | 0.010 | — | — | 30 % circumference over stator length |
| ankle ring fins (Thermal decides) | — | — | — | 0.066 | removal, 4 × 3 mm fins |

- **Row 3 answer: full −0.316 kg [EST] (no Thermal items), −0.354 with tube windows.** Credit now at half: **−0.158 / −0.177**. Full only after G4 (SIMP + P2 verify, CAD-measured trimmed STEP). The R-122 −0.16 full / −0.08 credit understates the row by about 2×.
- Optional, Thermal-owned: ankle ring fins −0.265 kg robot (CAD calc). They are thermal parts; flag only, not proposed (Thermal decides; same h-uncertainty as R-069 knee).
- Gate risk unchanged: G3/G4 static + fatigue at the rear cap (cable bore rim) and flange scallops; Thermal for windows.
- Not in R-122: arm/waist/wrist housings have no CAD in this module, so no pocketing figure can be given; G4 scope covers legs only.

## Fastener items (new, for Materials; see `FASTENER_BOM.md`)
- Ti-6Al-4V on non-structural actuator fasteners: **−0.091 kg [CALC/EST]** (384 screws: covers, readheads, drive mounts); **−0.074** if Thermal keeps steel drive-mount screws. Materials prices/qualifies (galling, anti-seize). Structural 12.9 screws are not candidates (HD ≥ 12.9).
- **Risk against the plan:** counted actuator fastener mass on the legs ≈ 0.82 kg vs ≈ 0.30 kg booked in `cad_mass.py` → up to **+0.5 kg** under-booking [CALC; lengths EST]. Arbiter to consider in the R13 regen; Actuators will replace it with CAD fastener counts in G4.
