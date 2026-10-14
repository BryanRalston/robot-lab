"""T-030 push-fall batch for the A44 fall mode (R-042). CPU MuJoCo on sim/v3/humanoid_v3.xml.
Scripted controller: standing PD + ankle balance (as sim/v3/balance_v3.py) -> lateral push -> fall detect
-> FALL mode (knee drop, fall-side arm tuck, hip-first lean via hip roll + waist pitch).
Shoulder pad = 3x3 point patch on the shoulder-pitch output body (L/R_shoulderP), constant-force crush:
plateau F_p reached over 2 mm [EST], held to crush s, then densification k_d [EST]. Forces applied with mj_applyFT.
Outputs one JSON line per run + summary. Usage:
  python t030_pushfall.py --pad 40 --runs 50 --dirs L,R,LB --out results/t030_pad40.jsonl
  python t030_pushfall.py --smoke   (one short fall, 30 mm pad)"""
import collections
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
P.add_argument('--tuck',default='R5',choices=['R5','A','B','D','preload'],help='R-065 T-031: R5 (Arms), A/B/D inside-chest-outline candidates (tuck_search.py), preload = R5 + adduction/pitch bias into chest')
P.add_argument('--preload-Nm',type=float,default=30.0,help='preload torque for --tuck preload [EST]')
P.add_argument('--forearm-crush-N',type=float,default=0.0,help='T-031(c): forearm crush element plateau N (0 = none)')
P.add_argument('--forearm-crush-stroke',type=float,default=0.030,help='forearm element stroke m [EST]')
P.add_argument('--hc-stroke',type=float,default=0.038,help='usable stroke m (Materials fd46ad8 lot-tested band 38-42 mm; gate 38)')
P.add_argument('--spike',type=float,default=1.0,help='start-spike factor over the first 2 mm (2.2 = un-pre-crushed core sensitivity)')
P.add_argument('--area-cm2',type=float,default=109.0)
P.add_argument('--carry',action='store_true',help='P-042 20 kg carry: release load first, then tuck')
P.add_argument('--release-s',type=float,default=0.22,help='hook release time s (Arms R7: 0.12-0.22; default worst 0.22)')
P.add_argument('--chest-k',type=float,default=0.0,help='T-031 spring proxy: chest contact stiffness N/m on torso geoms (solref); 0 = off. Rev2 proxy k_eq 0.53e6, zeta 1.0')
P.add_argument('--chest-zeta',type=float,default=1.0,help='damping ratio for --chest-k (rev2 proxy zeta 1.0)')
P.add_argument('--chest-plateau',type=float,default=0.0,help='T-031 chest crush pad plateau N (rev2: floor 16600@15deg / 17700@0deg; ceiling 22350). 0 = off')
P.add_argument('--chest-stroke',type=float,default=0.062,help='chest pad usable stroke m before densification (rev2: 62 mm; FAIL if exceeded)')
P.add_argument('--chest-standout',type=float,default=0.037,help='R-088: chest-pad outer face forward of sim/v3 torso front (0.11) in m')
P.add_argument('--pad-lever',type=float,default=0.064,help='Arms R7: pad centre to shoulder_pitch bearing lever m (was 0.06)')
P.add_argument('--pad-e',type=float,default=0.010,help='Arms R7: pad centre offset from roll-bearing plane m (e<=0.010, s0>=2)')
P.add_argument('--out',default=None); P.add_argument('--smoke',action='store_true')
P.add_argument('--no-fallmode',action='store_true',help='baseline: keep standing PD through the fall')
A=P.parse_args()
# pad law. 30 mm: v3 fall_model s=0.7t+3=24 mm, F_p chosen = gate 9.17 kN (bottom-out => E_sh>220 J).
# 40 mm: Industrial Design SHOULDER_PAD.md (d80df32): s=31 mm, F_p=7.10 kN (109 cm2 x 0.65 MPa EPP80 [EST]).
PAD={'30':dict(t=0.030,s=0.024,Fp=9170.0,face=0.105),'40':dict(t=0.040,s=0.031,Fp=7100.0,face=0.105),
     'hc':dict(t=0.0635,s=A.hc_stroke,Fp=A.hc_plateau,face=0.080,faceh=0.100,core=0.062)}[A.pad]   # R4: stack 57 core+0.5 plate+6 EPP [ID]; stroke 0.72x57=41.0 mm; plate 80w x 100h
PAD.setdefault('faceh',PAD['face']); PAD.setdefault('core',PAD['face'])
if A.pad=='hc': A.pad_model='honeycomb'
RAMP=0.002; KD=2.0e6; MU=0.8; ARM=A.pad_lever; C0=27700.0; DPW=0.085; GATE_F=9170.0; GATE_M=9170.0*ARM
# Roll bearing CRBH 6013 A (Arms R7): C0 24.3 kN, dp~75 mm; s0 = C0/P0, pass >=2
C0_ROLL=24300.0; DPW_ROLL=0.075; PAD_E=A.pad_e
PATCH=PAD['face']; PAD_Y=0.06 if A.pad=='hc' else 0.152; PAD_Z=0.0   # Arms R7: pad on roll-yaw link (upper_arm); ~link half-width + boss [EST]
CHEST_FACE=0.11+A.chest_standout  # R-088: old torso half-x 0.11 + 37 mm standout
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,'sim','v3','humanoid_v3.xml')); d=mujoco.MjData(m); dt=m.opt.timestep
if A.chest_k>0:   # R-070: real chest stiffness on torso contact geoms
    _tb=m.body('torso').id; _b=2*A.chest_zeta*math.sqrt(A.chest_k*m.body_subtreemass[_tb])
    for _g in range(m.ngeom):
        if m.geom_bodyid[_g]==_tb: m.geom_solref[_g]=[-A.chest_k,-_b]
names=[m.actuator(i).name for i in range(m.nu)]; jid=m.actuator_trnid[:,0]; qa=m.jnt_qposadr[jid]; va=m.jnt_dofadr[jid]; lim=m.actuator_ctrlrange[:,1]
ai=lambda n:names.index(n); kp=np.clip(lim*3,30,600); kd=0.04*kp; MASS=m.body_subtreemass[1]
footg=[m.geom(n).id for n in ('l_foot','r_foot')]; floor=m.geom('floor').id
def nominal():
    mujoco.mj_resetData(m,d)
    for s in 'lr':
        for j,v in (('hip_pitch',-0.25),('knee',0.5),('ankle_pitch',-0.25),('elbow',-0.3)): d.qpos[m.jnt_qposadr[m.joint(f'{s}_{j}').id]]=v
    mujoco.mj_forward(m,d); lo=min(d.geom_xpos[g][2]-0.02 for g in footg); d.qpos[2]-=lo-0.0005; mujoco.mj_forward(m,d); return d.qpos.copy()
if A.forearm_crush_N>0:
    for g in ('l_forearm','r_forearm','l_hand','r_hand'): m.geom_contype[m.geom(g).id]=0; m.geom_conaffinity[m.geom(g).id]=0
q0=nominal()
GRID=[(gx,gz) for gx in np.linspace(-PAD['face']/2,PAD['face']/2,3) for gz in np.linspace(-PAD['faceh']/2,PAD['faceh']/2,3)]
def pad_points(side):   # Arms R7: pad on roll-yaw link (upper_arm); crush axis = body ±y
    b=m.body(('L' if side>0 else 'R')+'_upper_arm').id; R=d.xmat[b].reshape(3,3); c=d.xpos[b]
    n=R@np.array([0,side,0.]); pts=[c+R@np.array([gx,side*(PAD_Y+PAD['t']),PAD_Z+gz]) for gx,gz in GRID]; return b,pts,n
EPS=np.array([0,.25,.5,.75,.95]); SIG=np.array([0,.5,.7,1.6,2.32])*1e6   # ARPRO 5170 (R042_EPP_SHOULDER.md); >75 % extrapolated [EST]
ANG_T=[0,15,25]; ANG_R=[0.98,0.93,0.73]   # Materials fd46ad8 plateau ratio vs off-axis angle; normalised to 0 deg; >25 deg held + flagged unknown
ANGF=[1.0]
def pad_law(c):
    if c<=0: return 0.0
    if A.pad_model=='curve' and c/PAD['t']>0.75: return float(SIG[3])*1.45*A.area_cm2*1e-4   # beyond ARPRO data: run flagged UNKNOWN, force held (not extrapolated)
    if A.pad_model=='curve': return float(np.interp(c/PAD['t'],EPS,SIG))*1.45*A.area_cm2*1e-4 + (KD*(c-0.95*PAD['t']) if c>0.95*PAD['t'] else 0.)
    F=PAD['Fp']*min(c/RAMP,1.0)*ANGF[0]*(A.spike if (A.pad=='hc' and c<=RAMP) else 1.0)
    return F+KD*(c-PAD['s']) if c>PAD['s'] else F
TUCKS=dict(R5=(-5,-60,-20,-110),A=(0,0,0,0),B=(5,0,0,0),D=(5,-30,10,-20),preload=(-5,-60,-20,-110))   # deg; A/B/D from tuck_search.py, Arms to confirm
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
            for j,v in zip(('shoulder_roll','shoulder_yaw','shoulder_pitch','elbow'),TUCKS[A.tuck]): q[m.jnt_qposadr[m.joint(f'{SS}_{j}').id]]=D(v)*(sg if j in ('shoulder_roll','shoulder_yaw') else 1)   # Arms R5 tuck, 8.6 mm clear (R mirrored)
    return q
DIRS={'L':(0,1.),'R':(0,-1.),'LB':(-0.7071,0.7071),'LF':(0.7071,0.7071),'RF':(0.7071,-0.7071),'F':(1.,0.)}
LEG=lambda S: np.linalg.norm(d.xpos[m.body(S+'_thigh').id]-d.xpos[m.body(S+'_foot').id])
def run(dirn,J,rng):
    nominal(); qt=q0.copy(); push=np.array([*DIRS[dirn],0.])*J/0.1; side=1 if DIRS[dirn][1]>=0 else -1; fwd=dirn in ('F','LF','RF') and A.dirs.startswith('F')
    t_det=None; t_rel=None; fc_max=0.; ang_unknown=False; tau_g=0.; FT=None; leg0=leg1=None; Warm=0.; ang0=None; angpk=None; bypass=False; t_fm=None; t_imp=None; com_trig=None; com_imp=None; Wsh=0.; Woth=0.; Fpk=0.; cmax=0.; cen=np.zeros(2); cw=0.; prev_c={}; chest_g=0.; _na=max(1,round(0.002/dt)); _vb=collections.deque(maxlen=_na+1); hand_thigh_min=1e9; outside_core=0; chest_cmax=0.; chest_ang0=None; chest_angpk=None; chest_Fpk=0.; chest_bottomed=False; chest_ang_fail=False; m_eff=None; first_contact=None
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
        else:
            tau=kp*(qt[qa]-d.qpos[qa])-kd*d.qvel[va]
            if A.tuck=='preload':
                for s_,sg in (('l',1),('r',-1)): tau[ai(s_+'_shoulder_roll')]-=A.preload_Nm*sg; tau[ai(s_+'_elbow')]-=A.preload_Nm
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
                    if t_imp is None: t_imp=t; com_imp=com[2]; leg1=0.5*(LEG('L')+LEG('R')); first_contact='shoulder_pad'
        if Ftot>0:
            _,_,nn=pad_points(1 if DIRS[dirn][1]>0 else -1); a=round(math.degrees(math.acos(max(-1,min(1,-nn[2])))),1)   # pad normal vs straight-down: off-axis angle
            if ang0 is None: ang0=a
            if Ftot>=Fpk: angpk=a
        Fpk=max(Fpk,Ftot); Fpad_now=Ftot
        if A.forearm_crush_N>0:   # T-031(c): constant-force element on the chest-facing (torso +x) side of each forearm; native forearm/hand floor contact disabled
            tx=d.xmat[m.body('torso').id].reshape(3,3)[:,0]; T=A.forearm_crush_stroke
            for g in ('l_forearm','r_forearm'):
                gi=m.geom(g).id; Rg=d.geom_xmat[gi].reshape(3,3); bb=m.geom_bodyid[gi]
                for e in (-0.8,0,0.8):
                    p=d.geom_xpos[gi]+Rg[:,2]*m.geom_size[gi][1]*e+tx*(m.geom_size[gi][0]+T); c=-p[2]
                    if c>0:
                        Fc=A.forearm_crush_N/3*min(c/RAMP,1.0)+(KD*(c-T) if c>T else 0.)
                        d.xfrc_applied[bb,2]+=Fc; d.xfrc_applied[bb,3:]+=np.cross(p-d.xipos[bb],[0,0,Fc]); fc_max=max(fc_max,c)
        # T-031 chest crush pad (Materials/Torso rev2 / R-088): plateau on torso, outer face CHEST_FACE forward, no rebound
        if A.chest_plateau > 0:
            tb=m.body('torso').id; Rt=d.xmat[tb].reshape(3,3); ct=d.xpos[tb]; nx=Rt[:,0]  # torso +x = chest forward
            # 3x3 patch on pad face (98 mm); standout from body origin along +x
            CGRID=[(gy,gz) for gy in np.linspace(-0.049,0.049,3) for gz in np.linspace(-0.049,0.049,3)]
            Fctot=0.; cang=None
            for gy,gz in CGRID:
                p=ct+nx*CHEST_FACE+Rt[:,1]*gy+Rt[:,2]*gz; c=-p[2]
                if c>0:
                    # angle: pad crush axis is -nx (into chest); vs ground +z → angle between -nx and -z = angle(nx, z)? force into ground is along -z from pad; pad normal outward = +nx
                    # off-axis = angle between pad outward (+nx) and groundward (-z)
                    cang=math.degrees(math.acos(max(-1,min(1,float(np.dot(nx,[0,0,-1]))))))
                    ang_scale=float(np.interp(cang,[0,15,25],[1.0,0.93,0.73]))
                    Fp=A.chest_plateau*ang_scale
                    F=Fp/9*min(c/RAMP,1.0)+(KD*(c-A.chest_stroke) if c>A.chest_stroke else 0.)
                    d.xfrc_applied[tb,2]+=F; d.xfrc_applied[tb,3:]+=np.cross(p-d.xipos[tb],[0,0,F])
                    Fctot+=F; chest_cmax=max(chest_cmax,c)
                    if c>A.chest_stroke: chest_bottomed=True
                    if t_imp is None: t_imp=t; com_imp=com[2]; leg1=0.5*(LEG('L')+LEG('R')); first_contact='chest_pad'
            if Fctot>0:
                if chest_ang0 is None: chest_ang0=cang
                if Fctot>=chest_Fpk: chest_angpk=cang
                chest_Fpk=max(chest_Fpk,Fctot)
                if cang is not None and cang>15: chest_ang_fail=True
                if m_eff is None and chest_g>1: m_eff=chest_Fpk/(chest_g*9.81)
        # hand-to-thigh clearance (both sides) over the fall
        for hs,ts in (('L_hand','L_thigh'),('R_hand','R_thigh'),('L_hand','R_thigh'),('R_hand','L_thigh')):
            hand_thigh_min=min(hand_thigh_min, float(np.linalg.norm(d.xpos[m.body(hs).id]-d.xpos[m.body(ts).id])) - 0.043 - 0.06)  # hand half-y + thigh capsule r [EST]
        # impacts outside pad core footprint (centroid beyond core/2)
        if cw>0 and A.pad=='hc':
            core_h=PAD.get('core',PAD['face'])
            if max(abs(cen[0]/cw), abs(cen[1]/cw)) > core_h/2: outside_core=1
        for i in range(d.ncon):   # positive (compressive) work of all other ground contacts except feet
            cn=d.contact[i]; gs={cn.geom1,cn.geom2}
            if floor not in gs or gs&set(footg): continue
            mujoco.mj_contactForce(m,d,i,f6); og=(gs-{floor}).pop(); bb=m.geom_bodyid[og]
            v=np.zeros(6); mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,bb,v,0)
            vel=v[3:]+np.cross(v[:3],cn.pos-d.xpos[bb]); Woth+=f6[0]*max(-vel[2],0)*dt
            if Fpad_now>0 and m.body(bb).name in ('torso','L_upper_arm','R_upper_arm','L_shoulderP','R_shoulderP'): bypass=True   # shoulder structure grounds while element loaded = hit outside face
            if Ftot>0 and m.body(bb).name in ('torso','L_upper_arm','R_upper_arm','L_shoulderP','R_shoulderP'): bypass=True   # shoulder structure touches ground while element loaded = hit outside face
            if t_imp is None: t_imp=t; com_imp=com[2]; leg1=0.5*(LEG('L')+LEG('R')); first_contact=m.body(bb).name
        ia=ai(('l' if side>0 else 'r')+'_shoulder_roll'); pw=d.ctrl[ia]*d.qvel[va[ia]]
        if t_fm is not None and pw<0: Warm+=-pw*dt
        mujoco.mj_step(m,d)
        _v=np.zeros(6); mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,m.body('torso').id,_v,0)
        _vb.append(_v[3:].copy())
        if t_fm is not None and len(_vb)>=_na+1: chest_g=max(chest_g,float(np.linalg.norm(_vb[-1]-_vb[-1-_na]))/(_na*dt)/9.81)
        if t_fm is not None:
            for s_ in 'lr':
                jd=m.jnt_dofadr[m.joint(s_+'_shoulder_pitch').id]; tg=abs(d.qfrc_actuator[jd]-m.dof_armature[jd]*d.qacc[jd]+d.qfrc_constraint[jd]); tau_g=max(tau_g,tg)
    share=Wsh/(Wsh+Woth) if Wsh+Woth>0 else None; M=Fpk*ARM
    fs_rad=C0/(Fpk+2*M/DPW) if Fpk>0 else None; fs_ax=C0/(2*M/DPW+0.44*Fpk) if Fpk>0 else None
    # CRBH 6013 roll bearing static SF: Fr~Fpk, M=Fpk*e, P0=Fr+2M/dp+0.44Fa (Fa~0 head-on)
    Mroll=Fpk*PAD_E; P0=Fpk+2*Mroll/DPW_ROLL if Fpk>0 else None; s0=C0_ROLL/P0 if P0 else None
    if m_eff is None and chest_Fpk>0 and chest_g>1: m_eff=chest_Fpk/(chest_g*9.81)
    crouch=(com_trig-com_imp) if (com_trig is not None and com_imp is not None) else None
    return dict(chest_k=A.chest_k,chest_plateau=A.chest_plateau,chest_stroke_mm=A.chest_stroke*1e3,chest_crush_max_mm=round(chest_cmax*1e3,1),chest_bottomed=chest_bottomed,chest_impact_angle_deg=chest_ang0,chest_peak_angle_deg=chest_angpk,chest_angle_gt15=chest_ang_fail,chest_peak_N=round(chest_Fpk),m_eff_kg=None if m_eff is None else round(m_eff,2),torso_peak_g=round(chest_g,1),forearm_crush_max_mm=round(fc_max*1e3,1),tuck=A.tuck,shoulder_pitch_gear_peak_Nm=round(tau_g,1),CRBH_s0=None if s0 is None else round(s0,2),CRBH_s0_pass=bool(s0 is not None and s0>=2.0),hand_thigh_min_m=None if hand_thigh_min>1e8 else round(hand_thigh_min,4),outside_core=bool(outside_core),first_contact=first_contact,pad_lever_m=ARM,angle_beyond_25_unknown=ang_unknown,spike=A.spike,hc_stroke_mm=A.hc_stroke*1e3,t_release=t_rel,carry=A.carry,arm_used='tuck',dir=dirn,J=round(J,1),pad_mm=A.pad,fell=bool(t_imp is not None),t_detect=t_det,t_fallmode=t_fm,t_impact=t_imp,
        crouch_at_impact_m=(leg0-leg1) if (leg0 and leg1) else None,com_drop_at_impact_m=crouch,E_sh_J=round(Wsh,1),E_other_J=round(Woth,1),shoulder_share=share,pad_peak_N=round(Fpk),pad_crush_max_mm=round(cmax*1e3,1),
        bottomed=(cmax>0.75*PAD['t']) if A.pad_model=='curve' else (cmax>PAD['s']),beyond_data_unknown=bool(A.pad_model=='curve' and cmax>0.75*PAD['t']),impact_angle_deg=ang0,peak_angle_deg=angpk,bypass_contact=bypass,pad_model=A.pad_model,arm=A.arm,W_arm_backdrive_J=round(Warm,1),M_bearing_Nm=round(M,1),fs_radial=fs_rad,fs_axial=fs_ax,contact_centroid_mm=(cen/cw*1e3).round(1).tolist() if cw>0 else None)
JD=lambda o: o.item() if hasattr(o,"item") else str(o)
rng=np.random.default_rng(A.seed); J0,J1=map(float,A.impulse.split(','))
dirs=[A.dirs.split(',')[0]] if A.smoke else A.dirs.split(','); n=1 if A.smoke else A.runs; R=[]
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
    Ecap=PAD['Fp']*0.93*PAD['s'] if A.pad=='hc' else None; S.update(E_cap_worst15_J=Ecap,E_cap_gate_ok=bool(Ecap is None or Ecap>=292.0))
    S.update(CRBH_s0_min=min((r['CRBH_s0'] or 99) for r in ok), outside_core_n=sum(r['outside_core'] for r in ok),
             hand_thigh_min_m=min((r['hand_thigh_min_m'] or 99) for r in ok),
             torso_peak_g_max=max(r['torso_peak_g'] for r in ok),
             chest_bottomed_n=sum(1 for r in ok if r.get('chest_bottomed')),
             chest_angle_gt15_n=sum(1 for r in ok if r.get('chest_angle_gt15')),
             chest_crush_max_mm=max(r.get('chest_crush_max_mm') or 0 for r in ok))
    if A.dirs.startswith('F'):
        S['PASS']=bool(S['gear_pitch_max']<=369.0 and S.get('torso_peak_g_max',0)<=38.0 and S.get('chest_bottomed_n',0)==0 and S.get('chest_angle_gt15_n',0)==0)
    else: S['PASS']=bool(S['gear_pitch_max']<=369.0 and S['E_cap_gate_ok'] and S['angle_p95']<=15.0 and S['angle_unknown']==0 and S['share_p95']<=0.40 and S['M_max']<=GATE_M and S['F_max']<=GATE_F and S['crouch_min']>=0.15 and S['bottomed']==0 and S['bypass']==0 and S['unknown']==0 and S['centroid_abs_p95_mm']<=(15.0 if A.pad=='hc' else PAD['face']*500) and S.get('CRBH_s0_min',99)>=2.0)
print(json.dumps(S,default=JD)); fo and fo.write(json.dumps(S,default=JD)+'\n')
