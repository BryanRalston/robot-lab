"""L77: D96 trimmed release housing (knee_twin_housing_release_r116b) vs L60 top plate at z 816 (original) and z 820 (+4), knee 0..145, true OCC."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
out={}
for a in (0,30,60,90,110,120,125,130,135,140,143,145):
    P=M.build({'L_knee':a}); h=[p for p in P if p['name'].startswith('L_knee twin housing')][0]['solid']; t=[p for p in P if p['name'].startswith('L_knee trunnion bracket top plate')][0]['solid']
    out[a]=dict(gap_z816=round(float(h.distance(t)),2),gap_z820=round(float(h.distance(t.translate(cq.Vector(0,0,4)))),2),housing_zmax=round(h.BoundingBox().zmax,2))
    print(a,out[a],flush=True)
json.dump(out,open(f'{HERE}/results/r031/housing_plate_gap_l77.json','w'),indent=1)
