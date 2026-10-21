# Waist pitch PU end stops + limiter keep-out (Actuators D102c eb5520f)
Stack (+y): motor -> CSG-25 -> friction limiter (0.394 kg, ø90/ø66, L 23, slip 170 N·m) -> yoke.
- Keep-out: ø90 (r_clear 47) × 23 mm on the pitch axis, y 55–78 (was Mayr ø95 × 67, 2.88 kg; rejected).
- Absolute encoder ring: YOKE side of the limiter (y 78–84, ø66 bore), so it reads true torso pitch after slip.
- PU stops: torso-side of limiter (torso cheek lugs, r_lug 100 mm, |y| 72–100, two per cheek: one per range end).
## Sizing (PUR90A layered stack, curve and data from actuators/results/KNEE_STOP_PU_D99.md, ASTM D575 quasi-static)
D99 basis: 25 % strain -> 1.40 J/cm³ PU, 10.9 MPa, shape factor 0.50, curve efficiency η = E/(F·δ) = 0.51.
- 356 J shared by 2 lugs (one per cheek) = 178 J/lug. Travel 0.30 rad × 100 mm = 30 mm = 25 % of 120 mm PU length.
- PU per lug: 127 cm³ = 2 columns 24 × 22 mm (A 1060 mm²) × 12 layers × 10 mm + 1 mm 7075 shims, stack ≈ 135 mm.
- Peak at 356 J (25 %): 11.6 kN/lug -> **2.32 kN·m > 1.7 kN·m target: FAIL**.
- Physics floor: T_peak ≥ E/(η·θ) = 356/(0.51·0.30) = 2.33 kN·m for any PU/TUBUS-type progressive elastomer
  (ACE TUBUS TA is also progressive). Meeting ≤1.7 kN·m needs η ≥ 0.70 (hydraulic/constant-force) or travel ≥ 0.41 rad (23.5°).
- 25 % at exactly 356 J = zero bottoming margin; 22 % variant = 161 cm³/lug, stack ≈ 170 mm.
- Mass: PU 0.15 + shims/plates/pin 0.09 = 0.24 kg/lug, ×4 = **0.97 kg**.
## Travel / clearance
Contact at range ends (−30°, +60°, sim v3), overtravel to −47° / +77°. Stack is tangential, 135 mm at r 100 -> spans ~77° of arc
per lug; both range-end lugs per cheek fit in the 360−90 = 270° free arc only if the stacks sit on the strike wings, not the cheek.
The pitch range itself is untouched (stops beyond it). The overtravel to −47/+77 has NOT been swept against hip/pelvis
geometry (the earlier sweep covered −30/+60 only): OPEN.
