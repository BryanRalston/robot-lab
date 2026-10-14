"""T-030 push-fall batch for the A44 fall mode (R-042). CPU MuJoCo on sim/v3/humanoid_v3.xml.
Scripted controller: standing PD + ankle balance (as sim/v3/balance_v3.py) -> lateral push -> fall detect
-> FALL mode (knee drop, fall-side arm tuck, hip-first lean via hip roll + waist pitch).
Shoulder pad = 3x3 point patch on the shoulder-pitch output body (L/R_shoulderP), constant-force crush:
plateau F_p reached over 2 mm [EST], held to crush s, then densification k_d [EST]. Forces applied with mj_applyFT.
Outputs one JSON line per run + summary. Usage:
  python t030_pushfall.py --pad 40 --runs 50 --dirs L,R,LB --out results/t030_pad40.jsonl
  python t030_pushfall.py --smoke   (one short fall, 30 mm pad)"""
import mujoco, numpy as np, json, argparse, os, math, time
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..','..'))
P=argparse.ArgumentParser()
P.add_argument('--pad',default='hc',choices=['hc','30','40'],help='hc = ID R4 cartridge (329a79a, R-054): HexWeb CR III 4.5 pcf pre-crushed 62x62x57 core, 80x100 face plate, primary'); P.add_argument('--runs',type=int,default=50)
P.add_argument('--dirs',default='L,R,LB',help='L,R,LB side batch (T-030); F = forward fall (T-031)'); P.add_argument('--seed',type=int,default=0)
P.add_argument('--impulse',default='40,80',help='push impulse range N*s (60 N*s worst case per A44 margin note)')
P.add_argument('--latency',type=float,default=0.05,help='fall-detect latency s [EST]')
P.add_argument('--knee',type=float,default=1.2,help='FALL-mode knee target rad [EST, tune on PC]')
P.add_argument('--hc-plateau',type=float,default=9170.0,help='honeycomb plateau N: gate batch 7050; R4 x1.0 6880, x1.3 8940')
P.add_argument('--pad-model',default='curve',choices=['curve','plateau'],help='curve: ARPRO 5170 x1.45 (Materials 5f8f149, default); plateau: ID d80df32 constant force (contrast only)')
P.add_argument('--arm',default='tuck',choices=['tuck'],help='R-057: tuck is permanent for every fall; reach/brace removed, no clutch credit')
P.add_argument('--hc-stroke',type=float,default=0.038,help='usable stroke m (Materials fd46ad8 lot-tested band 38-42 mm; gate 38)')
P.add_argument('--spike',type=float,default=1.0,help='start-spike factor over the first 2 mm (2.2 = un-pre-crushed core sensitivity)')
P.add_argument('--area-cm2',type=float,default=109.0)
P.add_argument('--carry',action='store_true',help='P-042 20 kg carry: release load first, then tuck')
P.add_argument('--release-s',type=float,default=0.05,help='hook release time s [EST, Arms to confirm]')
P.add_argument('--out',default=None); P.add_argument('--smoke',action='store_true')
P.add_argument('--no-fallmode',action='store_true',help='baseline: keep standing PD through the fall')
A=P.parse_args()
# pad law. 30 mm: v3 fall_model s=0.7t+3=24 mm, F_p chosen = gate 9.17 kN (bottom-out => E_sh>220 J).
# 40 mm: Industrial Design SHOULDER_PAD.md (d80df32): s=31 mm, F_p=7.10 kN (109 cm2 x 0.65 MPa EPP80 [EST]).
PAD={'30':dict(t=0.030,s=0.024,Fp=9170.0,face=0.105),'40':dict(t=0.040,s=0.031,Fp=7100.0,face=0.105),
     'hc':dict(t=0.0635,s=A.hc_stroke,Fp=A.hc_plateau,face=0.080,faceh=0.100,core=0.062)}[A.pad]   # R4: stack 57 core+0.5 plate+6 EPP [ID]; stroke 0.72x57=41.0 mm; plate 80w x 100h
PAD.setdefault('faceh',PAD['face']); PAD.setdefault('core',PAD['face'])
if A.pad=='hc': A.pad_model='honeycomb'
RAMP=0.002; KD=2.0e6; MU=0.8; ARM=0.06; C0=27700.0; DPW=0.085; GATE_F=9170.0; GATE_M=9170.0*0.06
PATCH=PAD['face']; PAD_Y=0.13 if A.pad=='hc' else 0.152; PAD_Z=-0.005 if A.pad=='hc' else 0.0   # pad centre lateral of shoulder-pitch joint: upper-arm offset 0.112 + capsule r 0.04 (sim/v3 geometry)
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,'sim','v3','humanoid_v3.xml')); d=mujoco.MjData(m); dt=m.opt.timestep
names=[m.actuator(i).name for i in range(m.nu)]; jid=m.actuator_trnid[:,0]; qa=m.jnt_qposadr[jid]; va=m.jnt_dofadr[jid]; lim=m.actuator_ctrlrange[:,1]
ai=lambda n:names.index(n); kp=np.clip(lim*3,30,600); kd=0.04*kp; MASS=m.body_subtreemass[1]
footg=[m.geom(n).id for n in ('l_foot','r_foot')]; floor=m.geom('floor').id
def nominal():
    mujoco.mj_resetData(m,d)
    for s in 'lr':
        for j,v in (('hip_pitch',-0.25),('knee',0.5),('ankle_pitch',-0.25),('elbow',-0.3)): d.qpos[m.jnt_qposadr[m.joint(f'{s}_{j}').id]]=v
    mujoco.mj_forward(m,d); lo=min(d.geom_xpos[g][2]-0.02 for g in footg); d.qpos[2]-=lo-0.0005; mujoco.mj_forward(m,d); return d.qpos.copy()
q0=nominal()
GRID=[(gx,gz) for gx in np.linspace(-PAD['face']/2,PAD['face']/2,3) for gz in np.linspace(-PAD['faceh']/2,PAD['faceh']/2,3)]
def pad_points(side):   # world points of the outer pad face (undeformed) and outward normal
    b=m.body(('L' if side>0 else 'R')+'_shoulderP').id; R=d.xmat[b].reshape(3,3); c=d.xpos[b]
    n=R@np.array([0,side,0.]); pts=[c+R@np.array([gx,side*(PAD_Y+PAD['t']),PAD_Z+gz]) for gx,gz in GRID]; return b,pts,n   # hc: shoulder-cap shell base ~y+0.30 torso frame (Arms R5 7f0ff7a) = 0.13 outboard of pitch joint
EPS=np.array([0,.25,.5,.75,.95]); SIG=np.array([0,.5,.7,1.6,2.32])*1e6   # ARPRO 5170 (R042_EPP_SHOULDER.md); >75 % extrapolated [EST]
ANG_T=[0,15,25]; ANG_R=[0.98,0.93,0.73]   # Materials fd46ad8 plateau ratio vs off-axis angle; normalised to 0 deg; >25 deg held + flagged unknown
ANGF=[1.0]
def pad_law(c):
    if c<=0: return 0.0
    if A.pad_model=='curve' and c/PAD['t']>0.75: return float(SIG[3])*1.45*A.area_cm2*1e-4   # beyond ARPRO data: run flagged UNKNOWN, force held (not extrapolated)
    if A.pad_model=='curve': return float(np.interp(c/PAD['t'],EPS,SIG))*1.45*A.area_cm2*1e-4 + (KD*(c-0.95*PAD['t']) if c>0.95*PAD['t'] else 0.)
    F=PAD['Fp']*min(c/RAMP,1.0)*ANGF[0]*(A.spike if (A.pad=='hc' and c<=RAMP) else 1.0)
    return F+KD*(c-PAD['s']) if c>PAD['s'] else F
def fall_targets(q,side,side_only=True):  # side=+1 falling to robot's left (+y)
    q=q.copy(); S='l' if side>0 else 'r'; O='r' if side>0 else 'l'
    for s in 'lr':
        q[m.jnt_qposadr[m.joint(f'{s}_hip_pitch').id]]=-A.knee/2-0.1; q[m.jnt_qposadr[m.joint(f'{s}_knee').id]]=A.knee; q[m.jnt_qposadr[m.joint(f'{s}_ankle_pitch').id]]=-0.6
    if side_only:   # hip-first lean, side falls only
        rl=m.jnt_range[m.joint(f'{S}_hip_roll').id]; q[m.jnt_qposadr[m.joint(f'{S}_hip_roll').id]]=rl[1] if side>0 else rl[0]   # pelvis toward fall side (hip-first)
        rl=m.jnt_range[m.joint(f'{O}_hip_roll').id]; q[m.jnt_qposadr[m.joint(f'{O}_hip_roll').id]]=rl[1] if side>0 else rl[0]
        q[m.jnt_qposadr[m.joint('waist_pitch').id]]=0.5
    if True:   # R-057 permanent tuck, both arms on forward falls
        D=math.radians
        for SS,sg in ((('l',1),('r',-1)) if not side_only else ((S,side),)):
            for j,v in (('shoulder_roll',D(-5)*sg),('shoulder_yaw',D(-60)*sg),('shoulder_pitch',D(-20)),('elbow',D(-110))): q[m.jnt_qposadr[m.joint(f'{SS}_{j}').id]]=v   # Arms R5 tuck, 8.6 mm clear (R mirrored)
    return q
DIRS={'L':(0,1.),'R':(0,-1.),'LB':(-0.7071,0.7071),'F':(1.,0.)}
LEG=lambda S: np.linalg.norm(d.xpos[m.body(S+'_thigh').id]-d.xpos[m.body(S+'_foot').id])
def run(dirn,J,rng):
    nominal(); qt=q0.copy(); push=np.array([*DIRS[dirn],0.])*J/0.1; side=1 if DIRS[dirn][1]>=0 else -1; fwd=dirn=='F'
    t_det=None; t_rel=None; ang_unknown=False; tau_g=0.; FT=None; leg0=leg1=None; Warm=0.; ang0=None; angpk=None; bypass=False; t_fm=None; t_imp=None; com_trig=None; com_imp=None; Wsh=0.; Woth=0.; Fpk=0.; cmax=0.; cen=np.zeros(2); cw=0.; prev_c={}
    E0=None; T=4.0 if not A.smoke else 2.5; f6=np.zeros(6)
    for k in range(int(T/dt)):
        t=d.time; com=d.subtree_com[1].copy()
        if t_fm is None:
            e=com[:2]-0.5*(d.geom_xpos[footg[0]][:2]+d.geom_xpos[footg[1]][:2])
            tau=kp*(qt[qa]-d.qpos[qa])-kd*d.qvel[va]
            for s in 'lr':
                tau[ai(s+'_ankle_pitch')]+=MASS*9.81*e[0]+20*d.qvel[0]; tau[ai(s+'_ankle_roll')]-=MASS*9.81*e[1]+20*d.qvel[1]
            roll=math.degrees(math.atan2(d.xmat[1][7],d.xmat[1][8]))
            cp=e[1]+d.qvel[1]*math.sqrt(com[2]/9.81)
            pitch=math.degrees(math.atan2(-d.xmat[1][6],d.xmat[1][8])); cpx=e[0]+d.qvel[0]*math.sqrt(com[2]/9.81)
            if t>1.0 and t_det is None and (abs(roll)>10 or abs(cp)>0.20 or abs(pitch)>10 or abs(cpx)>0.25): t_det=t; com_trig=com[2]; leg0=0.5*(LEG('L')+LEG('R'))
            if t_det is not None and t>=t_det+A.latency and not A.no_fallmode: t_fm=t; t_rel=t+(A.release_s if A.carry else 0.)
            if t_rel is not None and t>=t_rel and qt is not FT: FT=fall_targets(q0,side,not fwd); qt=FT
        else: tau=kp*(qt[qa]-d.qpos[qa])-kd*d.qvel[va]
        d.ctrl[:]=np.clip(tau,-lim,lim); d.xfrc_applied[:]=0
        if 1.0<=t<1.1: d.xfrc_applied[1,:3]=push
        if A.carry and (t_rel is None or t<t_rel):   # P-042 20 kg hook carry: 98 N down per hand until released
            for h in ('L_hand','R_hand'): d.xfrc_applied[m.body(h).id,2]-=98.1
        Ftot=0.
        for sd in (1,-1):
            b,pts,n=pad_points(sd)
            angn=math.degrees(math.acos(max(-1,min(1,-n[2])))); ANGF[0]=float(np.interp(angn,ANG_T,ANG_R))/0.98 if A.pad=='hc' else 1.0
            if A.pad=='hc' and angn>25 and any(-p[2]>0 for p in pts): ang_unknown=True
            for i,p in enumerate(pts):
                c=-p[2]; F=pad_law(c)/9 if c>0 else 0.
                if F>0:
                    v=np.zeros(6); mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,b,v,0)
                    vel=v[3:]+np.cross(v[:3],p-d.xpos[b]); vt=vel[:2]; ft=-MU*F*vt/max(np.linalg.norm(vt),0.05)

                    d.xfrc_applied[b,:3]+=[ft[0],ft[1],F]; d.xfrc_applied[b,3:]+=np.cross(p-d.xipos[b],[ft[0],ft[1],F])
                    Wsh+=F*max(-vel[2],0)*dt; Ftot+=F; cmax=max(cmax,c); cen+=F*np.array(GRID[i]); cw+=F
                    if t_imp is None: t_imp=t; com_imp=com[2]; leg1=0.5*(LEG('L')+LEG('R'))
        if Ftot>0:
            _,_,nn=pad_points(1 if DIRS[dirn][1]>0 else -1); a=round(math.degrees(math.acos(max(-1,min(1,-nn[2])))),1)   # pad normal vs straight-down: off-axis angle
            if ang0 is None: ang0=a
            if Ftot>=Fpk: angpk=a
        Fpk=max(Fpk,Ftot); Fpad_now=Ftot
        for i in range(d.ncon):   # positive (compressive) work of all other ground contacts except feet
            cn=d.contact[i]; gs={cn.geom1,cn.geom2}
            if floor not in gs or gs&set(footg): continue
            mujoco.mj_contactForce(m,d,i,f6); og=(gs-{floor}).pop(); bb=m.geom_bodyid[og]
            v=np.zeros(6); mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,bb,v,0)
            vel=v[3:]+np.cross(v[:3],cn.pos-d.xpos[bb]); Woth+=f6[0]*max(-vel[2],0)*dt
            if Fpad_now>0 and m.body(bb).name in ('torso','L_upper_arm','R_upper_arm','L_shoulderP','R_shoulderP'): bypass=True   # shoulder structure grounds while element loaded = hit outside face
            if Ftot>0 and m.body(bb).name in ('torso','L_upper_arm','R_upper_arm','L_shoulderP','R_shoulderP'): bypass=True   # shoulder structure touches ground while element loaded = hit outside face
            if t_imp is None: t_imp=t; com_imp=com[2]; leg1=0.5*(LEG('L')+LEG('R'))
        ia=ai(('l' if side>0 else 'r')+'_shoulder_roll'); pw=d.ctrl[ia]*d.qvel[va[ia]]
        if t_fm is not None and pw<0: Warm+=-pw*dt
        mujoco.mj_step(m,d)
        if t_fm is not None:
            for s_ in 'lr':
                jd=m.jnt_dofadr[m.joint(s_+'_shoulder_pitch').id]; tg=abs(d.qfrc_actuator[jd]-m.dof_armature[jd]*d.qacc[jd]+d.qfrc_constraint[jd]); tau_g=max(tau_g,tg)
    share=Wsh/(Wsh+Woth) if Wsh+Woth>0 else None; M=Fpk*ARM
    fs_rad=C0/(Fpk+2*M/DPW) if Fpk>0 else None; fs_ax=C0/(2*M/DPW+0.44*Fpk) if Fpk>0 else None
    crouch=(com_trig-com_imp) if (com_trig is not None and com_imp is not None) else None
    return dict(shoulder_pitch_gear_peak_Nm=round(tau_g,1),angle_beyond_25_unknown=ang_unknown,spike=A.spike,hc_stroke_mm=A.hc_stroke*1e3,t_release=t_rel,carry=A.carry,arm_used='tuck',dir=dirn,J=round(J,1),pad_mm=A.pad,fell=bool(t_imp is not None),t_detect=t_det,t_fallmode=t_fm,t_impact=t_imp,
        crouch_at_impact_m=(leg0-leg1) if (leg0 and leg1) else None,com_drop_at_impact_m=crouch,E_sh_J=round(Wsh,1),E_other_J=round(Woth,1),shoulder_share=share,pad_peak_N=round(Fpk),pad_crush_max_mm=round(cmax*1e3,1),
        bottomed=(cmax>0.75*PAD['t']) if A.pad_model=='curve' else (cmax>PAD['s']),beyond_data_unknown=bool(A.pad_model=='curve' and cmax>0.75*PAD['t']),impact_angle_deg=ang0,peak_angle_deg=angpk,bypass_contact=bypass,pad_model=A.pad_model,arm=A.arm,W_arm_backdrive_J=round(Warm,1),M_bearing_Nm=round(M,1),fs_radial=fs_rad,fs_axial=fs_ax,contact_centroid_mm=(cen/cw*1e3).round(1).tolist() if cw>0 else None)
JD=lambda o: o.item() if hasattr(o,"item") else str(o)
rng=np.random.default_rng(A.seed); J0,J1=map(float,A.impulse.split(','))
dirs=['L'] if A.smoke else A.dirs.split(','); n=1 if A.smoke else A.runs; R=[]
fo=open(A.out,'w') if A.out else None
if fo: os.makedirs(os.path.dirname(os.path.abspath(A.out)),exist_ok=True)
t0=time.time()
for dn in dirs:
    for i in range(n):
        r=run(dn,(J1 if A.smoke else rng.uniform(J0,J1)),rng); R.append(r); print(json.dumps(r,default=JD),flush=True)
        if fo: fo.write(json.dumps(r,default=JD)+'\n'); fo.flush()
ok=[r for r in R if r['fell'] and r['shoulder_share'] is not None]
S=dict(summary=True,pad_mm=A.pad,runs=len(R),fell=len(ok),wall_s=round(time.time()-t0,1))
if ok:
    S.update(share_p95=float(np.percentile([r['shoulder_share'] for r in ok],95)),M_max=max(r['M_bearing_Nm'] for r in ok),
      crouch_min=min((r['crouch_at_impact_m'] or 0) for r in ok),bottomed=sum(r['bottomed'] for r in ok),fs_radial_min=min(r['fs_radial'] or 99 for r in ok))
    S.update(stroke_max_mm=max(r['pad_crush_max_mm'] for r in ok),F_max=max(r['pad_peak_N'] for r in ok),bypass=sum(r['bypass_contact'] for r in ok),unknown=sum(r['beyond_data_unknown'] for r in ok),
      angle_p95=float(np.percentile([r['impact_angle_deg'] or 0 for r in ok],95)),centroid_abs_p95_mm=float(np.percentile([max(map(abs,r['contact_centroid_mm'] or [0,0])) for r in ok],95)))
    S.update(gear_pitch_max=max(r['shoulder_pitch_gear_peak_Nm'] for r in ok),angle_unknown=sum(r['angle_beyond_25_unknown'] for r in ok))
    if A.dirs=='F': S['PASS']=bool(S['gear_pitch_max']<=369.0)
    else: S['PASS']=bool(S['angle_p95']<=15.0 and S['angle_unknown']==0 and S['share_p95']<=0.40 and S['M_max']<=GATE_M and S['F_max']<=GATE_F and S['crouch_min']>=0.15 and S['bottomed']==0 and S['bypass']==0 and S['unknown']==0 and S['centroid_abs_p95_mm']<=(15.0 if A.pad=='hc' else PAD['face']*500))
print(json.dumps(S,default=JD)); fo and fo.write(json.dumps(S,default=JD)+'\n')
