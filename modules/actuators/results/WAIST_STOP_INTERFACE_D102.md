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

## Rev c (~11:45 ET): integrated torque limiter (T&R final spec + overrides). Supersedes the rev b recommendations
**Basis.** Torso inertia 1.44 / 3.52 kg·m² (T&R); drive 0.652 kg·m² (rev b). Elastomer-only stop fails: gear share 0.30–0.37 caps the stop peak at ≈ 550–660 N·m, which needs 13–27° of travel. **Rev b's 277 N·m used I_body 3.0 [EST] (share 0.179). T&R's 0.296 static split is correct for 1.55 kg·m², and the dynamic share is higher (0.33–0.40).** Off-the-shelf limiters are too heavy: Mayr ROBA-slip hub size 2 Type 100.21_ (130–250 N·m, ø88 × 57 mm, 1.6 kg; Mayr K.123.V16 p.6) and Torso's EAS-compact size 2 (+2.77 kg).

### Topology
motor → CSG-25 → **friction limiter** → yoke/torso. **The PU end stops act torso ↔ pelvis**, on the torso side of the limiter. When the torso hits a stop, the drive inertia (0.652) can only decelerate through the limiter slip torque Tc. The gear torque is therefore capped at Tc plus the small inertia of the output node; the drive energy goes into limiter slip, not gear wind-up.

### Design (CAD: waist_clutch_cad_d102c.py → cad/waist_torque_limiter_d102c.step, results/waist_torque_limiter_mass_d102c.json)
- **Friction annulus ø90 / ø66** (inside the ø100 keep-out). 2 faces; mean friction radius 39.3 mm.
- Stack: CSG-25 output flange | sintered-bronze lining | 42CrMo4 yoke slip ring with 3 drive lugs | lining | pressure plate (7075 body with a 1.5 mm steel face) | **Belleville DIN 2093 Group 2 Series B, 80/41/3 [EST: confirm F(s) in the DIN EN 16983 table]** | M68×1.5 7075 lock-nut ring. Stack length 23 mm axial.
- **Friction pair:** sintered bronze on steel, dry. μ 0.15–0.45 range (Shigley, Mechanical Engineering Design, friction-material table, sintered metal dry [verify edition/table]); μ_design 0.30.
- **Clamp force:** F = Tc/(2·μ·r_m) = 170/(2 × 0.30 × 0.0393) = **7.2 kN**, at s ≈ 0.55·h0 on the flat part of the Belleville curve.
- **Slip-torque set:** **Tc = 170 N·m**, set by measured break-away on a bench (not by nut angle). Tolerance ±10 % for run-in, humidity and μ: **153–187 N·m**.
  - Margin over the 115 N·m operating peak: 153/115 = 1.33.
  - Under 204: 187 gives a dynamic gear peak of 193 (below).
- **Mass (CAD volume):** linings 2 × 0.039, slip ring 0.107, steel face 0.042, 7075 plate 0.040, Belleville 0.087, nut ring 0.021, pins/bushing 0.019 = **0.394 kg** (≤ 0.4, 2 % margin).

### Dynamic proof (3-DOF time domain: waist_clutch_d102c.py)
Model: drive 0.652 through the nonlinear CSG-25 stiffness (Table 43) → output node Jo 1e-3 [EST] → stick/slip clutch (Kc 2e5 N·m/rad, slip at Tc) → torso → PU stop (D575 curve ×1.3 [EST]). Both directions are covered by the motor at 0 / +115 / −115 N·m.

| case | torso | gear peak | stop peak | limiter slip / energy | no limiter |
|---|---|---|---|---|---|
| **governing fault: 8.32 rad/s unpowered, Tc 153/170/187** | 1.44 | 159 / 176 / **193** | 1.12–1.14 kN·m | 11.5–16.1°, 37–43 J | gear 422 |
| same | 3.52 | 156 / 173 / **190** | 1.70–1.71 kN·m | 6.1–11.5°, 20–31 J | gear 315 |
| 7.0 rad/s (motor 0 / +115 / −115) | 1.44 | 177 / 179 / 181 | 1.03–1.11 kN·m | up to 50°, 149 J (motor +) | 462 |
| 7.0 rad/s | 3.52 | 174 / 176 / 175 | 1.54–1.66 kN·m | up to 41.5°, 123 J (motor +) | 290 |
| 7.0, Tc band 153 / 187, motor + | 3.52 | 159 / **193** | 1.65–1.67 kN·m | 59° / 31°, 156 / 101 J | — |
| **routine powered TUCK 2.5–4.1 rad/s** (Controls 19f27ef) | 1.44 / 3.52 | 114–177 | 0.31–1.05 kN·m | 0–17.7°, ≤ 53 J | 172–257 |

**The gear stays ≤ 204 N·m in every case** (max 193, at the Tc +10 % edge). Without the limiter it reaches 257–462 N·m: over repeated peak, and over momentary 369 at 7–8.3 rad/s with the 1.44 torso.

- The PU stop (Torso) for the 324 J gate must be sized with E25 ≥ 356 J and 25 % at ≥ 0.30 rad (17°). Its peak is then 1.7 kN·m ≤ 2.5 with no bottoming (strain 0.14). The stop, not the limiter, carries the 324 J; the limiter sheds ≤ 43 J unpowered and ≤ 156 J if the motor drives into the stop.

### Heat and wear
- **Worst case, all 324 J into the limiter** (bound): steel/bronze friction mass 0.227 kg × ≈ 450 J/kg·K gives **ΔT bulk ≈ 3.2 °C**.
  - Flash rise: q = Tc·Δω/A = 170 × 8.32 / 5884 mm² = 0.24 W/mm² for ≤ 0.1 s gives **≈ 5–7 °C** (semi-infinite steel).
  - Sintered bronze limit ≈ 300 °C. **No overheating; mass is not heat-bound.** The minimum mass that works is the CAD 0.39 kg, set by stiffness and strength, not heat.
- **Wear** [EST energy-based rate 0.2 mm³/kJ for dry sintered metal]:
  - Routine event (≤ 53 J): 3.6 nm per face.
  - Fault (324 J): 22 nm.
  - Allowance: 5 % preload loss = 0.36 kN / ≈ 5 kN/mm Belleville rate = 0.036 mm per face → **≈ 10 000 routine events or > 1000 fault events before re-torque.**
- **Inspection rule:**
  - Log limiter slip (output encoder vs motor encoder × N).
  - Bench-check break-away torque (153–187) at each service, after any fault event > 100 J, or when cumulative logged slip energy exceeds 10 kJ. Re-shim or re-torque the nut if outside the band.
  - **The joint absolute encoder must read the yoke side of the limiter** (AksIM-2 ring on the yoke, not the gear output). Otherwise a slip leaves a position offset. Re-engagement is automatic (friction): no reset is needed, but re-home and compare encoders after a slip.
- **Rotary damper (one line):** a viscous damper sized for 324 J at ≤ 204 N·m gear share runs ≈ 0.6–1.0 kg [EST], is speed-dependent and offers no hard torque cap. Rejected.

### Can the drive brake at 3–11 rad/s output? (Controls' 2.8 rad/s [EST])
- **CSG-25-100 input limits** (HD Table 3, grease): max input 5600 rpm (**5.86 rad/s output**, momentary); limit for average input speed 3500 rpm (**3.67 rad/s**).
- **TBM2G-06808A** (§9.4.1 p.272): Nmax 8000 rpm (8.4 rad/s output); Ke 10.4 Vrms/krpm cold (14.7 V peak line-line/krpm), 9.24 hot; Tp 1.54 N·m → 115 N·m at the output.
- **Bus 84 V** (D3) on G-TWI R50/100 (max supply 95 V, MAN-G-TWI Table 3 / install guide):
  - Controlled torque (EMF ≤ 0.96 × bus) up to ≈ 5.5 krpm = **5.75 rad/s**.
  - EMF reaches 95 V at 6.5 krpm cold (6.8 rad/s).
  - At 8.32 rad/s (7.9 krpm) EMF is 117 V cold / 104 V hot, **above the drive's 95 V absolute max**. This needs a regen sink: battery charge acceptance, or a bus clamp/shunt.
- **Answer:** active braking is possible up to ≈ 5.7 rad/s (bus-limited), with the gear's grease momentary limit at 5.9 rad/s. **Controls' 2.8 rad/s is conservative but uncited. The cited figures are 3.67 rad/s average (gear) and 5.75 rad/s (bus).** Above ≈ 6.8 rad/s back-driving can over-volt the drive, so tripped 7–8.3 rad/s events also need the regen clamp. Braking cannot replace the limiter: the braking torque (≤ 115 N·m) is below the stop loads and does not cap gear wind-up at contact.

## Correction 2026-10-21 (after Torso c2db98c)
The 356 J PU stop gate double-counted. 216 J already includes ×1.5 on ½(3.52+0.652)·8.32² = 144 J, and the drive inertia (0.652) sheds its energy through limiter slip, not the PU. **PU stop gate = 1.5 × ½·3.52·8.32² = 183 J** (torso only). Torso's wing stop at 1.19 kN·m peak / 0.71 kg meets it. The gear peak stays ≤193 N·m (set by slip torque + drive inertia, independent of stop stiffness). P-162 brake reaction: use a bolt circle or keep the pin ≤14 mm from the CRBH plane (tilt 0.63 vs 0.61 kN·m).
