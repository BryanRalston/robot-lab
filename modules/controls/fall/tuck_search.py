"""R-065 / R-102 / Arms R10: tuck search + per-direction pad-angle table.
1) Inside-chest-outline candidates (original R-065).
2) Per-direction tuck for pad crush-axis <=15 deg (R-102): tuck B side/forward;
   diagonals = tuck B + waist yaw +/-45 toward fall shoulder. Writes tuck_search.json
   and updates angles in fall_config.json / tuck_per_dir_r102.json.
Light FK + mj_geomDistance only. No training."""
import mujoco,numpy as np,math,itertools,json,os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))
HERE=os.path.dirname(os.path.abspath(__file__))
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,'sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
# forearm 287 mm sensitivity
for s in 'LR':
    h=m.body(f'{s}_hand').id; v=m.body_pos[h].copy(); n=np.linalg.norm(v)
    if n>0: m.body_pos[h]=v+v/n*0.017
D=math.radians; tb=m.body('torso').id; J=lambda n:m.jnt_qposadr[m.joint(n).id]
arm=[m.geom(g).id for g in ('l_upper_arm','l_forearm','l_hand')]; obst=[m.geom(g).id for g in ('torso','pelvis','l_thigh','r_thigh','head')]
def ext_x(gi,R,c):
    Rg=d.geom_xmat[gi].reshape(3,3); p=d.geom_xpos[gi]; sz=m.geom_size[gi]
    if m.geom_type[gi]==3: pts=[p+Rg[:,2]*sz[1]*e for e in (-1,1)]; r=sz[0]
    else: pts=[p+Rg@np.array([a*sz[0],b*sz[1],cc*sz[2]]) for a in (-1,1) for b in (-1,1) for cc in (-1,1)]; r=0
    return max((R.T@(q-c))[0] for q in pts)+r
CROUCH=[False]
def ev(roll,yaw,pitch,elb,wy=0):
    d.qpos[:]=0; d.qpos[3]=1
    if CROUCH[0]:
        for sd in 'lr':
            for j,v in (('hip_pitch',-40.1),('knee',68.8),('ankle_pitch',-34.4)): d.qpos[J(f'{sd}_{j}')]=D(v)
    d.qpos[J('waist_yaw')]=D(wy)
    for j,v in (('shoulder_roll',roll),('shoulder_yaw',yaw),('shoulder_pitch',pitch),('elbow',elb)): d.qpos[J(f'l_{j}')]=D(v)
    mujoco.mj_forward(m,d); R=d.xmat[tb].reshape(3,3); c=d.xpos[tb]
    fx=max(ext_x(g,R,c) for g in arm[1:]); clr=min(mujoco.mj_geomDistance(m,d,a,o,0.5,None) for a in arm for o in obst)
    return fx,clr
def pad_ang_arms(az, wy=0):
    """Arms R10 ground-normal method (design table)."""
    R=d.xmat[tb].reshape(3,3)
    rollbody=m.jnt_bodyid[m.joint('l_shoulder_roll').id]
    n=R.T@d.xmat[rollbody].reshape(3,3)[:,1]
    a=np.radians(az); g=np.array([np.sin(np.radians(85))*np.cos(a),np.sin(np.radians(85))*np.sin(a),-np.cos(np.radians(85))])
    w_=np.radians(wy); Rz=np.array([[np.cos(w_),-np.sin(w_),0],[np.sin(w_),np.cos(w_),0],[0,0,1]])
    ang=float(np.degrees(np.arccos(np.clip(n@(Rz.T@g),-1,1))))
    return ang
def tau_est():
    sh=d.xpos[m.body('L_upper_arm').id]; e=d.xpos[m.body('L_forearm').id]; w=d.xpos[m.body('L_hand').id]
    com=0.5*sh+0.25*(e+w); return float(9.54*187.5*abs(com[2]-sh[2]))

CHEST=0.11+0.037; out=[]
for roll,yaw,pitch,elb in itertools.product([-5,0,10,20],[-60,-30,0,30],[-20,0,20,40,60],[0,-30,-60,-90,-110]):
    fx,clr=ev(roll,yaw,pitch,elb)
    if fx<=CHEST and clr>=0.010: out.append(dict(roll=roll,yaw=yaw,pitch=pitch,elbow=elb,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1)))
ad=[]
for roll,yaw,pitch,elb in itertools.product([-5,0,5],[-60,-45,-30,0,30],[0,10,20,30,40],[0,-20,-45,-70,-90]):
    fx,clr=ev(roll,yaw,pitch,elb)
    if fx<=CHEST and clr>=0.010: ad.append(dict(roll=roll,yaw=yaw,pitch=pitch,elbow=elb,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1)))
ad.sort(key=lambda r:(abs(r['pitch']),-r['clear_mm']))
CROUCH[0]=True; cr={}
for k,p in dict(A=(0,0,0,0),B=(5,0,0,0),D=(5,-30,10,-20),R5=(-5,-60,-20,-110)).items():
    fx,clr=ev(*p); cr[k]=dict(pose=p,front_x_mm=round(fx*1e3,1),clear_mm=round(clr*1e3,1))
# Per-direction R-102 / R10 table
per={}
CROUCH[0]=True
for dn,az,wy,pose,note in [
    ('L',90,0,(5,0,0,0),'tuck B side; R5 retired'),
    ('R',-90,0,(5,0,0,0),'tuck B side mirror'),
    ('F',0,0,(5,0,0,0),'chest pad primary'),
    ('LF',45,-45,(5,0,0,0),'B + waist yaw -45'),
    ('LB',135,45,(5,0,0,0),'B + waist yaw +45'),
    ('RF',-45,45,(5,0,0,0),'B + waist yaw +45 mirror'),
    ('RB',-135,-45,(5,0,0,0),'B + waist yaw -45 mirror'),
    ('LB_fallback',135,0,(-15,30,30,-75),'arm-only if waist slow'),
]:
    roll,yaw,pitch,elb=pose
    # arm at wy=0 for Arms angle method; clearance with wy in FK
    fx0,clr0=ev(roll,yaw,pitch,elb,0)
    ang=pad_ang_arms(az if dn!='R' else 90, wy if dn not in ('R','RF','RB') else -wy if dn=='R' else wy)
    # re-eval clearance with waist
    fx,clr=ev(roll,yaw,pitch,elb,wy)
    tau=tau_est()
    per[dn]=dict(roll=roll,yaw=yaw,pitch=pitch,elbow=elb,waist_yaw=wy,az=az,
                 pad_angle_deg=round(ang,1),margin_15=round(15-ang,1),clear_mm=round(clr*1e3,1),
                 tau_fall_est_Nm=round(tau,1),ok=bool(ang<=15 and clr>=0.010 and tau<=369),note=note)
# LF/LB at wy +/-30 for timing partial
for dn,az,wy in (('LF_wy30',45,-30),('LB_wy30',135,30)):
    ev(5,0,0,0,0); ang=pad_ang_arms(az,wy)
    per[dn]=dict(waist_yaw=wy,pad_angle_deg=round(ang,1),margin_15=round(15-ang,1),ok=ang<=15,
                 note='partial waist if 45 too slow')

CROUCH[0]=False; r5=ev(-5,-60,-20,-110)
out.sort(key=lambda r:(-r['clear_mm']))
res=dict(chest_front_mm=CHEST*1e3,forearm_ext_mm=17,R5_tuck=dict(front_x_mm=round(r5[0]*1e3,1),clear_mm=round(r5[1]*1e3,1)),
         n_ok=len(out),candidates=out[:12],adducted_n=len(ad),adducted=ad[:12],crouched_check=cr,
         per_direction_r102=per,R5_retired=True)
json.dump(res,open(os.path.join(HERE,'tuck_search.json'),'w'),indent=1)
json.dump(per,open(os.path.join(HERE,'tuck_per_dir_r102.json'),'w'),indent=1)
print(json.dumps(per,indent=1))
