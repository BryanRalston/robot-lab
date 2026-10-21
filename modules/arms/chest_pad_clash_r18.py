"""R18: left-arm clash sweep vs the T-031 chest pad, cross-body poses (right arm mirrors). clash_r13 approach: sim/v3 kinematics.
Arm surfaces are sampled from the real sim geoms: upper-arm capsule r40, forearm capsule r38, hand box 16x43x70 half (wrist joints 0).
The W2 carrier + pad envelope are sampled from cad/r15 STL, placed via L_shoulderP * Rx(roll) (same as r15_cover_clash).
Chest pad, torso frame: Torso R-146 / R1_ARCHITECTURE (land face x +0.056, y +-0.049, z 0.171..0.269), plus a +2 mm PC bezel/ID trim ring
[EST], so y +-0.051 and z 0.169..0.271. Face x: BEFORE +0.159 (100 core), AFTER +0.175 (116 core, ID 341ef4a).
Gate: >= 10 mm. Poses where any arm sample is inside the torso box (x+-0.11, y+-0.17, z0.05..0.31, crude; pad region excluded) are
self-colliding with the torso anyway, so they are listed as infeasible and not counted against the pad."""
import mujoco,numpy as np,json,os,itertools,trimesh
H=os.path.dirname(os.path.abspath(__file__))
m=mujoco.MjModel.from_xml_path(os.path.join(H,'../../sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
J=lambda n:m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)]; B=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
G=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,n)
rng=np.random.default_rng(0)
def caps(r,h,n=500):
    u=rng.uniform(0,2*np.pi,n); z=rng.uniform(-h-r,h+r,n); zc=np.clip(z,-h,h); dz=z-zc; rr=np.sqrt(np.maximum(r*r-dz*dz,0))
    return np.c_[rr*np.cos(u),rr*np.sin(u),z]
def boxs(hx,hy,hz,n=400):
    p=rng.uniform(-1,1,(n,3)); k=rng.integers(0,3,n); p[np.arange(n),k]=np.sign(p[np.arange(n),k]); return p*[hx,hy,hz]
LOC={'upper_arm':caps(.04,.085),'forearm':caps(.038,.108),'hand':boxs(.016,.043,.07)}
GN={'upper_arm':'l_upper_arm','forearm':'l_forearm','hand':'l_hand'}
CAR=np.vstack([trimesh.load(os.path.join(H,'cad/r15',f)).sample(800,seed=1) for f in ('carrier_w2.stl','pad_envelope_w2.stl')])/1000
Rx=lambda a:np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
def padgap(P,xmax):
    lo=np.array([.056,-.051,.169]); hi=np.array([xmax,.051,.271]); return np.linalg.norm(np.maximum(np.maximum(lo-P,P-hi),0),axis=1)
import cadquery as cq
from scipy.spatial import cKDTree
_st=cq.importers.importStep(os.path.join(H,'../design/cad/covers/chest_pad_bezel_r2.step'))
MS=[]
for so in _st.solids().vals():
    v,f=so.tessellate(0.2,0.2); MS.append(trimesh.Trimesh(np.array([[p.x,p.y,p.z] for p in v]),np.array(f)))
STEPM=trimesh.util.concatenate(MS); STEPM.vertices=(STEPM.vertices-[0,0,1280.0])/1000  # global -> torso frame (R-146: z 1451 global = 0.171 torso)
_sp=np.vstack([trimesh.sample.sample_surface_even(mm,max(2000,int(mm.area/4)))[0] for mm in MS]); _sp=(_sp-[0,0,1280.0])/1000
SB=[((mm.bounds[0]-[0,0,1280.0])/1000,(mm.bounds[1]-[0,0,1280.0])/1000) for mm in MS if mm.volume/np.prod(mm.bounds[1]-mm.bounds[0])>0.75]  # solid prisms only; thin fairing/posts use surface distance
KD=cKDTree(_sp); BB=(STEPM.bounds[0]-0.002,STEPM.bounds[1]+0.002)
def stepgap(P):
    dd=np.linalg.norm(np.maximum(np.maximum(BB[0]-P,P-BB[1]),0),axis=1)+0.0  # lower bound; exact KD only within 25 mm of the bbox
    c=dd<0.025
    if c.any(): dd[c]=KD.query(P[c])[0]
    near=((P>BB[0])&(P<BB[1])).all(1)
    if near.any():  # inside test: each STEP body is a prism/box, so its own AABB; only bodies whose volume fills >75 % of their AABB (rtree not on the box for mesh.contains)
        for lo_,hi_ in SB: dd[((P>lo_)&(P<hi_)).all(1)]=0
    return dd
STEP_ON=True
tlo=np.array([-.11,-.17,.05]); thi=np.array([.11,.17,.31])
def ev(sp,sr,sy,el):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for n,a in (('l_shoulder_pitch',sp),('l_shoulder_roll',sr),('l_shoulder_yaw',sy),('l_elbow',el)): d.qpos[J(n)]=np.radians(a)
    mujoco.mj_forward(m,d); t=B('torso'); Rt=d.xmat[t].reshape(3,3); to=d.xpos[t]
    pts={}
    for k,loc in LOC.items():
        g=G(GN[k]); W=d.geom_xpos[g]+loc@d.geom_xmat[g].reshape(3,3).T; pts[k]=(W-to)@Rt
    Rs=d.xmat[B('L_shoulderP')].reshape(3,3); o=d.xpos[B('L_shoulderP')]+Rs@np.array([0,.112,-.04])
    pts['W2_carrier']=((CAR@(Rs@Rx(np.radians(sr))).T)+o-to)@Rt
    inside_t=any((((P>tlo+0.002)&(P<thi-0.002)).all(1)).any() for k,P in pts.items() if k!='W2_carrier')
    r=dict(pose=[sp,sr,sy,el],infeasible_torso=bool(inside_t))
    for tag,xm in (('before',.159),('after',.175)):
        gg={k:float(padgap(P,xm).min()*1000) for k,P in pts.items()}; r[tag]=min(gg.values()); r[tag+'_part']=min(gg,key=gg.get)
    if STEP_ON:
        gg={k:float(stepgap(P).min()*1000) for k,P in pts.items()}; r['step']=min(gg.values()); r['step_part']=min(gg,key=gg.get)
    return r
named=dict(tuck_B=(5,0,0,0),roll_soft_127=(-30,127,0,0),hand_to_opp_shoulder=(-60,-15,-90,-140),hand_to_opp_shoulder_high=(-90,-15,-60,-140),
           hands_together_chest=(-60,-15,-60,-100),hands_together_low=(-30,-10,-45,-90),P042_two_hand_carry=(-45,-10,-30,-90),
           P042_carry_close=(-25,-10,-40,-110),forearm_across_chest=(-20,-15,-90,-130),elbow_fold_front=(-90,0,0,-140))
print('watertight',[mm.is_watertight for mm in MS])
out={'named':{k:ev(*v) for k,v in named.items()}}
rows=[ev(*p) for p in itertools.product(range(-120,61,10),range(-15,31,5),range(-150,151,15),range(-140,1,10))]
rows+= [ev(sp,127,sy,el) for sp,sy,el in itertools.product(range(-150,61,15),range(-150,151,30),range(-140,1,20))]
feas=[r for r in rows if not r['infeasible_torso']]
out['n_poses']=len(rows); out['n_feasible']=len(feas)
for tag in ('before','after'):
    w=min(feas,key=lambda r:r[tag]); out[f'min_{tag}']=w
    out[f'n_lt10_{tag}']=sum(r[tag]<10 for r in feas); out[f'n_contact_{tag}']=sum(r[tag]<=0 for r in feas)
new=[r for r in feas if r['after']<10 and r['before']>=10]; out['n_new_fail']=len(new)
out['new_fail_examples']=sorted(new,key=lambda r:r['after'])[:15]
fails=[r for r in feas if r['after']<10]
out['fail_parts_after']={p:sum(r['after_part']==p for r in fails) for p in ('upper_arm','forearm','hand','W2_carrier')}
def rngs(rs,i): v=[r['pose'][i] for r in rs]; return [min(v),max(v)] if v else None
out['fail_ranges_after']={n:rngs(fails,i) for i,n in enumerate(('pitch','roll','yaw','elbow'))}
out['newfail_ranges']={n:rngs(new,i) for i,n in enumerate(('pitch','roll','yaw','elbow'))}
# limit candidate: inward yaw limit as function of elbow, for poses with roll<=0 (cross-body)
lim={}
for el in range(-140,1,10):
    s=[r for r in feas if r['pose'][3]==el and r['after']<10]
    lim[el]=dict(yaw_fail=rngs(s,2),pitch_fail=rngs(s,0)) if s else None
out['after_fail_by_elbow']=lim
out['roll127_min_after']=min((r for r in feas if r['pose'][1]==127),key=lambda r:r['after'])
for tag in ('step',):
    w=min(feas,key=lambda r:r[tag]); out['min_step']=w; out['n_lt10_step']=sum(r['step']<10 for r in feas); out['n_contact_step']=sum(r['step']<=0 for r in feas)
    fs=[r for r in feas if r['step']<10]
    out['step_fail_parts']={p:sum(r['step_part']==p for r in fs) for p in ('upper_arm','forearm','hand','W2_carrier')}
    out['step_fail_ranges']={n:rngs(fs,i) for i,n in enumerate(('pitch','roll','yaw','elbow'))}
    out['step_fail_by_elbow']={el:(dict(yaw=rngs([r for r in fs if r['pose'][3]==el],2),pitch=rngs([r for r in fs if r['pose'][3]==el],0)) if any(r['pose'][3]==el for r in fs) else None) for el in range(-140,1,10)}
    out['step_new_vs_R18']=sum(r['step']<10 and r['after']>=10 for r in feas)
    out['step_roll127_min']=min((r for r in feas if r['pose'][1]==127),key=lambda r:r['step'])
    out['step_bbox_torso_m']=[list(np.round(STEPM.bounds[0],4)),list(np.round(STEPM.bounds[1],4))]
json.dump(out,open(os.path.join(H,'chest_pad_clash_r18.json'),'w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k.startswith(('step','n_','min_step'))}),json.dumps({k:(v['after'],v['step']) for k,v in out['named'].items()}))
