# Job 3 diagnosis and job 3c (Torso, 2026-10-21; R-149, Robot Lab job 3 ruling, T&R b1fe48f)

## 1. Status of pocketing credit
**All pocketing credit is pulled.** Job 3 / 3b FAIL (fea/job3/REPORT.md). **P-148 (rails) and P-149 (partition) are ON HOLD** until job 3c passes. P-145, P-146, P-147 and P-150 do not depend on job 3 and stand.

## 2. Where LC1 33.5 kN and the 0.05 mm gate came from (R-149 item 1)
- **33.5 kN:** git `-S` trace: first in 1f3a99b (R-079, 2026-10-14, T031 rev 2 "backing sized at 22.35 kN × 1.5"), then 357cca1 (R-084), then ed6fe55. It came from the task instruction "size the backing for the new ceiling × 1.5 margin" and R-084 "22.35 kN × 1.5 = 33.5 kN": a backing sizing load, not a cited design load. In 946aa68 (FEA spec FINAL) **I then also applied SF ≥ 2 on top of an allowable that already contains 1.5** (480/1.5 = 320, R-123). That is 1.5 × 2 × 1.5 = 4.5 on typical yield. **That stacking was mine and unsourced.**
- **0.05 mm land deflection gate:** introduced by me in **946aa68** ("land deflection ≤ 0.05 mm at LC1 (≥ 10× pad stiffness of 0.53 MN/m)"). **No source; the arithmetic is wrong.** 10 × 0.53 MN/m = 5.3 MN/m gives 22.35 kN / 5.3 MN/m = **4.2 mm**, not 0.05 mm. I admit this error. Every job 3 "land deflection FAIL" was judged against it.
- **Both are superseded by T&R b1fe48f** (reliability/CHEST_DESIGN_LOAD.md):
  - Limit 29.0 kN, ultimate 43.5 kN.
  - LC1a: normal, uniform on 101 × 101. LC1b: ±25 mm offset. LC1c: 25°, 21.2 kN normal + 9.9 kN sideways.
  - At limit: ≤ fall allowable min(A-basis, Sy/1.1), 7075 ≈ 386 MPa (assumed). No permanent set; CFRP first-ply FI ≤ 1. Buckling ≥ 1.5.
  - At ultimate: no rupture, buckling ≥ 1.0.
  - **Land stiffness ≥ 5.3 MN/m (≤ 5.5 mm at 29 kN).** The 0.05 mm gate and SF ≥ 2 stacking are deleted. Mode 1 ≥ 80 Hz and LC2 per R-127 are kept.
  - The R-149 item 2 deflection proposal (≥ 5.3 MN/m, plus no contact across the pack gap) is therefore **adopted by T&R as the gate**. Remaining Torso add-on (proposal): land deflection at 29 kN + 2 mm ≤ the pad-land-to-pack-lid clearance.

## 3. Why job 3 failed (model, not only design)
- The stand-in had the 12 mm bulkhead carried **only by two 12 × 20 mm posts** to the pelvis, with no shell, pack bay or side frames. LC1 was a two-post cantilever: 58 mm deflection, post ligament 1.5 GPa, buckling 1.0 (posts). Mode 1 64 Hz was the torso mass on the posts. LC2 was post bending.
- The job 3 pelvis was the old 140 × 260 × 60 stand-in, not model_v4 (170 × 370 × 104 × 4, open top/bottom, plus an 8 mm waist deck). Fixed in 5abcd56 / 3c.
- **Found while building 3c:** the job 3 partition (x −10, z 0–300) and the bulkhead lower edge ran through the model_v4 pack envelope (185 × 220 × 144, torso z 60–204). In 3c the partition is above the pack (z 205–300) and the pack bay is a closed box.
- **3b fix:** the model_v4 pelvis is open top/bottom, so R-127's candidate "top/bottom webs" do not exist. The only sandwich candidate is the 8 mm waist/hip-yaw deck (Legs interface). The 3b pelvis-wall sandwich is withdrawn (side walls fail shear, R-127). **3b credit 0**; the deck sandwich is a later Legs-agreed item.

## 4. Job 3c design: closed boxes, mass at full (`fea_job3c.yaml`)
- **Pack-bay torsion box** replaces the posts. 7075: sides y ±115, 3 mm (the pack rail walls); front web x +106 and rear web x −84, 2 mm; lid 1.5 mm at z 140 (pack lid). Seated on the model_v4 pelvis plus the 8 mm deck.
- **Closed sternum box:** 2 shear webs at y ±60, 3 mm, plus a 3 mm top cap at z 300, tying the bulkhead/land back to the bay rear web.
- Loads and gates per T&R b1fe48f (§2). LC1 variants LC1a/b/c at 29 kN against fall allowables (bulkhead/box 386 = 1.5 × 257, ST 3.0 in; pelvis 406 = 1.5 × 271; CFRP FI proxy 450 [EST]). LC1u at 43.5 kN against Ftu ≈ 504 [EST, verify MIL-HDBK-5H] for no rupture. LC2 SF 1.0 on R-128 allowables (R-127). Mode 1 ≥ 80. Buckling ≥ 1.5 on LC1a.
- **[COARSE] box run (h 25 mm, 23.7k nodes, 49 s; fea/job3c_COARSE_results.json):**
  - **Fixed:** land deflection **1.54 mm at 29 kN (k ≈ 19 MN/m ≥ 5.3, PASS)**, 2.1 mm offset, 1.3 mm at 25°. Buckling **4.6 (≥ 1.5, PASS)**. Mode 1 **382 Hz (≥ 80, PASS; was 64)**. LC2 bulkhead SF **1.14, pelvis 2.79 (PASS; was 0.77 posts)**. LC3–LC6 PASS.
  - **Still failing:** bulkhead-group stress SF 0.86 (LC1a), 0.56 (LC1b), 0.82 (LC1c), 0.75 (ultimate). Pelvis 0.82 (LC1b), 0.996 (ultimate). At h 25 on 2–3 mm walls these are junction peaks (web-to-lid, land step) and not converged. The refined run on the bryan PC decides.
  - Pre-sized fixes if the refined peaks stay: R3 fillets at web/lid/land junctions, a 3 mm lid, and webs 3 → 4 mm locally under the land.
- **Mass at full (mesh):** bulkhead + land + rib + boxes **3.41 kg**, against job 3 bulkhead + posts **1.99 kg** → **+1.43 kg [CALC, full]**. Not yet credited against the pack enclosure walls/rails (0.75 + 0.20) that the bay box partly replaces. That overlap must be itemised with Electronics/pack before any credit (half credit at most). Pelvis 3.21 kg is the model_v4 shell plus deck (existing, not new). Partition 0.04 kg.
- **Verdict:** 3c fixes stiffness, buckling, mode 1 and LC2 at coarse mesh, at a large full-mass cost. Stress is open pending the refined PC run.

## 5. Cartridge spec additions (T&R b1fe48f)
- **Dynamic crush coupon per lot:** drop or impact at **5.7 m/s**. Peak force ≤ **29.0 kN** (98 × 98 face, 0°), plateau within the R-102 band (quasi-static equivalent 19.5–22.3 kN). Record densification strain.
- **Pre-crush inspection:** pre-crush depth and evenness (no cell tearing; first-peak removed, initial peak ≤ 1.05 × plateau), dimensional check 98 × 98 × 116 ±0.5, bond-face flatness ≤ 0.2 mm, ribbon direction marked (L along z).
