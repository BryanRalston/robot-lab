"""R-022 A5 check: re-run Actuators' ankle_stroke.py rule (v3/cad/model.py layout, 73 mm lever, TBM2G-06013)
over the ROM the gaits actually use (Legs npz: ankle pitch to -55 walk 1.2 / -59.9 stairs; |roll| <= 13.8) and the
contract mechanical ROM -60..+40. Rule: min pin-to-pin >= body + stroke + 14 (rod end). Run from repo root."""
import json, os, sys, itertools
R=os.path.abspath('.'); sys.path.insert(0,f'{R}/v3/cad'); os.chdir(f'{R}/v3/cad'); import model
S=json.load(open(f'{R}/modules/actuators/results/sizing.json'))['sel']['ankle_pitch']; mot=S['d']['motor']
orig=model.linear_actuator; rec={}
def la(n,*a,**k):
    L=orig(n,*a,**k); rec.setdefault(n,[]).append(L); return L
model.linear_actuator=la; model.P['ankle_lever']=73
def run(P,Rr):
    rec.clear()
    for p,r in itertools.product(P,Rr):
        model.PARTS.clear(); model.CHAINS.clear(); model.POSE.clear(); model.POSE.update({'L_ankle_pitch':p,'L_ankle_roll':r}); model.build_leg(1)
    Ls=[L for n,v in rec.items() if 'ankle' in n for L in v]; body=model.menv(mot)[1]+36+60; st=max(Ls)-min(Ls)
    return dict(Lmin=round(min(Ls),1),Lmax=round(max(Ls),1),stroke=round(st,1),need=round(body+st+14,1),margin=round(min(Ls)-body-st-14,1))
cases={'A_actuators_-45..40_x_25':((-45,-30,-15,0,20,40),(-25,0,25)),
 'B_mech_-60..40_x_25':((-60,-50,-45,-30,-15,0,20,40),(-25,0,25)),
 'C_mech_-60..40_x_15':((-60,-50,-45,-30,-15,0,20,40),(-15,0,15)),
 'D_mech_-60..40_x_12':((-60,-50,-45,-30,-15,0,20,40),(-12,0,12)),
 'E_loaded_-50..40_x_25':((-50,-45,-30,-15,0,20,40),(-25,0,25))}
out={k:run(*v) for k,v in cases.items()}
json.dump(out,open(f'{R}/modules/arbiter/a5_ankle_rom.json','w'),indent=1); print(json.dumps(out,indent=1))
