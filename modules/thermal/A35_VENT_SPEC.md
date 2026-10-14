# A35: hip_pitch and knee cover vent spec (RL Thermal, 2026-10-14). **ID designs to this (A36); J-T1 CFD on the 'bryan' PC will confirm it.**
Context: R-030 P-026 (no closed PC over hip_pitch or knee; louvred ≥ 30 % or CF/Al). Basis: `thermal/R1_BUDGET.md` (0040976), worst side, 1.0 m/s with 20 kg carry, 35 °C ambient. Hand calc, [EST] where noted.

## 1. What the vents must achieve
| joint (worst side) | heat into housing W (cu + fe) | winding→case ΔT K | **max case ΔT for winding ≤ 130 °C** | max R_case-air K/W | open, no cover (R1) | **min effective h on the housing** | **target h** |
|---|---|---|---|---|---|---|---|
| hip_pitch (R) | 43.4 (38.0 + 5.4) | 21.1 | 73.9 K | 1.70 | 62.6 K, R 1.44 (h 12) | **10.2 W/m²K** | **≥ 15 W/m²K** |
| knee (L) | 42.1 (36.7 + 5.4) | 20.4 | 74.6 K | 1.77 | 60.8 K, R 1.44 (h 12) | **9.8 W/m²K** | **≥ 15 W/m²K** |
h is per unit CAD housing area × fin factor 2 (same basis as `actuators/size.py`). At target h 15 the case runs about +50 K and the winding about 106 °C, which leaves room for +15 K if drives end up on the housings (P-027 says off-housing). The closed-PC R1 case was equivalent to h ≈ 8, which is what failed.

**D68 revision (2026-10-14):** re-solved with temperature-dependent R and Kt (`d68_rerun.py`). The minimum effective h is now **10.8 W/m²K (hip_pitch) / 10.3 (knee) for winding ≤ 155 °C**, and **12.8 / 12.3 to stay under a 130 °C advisory trip**. These were 10.2 / 9.8 at the old 130 °C constant-R basis. The **target h ≥ 15 W/m²K and all vent geometry below are unchanged**: at h 15 the windings run below the 120–130 °C derate trip.

## 2. Vent geometry (per joint, per leg)
- **Open area:** the air through the cavity may rise ≤ 15 K at 43 W, so 2.9 L/s. Driving velocity is ~1.0 m/s walking (thigh swing adds up to ~2 m/s, not credited); C_d 0.6 [EST].
  - **Inlet ≥ 50 cm², and ≥ 30 % of the panel area over the housing.**
  - **Outlet ≥ 60 cm² (1.2× inlet for heated-air expansion and buoyancy), and ≥ 35 %.**
  - The panel area over each housing is about 430 cm² (1.5 × the half housing area) [EST, needs ID CAD]. At 30–35 % open that gives about 130–150 cm² total, which meets both numbers.
- **Airflow path:**
  - Inlet on the front (ram) face, low, at the lower end of the actuator.
  - Air runs axially along the actuator over the motor cans and fins. Orient fins and louvres axially; no cross-baffles.
  - Exhaust rear/outboard, high (wake low-pressure side + buoyancy, so it also chimneys when the robot stands still).
  - **hip_pitch:** inlet front-lower thigh under the P-023 skirt line; exhaust rear-upper at the skirt hem. **The exhaust must not pass over the thigh-clamp collar.** Route it outboard, or put the collar upstream.
  - **knee:** inlet front-lower through the P-022 knee cap; exhaust rear (popliteal) high.
- **Standoff gap:** **≥ 8 mm** between fin tips/can and the inner cover surface along the whole flow path. The laminar boundary layer is about 5 mm at 1.5 m/s over 0.1 m, so this leaves room for the flow. Never < 5 mm locally.
- **Louvres:** slots ≥ 3 mm wide (dust/finger-safe per ID). Avoid mesh finer than 2 mm (pressure loss). Inlet louvres angled into the flow.
- Equivalent alternative: a CF or Al panel bonded to the housing with TIM, acting as a spreader with its outside exposed. It passes if its effective h on the housing is ≥ 15 W/m²K; Thermal checks each design.

## 3. Bondline (≤ 60 °C at 35 °C means the collar may rise ≤ 25 K)
Vents alone can't do this: the case is at about +50 K even at target h. Requirements (with P-027 / A37, Materials):
- Leave the collar uncovered and in free stream, upstream of the hip_pitch exhaust.
- Thermal break between the motor/lever and the collar: R_break ≥ 20 K/W **including the fasteners** (G10/PEEK washers and bushings, Ti or SS bolts) [EST]. Basis: collar + femur fin to air R_col ≈ 3–14 K/W [EST], so ΔT_col = ΔT_case·R_col/(R_col+R_break) ≤ 25 K.
- Drives off the housing (P-027).

## 4. Open items
- J-T1 (CFD, 'bryan' PC via Robot Lab): confirm h ≥ 15 and the collar ≤ 60 °C with ID's louvre CAD, at walking, at stand-still (natural convection only) and at 35 °C.
- ID: the real panel area over each housing (the 430 cm² is [EST]).
- Standing still with no walking airflow was not computed. The low-inlet/high-outlet chimney is required for that case.
