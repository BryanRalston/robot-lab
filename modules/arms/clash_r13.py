"""R13 clash check (light, sim/v3 kinematics, left side; right mirrors). Pad assembly per ID 00ff254 on the roll output, roll-only frame
(x = roll axis, +y = pad normal at roll 0): face plate 62x62 Y23..27, tray+core 54.8 sq Y27..102.3, centre Z -20. Stand-off ribs Y0..23 sit
inside the plate shadow. Sampled as solid boxes. Obstacles: head sphere r100 (sim geom) + 10 mm hair/cover allowance [EST], neck cylinder
r40 z0.295..0.37 [EST], torso/cover box x+-0.11 y+-0.17 z0.05..0.31 (tuck_r6), 7013 housing cyl r50 on shoulder_P (stator, moves with pitch,
not roll) axial x -0.090..-0.034 [EST: pad x-range +-31 + 3 mm gap; CAD must confirm], own forearm capsule r38 (tuck_r6), hand r45.
Gate: >= 10 mm clear (tuck_r6 rule). Pad proud +15 mm vs R8 is inherent in Y 102.3."""
import mujoco,numpy as np,json,os,itertools
H=os.path.dirname(os.path.abspath(__file__))
m=mujoco.MjModel.from_xml_path(os.path.join(H,'../../sim/v3/humanoid_v3.xml')); d=mujoco.MjData(m)
J=lambda n:m.jnt_qposadr[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)]; B=lambda n:mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n)
def boxpts(x,y,z,n=7): return np.array([[a,b,c] for a in np.linspace(*x,n) for b in np.linspace(*y,n) for c in np.linspace(*z,n)])
PAD=np.vstack([boxpts((-.031,.031),(.023,.027),(-.051,.011)),boxpts((-.0274,.0274),(.027,.1023),(-.0474,.0074))])
lo=np.array([-0.11,-0.17,0.05]);hi=np.array([0.11,0.17,0.31])
bx=lambda P:np.linalg.norm(np.maximum(np.maximum(lo-P,P-hi),0),axis=1)
Rx=lambda a:np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
def segd(P,a,b):
    ab=b-a; t=np.clip(((P-a)@ab)/(ab@ab),0,1); return np.linalg.norm(P-(a+t[:,None]*ab),axis=1)
def ev(sp,sr,sy=0,el=0,ext=0.017):
    mujoco.mj_resetData(m,d); d.qpos[2]=1.16
    for n,a in (('l_shoulder_pitch',sp),('l_shoulder_roll',sr),('l_shoulder_yaw',sy),('l_elbow',el)): d.qpos[J(n)]=np.radians(a)
    mujoco.mj_forward(m,d); t=B('torso'); Rt=d.xmat[t].reshape(3,3); rel=lambda p:Rt.T@(p-d.xpos[t])
    Rs=d.xmat[B('L_shoulderP')].reshape(3,3); o=d.xpos[B('L_shoulderP')]+Rs@np.array([0,.112,-.04])
    Rr=Rs@Rx(np.radians(sr)); P=np.array([rel(o+Rr@p) for p in PAD])
    hd=rel(d.xpos[B('head')]+d.xmat[B('head')].reshape(3,3)@np.array([.01,0,.08]))
    g_head=np.min(np.linalg.norm(P-hd,axis=1))-0.110
    g_neck=np.min(segd(P,np.array([0,0,.295]),np.array([0,0,.37])))-0.040
    g_torso=np.min(bx(P))
    # housing (stator) in shoulderP frame
    Ph=np.array([Rs.T@(o+Rr@p-o) for p in PAD]); inx=(Ph[:,0]>-0.090)&(Ph[:,0]<-0.034)
    g_hous=np.min(np.where(inx,np.hypot(Ph[:,1],Ph[:,2])-0.050,1.0)); g_hous_ax=np.min(Ph[:,0])-(-0.034)
    e=rel(d.xpos[B('L_forearm')]); w=rel(d.xpos[B('L_hand')]); w=w+(w-e)/np.linalg.norm(w-e)*ext
    g_fa=min(np.min(segd(P,e,w))-0.038,np.min(np.linalg.norm(P-w,axis=1))-0.045)
    r=dict(pose=[sp,sr,sy,el],head=g_head,neck=g_neck,torso=g_torso,housing_axial=g_hous_ax,housing_radial_if_overlap=g_hous,forearm_hand=g_fa)
    return {k:(round(float(v)*1000,1) if isinstance(v,(float,np.floating)) else v) for k,v in r.items()}
out={}
out['tuck_B']=ev(5,0,0,0)
out['R5_tuck']=ev(-20,-5,-60,-110)
sw=[ev(sp,sr) for sp,sr in itertools.product(range(-180,61,15),range(-15,181,5))]
def worst(rows,k): return min(rows,key=lambda r:r[k])
out['abduction_sweep_worst']={k:worst(sw,k) for k in ('head','neck','torso')}
out['head_limit']={}
for sp in (0,-30,-60,-90):
    rows=[ev(sp,sr) for sr in range(90,181,1)]
    bad=[r['pose'][1] for r in rows if min(r['head'],r['neck'])<10]
    out['head_limit'][sp]=dict(first_roll_lt10mm=bad[0] if bad else None,min_head=min(r['head'] for r in rows),min_neck=min(r['neck'] for r in rows),
                                at135=[r for r in rows if r['pose'][1]==135][0])
el=[ev(sp,sr,sy,elb) for sp,sr,sy,elb in itertools.product(range(-90,61,30),range(-15,91,15),range(-150,151,30),range(-140,1,20))]
out['elbow_fold_worst']=worst(el,'forearm_hand'); out['n_fold_lt10']=int(sum(r['forearm_hand']<10 for r in el)); out['n_fold']=len(el)
out['abduction_n']=len(sw); out['abduction_lt10_torso']=int(sum(r['torso']<10 for r in sw))
json.dump(out,open(os.path.join(H,'clash_r13.json'),'w'),indent=1); print(json.dumps(out,indent=1))
