"""D96 re-sweep: runs Legs' drive_plate_sweep_d95_l74.py (af1b331) unchanged except: knee housing -> release_r116b (fin-tip trim),
ankle-roll stop carrier with the D96 relief, output -> results/resweep_d96.json. Adds the housing <-> L60 top plate distance."""
import os,sys,json
H=os.path.dirname(os.path.abspath(__file__)); LG=os.path.join(H,'../legs')
src=open(os.path.join(LG,'drive_plate_sweep_d95_l74.py')).read()
src=src.replace("'knee_twin_housing_release_r116'","'knee_twin_housing_release_r116b'")
src=src.replace("f'{HERE}/results/r031/drive_plate_sweep_d95_l74.json'","os.path.join(%r,'results/resweep_d96.json')"%H)
src=src.replace("import cadquery as cq, model_v4 as M","import cadquery as cq, model_v4 as M\nexec(open(%r).read().split('out=[]')[0].split('M.add=add')[0]+'M.add=add')"%os.path.join(H,'ankle_carrier_relief_d96.py'))
g={'__file__':os.path.join(LG,'drive_plate_sweep_d95_l74.py'),'__name__':'__main__'}
exec(compile(src,'l74_d96','exec'),g)
M=g['M']; out={}
for pz in [{'L_knee':k} for k in range(0,146,5)]+[{'L_hip_pitch':20,'L_knee':145},{'L_hip_pitch':-107.3}]:
    parts=M.build(pz); h=[p for p in parts if p['name'].startswith('L_knee twin housing')][0]
    tp=[p for p in parts if p['name'].startswith('L_knee trunnion bracket top plate')][0]
    out[str(pz)]=round(float(h['solid'].distance(tp['solid'])),2)
print('housing-top plate',out)
r=json.load(open(os.path.join(H,'results/resweep_d96.json'))); r['_housing_to_L60_top_plate_mm']=out
json.dump(r,open(os.path.join(H,'results/resweep_d96.json'),'w'),indent=1)
