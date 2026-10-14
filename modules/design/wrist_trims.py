"""Wrist fairing trims (R-059 accepted +0.079 pair). Base: 0.095/side (skin 0.044 m2 PC 1.5 + 4 inserts)."""
import json,os,math
H=os.path.dirname(os.path.abspath(__file__)); PCA=1.8; per=2*(124-70)+math.pi*70
it={}
it['1.2 mm PC on the y-flats (low draw, 2 x 54 x 96 mm)']=-2*0.054*0.096*0.3e-3*1200
it['dorsal motor slots 20 % (3 mm slots, 2 rows/unit)']=-0.20*(per/2*96e-6)*PCA*0.85*0.5
it['shorter blends 25->15 mm (elbow) and 20->12 mm (cuff); cuff edge held at z >= +10 over |y|<=62 (Arms sweep)']=-(per*18e-6)*PCA
it['palm-side half as open frame (Arms-accepted: openings <=10 mm radiused, 4 mm members, ~55 % open)']=-0.55*(0.0440-0.0059)/2*PCA*0.9
side=sum(it.values())
guard=0.015*0.140*1.0e-3*1200
out=dict(contingency_PTFE_guard_strip_kg_side=round(guard,4),contingency_pair=round(2*guard,4),items_kg_side={k:round(v,4) for k,v in it.items()},trim_side=round(side,4),trim_pair=round(2*side,3),new_pair=round(0.190+2*side,3),new_delta_vs_plain=round(0.079+2*side,3))
json.dump(out,open(os.path.join(H,'wrist_trims.json'),'w'),indent=1); print(json.dumps(out,indent=1))
