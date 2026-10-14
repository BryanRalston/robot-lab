"""Legs L55/L58/L61: knee grille bulge, panel tab bosses, trunnion-boss fairing clearance.
Outputs knee_bulge_tabs_l61.json. RL Industrial Design.
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
PCA = 1.8  # kg/m2 PC 1.5

fin_past = 4.7
bulge5, standoff = 5.0, 8.0
bulge_a35 = fin_past + standoff  # 12.7
Gw, Gh = 115.0, 110.0

def bulge_kg(h):
    wall_m2 = 2 * (Gw + Gh) * h * 1e-6
    return round(wall_m2 * PCA, 4), round(2 * wall_m2 * PCA, 3)

kg5s, kg5p = bulge_kg(bulge5)
kg13s, kg13p = bulge_kg(bulge_a35)

# Adopt 12.7 mm: A35 is binding (R-050/A35). Legs' 5 mm alone leaves only 0.3 mm to the fin tip.
bulge = dict(
    source='Legs L55 / d81dcba: rev B fins up to 4.7 mm past v5 thigh keep-out',
    legs_request_mm=bulge5,
    clearance_if_5mm=round(bulge5 - fin_past, 2),
    a35_rule_mm=standoff,
    bulge_for_a35_mm=bulge_a35,
    adopted_mm=bulge_a35,
    reason='5 mm clears the envelope (0.3 mm) but fails A35 fin tip >=8 mm from cover inner face; adopt 12.7 mm',
    mass_5mm_kg_pair=kg5p,
    mass_adopted_12p7_kg_pair=kg13p,
    mass_adopted_kg_side=kg13s,
    vents='A35 open areas unchanged (slots move with the blister; inlet/outlet cm2 same)',
)

# L58 tabs
bosses = [dict(x=-38, y=y, z=z, thread='M2.5') for y in (100, 160) for z in (700, 780)]
tabs = dict(
    source='Legs L58',
    tips=[dict(x=-38, y=100, z=700), dict(x=-38, y=160, z=780),
          dict(x=-38, y=100, z=780), dict(x=-38, y=160, z=700)],
    tab_size_mm=(29.5, 8, 2),
    band_x=-8.5,
    panel_bosses=bosses,
    pocket_corners='y 100/160, z 700/780 (60 x 80 mm span matches 80x60 cover over drive box)',
    alignment='PASS — bosses on panel inner face at tab tips; screw axis +x into tab',
    legs_clearance='>=10.4 mm to hip screw (knee_drive_tabs_r062.json); drives clear by 2 mm',
)

# L61 bosses vs fairing
clash = 9.0  # EST mm into keep-out
relief_h = clash + 3.0
# Preferred: open window 0 g (flanks bare of fins)
# Alt blister mass
blister_robot = round(2 * 2 * (2 * (40 + 30) * relief_h * 1e-6 * PCA), 3)
l61 = dict(
    boss='ø26 x 20 mm ULTEM 4001, 14 mm proud of cheek (L61 final / 8908089)',
    fin_clearance_mm=9.0,
    fin_source='knee_boss_clear_r106.json mins 9.0 over knee 0-135°',
    thigh_shell=dict(
        method='EST hand: cheek outer ~55 mm local after L60 DY=3; boss tip +14 → 69; old keep-out ~60',
        clash_mm_EST=clash,
        through_flexion='fin clearance holds 9 mm all angles; shell clash is pose-independent (boss on thigh-side cheek, fixed in thigh frame)',
        verdict='CLASH ~9 mm EST into outboard thigh fairing keep-out',
    ),
    grille='Front/rear +12.7 mm housing grille bulge does not cover ±y cheek bosses',
    fix=dict(
        preferred='open window ~40x30 mm per cheek in outboard fairing (0 g); ±y flanks already fin-free (L48/L55)',
        alt_blister_mm=relief_h,
        alt_blister_kg_robot=blister_robot,
        adopted='open window 40x30 per cheek, 0 kg',
        adopted_kg=0.0,
    ),
)

# TPU film P-052 — cited densities
area = 0.098 * 0.098
cites = [
    dict(source='DoonX 0.3 mm clear TPU film', url='https://www.doonx.com/products/0-3mm-clear-tpu-film',
         rho_g_cm3=1.20, method='ASTM D792 specific gravity'),
    dict(source='Covestro Platilon U 4201 AU', url='https://solutions.covestro.com/en/products/platilon/platilon-u-4201-au_000000000000805921',
         rho_g_cm3=1.15, method='calculated density (TDS)'),
    dict(source='BondaBand FPA-87-B aliphatic TPU', url='https://www.bondaband.com/uploads/bond-sub/datasheets-and-downloads/spec-sheet-fpa-87-b-pdf.pdf',
         rho_g_cm3=1.13, method='datasheet approx 1.13±0.04'),
]
rows = []
for c in cites:
    for t_mm in (0.3, 0.4, 0.5):
        g = area * (t_mm / 1000) * (c['rho_g_cm3'] * 1000) * 1000  # kg *1000 = g... 
        # area_m2 * thickness_m * density_kg/m3 = kg
        kg = area * (t_mm * 1e-3) * (c['rho_g_cm3'] * 1000)
        rows.append(dict(cite=c['source'], t_mm=t_mm, rho=c['rho_g_cm3'], mass_g=round(kg * 1000, 2), mass_kg=round(kg, 4)))
# Pick: DoonX 1.20 at 0.4 mm mid of 0.3-0.5 (matches prior script ~4.6 g); also report band
pick = dict(face_mm=(98, 98), area_m2=round(area, 6),
            recommended=dict(cite='DoonX 0.3 mm clear TPU (ASTM D792 SG 1.20)', rho=1.20, t_mm=0.4,
                             mass_g=round(area * 0.4e-3 * 1200 * 1000, 2),
                             mass_kg=round(area * 0.4e-3 * 1200, 4),
                             range_0p3_to_0p5_g=[round(area * t * 1e-3 * 1200 * 1000, 2) for t in (0.3, 0.5)]),
            covestro_alt=dict(cite='Platilon U 4201 AU ρ 1.15', t_mm=0.4,
                              mass_g=round(area * 0.4e-3 * 1150 * 1000, 2)),
            table=rows, urls=[c['url'] for c in cites])

out = dict(grille_bulge=bulge, tab_alignment=tabs, l61_boss_clearance=l61, tpu_film_p052=pick)
json.dump(out, open(os.path.join(H, 'knee_bulge_tabs_l61.json'), 'w'), indent=1)
print('bulge adopted', bulge['adopted_mm'], 'mm', bulge['mass_adopted_12p7_kg_pair'], 'kg pair')
print('tabs', tabs['alignment'])
print('L61 fix', l61['fix']['adopted'], l61['fix']['adopted_kg'])
print('TPU', pick['recommended'])
