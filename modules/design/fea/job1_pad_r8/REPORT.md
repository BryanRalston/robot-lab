# Job 1 report — shoulder pad R8 option B FEA (R-079)

**Overall: FAIL.**

Four cases, each gated on the six criteria in `BRIEF.md`. A case passes only when every criterion passes. The axial-shear cases fail the CRBH 6013 static safety factor.

## Criteria

| case | von Mises MPa | bond MPa | bearing s0 | defl mm | M4 slip | tab bearing SF | case |
|---|---:|---:|---:|---:|---|---:|---|
| axial_e0 | 11.7 PASS | 0.62 PASS | 1.45 FAIL | 0.014 PASS | no slip (593 N < 825 N) | 1.62 PASS | FAIL |
| axial_e10 | 17.2 PASS | 0.62 PASS | 1.29 FAIL | 0.024 PASS | no slip (593 N < 825 N) | 1.62 PASS | FAIL |
| down_e0 | 12.7 PASS | 0.62 PASS | 2.63 PASS | 0.015 PASS | no slip (593 N < 825 N) | 1.62 PASS | PASS |
| down_e10 | 16.9 PASS | 0.62 PASS | 2.09 PASS | 0.023 PASS | no slip (593 N < 825 N) | 1.62 PASS | PASS |

Limits: von Mises ≤ 320 MPa, bond ≤ 7.7 MPa, bearing s0 ≥ 2.0, deflection ≤ 1 mm, preload × μ > shear per bolt, tab bearing SF ≥ 1.5 on 480 MPa.

## Method

Python 3.12 on this PC has numpy and scipy. scikit-fem, gmsh and CalculiX are not installed. The link, the 62×62×10 boss and the 0.5 mm tray are one conforming hex8 mesh (full 2×2×2 integration, E = 71.7 GPa, ν = 0.33). The roll-output face of the link (Z = −39 mm) is fixed. The core is not meshed: 9.17 kN at 15° is a uniform traction on the 61.8 mm square (normal 8.86 kN inward, tangential 2.37 kN). Arm weight is a separate force on the bottom of the link.

The hex8 element recovers uniaxial tension (100.00 MPa against 100 MPa) and a stocky cantilever within 8.9% of Timoshenko (0.0244 mm vs 0.0268 mm; the element is slightly stiff).

Peak von Mises is the hex8 Gauss maximum outside a 6 mm band on the fixed roll-output face and outside a 3 mm band on the boss/link re-entrant edge. Those two lines are support and sharp-corner artifacts; the absolute maximum is reported beside the filtered peak. The hole-contact peak is a bearing stress and is gated by the tab bearing SF, not added again as a von Mises fail, provided the joint does not slip.

Production mesh pitch is 4 mm (one 0.5 mm element through the tray). The axial e = 10 mm case was repeated at 2 mm (22232 elements): filtered von Mises 17.2 MPa, absolute peak 51.4 MPa, pad deflection 0.0242 mm. The filtered peak does not climb toward 320 MPa.

## Loads and bearing

Normal 8857.5 N (−Y, into the robot). Tangential 2373.4 N, either +X/−X along the roll axis (the sign with the lower s0 is kept) or −Z (downward).

Arm distal to the roll bearing: 6.05 kg, weight 59.3 N, tuck B (pitch +5°, roll 0, yaw 0, elbow 0). COM at x,y,z = (-33.9, -10.0, -387.0) mm relative to the CRBH centre. The weight changes s0 by about 0.01.

CRBH 6013 A, C0 = 24.3 kN, dp = 75 mm. P0 = Fr + 2M/dp + 0.44 Fa (IKO static equivalent, catalog formula (2); M in N·m with dp in m). Fr is the radial resultant, Fa the axial component, M the tilting moment sqrt(My² + Mz²). Torque about the roll axis, Mx, is spin: the gear holds it, and it is not inside P0.

The pad centre sits at Z = −64 mm (model_v4 link centre; R7's 0.064 m offset) and the contact face is at Y = 87.0 mm (link face +10 mm, boss 10, tray 0.5, core 60, spreader 0.5, EPP 6). A normal force at that point makes roll torque Mx = Fn × 0.064 m and, with axial offset e, tilting moment Fn × e. An axial tangential force at the same point makes tilting moment Fs × sqrt(Y² + Z²). R7's published table uses only M = Fn·e and Fa = Fs (s0 2.45 at 0 mm, 1.98 at 10 mm). That table is reproduced below. 1.98 is already under the gate of 2.0. The table also leaves out the tangential force's lever arm, so it is not the value gated here.

| e mm | R7 simplified s0 (M = Fn·e, Fa = Fs) |
|---:|---:|
| 0 | 2.45 |
| 10 | 1.98 |

Gated s0 uses the contact line of action. The same formula with the line of action moved in to the bond or to the link face still fails both axial cases:

| case | s0 contact (gated) | s0 at bond | s0 at link face | Mx N·m | Mtilt N·m |
|---|---:|---:|---:|---:|---:|
| axial_e0 | 1.45 | 1.71 | 1.73 | -566 | 258 |
| axial_e10 | 1.29 | 1.58 | 1.62 | -566 | 333 |
| down_e0 | 2.63 | 2.63 | 2.63 | -773 | 2 |
| down_e10 | 2.09 | 2.09 | 2.09 | -773 | 91 |

Downward shear is radial, so its tilting moment is only Fn and Fs times e. Those two cases clear s0 ≥ 2. Both axial cases are below 2.

Roll-axis torque Mx is -566 N·m in the axial cases (Fn × 64 mm) and -773 N·m when the shear is also downward (extra Fs × Y). CSG-25 momentary peak is 369 N·m. Mx is outside the six gates. It is large enough that the roll gear, not only the crossed roller, needs a look.

## Bond, bolts, tray

Core–tray DP490 on 61.8 mm square (3819 mm²). Shear 0.62 MPa, compression 2.32 MPa, peel 0. The gate uses shear (the 23 MPa lap-shear rating / 3 = 7.7 MPa). Compression is the crush pressure and is also under 7.7 MPa. The honeycomb holds the pressure near the plateau, so an offset of the whole pad (e = 0 or 10 mm) does not concentrate the bond.

Four M4 12.9, preload 5500 N, μ = 0.15. Friction per bolt 825 N. Shear per bolt 593.3 N (2.37 kN / 4; the pad resultant is centred on the bolt group). Margin 1.39. No slip. The impact compression on the faying face is extra clamp and is not credited.

Tab bearing uses the bolt diameter, σ = F/(d t) = 296.7 MPa on 4 × 0.5 mm. SF vs 480 MPa is 1.62 (limit 1.5). Tear-out, not a gate: 125 MPa, SF 2.64 vs 330 MPa, with 4.75 mm from the hole wall to the tray edge (bolt centres at ±24 mm, tray edge at ±31 mm, hole diameter 4.5 mm).

A plane-stress model of that corner hole, cosine bearing load 593.3 N (the nodal resultant matches that force), gives a contact-ring von Mises of 410 MPa and 346 MPa off the contact ring. The ligament value is above the 320 MPa von Mises limit. It is the bearing-type path. The slip check says that path is not the service load: friction holds while μ × preload (825 N) stays above 593 N (μ above 0.11 at this preload). The gated von Mises is the hex8 service stress. The absolute hex8 peak on the 2 mm mesh is 51 MPa, still under 320; it rose at the re-entrant edge while the filtered peak stayed near 17 MPa.

## Assumptions

- Qualified layout: bearing midplane at the link, pad centre shifted by e. model_v4's `sw()` bearing sits at x = L/2+4 on a generic envelope; that drawing cannot meet e ≤ 10 mm and the 1–6 mm boss overhang together.
- Link is the model_v4 60×40×50 block. The face at Z = −39 mm stands in for the roll-output connection. Stress in that face is excluded. Neck compliance between that face and the CRBH is not meshed; at this section size it does not move a 0.01 mm deflection up to the 1 mm limit.
- Boss 62×62×10 is solid 7075 and integral. The booked 0.024 kg is about a quarter of a solid 62×62×10 at 2.81 g/cm³ (about 0.108 kg). Mass is unchanged by this job.
- Tray floor matches the boss. Lips locate the core and do not carry load (SHOULDER_PAD: the bond carries shear). Bolt holes are Ø4.5 on centres ±24 mm.
- Core, spreader and EPP are the crush stack. Structural deflection is the metal displacement at the bond patch, not the core crush.
- Tuck is tuck B, the current Arms pose. The withdrawn pitch −30 / elbow −110 tuck is not the load case. Distal mass is the catalog split in `arm_inertials_r3.json`, not the lighter sim bodies.
- μ = 0.15 and 5.5 kN preload are the Arms R8 figures for this M4×8 joint (class 12.9). The superseded R7 doubler note (class 8.8, 2 kN) is not used.
- Bearing SF is the equilibrium s0 at the contact line of action, including arm weight. The R7 simplified column is shown and is not the gate.

## Files

- `fea_job1.py` — model, checks, this report
- `results.json` — numbers behind the table

