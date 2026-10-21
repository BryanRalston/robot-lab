# L74 twin-strap 3D FEA brief: L60 knee trunnion top plate + R8 notch + twin straps (P-156 Option B, Robot Lab conditional approval)
Owner RL Legs. Runs on Grok Build, heavy compute on the bryan PC. Inputs: `results/r031/p156_rev5_optionB.md/.json` (L74 hand calc), `l60_cutout_optB_l74.py`,
`knee_bracket_move_l60.py` (L60 geometry), `results/a38/TRUNNION_BREAK.md` (L61 loads), L71 addendum (G10/PEM break), L58 (band clamps/tabs), `grokbuild/fea_tet.py` (materials, mesher).
Booking: straps at **0 kg** until this FEA, the fall case and the thermal-break check pass (Robot Lab). Thermal 26cff58: notch passes at **71.1 °C standing**; minimum notch ≈ **500 mm²** for a 5 K margin (do not shrink the R8 notch below that if a stress fix trims it).

## Geometry (thigh frame, L leg, mm; take exact solids from model_v4 + knee_bracket_move_l60.py, DY 3.0 / DZ 1.5)
- Top plate: 7075-T7351, 8 thick, x −175…−40, y 32–228, **z 820–828 (raised 4.0 mm vs L60, L75 gap fix; cheeks +4 mm)**. Trunnion pins at **(−130, 85/175, 770)** (model_v4 KNEE_G: ktx −130, ktz knee_z+270, y 130 ± 45). Trunnion cheeks, pins and bush bosses as L61/L62 (ULTEM 4001 bushes as k 0.26 non-structural contact; pins bonded per R-112).
- **Notch:** x −34.5…−61 × y 104–156 through the plate, **R8 corners** (all 4), edges broken 0.3 × 45°. The plate ends at x −40, so the notch is the 21 × 52 plate cut-out plus the open strip forward of the plate.
- **Central strut (x −45…5, y 110–150) deleted.**
- **Twin straps:** 7075-T7351, 20 (y) × 8 (z), at y 84–104 and 156–176, integral with the plate (machined from the same plate), running forward at z 820–828 to x −8.5 (band-clamp rear face): **free length 31.5 mm (x −40 → −8.5), both ends fixed** (integral with the plate; bolted keyed pad at the clamp). Plate-to-strap fillets **R8 in plan**, R2 vertical edges; no sharp re-entrant corner anywhere on the load path (L69 lesson: a sharp edge is a singularity, not a result).
- **Strap joint (thermal break, mandatory — Thermal 26cff58 / L71):** each strap ends in a 20 × 8 × 25 pad that bolts to a **G10 isolator block** on the L58 drive band clamp ear (clamp ears at y 100/160, x −8.5), exactly as the L71 knee drive plate mounting:
  - Strap pad 30 (y) × 8 → G10 block with **4 × M6 12.9 into PEM inserts in the G10** from the strap side (e/D 2.0, pitch 3D).
  - G10 block → band clamp ear with **4 × separate M6 from the clamp side**; the screw sets do not meet (**G10 web 6 mm** between thread ends → 27.6 K/W per block, 13.8 K/W for the two in parallel, k 0.29 W/mK [EST, Materials to cite]; ≥ 10 K/W basis), so there is no metal path strap → clamp → femur bond.
  - Pad keyed 2 mm into the G10 face on both x faces (tongue-in-groove) so tension and compression bear on G10; bolts carry preload + backup shear.
  - G10 block 30 (y) × 25 (z) × 12 (x); G10/FR4 allowables: Materials to cite (no number assumed) — report G10 bearing (hand 112 MPa at fall 65/35) and shear-out.
  - **Clamp slip:** friction alone cannot react the screw z-thrust (fall 29 kN needs 97 kN normal at μ 0.3; walk 6.7 kN needs 22 kN). The L58 clamp ear must abut a **positive axial shoulder on the L22 bonded split collar**; model the shoulder contact.
  - Why this and not a bonded femur saddle: a saddle is metal-to-femur at the bond (violates the no-metal-path rule, femur bond 69.1–71 °C limit, Thermal 389f91b); the band clamps already exist (L58) and the G10/PEM detail is already qualified in concept (L71), so no new interface on the femur.
- Clearance only (not loaded): **release knee housing** (pivots with the knee: sweep knee 0–145, L75 measured 0.48 mm at 145 with the plate at z 816 → raised plate gives 4.48 nominal) `knee_twin_housing_release_r116.step` rev B (D95). Report the min distance housing ↔ plate/straps/notch edges, gate **≥ 3.0 mm** (see L75 for the fin-top gap).

## Material (single-path, R-127/R-128)
7075-T7351 plate ≤ 1.5 in, A-basis by thickness: **262 MPa design (393/1.5)**, **393 fall limit**, fatigue **amplitude 58 MPa** (Materials R144, ≤ 1e8 cycles). E 71.7 GPa, ν 0.33. G10: linear elastic, properties from Materials (state source).

## Load cases (L60/L61 basis, apply at the trunnion pins through the bushes)
1. **Walk:** screw force 3364 N per side along the screw axis (knee screws at y ±45, trunnion x −125 per CONTRACTS §F, use model_v4 pose at the walking peak knee angle); bracket couple 5.77 kN equivalent. Fatigue: 0…peak, amplitude = peak/2 [EST, as L74].
2. **Design:** 5053 N per side (240 N·m ÷ 47.5 mm), couple 8.66 kN.
3. **Asymmetric:** 5053 N one side, 3364 N other side (single screw lead), checks strap-to-strap load share.
4. **Fall (T&R modules/reliability/L60_FALL_LOAD.md 2e9b25c [EST]):** **FALL_LOAD_N = 29 000 N** axial along the screw line (drive cap 2 × 7267 N rated × DF 2.0), **14.5 kN per screw**, applied at the trunnion pins (−130, 85/175, 770), **tension AND compression**, at **knee 90° and 135°** (screw axis from model_v4 at each pose), plus the **asymmetric 0.65/0.35 split**. SF = 393/σ ≥ 1.0 everywhere (plate, notch R8 corners, strap roots, pads, bolts, G10).
   - **Peak-thrust scaling:** FALL_LOAD_N scales linearly with K_PEAK = F_peak/7267 (Actuators; 1.0 until they give a peak above rated). Report SF at K_PEAK = 1.0 and the K_PEAK at which SF = 1.0.
   - **Stop impact:** if the 135° knee stop is the screw stroke end inside the actuator (not found in the repo — Actuators to state), add STOP_IMPACT_N (TBD by Actuators) on the same path; until supplied, report the capacity.
   - Also report capacity (load to 393 / G10 limit).
   - Hand [EST, l75_strap_checks.json; couple scaled 8.66 kN per 5053 N total thrust → 49.7 kN at fall]: straps 24.9 kN equal / 32.3 kN at 65/35 → net SF 2.53 / 1.95, strap root (R8, Kt 1.5) 1.69 / 1.30; buckling none (L/r 13.6 pinned, σE 3800 MPa); bolts 4 × M6 12.9 shear SF 2.57, 7075 pad bearing 168 MPa → SF 2.7 vs the R-128 455 tier (e/D 2.0; 381 tier at e/D 1.5 → 2.27).
Boundary: G10 block clamp-side faces fixed (band clamp rigid, conservative); separately run with the clamp as 7075 band on the ø50 femur tube to report the stiffness effect (< 10 % peak change expected).

## Mesh / convergence
Quadratic tets. Notch R8 corners and strap-root fillets: edge size ≤ 0.5 mm, ≥ 4 elements through the 8 mm plate. Ladder **h, h/1.5, h/2** (3 levels); converged when peak stress AND fatigue amplitude change < 5 % between the last two, no singular points (report any peak sitting on a sharp edge/BC as an artifact and fix the geometry, not the result).

## Acceptance
| Location | Static (design) | Fatigue (walk amplitude) | Fall |
|---|---|---|---|
| Notch R8 corners | SF ≥ 1.0 vs 262 (report vs 1.5×: ≥ 1.5) | SF ≥ 1.0 vs 58 (target 1.4) | capacity reported; SF ≥ 1.0 vs 393 at FALL_LOAD_N |
| Strap roots / straps | same | same (hand 3.2) | same |
| G10 isolator | report to Materials | report | report |
| Clearance to release housing (plate, straps, notch), knee 0–145 | ≥ 3.0 mm | — | — |
| Hip skirt (P-023) to notch/outlet/shroud, full hip ROM | ≥ 15 mm (ID rev 6 gate) | — | — |
| Strap compression buckling | eigen-buckling factor ≥ 3 at FALL_LOAD_N | — | — |
Hand references (L74): straps 27 MPa design / 9 MPa × Kt 2 amplitude [EST]; band check now void (no central strut).

## Report
Write `results/r031/L74_TWIN_STRAP_FEA.md` + json: mesh stats, convergence table, SF per case and location, fall capacity, G10 stresses, housing clearance, mass (CAD volume × 2.81) vs the L74 −0.029 pair [EST]. Label anything assumed [EST].

## Addendum L76: G10 orientation
The G10 isolator blocks must be cut so the strap-to-clamp heat path runs through the laminate thickness (k 0.288, ASTM C177). Any in-plane heat path must be 13.5 mm or longer (k 0.9 [EST]). Bearing allowables: 128 MPa fall, 64 MPa sustained (Materials 6b04d2f).
