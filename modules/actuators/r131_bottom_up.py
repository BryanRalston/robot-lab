"""R-131 bottom-up per-unit mass table for the 32 driven units -> results/R131_BOTTOM_UP.json (+ .md written by hand from it).
Sources: legs = results/sizing.json (v3 actuator() with v4 selections: mass_model, housing_model, housing_cad incl. cad_mass FAST);
arms/waist = v3/analysis v3.py actuator() pieces (parts.py catalog: TBM2G, CSG, CRBH, AksIM-2) ; wrists = d70_wrist_rotary.py unit dict;
fasteners = results/fastener_bom.json; drive = Elmo G-TWI 22.2 g (MAN-G-TWI v2.011 p.10); harness = results/harness.json (one line).
Output hub (rotary): 7075 disc OD = CRBH bore, 8 mm, bore 0.4 OD, 50 % pocketed [EST] - needed and booked nowhere except possibly the +0.04.
Rotor support bearing (screw units): 6805-class thin bearing 0.022 kg [EST]; 7202 pair 2 x 0.045 [EST, SKF typical; no repo datasheet]."""
import json, math, os, sys
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f'{H}/../..')
sys.path.insert(0, f'{R}/v3/analysis'); sys.argv = ['x']
import v3 as V, parts as PT
st = json.load(open(f'{R}/v3/analysis/results/v3.json'))['state']
SZ = json.load(open(f'{H}/results/sizing.json'))['sel']
FB = json.load(open(f'{H}/results/fastener_bom.json'))['rows']
HAR = json.load(open(f'{H}/results/harness.json'))['total_kg']
ENC = 2*(PT.ENC['ring_mass']+PT.ENC['head_mass']); DRV_OLD = PT.DRIVE['mass']; DRV = 0.0222
BORE = {'CRBH 208 A': 20, 'CRBH 258 A': 25, 'CRBH 3010 A': 30, 'CRBH 4010 A': 40, 'CRBH 5013 A': 50, 'CRBH 6013 A': 60, 'CRBH 7013 A': 70}
def hub(b): d = BORE[b]; return 0.5*math.pi/4*(d**2-(0.4*d)**2)*8*2.81e-6
def fast(unit_prefix): 
    rows = [r for r in FB if r['unit'].startswith(unit_prefix)]; n = rows[0]['n_robot']//rows[0]['n_unit']
    return sum(r['steel_g'] for r in rows)/1000/n
units = []
# ---- legs
for j, cnt in (('hip_yaw', 2), ('hip_roll', 2)):
    s = SZ[j]; b = 'CRBH 6013 A'
    core = s['mass_model'] - s['housing_model'] - ENC - DRV_OLD - 0.07      # motor + gear + CRBH (catalog)
    units.append(dict(unit=j, n=cnt, basis='v3 actuator() + CAD housing (sizing.json)', motor_gear_bearing=core, housing=s['housing_cad'] - 0.0498,
        enc=ENC, drive=DRV, fasteners=fast(j), out_hub=hub(b), adder_booked=0.07, fast_allow_booked=0.0498, fast_screws_booked=0.0348, conn_allow_booked=0.015))
for j, cnt, pre in (('hip_pitch', 4, 'hip_pitch'), ('knee', 4, 'knee'), ('ankle_pitch', 4, 'ankle')):
    s = SZ[j]; per = s['mass_model']/2
    core = per - s['housing_model']/2 - ENC - DRV_OLD - 0.18                 # motor + nut + shaft
    units.append(dict(unit=j+' (per motor side)', n=cnt, basis='v3 actuator() linear + CAD housing (sizing.json)', motor_gear_bearing=core, housing=s['housing_cad']/2 - 0.0236,
        enc=ENC, drive=DRV, fasteners=fast(pre), support_brg_7202=0.09, rotor_brg=0.022, adder_booked=0.18, fast_allow_booked=0.0236, fast_screws_booked=0.0136, conn_allow_booked=0.010, linkage='LINKAGE_TABLE (separate line)'))
# ---- arms / waist v3 rows
for j, cnt in (('waist_yaw', 1), ('waist_pitch', 1), ('shoulder_pitch', 2), ('shoulder_roll', 2), ('shoulder_yaw', 2), ('elbow', 2)):
    d = st['J'][j]; M = V.mot(d['motor'], d['w']); b = st['bearing'][j]; g = PT.CSG[d['gear']]; gm = g['mass'] or PT.CSG_MASS_EST[d['gear']]
    units.append(dict(unit=j, n=cnt, basis='v3 actuator() row', motor_gear_bearing=M['mass']+gm+PT.CRBH[b]['m'], bearing_v3=b, housing=V.housing(M, d['gear'], b)['mass'],
        enc=ENC, drive=DRV, fasteners=fast(j), out_hub=(0 if j == 'shoulder_roll' else hub(b)), adder_booked=0.07, fast_allow_booked=0.03))
# ---- wrists (D70/D76 unit basis)
for j, cnt in (('wrist_roll', 2), ('wrist_pitch', 2), ('wrist_yaw', 2)):
    units.append(dict(unit=j, n=cnt, basis='D70/D76 unit dict (d70_wrist_rotary.py)', motor_gear_bearing=0.111+0.09+0.05, housing=0.06, enc=0.0097, drive=DRV,
        fasteners=fast(j), out_hub=hub('CRBH 258 A'), adder_booked=0.0, fast_allow_booked=0.015, drive_booked=0.0))
# ---- overlap per adder (true, item by item)
ov = dict(rot_003_legs=0, rot_004=0, lin_010=0, lin_008=0, conn_allow=0, drive=0, wrist_drive_unbooked=0)
for u in units:
    n = u['n']
    if u['unit'] in ('hip_yaw', 'hip_roll'):
        ov['rot_003_legs'] += 0.03*n                    # fasteners now counted in the BOM (+0.517)
        ov['rot_004'] += (0.04 - u['out_hub'])*n
        ov['conn_allow'] += u['conn_allow_booked']*n
    elif 'per motor side' in u['unit']:
        ov['lin_010'] += (0.10 - u['rotor_brg'])*n       # linkage in LINKAGE_TABLE; rotor bearing is real content
        ov['lin_008'] += max(0, 0.08 - u['support_brg_7202'])*n
        ov['conn_allow'] += u['conn_allow_booked']*n
    elif u['adder_booked']:
        ov['rot_004'] += (0.04 - u['out_hub'])*n         # 0.03 netted in the +0.875
    if u.get('drive_booked', 1) == 0: ov['wrist_drive_unbooked'] -= DRV*n   # adverse: drive booked nowhere
    else: ov['drive'] += (DRV_OLD - DRV)*n
ov = {k: round(v, 3) for k, v in ov.items()}
for u in units:
    for k, v in list(u.items()):
        if isinstance(v, float): u[k] = round(v, 4)
    u['bottom_up_unit'] = round(sum(u.get(k, 0) for k in ('motor_gear_bearing', 'housing', 'enc', 'drive', 'fasteners', 'out_hub', 'support_brg_7202', 'rotor_brg')), 4)
credit_vs_ledger = round(sum(v for k, v in ov.items() if k not in ('drive', 'wrist_drive_unbooked')), 3)
res = dict(units=units, n_units=sum(u['n'] for u in units), harness_line_kg=round(HAR, 4), overlap=ov,
    adders_credit_full=credit_vs_ledger, drive_credit_on_booked=ov['drive'], wrist_drive_addition=ov['wrist_drive_unbooked'],
    total_credit=round(credit_vs_ledger + ov['drive'] + ov['wrist_drive_unbooked'], 3))
json.dump(res, open(f'{H}/results/R131_BOTTOM_UP.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'units'}, indent=1))
for u in units: print(u['unit'], u['n'], u['bottom_up_unit'], u.get('out_hub'), round(u['motor_gear_bearing'], 3))
