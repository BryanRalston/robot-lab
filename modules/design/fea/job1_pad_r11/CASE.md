# Job 1 / Job 8 add-on rerun — pad R10 core on stand-off R11 (route via Robot Lab; bryan PC or RL box)
Supersedes job1_pad_r10/CASE.md geometry for the stand-off. Reuse job1_pad_r10/fea_r10.py (same loads, gates, mesh rules).
- Stand-off R11 (modules/design/pad_r11_standoff.json; CAD cad/shoulder_pad/): R13 flange OD70/ID44×5 (8×M4 12.9 PCD62 + 2×Ø6 m6 fitted dowels), closed box 44×44×2.5 wall, Y 0–23, centred X 0 / Z −15; **solid** plate 62×62×4, Y 23–27, centred Z −20; R3 fillets at box roots and box/plate junction.
- Pad: 0.5 mm tray, 4×M4 ±24, core 54.8² centred (e, −20); contact Y 102.3. CRBH 7013 A.
- Loads: 7.0 kN at 15° governing (Fn 6761, Fs 1812), axial + down; μ 0.15 sensitivity only. e = 0, 5 qualified; 10 informative.
- Mesh: ≥3 elements through the 2.5 mm wall and 4 mm plate; report filtered and absolute peaks.
- Report: s0, raw roll Mx + CSG-25 SF, box/plate vM (working limit 320 MPa; ultimate check 480 MPa, per R-123), pad deflection (≤1 mm), dowel/bolt shear with fitted dowels, bond, slip, tab.
- ID hand calc expectation: box 215 MPa (calibrated ×2.86 to R10 FEA ribs), plate 149 MPa, deflection ≤0.69 mm (calibrated), dowel SF 2.6.

## Gates (R-123(d), ca66b9b) — 7075-T6 basis 480/560/70 GPa
- von Mises ≤ 320 MPa working (any case); 480 MPa ultimate check
- s0 ≥ 2.0 at e = 0 and 5 mm (10 mm informative)
- roll torque Mx ≤ 351 N·m (369 / 1.05, raw, no clutch credit)
- pad deflection ≤ 1 mm
