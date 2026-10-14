"""P-052 sternum bezel (R-094 / Torso ab432da §25.1).
Pad 1 mm CF face = visible skin at x~+0.147; PC bezel ring replaces the full P-052 plate.
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))

# --- Bezel ring: 1.5 mm PC, 15 mm radial (R-094 +0.015 EST) ---
# Inner clear 90x90 (centre free); flange overlap on pad face <=4 mm; outer ~120x120
RHO_PC = 1.20  # g/cm3
t = 0.15
flange_cm2 = 12.0**2 - 9.0**2          # 63
flange_g = flange_cm2 * t * RHO_PC     # 11.34 g
# Short cosmetic sidewall closing the pad edge (~8 mm), not bonded to core
side_g = 4 * 9.8 * 0.8 * t * RHO_PC    # 5.64 g
# 15 mm blend lip on bezel outer (to shell) — PC skirt, not a full second plate
blend_g = (4 * 12.75 * 1.5) * t * RHO_PC  # mid-perimeter * width * t * rho = 13.77? 
# Use annular planform of 15 mm band outside 120: 15^2-12^2 = 81 cm2 but only the
# developed blend strip ~ perimeter_mid * slope; keep as light lip = same 15 mm flange extension
blend_g = (15.0**2 - 12.0**2) * t * RHO_PC * 0.5  # half credit for draft wall [EST] → 7.29 g
captive_g = 4 * 2.5  # captive M4 [EST]

bezel_ring_g = flange_g + side_g  # core "ring" comparable to R-094 0.015
bezel_with_blend_captive_g = bezel_ring_g + blend_g + captive_g

# Compliant gasket: 1 mm stand-off, no clamping preload
gsk_g = (4 * 9.4 * 0.4) * 0.10 * 0.40   # overlap strip, 1 mm, silicone ~0.40 g/cm3 → ~0.60 g
# Foam edge seal (does not bond to core walls)
seal_g = 4 * 9.8 * 0.5 * 0.5 * 0.05     # 5x5 mm, 50 kg/m3 → 0.49 g
# TPU film 0.3-0.5 mm on 98x98 face → 3-5 g
film_g = 9.8 * 9.8 * 0.04 * 1.20        # 0.4 mm → 4.61 g

# Parent asks: ID mass = bezel + gasket + seal + film
# Include blend + captives in bezel assembly (attached with the bezel)
id_parts_g = dict(
    bezel_flange_15mm=round(flange_g, 2),
    bezel_sidewall=round(side_g, 2),
    blend_15mm_to_shell=round(blend_g, 2),
    captive_M4_x4=round(captive_g, 2),
    compliant_gasket_1mm=round(gsk_g, 2),
    foam_edge_seal=round(seal_g, 2),
    TPU_film_0p4mm_on_face=round(film_g, 2),
)
id_kg = sum(id_parts_g.values()) / 1000
bezel_gasket_seal_film_kg = (flange_g + side_g + blend_g + captive_g + gsk_g + seal_g + film_g) / 1000
plate = 0.058
cf_shell = 0.045

d = dict(
    P='P-052',
    ruling='R-094',
    supersedes='R-093 / R-088 full PC sternum plate (0.058 kg)',
    design=(
        'Chest pad 1 mm CF face is the visible sternum skin at x~+0.147 (37 mm proud). '
        'Pad bonded to 7075 land with structural epoxy. '
        '1.5 mm PC bezel ring is secondary hold + cosmetic edge; 4 captive M4s into inserts '
        'at (y,z)=(+-0.040, +0.180/+0.260). Flange overlaps face <=4 mm with 1 mm stand-off on '
        'compliant gasket (no clamping preload); centre 90x90 free. Edge closed by bezel sidewall '
        '+ foam seal (seal does not bond to core walls). 0.3-0.5 mm TPU film on face; 15 mm blend to shell.'
    ),
    service_rule='Visible dent >1 mm deep, or any crush => replace the pad. Crushed face = replace-me indicator.',
    geometry=dict(
        pad_centre_xyz=(0.100, 0.0, 0.220),
        skin_x_approx=0.147,
        inserts_yz=[(0.040, 0.180), (-0.040, 0.180), (0.040, 0.260), (-0.040, 0.260)],
        source='Torso ab432da §25.1',
    ),
    items_g=id_parts_g,
    bezel_ring_only_kg=round(bezel_ring_g / 1000, 3),
    id_mass_kg=round(id_kg, 3),
    id_mass_bezel_gasket_seal_film_kg=round(bezel_gasket_seal_film_kg, 3),
    vs_plate_0p058=dict(was=plate, now=round(id_kg, 3), delta=round(id_kg - plate, 3)),
    vs_cf_shell_removed_0p045=dict(
        cf_shell_removed=cf_shell,
        id_added=round(id_kg, 3),
        net=round(id_kg - cf_shell, 3),
    ),
    r094_ledger=dict(
        ring_booked=0.015,
        cf_shell_half_credit=-0.0225,
        replaces_r093_plate=-0.058,
        arbiter_net=-0.066,
        script_ring=round(bezel_ring_g / 1000, 3),
        script_id_full=round(id_kg, 3),
    ),
    conditions=[
        'Face finished (clear coat or texture) — R-094',
        'Torso/Materials: CF face OK for handling, UV, abrasion as outer skin',
        'Controls: T-031 with skin at x~+0.147',
        'No clamping preload (1 mm gasket stand-off)',
        'Foam edge seal must not bond to honeycomb core walls',
    ],
    not_id_mass=['7075 land+rib +0.030 (Torso)', 'pad core + 1 mm CF face (chest pad line)', 'structural epoxy'],
)
json.dump(d, open(os.path.join(H, 'sternum_plate.json'), 'w'), indent=1)
print('bezel_ring', d['bezel_ring_only_kg'], 'ID full', d['id_mass_kg'])
print('vs plate', d['vs_plate_0p058'])
print('vs CF shell', d['vs_cf_shell_removed_0p045'])
print(d['items_g'])
