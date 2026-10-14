"""v5 cover set mass estimate (RL Industrial Design, R1). Basis: R-027 / P-020 (thermoformed PC 1.5 mm, rho 1.20).
Leg panel areas = Legs keep-out hull area (legs/results/v5/envelopes.json, uncommitted Legs WIP, 5 mm offset) x skin fraction [EST].
Upper body = cylinder/box approximations from model_v4 dims [EST]. All [EST] until A29 measures panels on CAD."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
env=json.load(open(os.path.join(H,'..','legs','results','v5','envelopes.json')))
PC=1.20*1.5; CF=1.55*1.0          # kg/m2: PC 1.5 mm vs CF 4x0.25 twill (R-027 densities)
INS=0.004                          # kg per panel: 4x M4 heat-set/bonded inserts + rim doubler [EST]
FAB=0.30; ELA=0.60                 # kg/m2: TPU-coated nylon 210D [EST]; TPE bellows 0.5 mm-equivalent [EST]
A=lambda n:env[n]['area_cm2']/1e4
# name, P-number, material, area per side m2, panels per side, sides
rows=[
 ('shin fairing (2 halves)','P-020','PC 1.5 (CF allowed)',A('shin_fairing')*0.70,2,2),
 ('thigh fairing (2 halves)','P-020','PC 1.5 (CF allowed)',A('thigh_fairing')*0.70,2,2),
 ('foot upper shell','P-020','PC 1.5',A('foot_upper')*0.40,1,2),
 ('upper-arm shell (2 halves)','P-020','PC 1.5',3.1416*0.095*0.26*0.85,2,2),
 ('forearm shell (2 halves)','P-020','PC 1.5',3.1416*0.085*0.25*0.85,2,2),
 ('shoulder cap','P-020','PC 1.5',0.030,1,2),
 ('knee cap','P-022 (new)','PC 1.5',0.030,1,2),
 ('hip skirt (flexible)','P-023 (new)','TPU-nylon fabric + PC rim strip',0.11,1,2),
 ('waist bellows band','P-024 (new)','TPE bellows',3.1416*0.30*0.09,1,1),
 ('ankle boot (flexible)','P-025 (new)','TPU-nylon fabric, zip',A('ankle_boot')*0.80,1,2),
]
out=[];tot={}
for n,p,m,a,k,s in rows:
    ar = FAB if 'fabric' in m else ELA if 'TPE' in m else PC
    kg=s*(a*ar+k*INS)+(s*0.015 if 'zip' in m else 0)+(s*0.02 if 'rim' in m else 0)
    out.append(dict(panel=n,P=p,material=m,area_m2_side=round(a,4),panels=k*s,kg=round(kg,3),cf_kg=round(s*(a*CF+k*INS),3) if 'CF' in m else None))
    tot[p]=tot.get(p,0)+kg
json.dump(dict(rows=out,totals={k:round(v,3) for k,v in tot.items()},pc_area_m2=round(sum(r['area_m2_side']*(2) for r in out if r['P']=='P-020'),3)),open(os.path.join(H,'cover_set_v5.json'),'w'),indent=1)
for r in out: print(r)
print({k:round(v,3) for k,v in tot.items()})
