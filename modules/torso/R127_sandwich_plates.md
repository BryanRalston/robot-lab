# R-127 option C(b): CF / Al-honeycomb sandwich for the torso and pelvis plates (Torso, 2026-10-21)

## Basis
- **Allowables:**
  - 7075 multi-path parts: 320 MPa (R-123). Single-path parts: A-basis/1.5, so 294 MPa for plate ≤2 in and 262 MPa above 25 mm (R-125 (b), R-127).
  - Fall peak: ≤436 MPa (R-127 (b)).
  - Core: the HexWeb CR III 5052 Table I **minimum** values (cited: HEX_CRIII, hexcel.com HexWeb_CRIII_DataSheet.pdf) ÷1.5.
    - 6.1 pcf: W shear 272 psi = 1.88 MPa, L shear 3.14 MPa, stabilized compression 4.69 MPa, density 98 kg/m³.
    - 8.1 pcf: compression 7.58 MPa.
  - **CF skins have no cited laminate data** (MATERIALS_DB: "laminate props not verified"). Quasi-isotropic, E 50 GPa, allowable **300 MPa [EST]**.
- **Sandwich section:** 1.0 mm QI CF skins, 6.1 pcf 1/8 core, plus 0.15 kg/m² film adhesive per face. Areal mass at 10 mm ≈ 4.2 kg/m² [CALC], against 16.9 kg/m² for 6 mm 7075.

## Per-plate result
| Plate | Current kg | Governing case | Sandwich needed | Check | Sandwich kg | Δ kg |
|---|---|---|---|---|---|---|
| Shoulder bulkhead 12 mm + land + rib | 0.60 | LC1 chest 33.5 kN, 0.30 m span, simply supported: M 2.51 kN·m, V 16.75 kN, depth 0.16 m | 1.75 mm skins on a **≥84 mm** core (W) / ≥50 mm (L) | core shear at 30 mm = **3.49 MPa vs 1.25 allowable: FAIL**. Core crush under the land 3.28 vs 3.13 MPa: FAIL at 6.1 pcf, PASS at 8.1 pcf (5.06). M8 flange: 16 × 12.9 preload [EST ~29 kN each] needs solid potted 7075 bushings (+0.16) | 0.63 at 50 mm | **+0.03 (no gain, and no space for 50 mm)** |
| Side plates | – | the torso has none (the CFRP shell already carries them) | – | – | – | 0 |
| Waist ring 7075 | 0.25 | waist 204×1.5 = 306 N·m, actuator bolt circle | hardpoint-dominated | no sandwich possible | – | 0 |
| Pack rails + latch | 0.20 | pack at 10 g, sliding contact | – | sandwich unsuitable (wear, latch) | – | 0 (P-148 pocketing instead) |
| Pelvis top/bottom webs (≈0.45 of 1.45 [EST split]) | 0.45 [EST] | LC3 306 N·m on the 60 mm box: flange force 5.1 kN | 10 mm sandwich | skin 9.8 MPa vs 300: PASS; core shear from LC6 is small: PASS; wrinkling 0.5·(Ef·Ec·Gc)^⅓ = 1.43 GPa ≫ 300: PASS; edges bonded to the kept 7075 nodes | 0.35 | **−0.10 [CALC on EST split]** |
| Pelvis side walls (≈0.35 [EST]) | 0.35 | LC2 side fall 9 kN shear on a 0.26 × 0.06 web | – | core shear 3.85 vs 1.25 MPa: **FAIL** | – | 0 |
| Pelvis hardpoint nodes (hip mounts, waist flange) | 0.65 [EST] | single path (legs to torso) | stay 7075, checked at 294 | – | – | 0 |

**Total: −0.10 kg [CALC on an EST mass split], so −0.05 at half credit.** R-126 assumed this item would contribute about −0.3 to −0.5 of its −1.2; that does not hold for the torso.

- **Insert pull-out:** hip and waist loads stay on the 7075 nodes. The sandwich webs attach by bond plus M5 potted inserts (Shur-Lok SL600-class, ~2.5 kN pull-out in 10 mm/6.1 pcf **[EST, no cited sheet]**). They carry web shear only: PASS [EST], but a cited insert datasheet and a G3 coupon test are required.
- **Job 3b [COARSE]** (`fea_job3b.yaml`, homogenized-sandwich pelvis, 11 mm wall; results in `fea/job3b_COARSE_results.json`):
  - The pipeline ran (6/6 solved, 13 s).
  - Pelvis SF: LC3, LC4 and LC5 pass. LC1, LC2 and LC6 fail. The failures peak at the fixed base and the post roots, which are coarse-mesh/homogenization singularities, but the side-fall trend agrees with the hand-calc FAIL. This is not a sign-off.
- **R-076:** CF is conductive. Sandwich skins count as earthed conductive surfaces for creepage and clearance (92 V bus). Mount bus parts on insulating standoffs, bond the skins to chassis PE, and put a 0.1 mm E-glass isolation ply at every CF–Al bond for galvanic protection (+0.005 [EST]).
- **Cost [EST]:** no list price was found for ACP or Rock West sandwich panels (ACP sells them but publishes no prices; quote needed). About $300 per 600 × 600 panel, $4 per potted insert, and $1.5k for bond fixtures/tooling: **≈ $2.0–2.5k [EST]** for the pelvis webs.
- **Legs interface (note only; Legs files not edited):** the pelvis hip-mount nodes and the bolt pattern are unchanged. Any sandwich web change needs Legs to confirm hip-mount stiffness in their job (L47 lever loads), because the pelvis is a single-path part.

## Recommendation
**Do not adopt the sandwich for the bulkhead, waist ring or rails.** The bulkhead fails core shear at any thickness that fits, and the others are hardpoint- or wear-dominated. The **pelvis top/bottom webs (−0.10 [EST]) are optional**, conditional on Legs' agreement, a fine-mesh job 3b and an insert/bond coupon at G3. Low value for its risk (bonded joints on a single-path part). The better torso lever is **7075 pocketing (job 3) plus P-145…P-150 (−0.25 [EST])**. Report to the Arbiter: C(b) torso share is **−0.10, not ~−0.4**.
