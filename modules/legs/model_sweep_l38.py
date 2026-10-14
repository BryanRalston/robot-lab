import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','model'))
import json,sys,clash_v4 as C, model_v4 as M
res=C.sweep(['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll'],st=15)
grid={}
for p in (-60,-45,-30,-15,0,15,30,40):
    for r in (-18,-9,9,18):
        c=C.clashes(M.build({'L_ankle_pitch':p,'L_ankle_roll':r}))
        c=[x for x in c if x[0].startswith('L_') or x[1].startswith('L_')]
        grid[f'{p},{r}']=c; print('grid',p,r,c[:3],flush=True)
combos={}
for lbl,pose in (('sit hip-90 knee120',{'L_hip_pitch':-90,'L_knee':120}),('deep squat hip-100 knee135',{'L_hip_pitch':-100,'L_knee':135}),('stance ankle -45 + roll 18',{'L_ankle_pitch':-45,'L_ankle_roll':18}),('ankle +40 roll -18',{'L_ankle_pitch':40,'L_ankle_roll':-18})):
    combos[lbl]=C.clashes(M.build(pose)); print(lbl,combos[lbl],flush=True)
json.dump(dict(sweep=res,grid=grid,combos=combos),open('/tmp/legsweep.json','w'),indent=1)
