> **SUPERSEDED 2026-10-14 (L48):** the tibia saddle (and the femur spreader/strap, Actuators fbe0def) are dropped per Thermal 9b9e169. Heat path = axial fins on the knee twin housing (D85). See §0.

# Legs knee thermal note: D69 saddle, P-041 breaks, A40 gait suggestions (2026-10-14)

## 0. Current (L48): housing fins, fin envelope (knee_fin_sweep.py -> results/r031/knee_fin_envelope.json)
- Sweep: knee 0-135 in 15 deg steps (screw stroke follows the linkage), housing surface vertices vs tibia/shank, thigh, trunnion cheeks and bracket, rods, right leg and knee-cap keep-out. Point-to-solid distance is used, which is conservative. Margin 3 mm.
- Allowed fin radial height (about the screw axis, 0 deg = front):
  - Front, 330-030: 12 mm at the trunnion end, 54-56 mm mid-length.
  - Diagonals 030-060 and 300-330: 7.6 mm at the trunnion end, 40 mm mid.
  - Rear, 150-210: 28 mm at the trunnion end, 57 mm mid. Rear diagonals 120-150 and 210-240: 28-30 mm at the end, 37 mm mid.
  - Outer +-y flanks, 060-120 and 240-300: none. The trunnion cheeks sit at 0 gap and the rods exit there.
  - Every trunnion-end limit is our knee trunnion bracket top plate [EST] at 135 deg. It can be reshaped if Actuators needs more height there.
  - Tibia, knee cap (>=150 mm), the other leg and the rods away from their exits never limit.
- Caveat: tessellation is coarse (2 mm tolerance; vertices concentrate at edges), so treat these as screening values. Actuators should re-check with the D85 CAD.
- Mass: fins 0.05 kg/knee [Thermal EST] (growth to 0.12). The knee is now +0.164 motor + 0.04 housing + 0.05 fins = **+0.254 kg/knee, +0.508 robot** (was +0.64), i.e. -0.13 kg robot (up to +0.00 at the 0.12 growth).

## 1. D69 + Thermal 26412c7: clamp-on 6061 finned saddle (replaces the bolted pad)
- **Placement** (shank frame, model_v4):
  - Tibia ø45 at x 14. Saddle z **320–415** (95 mm). The bottom sits ≥ 150 mm above the tibia collar top (tibia bottom z 136, collar ≈ 136–170).
  - The top is below the knee rod-end eyes, which sweep down to z 420.
- **Clearance** (swept ankle −45…+40 × roll ±18, box run):
  - The ankle screw bodies come to x ≥ 45.6 at z 320–400 and x ≥ 39.4 at z 400–420.
  - So the front sector carries **no fins**. Front wall ≤ 3 mm (x ≤ 39.5), chamfered at z > 400.
  - The 10 axial fins (95×20×1.5–2) go on the rear and sides, r ≤ 47.
  - Wetted area ≈ 10 × 2 × 0.095 × 0.020 = 0.038 m² plus the base: about **0.04 m²** (meets the ≥ 0.04 target).
- **Clamp:**
  - Split-C saddle, slot at the rear, 4× M4 (8.8) across the slot at ≥ 2 kN each.
  - Bore Ø45 H8, wrap ≥ 330°. The 40×60 gap pad (3 W/mK, 0.5 mm) sits in a 0.35 mm recess, so the metal lands still conform.
  - **No tube holes.**
  - The knee drives bolt to the saddle's flat rear face with a thin TIM, not to the housing.
- **Tube check under the clamp** (hand, [EST]):
  - Uniform pressure p = 8 kN / (95 × 45) = **1.9 MPa**, giving hoop stress pD/2t = 1.9·45/2.4 = **35 MPa compressive**.
  - The stress is static, so it adds no amplitude. A compressive mean is benign in Goodman.
  - External-pressure collapse (long-tube bound) is E/(4(1−ν²))·(t/R)³ = 3.3 MPa at 1.2 wall, SF 1.7. With P-047's 1.6 wall it is 7.8 MPa, SF 4.1. The short clamped length raises both.
  - **Condition:** the full-wrap conforming bore is required. With a pad-only line contact (2 × 120° patches), ring bending reaches several hundred MPa, which fails.
  - Fatigue: walking bending of the tibia sees the saddle ends as a stiffness step. Fix: 0.1 mm bore relief over the last 8 mm at each end, plus an anodized bore and MoS2 against fretting. The saddle sits inside the P-047 1.6 mm wall zone. T&R brief item 4 adds the saddle-end Kt.
- **Mass:** about **+0.32 kg/knee** (Actuators D69 motors +0.164 + housing +0.04 + saddle and fins about 0.12 [Thermal EST]), **+0.64 robot**.
- **Heat path vs P-040…P-044:**
  - Winding → housing → knee trunnion pins (PTFE washers = thermal break, so no heat to the thigh or the bonded thigh collar).
  - Housing → saddle, via a short flexible graphite (PGS) or braided strap across the trunnion. The housing pivots on the thigh trunnion, so a rigid bolted housing→shank pad is kinematically impossible. **Thermal and Actuators must size the strap** (it is in series with the 0.69 W/K).
  - Saddle → air. Tibia → collar attenuated to ≤ 42 °C (Thermal §3), which passes the 60 °C bond limit. The tibia collar uses the same DP490 spec and 60 °C rule (BOND_SPEC; confirmed by Legs).
  - P-041 (thermal breaks): G10 at the hip_pitch screw-to-thigh-clamp-collar joints only. G10 flanged bushes in the clamp eye tines, 1.5 mm, about 6 g per joint, 2 per leg: **+0.024 kg robot [EST]**. The knee needs none (PTFE + saddle path).
  - P-041 bolted variant (if a collar face joint is used): G10 1.5 mm under an M6 → joint stiffness ≈ ×0.5, load factor 0.22 → 0.36.
    - Creep/embedding 2–5 µm → preload loss ≈ 5–12 % [EST].
    - Fixes: hardened washers, re-torque after the first thermal cycle, Belleville stack.
    - Materials (A37) to confirm G10 vs PEEK. PEEK (E 3.6 GPa) is not recommended in a bolted stack because of creep.

## 2. Gait suggestions for Controls (A40: knees derate at 9–10 min at 1.2 m/s)
Data: `legs/results/walk_{0p8,1p0,1p2}.npz` (ID plans) and `legs/grokbuild/results/walk_trace.npz` (WBC r6).
| source | knee RMS τ N·m | peak | mean knee flexion |
|---|---|---|---|
| ID plan 0.8 | 65–69 | 131 | 64° |
| ID plan 1.0 | 68–73 | 142 | 63° |
| ID plan 1.2 | 71–76 | 154 | 61° (min 34–38°) |
| **WBC r6 1.2 (the A40 input)** | **105–108** | 206 | — |
- **The A40/D69 thermal case uses the failing r6 WBC trace.** Its knee RMS is 1.45× the ID plan, so copper loss is about 2.1×. Re-run A40 on the ID-plan or ref_m12 torques, or on a passing controller trace, before sizing hardware.
- The plans walk crouched, with about 61–64° mean knee flexion at pelvis z 1.04. Knee torque scales roughly with sin(flexion) × load.
  - Raising the CoM height and straightening the stance knee to about 15–25° should cut stance knee τ substantially. This needs an in-sim check; it is not computed here.
  - Cost: the knee is closer to singular, so swing-height and impact compliance must come from the ankle and hip.
- Longer DS (0.25–0.32) spreads load (r7 already shows this) and lowers peak τ. Avoid the r6 bounce/flight: impacts raise RMS.
- A slightly lower step frequency with a longer step at the same speed reduces the swing-knee accelerations. Check it against the A40 model.
- Toe-off: use the ankle (pitch has thermal margin, 88 °C) rather than knee extension for push-off.

## 3. Knee cooling options (Actuators/Thermal)
1. **Saddle (selected, above).**
2. Housing vents per A35 (h ≥ 15): Thermal shows about 83 °C winding.
3. Fallback fan (D69 (a)+(d), +0.25/knee) only if the saddle strap can't reach 0.69 W/K.
4. Lower knee RMS via gait (§2). Free on mass, and it may make D69 (a) partly unnecessary. **Recommend re-running A40 first.**
