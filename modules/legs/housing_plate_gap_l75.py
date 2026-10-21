"""L75: release knee housing (D95 knee_twin_housing_release_r116) vs L60 trunnion top plate: segments + true OCC gap at zero pose and knee ROM."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116' if n=='knee_twin_housing' else n,*a,**k)
out={}
for pz in [{}]+[{'L_knee':a} for a in (15,30,60,90,110,120,125,130,135,140,143,145)]+[{'L_hip_pitch':-100,'L_knee':135},{'L_hip_pitch':20,'L_knee':145}]:
    P=M.build(pz); h=[p for p in P if p['name'].startswith('L_knee twin housing')][0]; t=[p for p in P if p['name'].startswith('L_knee trunnion bracket top plate')][0]
    out[str(pz)]=dict(housing_seg=h['seg'],plate_seg=t['seg'],gap_mm=round(float(h['solid'].distance(t['solid'])),2),housing_zmax=round(h['solid'].BoundingBox().zmax,2))
json.dump(out,open(f'{HERE}/results/r031/housing_plate_gap_l75.json','w'),indent=1); print(out)
