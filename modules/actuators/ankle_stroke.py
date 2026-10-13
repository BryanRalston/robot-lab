"""R6 A5 (R-020 C2a): ankle RV12x4 stroke at the 73 mm lever over the full ankle range (pitch -45..+40 x roll -25..+25, v3 MJCF),
using the v3 CAD layout (v3/cad/model.py) with P['ankle_lever'] 70 -> 73 and the R5 motor TBM2G-06013 (sizing.json). Rule as v3/cad/stroke.py:
min pin-to-pin length >= body (motor env + 36 nut + 60 bearings/housing) + stroke (screw retracts through the hollow rotor) + 14 rod end."""
import json, os, sys, itertools
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.abspath(f'{H}/../../v3/cad')); os.chdir(os.path.abspath(f'{H}/../../v3/cad'))
import model
S=json.load(open(f'{H}/results/sizing.json'))['sel']['ankle_pitch']; mot=S['d']['motor']
orig=model.linear_actuator; rec={}
def la(name,*a,**k):
    L=orig(name,*a,**k); rec.setdefault(name,[]).append(L); return L
model.linear_actuator=la
ROLL=float(os.environ.get('ROLL',25)); PMIN=float(os.environ.get('PMIN',-45)); TAG=os.environ.get('TAG','73')
out={}
for arm in ((70,73) if TAG=='73' else (73,)):
    model.P['ankle_lever']=arm; rec.clear()
    for p,r in itertools.product(sorted(set([PMIN,-45,-30,-15,0,20,30,40])),(-ROLL,-ROLL/2,0,ROLL/2,ROLL)):
        model.PARTS.clear(); model.CHAINS.clear(); model.POSE.clear(); model.POSE.update({'L_ankle_pitch':p,'L_ankle_roll':r}); model.build_leg(1)
    for n,Ls in rec.items():
        if 'ankle' not in n: continue
        body=model.menv(mot)[1]+36+60; st=max(Ls)-min(Ls); need=body+st+14
        out[f'{arm}mm {n}']=dict(pitch=[PMIN,40],roll=ROLL,Lmin=round(min(Ls),1),Lmax=round(max(Ls),1),stroke=round(st,1),body=round(body,1),need_min_len=round(need,1),margin=round(min(Ls)-need,1),ok=min(Ls)>=need)
json.dump(out,open(f'{H}/results/ankle_stroke_{TAG}.json','w'),indent=1); print(json.dumps(out,indent=1))
