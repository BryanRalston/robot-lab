# D98 — r75 PU knee stop: sizing, placement, sweep, armature (2026-10-21, ~10:20 ET)
Scripts: knee_stop_pu_d98.py (→ knee_stop_pu_d98.json, cad/knee_stop_pu_r75_d98.step), knee_stop_sweep_d98.py (→ knee_stop_sweep_d98.json).

## 1. Armature (answers 0.553 vs sim/v3 0.2018)
- sim/v3 0.2018 = **one** TBM2G-06808 rotor (Jm 0.239 kg·cm², tbm2g §9.4.1) × N≈92² (old v3 knee). Stale: wrong motor, one rotor, wrong ratio.
- Twin TBM2G-07613D (Jm 0.576 kg·cm², tbm2g p.284) + 0.2 kg·cm² hub each [EST]: J_refl(q) = 1.552e-4 × N(q)², N(q) = 2π·arm(q)/5.
- **Flex sign resolved from model_v4:** knee axis +y, q>0 moves the shank to −x (q 90: shank x −420…28), +x forward (toe +130). → arm falls to 18.4 mm at 135°.

| knee ° | 0 | 30 | 60 | 75 | 90 | 120 | 133 | 135 | 143.6 |
|---|---|---|---|---|---|---|---|---|---|
| J_refl kg·m² | 0.079 | 0.314 | 0.524 | 0.553 | 0.506 | 0.230 | ~0.10 | 0.083 | 0.027 |

- 0.553 is the 75° peak only. At the stop, use ≈0.08–0.10. Physical stop energy at 6.37 rad/s = **57.0 J** (body 2.71 kg·m², rotor ≈1.9 J) [EST]. Design basis kept at **66 J**.

## 2. Sizing (66 J × ≥1.4 within 25 % strain; 25 % at ≤143.6°)
- At contact 135°, 25 % at 143.6° allows only 45 mm of PU. With ≥1.4 margin, that gives **1027–1036 N·m at 66 J**, not 830. Even with zero margin it gives ≥861 N·m. **830 N·m at 66 J is not reachable with contact at 135°.**
- **Chosen design: contact at 133°.** 2 stacks, each 28 (y) × 21 (radial), with 6 × 9.25 mm PUR90A layers, 5 × 1.5 mm steel shims, 2 × 3 mm 7075 end plates and a ø6 guide pin. Stack length 69 mm, centroid r 75 mm. Shape factor 0.62 per layer. V = 62.1 cm³.

| energy | strain | knee ° | pad force (2 stacks) | knee torque |
|---|---|---|---|---|
| 57.0 J (physical) | 19.5 % | 141.3 | 10.4 kN | 779 N·m |
| 62.7 J (T&R basis) | 20.5 % | 141.7 | 10.9 kN | **815 N·m** |
| **66 J (design)** | 21.0 % | 141.9 | 11.1 kN | **834 N·m** |
| **92.5 J (bottoming, 25 %)** | 25 % | **143.6** | 13.0 kN | 978 N·m |

- **Bottoming energy is 92.5 J** (T&R guessed ~97). Energy SF vs 66 J = 1.40; vs 62.7 J = 1.48.
- Cost: free flexion ends at 133°, not 135°. The Controls stop-speed basis assumed contact at 135° (6.37 rad/s); at 133° the speed is ≤ that [EST].
- Alternatives (same script): contact 132° → 761 N·m; 131° → 701 N·m (T 66 mm). Contact 135° → 1027 N·m.
- Quasi-static; PU rate stiffening not included [EST]. Buckling of the 69/21 stack is held by the guide pin and shims [EST, Gallagher].

## 3. Rotor reaction on the stop (sign, in the knee frame, +q = flexion about +y)
- On the stop the knee decelerates (α ≈ −297 rad/s² at 66 J). The rotors are still spinning in the flexion sense, so slowing them pushes the shank in **+flexion: +29.7 N·m**. This is part of the inertia the pad absorbs, so it **adds to the pad load** (already counted via I_body + J_refl).
- Screw: L(q) shortens with flexion (dL/dq = −0.35 mm/° at 133°). The rotor reaction therefore puts the screws in **tension: ≈1.47 kN for the pair, 0.73 kN per screw** at the 18–20 mm arm.
- A motor driving peak extension pushes the screws in **compression** (7.27 kN pair, D96). **The rotor term opposes the motor term and relieves the screw axial load on the stop.** For the screw it is excluded from the upper bound, as T&R B3 has it. Worst case per screw = motor peak 3.63 kN = 0.13 C0a (27.3 kN). The rotor alone is 0.03 C0a.
- Phase 1 (sudden flexion before the stop, rotor accelerating): the sign reverses and the rotor resists flexion (T&R's 5.18 kN pair at 47.5 mm is unchanged).

## 4. Placement and sweep (model_v4 + r116b housing, Legs L78 method, gate 3 mm)
- Centre (y 108–152): gap from the tibia front to the femur rear at r75 is only ~20–30 mm, so a 69 mm stack does not fit. Rejected by geometry.
- L78 outboard boxes (y 62–102/158–198): clash with the lever, rods and eyes (L78, 0.0 mm).
- **Chosen: stacks outboard of the knee screws, at y 32–60 and 200–228.** They are thigh-fixed on 7075 seats, joined by an 8+10 mm bar to a femur collar at about z 600. Strikers are 7075 lugs at r75 on arms from the tibia sides. Three striker-face offsets were swept: t0 = −4, −20 and +10 mm from the 133° plane.

| t0 | worst non-contact gap | result |
|---|---|---|
| −4 | **0.0** striker ↔ R ankle trunnion plate (hip yaw 45, knee 90) | FAIL |
| +10 | **0.0** same | FAIL |
| **−20** | **11.8** pad ↔ knee lever (knee 120). Strikers ↔ ankle screw bodies ≥ 6.4 (ankle −45…30, roll ±18) | **PASS** |

- t0 −20 other minima: pad ↔ ankle screw bodies 13.7 (knee 143.6, ankle −45), pad ↔ rods/eyes 19.0, seat bar ↔ rods 21.2, R-leg plate 12.0.
- Pad ↔ own striker is 2.3 mm at 131°, which is the intended approach (contact at 133°). Poses swept: knee 0–143.6, ankle pitch/roll extremes, hip pitch −100/+20, hip roll −20, hip yaw 45.
- [EST] The seat bar and collar are envelope boxes. Legs owns the collar detail.

## 5. Mass
0.403 kg per knee: PU 70 g, shims 69 g, end plates 27 g, strikers + arms 112 g, seats 48 g, collar bar 80 g [EST]. **0.807 kg robot** (P-159 was 0.263; +0.544).
