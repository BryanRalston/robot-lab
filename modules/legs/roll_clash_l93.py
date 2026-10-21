"""L93: hip roll sign check + L/R hip_pitch screw bodies / ankle screws / knee housings vs adduction, straight other leg and walking poses."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
def foot_y(pz,sd):
    f=[p for p in M.build(pz) if p['seg']==sd+'_foot']; return round(sum((p['solid'].BoundingBox().ymin+p['solid'].BoundingBox().ymax)/2 for p in f)/len(f),1)
out={'sign':{'L_roll_-10_footY':foot_y({'L_hip_roll':-10},'L'),'L_roll_0':foot_y({},'L'),'R_roll_-10_footY':foot_y({'R_hip_roll':-10},'R'),'R_roll_0':foot_y({},'R')}}
print(out,flush=True)
G=[('hip_pitch screw','hip_pitch screw'),('ankle screw','ankle screw'),('knee twin housing','knee twin housing')]
def mins(pz):
    ps=M.build(pz); r={}
    for a,b in G:
        A=[p for p in ps if p['name'].startswith('L_') and a in p['name'] and 'body' in p['name'] or (p['name'].startswith('L_') and a=='knee twin housing' and a in p['name'])]
        B=[p for p in ps if p['name'].startswith('R_') and b in p['name'] and 'body' in p['name'] or (p['name'].startswith('R_') and b=='knee twin housing' and b in p['name'])]
        r[a]=round(min([float(x['solid'].distance(y['solid'])) for x in A for y in B] or [999]),2)
    return r
add=lambda sd,v:{f'{sd}_hip_roll':v} if sd=='L' else {'R_hip_roll':v}
res={}
# straight other leg: L adducts (sign from check)
sL=-1 if out['sign']['L_roll_-10_footY']<out['sign']['L_roll_0'] else 1
sR=-1 if out['sign']['R_roll_-10_footY']>out['sign']['R_roll_0'] else 1
out['adduction_sign']={'L':sL,'R':sR}
for a in (0,3,6,8,10,12):
    res[f'single_straight_add{a}']=mins({'L_hip_roll':sL*a})
    res[f'double_add{a}']=mins({'L_hip_roll':sL*a,'R_hip_roll':sR*a})
# walking: stance L adducted, swing R pitch +-25 with roll at measured range
for a in (4,6,7.6,10):
    for sp in (-25,25):
        res[f'walk_stanceLadd{a}_swingRpitch{sp}']=mins({'L_hip_roll':sL*a,'R_hip_pitch':sp,'R_knee':40,'R_hip_roll':sR*-3})
        res[f'walk_stanceLadd{a}_swingRpitch{sp}_Radd6.1']=mins({'L_hip_roll':sL*a,'R_hip_pitch':sp,'R_knee':40,'R_hip_roll':sR*6.1})
out['res']=res; json.dump(out,open(f'{HERE}/results/r031/roll_clash_l93.json','w'),indent=1); print(json.dumps(out))
