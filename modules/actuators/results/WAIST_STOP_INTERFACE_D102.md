# D102 — waist-pitch actuator data for the P-160 yoke hard stop (T&R 3eacd56), 2026-10-21 ~11:20 ET
Script: waist_stop_interface_d102.py → waist_stop_interface_d102.json. Stop loads: 1.55 kN·m design / 2.3 kN·m ultimate (~10 kN per lug).

## 1. Gear
**Harmonic Drive CSG-25-100 component set** (strain wave, ratio 100), driven by a TBM2G-06808A. Source: CONTRACTS.md waist_pitch row (output peak 115.4 N·m; sim v3 ctrlrange 116).

## 2. Torsional stiffness (HD CSF/CSG catalog Table 43, ratio ≥ 80, size 25, p.50)
- Stiffness segments: T1 14 N·m, K1 3.1×10⁴ N·m/rad. T2 48 N·m, K2 5.0×10⁴. K3 5.7×10⁴ (catalog average values).
- Wind-up angle at each torque level:

| torque | 14 (T1) | 48 (T2) | 87 (rated) | **204 (repeated peak)** | 369 (momentary) | 650 (ratchet) |
|---|---|---|---|---|---|---|
| wind-up | 0.026° | 0.065° | 0.104° | **0.222°** | 0.388° | 0.670° |

## 3. Lost motion
Hysteresis loss 2.9×10⁻⁴ rad = **1 arc-min = 0.017°** (Table 44, size 25, ratio ≥ 80, p.50). Strain-wave gears have no gear backlash.

## 4. Torque limits (CSG rating table, CSG-25-100 row; Tables 6/7, p.16)
| limit | value |
|---|---|
| rated | 87 N·m |
| **repeated peak** (start/stop) | **204 N·m** |
| average limit | 140 N·m |
| **momentary peak** | **369 N·m** |
| **ratcheting** | **650 N·m** |
| buckling | 1700 N·m |
| motor peak at the output | 115.4 N·m |

## 5. Output bearing: IKO CRBH 6013 A (size.py BEAR[25]; IKO CRB catalog CRBH table, eq. (2))
- Ratings: C 18.8 kN, C0 24.3 kN. Dpw ≈ 75 mm [EST: (d+D)/2].
- **Allowable tilting moment** (static, Fr = Fa = 0): **M = C0·Dpw/2 = 0.91 kN·m at fs 1; 0.61 kN·m at fs 1.5.**
- **Combined load:** Fr + 2M/0.075 + 0.44·Fa ≤ 24.3 kN / fs. For shock, fs ≥ 1.5, the right side is 16.2 kN.
- A single 10 kN lug reacted as radial load on the bearing gives fs 2.43.
- **The 1.55/2.3 kN·m stop moment must not pass through this bearing as a tilting moment: it is 1.7–2.5× the static rating.** The stop must react torque about the pitch axis as a couple (2 lugs, or lug plus yoke) in the yoke structure. Any axial offset e between a lug and the bearing plane adds M = F·e (10 kN × 30 mm = 0.3 kN·m).

## 6. Stop stiffness, gap budget, deflection
**Case A — input locked** (brake or held rotor; the stop works in parallel with the gear):
- The stop must engage before 0.222° of output rotation (gear wind-up at the 204 N·m repeated peak), counting gear lost motion.
- **Recommended budget: total gap plus lost motion ≤ 0.10°.** The physical gap is ≤ 0.083° after the 0.017° lost motion. That is **0.15 mm at a 100 mm lug radius**, so a shimmed or zero-clearance stop is needed.
- **Stop stiffness ≥ 634 kN·m/rad (≈ 11 kN·m/°).**

| external torque | output rotation | stop deflection | gear torque | stop torque |
|---|---|---|---|---|
| 1.55 kN·m | 0.222° | **0.122°** | 204 (= repeated peak) | 1346 N·m |
| 2.3 kN·m | 0.284° | **0.184°** | 266 (≤ momentary 369, ≤ ratchet 650) | 2034 N·m |

- Bottoming angle: the stop is metal-rigid. Bottoming is at the gap; above 1.55 kN·m the gear exceeds repeated peak but stays ≤ momentary.

**Case B — as built (no brake: SAFE_SIT_HOLDING D94).** The input is not locked, so the gear torque = motor torque + rotor inertia reaction:
- **Static:** the current limit caps the gear at 115.4 N·m < 204. The stop takes the rest at any gap. The wind-up budget only applies if a brake or position-hold is added.
- **Dynamic:** the rotor (J_refl = 0.239 kg·m², Jm 0.239 kg·cm², TBM2G §9.4.1 p.272) winds the gear when the output stops.
  - **Rigid stop, impact torque = ω·√(J_refl·K3) = 117 N·m per rad/s** of joint speed at contact.
  - Speed limits at contact: 0.76 rad/s to stay at repeated peak with the motor on; 1.75 rad/s with the motor off; 2.17 rad/s momentary (motor on); 5.57 rad/s ratchet.
- **Soft stop** (Ks ≪ K_gear): gear torque = T_motor + T_stop·J_refl/(I_body + J_refl). With I_body ≈ 3 kg·m² [EST]: **230 N·m at 1.55 kN·m and 285 N·m at 2.3 kN·m with the motor at peak**, against the 204 limit. With motor torque zeroed at the stop it is 115 / 170 N·m.

## What T&R / Torso must change
1. **Torso:** react the stop torque as a couple in the yoke, not as a tilting moment through the CRBH 6013 A (allowable 0.61 kN·m at fs 1.5). Keep lug-to-bearing-plane offsets small and check Fr + 2M/Dpw + 0.44Fa ≤ 16.2 kN.
2. **T&R:** treat the gear as current-limited (115 N·m static) plus rotor inertia, not as a locked spring. Case A applies only if a brake is ever added: then gap ≤ 0.10° total and Ks ≥ 634 kN·m/rad.
3. **Controls/T&R:** to keep the gear ≤ 204 N·m at a stop event, either cap the joint speed at contact (≤ 0.76 rad/s rigid with the motor on) or zero the waist-pitch torque in the stop zone (≤ 1.75 rad/s). A compliant stop with motor-off allows full 1.55 kN·m at 115 N·m on the gear.
4. **2.3 kN·m ultimate:** the gear stays under momentary (369) and ratchet (650) in every case above. Inspect for ratcheting after an ultimate event.

## Rev b (~11:30 ET): drivetrain inertia, tripped-waist impact at 6.3 rad/s (Controls)
- **Input inertia:** motor rotor Jm 0.239×10⁻⁴ kg·m² (TBM2G manual §9.4.1, p.272) + CSG-25 wave generator 0.413×10⁻⁴ kg·m² (HD catalog Table 3, "moment of inertia, reflected to the wave generator (gear input)") = 0.652×10⁻⁴ kg·m². Encoder ring and hub are not included [EST, < 5 %].
- **Reflected to the output (× 100²): 0.652 kg·m².** This supersedes the rotor-only 0.239 in Case B above.
- **Drivetrain kinetic energy at 6.3 rad/s output: 12.9 J.**
- **Rigid stop (output halted; the inertia stops through the gear's own stiffness):**
  - T = ω·√(J·K3) = 6.3 × 193 = **1215 N·m** (piecewise-energy check 1214). **1330 N·m with the motor at peak.**
  - Gear strain energy is only 1.2 J at momentary (369) and 3.7 J at ratchet (650), against 12.9 J.
  - **Verdict: exceeds momentary (3.3×) and ratchet (1.9×) and reaches 0.71–0.78 of buckling (1700).** A rigid stop at 6.3 rad/s ratchets the CSG-25 even with the motor off.
- **Corrected speed limits at a rigid stop, motor off:**
  - 1.06 rad/s for repeated peak 204;
  - 1.91 rad/s for momentary 369;
  - 3.37 rad/s for ratchet 650.
  - With the motor at peak, subtract 0.60 rad/s (115 N·m ÷ 193).
- **Compliant stop instead** (Ks ≪ K_gear; the output and drivetrain decelerate together): gear torque = T_stop·0.652/(I_body + 0.652). With I_body ≈ 3 kg·m² [EST]:
  - 1.55 kN·m: **277 N·m** (> 204, < 369 momentary);
  - 2.3 kN·m: **411 N·m** (> 369, < 650 ratchet).
  - Add 115 N·m if the motor is still at peak: 392 / 526.

### Changes this adds for T&R / Torso / Controls
1. **The P-160 yoke stop must be compliant and energy-absorbing, not rigid metal.** It must absorb (I_body + 0.652)·6.3²/2 ≈ **72 J [EST, I_body 3]** with a peak ≤ 1.55 kN·m design. Its stiffness must be low enough that the deceleration time ≫ the gear-drivetrain period (2π√(0.652/5.7e4) = 21 ms). The rigid-stop Case A (634 kN·m/rad, 0.10° gap) applies only to static holding with a brake, never to the tripped-waist impact.
2. **Controls:** zero the waist-pitch torque on a trip. At 2.3 kN·m ultimate the gear still exceeds momentary (411), so the 2.3 kN·m event is an inspect/replace event (ratchet check).
3. Option if the gear must stay ≤ momentary at ultimate: a torque limiter (slip clutch, about 300–350 N·m) between the gear output and the yoke, or a softer stop that holds the peak ≤ 1.9 kN·m.
