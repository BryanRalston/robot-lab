"""L74 (2): P-156 rev 5/5a (ID a065aa3, thigh_knee_vents_r5.py) vs model_v4. Ducts modelled as SOLID envelope boxes (conservative), thigh frame, L leg:
plenum x -94..-34.5 y104-156 z643-681.9; chimney walls PA12 1.2 at y 103.5/156.5 x -34.5..-56 z682-793; baffle x -57..-56 y104-156 z688-792;
transfer duct x -76.4..-8.5 y104-248 z793-813; hood 5a x -100..-10, y 248-274 [EST: exit skin y 248 + 26 standoff], z 785-813.
Static gaps to thigh parts at zero pose; moving gaps over knee 0..145 + hip ROM; hood vs hip-skirt keep-out (pelvis-fixed) over hip pitch."""
import os,sys,json,math,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M, trimesh
from scipy.spatial import ConvexHull
def bx(x0,x1,y0,y1,z0,z1): return M.box(x1-x0,y1-y0,z1-z0,c=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
V=dict(plenum=(-94,-34.5,104,156,643,681.9),wall_py=(-56,-34.5,156.5,157.7,682,793),wall_ny=(-56,-34.5,102.3,103.5,682,793),
       baffle=(-57,-56,104,156,688,792),transfer=(-76.4,-8.5,104,248,793,813),hood=(-100,-10,248,274,785,813))
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for k,v in V.items(): M.add('V_'+k,'L_thigh',bx(*v),asm='V_'+k)
M.build_leg=bl
_st=M.step
M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116' if n=='knee_twin_housing' else n,*a,**k)   # D95 release housing rev B
POSES=[{}]+[{'L_knee':a} for a in (30,60,90,120,130,135,140,145)]+[{'L_hip_pitch':a} for a in (-107.3,-60,20,40)]+[{'L_hip_pitch':-100,'L_knee':135},{'L_hip_pitch':20,'L_knee':145},{'L_hip_roll':-20},{'L_hip_roll':45},{'L_hip_yaw':45},{'L_hip_yaw':-35}]
res={}
for pz in POSES:
    parts=M.build(pz); Vp=[p for p in parts if p['name'].startswith('V_')]
    for p in parts:
        if p['name'].startswith('V_'): continue
        if pz and p['seg']=='L_thigh': continue   # thigh-fixed: static, measured at zero pose
        b=p['solid'].BoundingBox()
        for v in Vp:
            bb=v['solid'].BoundingBox(); m=25
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(v['solid'].distance(p['solid'])),1); k=v['name']+' | '+p['name']
            if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
rows=sorted([[k,d,pz] for k,(d,pz) in res.items()],key=lambda t:t[1])
# hood vs hip skirt keep-out over hip pitch (rotate hood corners about the hip axis (0,130,920), +y)
E=ConvexHull(np.asarray(trimesh.load(f'{HERE}/results/v5/hip_skirt_keepout.stl').vertices)).equations
h=V['hood']; C=np.array([[x,y,z] for x in np.linspace(h[0],h[1],10) for y in np.linspace(h[2],h[3],4) for z in np.linspace(h[4],h[5],5)])
sk=[]
for a in (-107.3,-80,-60,-30,0,20,40):
    t=math.radians(a); Ry=np.array([[math.cos(t),0,math.sin(t)],[0,1,0],[-math.sin(t),0,math.cos(t)]]); P=(C-[0,130,920])@Ry.T+[0,130,920]
    sd=(P@E[:,:3].T+E[:,3]).max(1); sk.append(dict(hip_pitch=a,max_penetration_mm=round(float(-sd.min()),1) if sd.min()<0 else 0.0,min_outside_mm=round(float(sd.min()),1)))
kh=[p for p in M.build({}) if 'knee twin housing' in p['name'] and p['name'].startswith('L_')][0]['solid'].BoundingBox()
out=dict(housing_bbox=[round(v,1) for v in (kh.xmin,kh.xmax,kh.ymin,kh.ymax,kh.zmin,kh.zmax)],min_pairs=rows[:25],under_3mm=[r for r in rows if r[1]<3.0],hood_vs_skirt_keepout=sk)
json.dump(out,open(f'{HERE}/results/r031/p156_rev5_check_l74.json','w'),indent=1); print(json.dumps(out,indent=0))
