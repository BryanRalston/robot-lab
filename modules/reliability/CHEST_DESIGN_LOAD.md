# Chest design load for the torso FEA (LC1): T&R answer to Robot Lab / Torso, 2026-10-21
Trigger: Job 3/3b FAIL on LC1 33.5 kN (ff59d8f). **Decision: option (b), with the ceiling corrected for strain rate → limit load 29.0 kN.** (a) is replaced, and (c) is kept only as a robustness check, not a design case.

## 1. Where 33.5 kN came from
FEA_SPEC_torso_pocketing.md: "LC1 chest pad plateau 22.35 kN × 1.5 = 33.5 kN on the land". 22.35 kN is the T031 r2 quasi-static ceiling (2.327 MPa × 0.009604 m², the R-102 lot top 22.3 kN). It assumed a force-limited cartridge with a 1.5 ultimate factor, not a rigid impact.
- **Stacked factors in Job 3:** 33.5 kN (×1.5 on load) **and** SF ≥ 2 **on** an allowable that is already A-basis/1.5 (257). That is ≈ 4.5× on A-basis. It double-counts.
- **Two gates are unphysical:**
  - land deflection ≤ 0.05 mm at 33.5 kN implies k ≥ 670 MN/m, whereas the real need is k ≥ 5.3 MN/m (≥ 10× the pad's k_eq, T031 land check);
  - buckling ≥ 3 at 33.5 kN.

## 2. Reconciling 19.5–22.3 vs 19.5–29 kN (both are right, at different rates)
- **19.5–22.3 kN = quasi-static lot acceptance** (R-102/R-103 coupons, 0°). This is Torso's figure.
- **Strain rate:** Materials' rate factor for 5052 honeycomb at fall speed (≈ 3–6 m/s) is 1.10–1.30 [EST band, T031_CHEST_CRUSH; Torso's fea_chest_pad uses the same]. Torso's own screen model applies it on top of the 19.5/22.3 lot band, so **dynamic plateau = 21.5–29.0 kN**. That is my R-146 number.
- The 22.35 "ceiling" was never rate-enhanced against quasi-static coupons, so **it is not an upper bound at fall rate. 29.0 kN is** (22.3 × 1.30).

## 3. Force-limited load through the cartridge (116 mm core, ID 341ef4a)
| item | value |
|---|---|
| plateau upper bound (lot top × rate 1.30, 0°) | **29.0 kN** |
| initial peak | **none**: pre-crushed per the R-072 lot rule, no initial peak. Incoming inspection must verify (a non-pre-crushed core peaks ~1.5–2× the plateau) |
| elastic rise to the plateau | ≈ 0.2 mm; no overshoot beyond the plateau |
| usable stroke 0.70 × 116 | **81.2 mm** (densification ≈ 0.75 t = 87 mm) |
| T-031 gate 1.03 kJ at the weakest dynamic plateau, 15° (19.5 × 1.10 × 0.93 = 19.9 kN) | 51.7 mm; at the weakest quasi-static (18.1 kN) **57 mm → margin 1.42× stroke** |
| worst defined fall energies | T-031 gate 1.03 kJ (envelope); R-146 L3 527 J (29 mm); L2 368 J (19–20 mm) |
| energy to bottom (81.2 mm × 18.1 kN weakest) | **≥ 1.47 kJ = 1.43 × T-031 gate**, about 2.8× the standing-tip PE → **bottoming is not credible** for any defined fall |
| off-axis | 15° ×0.93, 25° ×0.73 normal (the plateau drops); tangential friction μ ≈ 0.3 [EST]. At 25°: 21.2 kN normal + ≈ 9.9 kN tangential (tan 25° bound, the R-146 bond-check case) |
| edge/partial-face contact | a smaller crushing area gives a lower force. Worst for the structure is **full 29 kN at ±25 mm eccentricity** on the land (edge-biased crush) → moment ≈ 0.73 kN·m |
| bypass paths | head: pad skin moved +28 mm with the 116 core → head gap ≈ 42 + 28 ≈ 70 mm (fd981f1 + 341ef4a, ID to confirm) ≥ 57 + 11 needed → **PASS**. Shoulder/arm: falls > 25° go to the shoulder pad, i.e. LC2/T-030 (separate case). Chest onto a raised edge or step: still through the cartridge (force ≤ crush of the loaded area). Bulkhead/chin before the pad: no, the pad protrudes. **No credible bypass into the sternum at > 29 kN** |

## 4. Recommended design chest load (pick: **(b) corrected**)
- **Limit load P_L = 29.0 kN** normal on the land (dynamic ceiling; already includes lot top and rate; no further dynamic factor, since the cartridge truncates the pulse).
- **Ultimate P_U = 1.5 × P_L = 43.5 kN.**
- **Application:**
  - **LC1a:** 29.0 kN uniform pressure on the 101 × 101 land, normal (−x).
  - **LC1b:** the same 29.0 kN with the patch centre offset ±25 mm in z and in y (2 runs, edge crush).
  - **LC1c:** 25° oblique, 21.2 kN normal + 9.9 kN tangential (z down and y), on the land and the socket wall.
- **Pass criteria (replace the Job 3 gates):**
  1. At **P_L 29.0 kN: σ ≤ the fall allowable min(A-basis, Sy/1.1)** per part (R-127/R-128). Use the fall/limit convention like every other fall case, with **no extra SF**. For a 7075-T651 3 in bulkhead (A-basis ≈ 386 [= 257 × 1.5]) that means ≤ 386 MPa. Pelvis and posts per their bands. CFRP Tsai-Wu ≤ 1.0 / first ply failure ≥ 1.0. **No permanent set** at the land.
  2. At **P_U 43.5 kN: no rupture or collapse**: σ ≤ Ftu (A-basis), buckling eigenvalue ≥ 1.0 (i.e. **≥ 1.5 at P_L**), bonded joints ≤ the ultimate shear.
  3. **Stiffness:** k_land ≥ 5.3 MN/m → δ ≤ 5.5 mm at 29 kN. **Delete the 0.05 mm gate.**
  4. Fatigue: not applicable (a fall event; the cartridge is replaced after each).
- **Equivalence:** in stress terms (b-corrected) at 29 kN vs 386 MPa is ≈ as demanding as (a) 33.5 kN vs ~446 MPa (it sits between (a) and (b) as Torso phrased them). It drops the Job 3 SF 2 double-count, and it is consistent with R-146 and Torso's own screen model.
- **(c) bottoming:** not a design case (≥ 1.43× the gate energy needed). Keep it as a **robustness check only**: at P_U 43.5 kN (≈ 1.5× the rate-enhanced plateau) the structure must not rupture, i.e. criterion 2. No unbounded load is assumed.
- **(a) 33.5 kN:** drop as a label; it is superseded by P_U 43.5 kN ultimate / 29.0 kN limit.

**If Torso had defaulted** to "(b) spec + (a) check": the 22.35 × 1.5 = 33.5 check is unconservative vs the 43.5 ultimate, and 22.35 as the limit ignores rate (−23 %). Use 29.0 / 43.5.

## 5. Impact on Job 3/3b and cross-checks
- **Job 3 is still a FAIL by a wide margin under the corrected load.** Ligament 1576 MPa at 33.5 → ≈ 1364 MPa at 29 kN vs 386 fall allowable → SF ≈ 0.28. Buckling 1.00 at 33.5 → ≈ 1.16 at 29 kN vs ≥ 1.5 required. Land 58.5 mm → ≈ 51 mm vs 5.5. **The load is not the problem; the post/ligament and land support are (≈ 4–5× short).** Torso must redesign the bulkhead load path (the T031 hand calc assumed a 0.30 m simply supported rib, 198 MPa at 22.35; the FEA posts are carrying it differently). Rerun Job 3 at LC1a–c on the bryan PC.
- **R-146:** consistent. R-146 used the 22.35 quasi-static ceiling and 29 kN dynamic for g and structure. The bulkhead hand calc scales to 216 × 29/24.4 = **257 MPa ≤ 386 fall allowable** (hand calc PASS, FEA disagrees → FEA governs).
- **Cartridge spec (FEA_SPEC_chest_pad, 116 mm):** stroke 81.2 mm, ≥ 10 % margin required → T-031 at 57 mm uses 70 % of stroke. PASS. Its "quasi-static ceiling ≤ 22.35 kN" pass line should add **"dynamic plateau ≤ 29.0 kN at 5.7 m/s"** (drop-tower coupon at fall rate). This verifies the 1.30 rate factor, the one [EST] input that sets P_L. If drop coupons show a rate factor > 1.30, P_L = 22.3 × measured factor.
- Pack: pack g and rails in R-146 already used up to 29 kN. Unchanged.

## 6. Open inputs
- A measured rate factor for 5052 4.5 pcf at 3–6 m/s (dynamic coupon, G5): this sets P_L.
- A-basis allowable for the actual bulkhead stock (257 × 1.5 assumed).
- ID to confirm the head gap with the 116 core (≈ 70 mm).
