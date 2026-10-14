"""R-047 cover offsets (>= 0.08 kg). RL Industrial Design. Basis: cover_set_v5.json (trimmed, measured:false), PC rho 1.20.
Mass of a thermoformed skin = formed area x average finished wall (mass conserved from sheet)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__)); cs=json.load(open(os.path.join(H,'cover_set_v5.json')))
row={r['panel'].split(',')[0].split(' (')[0]:r for r in cs['rows']}
PC=1.20e3
def skin(name,t=1.5e-3): r=row[name]; return r['area_m2_side']*2*t*PC
thigh=skin('thigh fairing'); knee=skin('knee cap'); foot=skin('foot upper shell')
items=[]
# 1 louvres (P-026): cut (CNC-trimmed) slots, 30 % open area on thigh fairing + knee cap; +15 % of removed mass back as slot rims/ribs
OPEN=0.30; RIB=0.15
d1=-(thigh+knee)*OPEN*(1-RIB)
# knee-housing grille (Legs 6f53d77 / Thermal 9b9e169): front face of finned housing (ø85 + 2x10 fins + 2x5 mm = 115 mm) x ~110 mm along y [EST] = 0.0127 m2/side;
# grille 60 % open replaces the 30 % louvres there. Rear face is already open (trimmed fairing is front + outboard only); no fins on +-y flanks.
G_A=0.115*0.110; G_OPEN=0.60; dg=-2*G_A*(G_OPEN-OPEN)*1.5e-3*PC*(1-RIB)
d1+=dg
items.append(dict(item='P-026 louvres 30 % open on thigh fairing + knee cap (cut slots, CNC trim)',kg=round(d1,3),
 evidence=f'calc: skin thigh {thigh:.3f} + knee {knee:.3f} kg x 0.30 open x (1-0.15 rib allowance); plus knee-housing front grille 115x110 mm/side at 60 % open merged over the louvres ('+f'{dg:.4f}'+' kg); R-030 P-026 requires >=30 % open; Thermal A35 per-joint spec pending'))
# 2 PC 1.2 mm average wall on low-draw panels: thigh outboard half (draw <=1.5:1) + foot top (<=1.5:1); louvred thigh outboard keeps 70 % of skin
outb=thigh/2*(1-OPEN); d2=-(outb+foot)*(0.3/1.5)
items.append(dict(item='PC 1.2 mm avg (min post-form 0.9 mm) on thigh outboard + foot top (low draw)',kg=round(d2,3),
 evidence=f'calc: (thigh outboard {outb:.3f} after louvres + foot {foot:.3f}) x 0.3/1.5; Materials REVIEW_R1 (a) basis 0.3 mm x area x 1.20; bending stiffness x0.51 (t^3) -> 2 formed ribs on thigh outboard, foot shell EPP-backed; dent check (Materials A15) open. Thigh front (2:1) and knee cap (2.5:1) stay 1.5 mm'))
# 3 printed small parts: hip-skirt rim strip PC 1.5 -> PA12 MJF 1.2 mm (crew preference only, R-027 item 2)
rim=2*0.020; d3=-rim*(1-(1.01*1.2)/(1.20*1.5))
items.append(dict(item='hip-skirt rim strips PC 1.5 -> printed PA12 MJF 1.2 mm',kg=round(d3,3),evidence='calc: 0.040 kg pair x (1 - 1.01*1.2/(1.20*1.5)); no-printing is a crew preference, not a Bryan rule (R-027 item 2)'))
# 4 shoulder pad vs R-042 booking
sp=json.load(open(os.path.join(H,'shoulder_pad.json'))); pk=sp['options'][sp['pick']]['kg_pair']
items.append(dict(item='shoulder pad R2 (5052 HC 3.1 pcf cartridge) vs R-042 booked 0.10',kg=round(pk-0.10,3),evidence='shoulder_pad.json; HC crush strength to be cited by Materials'))
sh=0.45*0.17508; add=dict()
for k,ar in (('PC',1.8),('CF',1.55)):
    add[k]=round(2*(sh*ar+2*0.004),3); add[k+'_louvred']=round(2*(sh*ar*(1-OPEN*(1-RIB))+2*0.004),3)
tot=round(sum(i['kg'] for i in items),3)
out=dict(items=items,shin_addback_option=dict(add,area_m2_side=round(sh,4),note='Legs 6f53d77 withdrew the shin no-cover zone; NOT in baseline (R-047 freeze); Arbiter decision'),thigh_grille_kg=round(dg,4),total_kg=tot,total_half_credit_kg=round(tot/2,3),target_kg=-0.08,
 meets_target_full=tot<=-0.08,meets_target_half_credit=tot/2<=-0.08,note='areas [EST] (R-040 credits covers at half until measured)')
json.dump(out,open(os.path.join(H,'cover_trims_r047.json'),'w'),indent=1)
for i in items: print(i['kg'],i['item'])
print(tot,tot/2)
