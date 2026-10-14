"""Merged PA12 thigh-rear / knee-drive cover (R-087).
One panel per side = fairing skin + integral 80x60x15 pocket + IP2X baffle.
Replaces ID a36 drive_bay_rear PC panels (+0.082) and Electronics §18.2f item 10 (41.8 g both legs).
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
RHO = 1.01  # g/cm3 PA12
T = 0.15    # cm wall
# Planform: single rear panel spanning low inlet + high outlet over drive bay z 688-792
# 130 mm wide x 170 mm tall = 221 cm2 [EST] — tighter than separate 132+180 panels
plan = 130 * 170 / 100  # 221
inn, out = 52.0, 63.0   # A35: >=50 / >=60
assert inn >= 50 and out >= 60
skin = (plan - inn - out) * T * RHO
# Pocket walls only (outer face = skin): 80x60x15 mm
pocket = 2 * (8.0 + 6.0) * 1.5 * T * RHO
# Labyrinth baffle in front of solder points (slots <=10 mm; >=8 mm standoff to live)
baffle = (5.0 * 4.0 + 2 * 5.0 * 0.6) * T * RHO
boss = 4 * 0.8 * RHO          # M2.5 bosses into clamp tabs
screws = 4 * 1.2              # captive M2.5
ribs = 6.0 * T * RHO
side_g = skin + pocket + baffle + boss + screws + ribs
pair = 2 * side_g / 1000
sep = 0.082 + 0.0418
d = dict(
    ruling='R-087', material='PA12 1.5 mm (rho 1.01 g/cm3)',
    planform_cm2_side=plan, inlet_open_cm2=inn, outlet_open_cm2=out,
    inlet_open_frac=round(inn / (plan * 0.4), 3), outlet_open_frac=round(out / (plan * 0.6), 3),
    items_g_side=dict(outer_skin=round(skin, 2), pocket_walls_80x60x15=round(pocket, 2),
                      ip2x_baffle=round(baffle, 2), m25_bosses_x4=round(boss, 2),
                      captive_m25_x4=round(screws, 2), stiff_ribs=round(ribs, 2)),
    kg_side=round(side_g / 1000, 4), kg_pair=round(pair, 3),
    vs_separate=dict(id_pc_panels=0.082, electronics_covers=0.0418, sum=round(sep, 3),
                     merged=round(pair, 3), saving=round(sep - pair, 3)),
    vs_R087_booked=dict(booked=0.040, merged=round(pair, 3), delta=round(pair - 0.040, 3),
                        flag='merged > booked; reconcile with Arbiter'),
    features=dict(
        tool_removal='4x M2.5 captive screws into tabs on Legs 2x G10-lined band clamps; tool required; no snap-only (Electronics C1)',
        legs_flag='TAB POSITIONS need Legs confirmation; no holes in 1.6 mm femur wall',
        ip2x='IEC 60529 finger 12 mm x 80 mm: no straight path to solder points; inner face >=8 mm from live OR labyrinth baffle; vent slots <=10 mm wide',
        clearance='>=3 mm to drive tops and cable exits; cable exits at bottom edge of pocket',
        a35='inlet 52 cm2 low (>=50, >=30%), outlet 63 cm2 high (>=60, >=35%)',
        pocket='integral 80x60x15 mm over 26x52x104 drive box (R-062 / L51, z 688-792)',
    ),
)
json.dump(d, open(os.path.join(H, 'knee_drive_panel.json'), 'w'), indent=1)
# Patch a36: replace drive_bay_rear mass with note pointing to merged panel
print(json.dumps({k: d[k] for k in ('kg_pair', 'vs_separate', 'vs_R087_booked', 'inlet_open_cm2', 'outlet_open_cm2')}, indent=1))
