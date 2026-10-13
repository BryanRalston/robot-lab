"""v3.2: roller-screw stroke check (was never checked). A linear actuator needs, at its SHORTEST pin-to-pin length,
room for motor + nut + bearings (body) + the retracted screw (= stroke, the screw runs back through the hollow rotor/tube) + rod end (14 mm).
Poses: knee 0..135, ankle pitch -45..40 with roll ±25. Writes out/stroke.json"""
import json,model,math,itertools
rec={}
orig=model.linear_actuator
def la(name,*a,**k):
    L=orig(name,*a,**k); rec.setdefault(name,[]).append(L); return L
model.linear_actuator=la
mL={n:model.menv(n)[1] for n in model.PT.MOT}
poses=[{'L_knee':a} for a in (0,30,60,90,120,135)]+[{'L_ankle_pitch':p,'L_ankle_roll':r} for p in (-45,0,40) for r in (-25,0,25)]
for p in poses:
    model.PARTS.clear();model.CHAINS.clear();model.POSE.clear();model.POSE.update(p);model.build_leg(1)
out={}
ST=model.ST
for n,Ls in rec.items():
    j='knee' if 'knee' in n else 'ankle_pitch'
    body=mL[ST['J'][j]['motor']]+36+60
    stroke=max(Ls)-min(Ls); need=body+stroke+14
    out[n]=dict(Lmin=round(min(Ls),1),Lmax=round(max(Ls),1),stroke=round(stroke,1),need_min_len=round(need,1),ok=min(Ls)>=need)
    print(n,out[n])
json.dump(out,open('out/stroke.json','w'),indent=1)
