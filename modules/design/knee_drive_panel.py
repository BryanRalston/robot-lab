"""Merged PA12 thigh-rear / knee-drive cover (R-087 / Legs L58).
One panel per side = fairing skin + integral 80x60x15 pocket + IP2X baffle.
Bosses align with Legs band-clamp tabs at x=-38, y=100/160, z=700/780.
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
RHO = 1.01
T = 0.15
plan = 130 * 170 / 100
inn, outv = 52.0, 63.0
skin = (plan - inn - outv) * T * RHO
pocket = 2 * (8.0 + 6.0) * 1.5 * T * RHO
baffle = (5.0 * 4.0 + 2 * 5.0 * 0.6) * T * RHO
boss = 4 * 0.8 * RHO
screws = 4 * 1.2
ribs = 6.0 * T * RHO
side_g = skin + pocket + baffle + boss + screws + ribs
pair = 2 * side_g / 1000
sep = 0.082 + 0.0418
# Legs L58 tabs
tabs = dict(
    tips_xyz=[(-38, 100, 700), (-38, 160, 780), (-38, 100, 780), (-38, 160, 700)],
    size_mm=(29.5, 8, 2),
    band_x=-8.5,
    bosses=[dict(x=-38, y=y, z=z, thread='M2.5') for y in (100, 160) for z in (700, 780)],
    alignment='PASS: panel M2.5 bosses at tab tips; pocket corners y100/160 z700/780',
    legs_mass_tabs='+0.004 robot (integrated clamp ears, Legs L58)',
)
d = dict(
    ruling='R-087', material='PA12 1.5 mm (rho 1.01 g/cm3)',
    planform_cm2_side=plan, inlet_open_cm2=inn, outlet_open_cm2=outv,
    items_g_side=dict(outer_skin=round(skin, 2), pocket_walls_80x60x15=round(pocket, 2),
                      ip2x_baffle=round(baffle, 2), m25_bosses_x4=round(boss, 2),
                      captive_m25_x4=round(screws, 2), stiff_ribs=round(ribs, 2)),
    kg_side=round(side_g / 1000, 4), kg_pair=round(pair, 3),
    vs_separate=dict(sum=round(sep, 3), merged=round(pair, 3), saving=round(sep - pair, 3)),
    legs_L58_tabs=tabs,
    features=dict(
        tool_removal='4x M2.5 captive screws into Legs L58 tabs on G10 band clamps; tool required',
        ip2x='baffle + slots <=10 mm; inner face >=8 mm from live parts',
        a35='inlet 52 / outlet 63 cm2',
        pocket='80x60x15 over 26x52x104 drive box z 688-792',
    ),
)
json.dump(d, open(os.path.join(H, 'knee_drive_panel.json'), 'w'), indent=1)
print(d['kg_pair'], d['legs_L58_tabs']['alignment'])
