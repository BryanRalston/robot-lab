# Legs R-031 fixes: P-046…P-050 + hip_pitch lever fatigue (2026-10-14)
Hand checks only (box light-work rule). Converged FEA goes to T&R on the bryan PC: brief `grokbuild/r031_fatigue_fea_brief.md`. Se = 87 MPa corrected, allowable amplitude 58 MPa (R-031 §6). All Kt and masses are [EST] until FEA/CAD confirm them.

## Hip_pitch lever (T&R §1, Actuators GROKBUILD_lever_fea_v2 Amendment 1)
- Load: 2030 N/pin at walk 1.2, fully reversed; 4542 N/pin design.
- G2 as briefed: b 25, d0 30.
  - Arm nominal stress 50.9 MPa at design. FEA peak ≈ 335 MPa → effective Kt ≈ 6.6.
  - Walk amplitude ≈ 150 MPa vs 58 allowed.
  - The hot spot is the bore-lip/cap re-entrant notch, not arm bending.
- Section family (`hp_lever_family_r031.py` → `results/r031/hp_lever_family.json`):
  - Sweep: b 25–35 × d0 30–40 × root blend R8/R12.
  - Cap merged into a full-depth web: no step between the bore cap and the arm. R ≥ 8 blends on both concave sides. Bore lip chamfer 1×45 plus an R1 edge.
  - Material: 7075-T6, with 17-4PH H1025 as the fallback.
- **Pick: 7075-T6, b 30, d0 36 (d1 19), R8 cap/arm blends.**
  - Hand amplitude 26.3 MPa at Kt 2.0. If the notch Kt of 6.6 survived, it would be 86.8 MPa, which fails.
  - Δmass +0.09 kg robot (2 levers) [hand EST]. **Superseded by L47-R: +0.430 kg robot measured on the RC STEP vs the booked sf15 part.**
- Fallback if FEA shows the notch remains: b 35, d0 40.
  - 57.4 MPa even at Kt 6.6.
  - +0.18 kg robot, which is < 0.25, so **steel is not needed**.
  - 17-4PH would cost about +0.25–0.3 kg robot (density 2.8×), so it is held only if the converged Kt > 6.6 at b35/d0 40.
- Envelope check needed (Actuators): b grows in x (the screw axis). Keep |y| ≤ 38.5 inside r < 34, ≥ 1 mm to the rod-end eye and RV12 sweep, and the arms ≥ 30° off the femur axis (L35).

## P-046 clevis and clamp Goodman at Se 87
- Clevis (R-023: 147 MPa design peak, pulse).
  - Goodman is 1.03 now. Reaching 1.5 needs the alternating stress ×0.69.
  - Fix: cheek thickness 14 → 17 mm (Z ∝ t², ×0.68) and fillet R6 → R8.
  - About +0.03 kg/leg, +0.06 robot [EST].
- Clamp (scaled ~1.1).
  - Fix: arm root 24 → 28 mm deep (Z ×1.36 → ~1.5) on the existing collar footprint.
  - +0.01/leg [EST].
- Both go in the converged FEA brief.

## P-047 tube walls outside the doubler
- Rule: SF ∝ t^1.35 (R-023).
- Femur 1.2 → 1.6 mm: SF 1.07 → 1.58.
  - Material 7050-T7451 (approved, R-031 §6.2): same density class, better fatigue/SCC. Applied in model_v4 (name and wall).
  - +0.035 kg/leg.
- Tibia ø45 1.2 → 1.6 mm: SF 1.03 → 1.52. +0.04 kg/leg.
- The sleeve stays as the doubler. Sleeve ends get a 15° taper for peel.
- Total about +0.15 kg robot [EST].

## P-048 femur tongue
A16 ø6 dowel through the tongue and tube (42CrMo4, +0.005/leg). Bore-opening contact check goes in the FEA brief.

## P-049 foot collar OD edge
- Collar OD edge gets an R2 plus a 10° taper.
- Fretting: steel flange to 7075 gets an anodize + MoS2 interface.
- Goes in the FEA brief.

## P-050 DP490 per-lot coupon test
- Per lot: 5 lap-shear coupons (ASTM D1002), tested at 23 and 60 °C, with the adherends prepared the same way as the part.
- Accept ≥ 80 % of the BOND_SPEC value. Added to G5.

## Mass (Legs R-031)
| item | robot kg |
|---|---|
| lever pick (Actuators part, our spec) | **+0.430 robot, L47-R (RC STEP 0.4642 vs booked sf15 0.2492)** |
| P-046 | +0.08 |
| P-047 | +0.15 |
| P-048 | +0.01 |
| **total** | **+0.33 (+0.42 fallback) [EST]** |
