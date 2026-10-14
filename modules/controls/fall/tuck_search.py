"""R-065 T-031(a): search sim/v3 arm poses that keep forearm+hand inside the chest outline (torso-frame x <= chest front 0.11 m)
and >= 10 mm clearance to torso, pelvis, thighs (R-058). FK + mj_geomDistance only (light). Left arm; right mirrors roll/yaw sign."""
import mujoco,numpy as np,math,itertools,json,os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,'sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
D=math.radians; tb=m.body('torso').id
arm=[m.geom(g).id for g in ('l_upper_arm','l_forearm','l_hand')]; obst=[m.geom(g).id for g in ('torso','pelvis','l_thigh','r_thigh','head')]
def ext_x(gi,R,c):   # max torso-frame x of a capsule/box geom (approx: ends + radius, box corners)
    Rg=d.geom_xmat[gi].reshape(3,3); p=d.geom_xpos[gi]; sz=m.geom_size[gi]
    if m.geom_type[gi]==3: pts=[p+Rg[:,2]*sz[1]*e for e in (-1,1)]; r=sz[0]
    else: pts=[p+Rg@np.array([a*sz[0],b*sz[1],cc*sz[2]]) for a in (-1,1) for b in (-1,1) for cc in (-1,1)]; r=0
    return max((R.T@(q-c))[0] for q in pts)+r
CROUCH=[False]
def ev(roll,yaw,pitch,elb):
    d.qpos[:]=0; d.qpos[3]=1
    if CROUCH[0]:
        for sd in 'lr':
            for j,v in (('hip_pitch',-40.1),('knee',68.8),('ankle_pitch',-34.4)): d.qpos[m.jnt_qposadr[m.joint(f'{sd}_{j}').id]]=D(v)   # FALL-mode crouch (knee 1.2 rad)
    for j,v in (('shoulder_roll',roll),('shoulder_yaw',yaw),('shoulder_pitch',pitch),('elbow',elb)): d.qpos[m.jnt_qposadr[m.joint('l_'+j).id]]=D(v)
    mujoco.mj_forward(m,d); R=d.xmat[tb].reshape(3,3); c=d.xpos[tb]
    fx=max(ext_x(g,R,c) for g in arm[1:]); clr=min(mujoco.mj_geomDistance(m,d,a,o,0.5,None) for a in arm for o in obst)
    return fx,clr
CHEST=0.11; out=[]
for roll,yaw,pitch,elb in itertools.product([-5,0,10,20],[-60,-30,0,30],[-20,0,20,40,60],[0,-30,-60,-90,-110]):
    fx,clr=ev(roll,yaw,pitch,elb)
    if fx<=CHEST and clr>=0.010: out.append(dict(roll=roll,yaw=yaw,pitch=pitch,elbow=elb,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1)))
ad=[]   # adducted subset (roll <= +5): keeps the arm inside the shoulder-cap pad footprint for side falls too (one pose for all directions)
for roll,yaw,pitch,elb in itertools.product([-5,0,5],[-60,-45,-30,0,30],[0,10,20,30,40],[0,-20,-45,-70,-90]):
    fx,clr=ev(roll,yaw,pitch,elb)
    if fx<=CHEST and clr>=0.010: ad.append(dict(roll=roll,yaw=yaw,pitch=pitch,elbow=elb,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1)))
ad.sort(key=lambda r:(abs(r['pitch']),-r['clear_mm']))
CROUCH[0]=True; cr={}
for k,p in dict(A=(0,0,0,0),B=(5,0,0,0),C=(0,0,20,-45),D=(5,-30,10,-20),R5=(-5,-60,-20,-110)).items():
    fx,clr=ev(*p); cr[k]=dict(pose=p,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1))
CROUCH[0]=False
r5=ev(-5,-60,-20,-110)
out.sort(key=lambda r:(-r['clear_mm']))
res=dict(chest_front_mm=CHEST*1e3,R5_tuck=dict(front_x_mm=round(r5[0]*1e3,1),clear_mm=round(r5[1]*1e3,1)),n_ok=len(out),candidates=out[:12],adducted_n=len(ad),adducted=ad[:12],crouched_check=cr)
json.dump(res,open(os.path.join(os.path.dirname(__file__),'tuck_search.json'),'w'),indent=1); print(json.dumps(res,indent=1))
