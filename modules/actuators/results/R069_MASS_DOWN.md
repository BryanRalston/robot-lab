# R-069 mass-down pass: actuator side (RL Actuators)

Only CITED (catalog) or MEASURED (CAD volume × density) savings are claimed. Box-light compute: CadQuery and the Controls 2-node winding model, no FEA.

## Ranked savings

| # | Part / joint | Now | New | Saving (robot) | Source | Margin check | Risks / conflicts |
|---|---|---|---|---|---|---|---|
| 1 | Knee rev B fins → rev C (both knees) | 0.0932 kg/knee, 0.0703 m² (`knee_fins_revb.json`) | 0.0605 kg/knee, 0.0459 m² (`r069_knee_fins_revc.json`, `cad/knee_twin_housing_finned_revc.step`, valid solid) | **−0.065 kg** | MEASURED: CAD volume × 6061 2.70 g/cm³ | Drives are now OFF the housing (R-066). `r069_knee_fin_trim.py`: at 0.045 m² with drives off, worst case carry r4 ×1.10 open is 104.6 °C at h 12 and 114.9 °C at h 10. Rev B as booked (0.0703, drives on) is 106.4 and 116.9. So every case is no worse than the approved basis, and all are ≤ 120 °C | Depends on the R-066 off-housing mount actually being built. If the drives go back onto the housing, rev C fails (carry open 119–123 °C at h 12, 0.045–0.06). Thermal and Controls must re-check. The knee stays vented. My P-042 carry numbers (91.4 on / 81.9 off) are about 8 K below Controls' 99.0 / 87.5, so Controls should reproduce this with their harness. |

**Total claimed: −0.065 kg. That is short of the 0.18 kg target by 0.115 kg.**

### Checked and rejected (no supported saving)
- **Wrist pitch CSG-14-100 → CSF-14-100:** HD catalog weight table (`hd_csf_csg_catalog.txt` l.1101) gives the same 0.09 kg for size 14, so the saving is 0. **CSF/CSG-11** (0.05 kg) has a repeated peak of 11 N·m, below the 14.7 needed. D76 stands.
- **Wrist yaw CSF-11-100:** this is already the smallest size that passes (8 is 0.026 kg but too weak; 11 is 1.24× on 8.9).
- **Hip yaw CSG-17 → CSG-14:** 36 N·m is below the 66 needed. **Hip roll CSG-25:** 204 vs 177 (1.15×), and the next size down fails. **Ankle pair:** 311 vs 305. No margin anywhere for a smaller gear or motor.
- **CRBH 258 A (wrist):** this is already the smallest in the IKO table. **D71 CRBH 7013 A:** fs 1.00 radial, no margin.
- **Housing pocketing / wall trims (hip yaw 0.214, hip roll 0.226, ankle 0.192, hip-pitch body 0.143 kg CAD):** there are no stress or FEA results in the repo for these housings, so no trim can be claimed. It needs FEA on Grok Build. This is the largest remaining lever.
- **Fasteners and brackets:** these are [EST] lines only, with no fastener CAD, so nothing is measurable.

## Fin vs trunnion-cheek check (Legs query), `knee_fin_cheek_check.py` → `results/knee_fin_cheek_check.json`
- Trunnion pads in `knee_twin_housing.step` are the planar faces at local x = ±92 (= world ±y), y −10…10, z 11.5…31.5 (20 × 20 mm).
- Rev B: **no fin sits on the pads.** Fin volume in the pad prism is 0, and the minimum fin-to-pad distance is 14.4 mm. With an assumed ±20 mm × full-height cheek plate [EST size], the volume is still 0 and the clearance is 5.7 mm.
- However, the outer rear fins (±60° edge) **overhang the ±92 planes by up to 10.4 mm** (713.6 mm³ per side, at y +26.6…+42.2, rear). A cheek larger than about 26 mm aft of the pad centre would hit them.
- **Rev C fixes this:** 12 rear fins × 17 mm (span ±50.7°) + 7 front × 9 mm. The x extent is 92.0, so nothing is outboard of the pad planes. The edge fins on Legs' 120/240° boundary are also gone. The area falls to 0.0459 m², and the thermal re-run is above (#1).
