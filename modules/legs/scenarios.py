"""Build reference trajectories for the six leg scenarios, run floating-base inverse dynamics, save results.
usage: python3 scenarios.py [scenario ...]   (one at a time keeps RAM small)"""
import sys, json, numpy as np, mujoco
from gait_lib import *
OUT=os.path.join(HERE,'results',os.environ.get('LEGS_OUT','')); os.makedirs(OUT,exist_ok=True)
TH_TO=np.radians(25); PEL_Z=1.04; FY=0.13; FC=0.06   # pelvis height while walking, foot lateral, foot centre x offset

def heel_off(p,th):
    Ry=np.array([[np.cos(th),0,np.sin(th)],[0,1,0],[-np.sin(th),0,np.cos(th)]])
    return p+np.array([TOE,0,-SOLE])+Ry@np.array([-TOE,0,SOLE])

def walk_plan(steps,Td,Ts,T0=1.0,T1=1.0,stairs=False,swing_h=0.07,th_to=0.0):
    """steps: list of (side, target ankle xyz). Flat-foot stance; optional heel-off (toe roll, angle th_to) of the
    trailing foot during the double support before lift-off. Returns per-frame feet pos, foot pitch, toe-contact flag, load share, ZMP ref."""
    feet={'l':np.array([0,FY,SOLE]),'r':np.array([0,-FY,SOLE])}
    seq=[]
    def cen(p): return np.array([p[0]+FC,p[1]])
    def mj(s): return 10*s**3-15*s**4+6*s**5
    def put(f,pitch,toe,a,z): seq.append(({k:v.copy() for k,v in f.items()},dict(pitch),dict(toe),a,z))
    one=lambda st: np.array([1.0,0]) if st=='l' else np.array([0,1.0])
    first=steps[0][0]; st0='r' if first=='l' else 'l'
    N0=int(T0/DT)
    for k in range(N0):
        s=(k+0.5)/N0; a=(1-s)*np.array([.5,.5])+s*one(st0); a=np.clip(a,0.02,1); a/=a.sum()
        z=(1-s)*0.5*(cen(feet['l'])+cen(feet['r']))+s*cen(feet[st0])
        f=dict(feet); th=th_to*mj(s) if s>0.5 else 0.0
        th=th_to*mj(max(0,(s-0.6)/0.4)); f[first]=heel_off(feet[first],th) if th>0 else feet[first]
        put(f,{first:th,st0:0.0},{first:th>0,st0:False},a,z)
    for i,(side,tgt) in enumerate(steps):
        st='r' if side=='l' else 'l'; p1=np.array(tgt,float); p0=heel_off(feet[side],th_to) if th_to>0 else feet[side].copy()
        ns=int(Ts/DT)
        for k in range(ns):
            s=(k+0.5)/ns; f={st:feet[st],side:swing(p0,p1,s,swing_h,0.06 if stairs else None)}
            th=th_to*(1-mj(min(1,s/0.5)))
            put(f,{side:th,st:0.0},{side:False,st:False},one(st),cen(feet[st]))
        feet[side]=p1
        nxt=steps[i+1][0] if i+1<len(steps) else None
        Tdd=Td if nxt else T1; nd=int(Tdd/DT)
        for k in range(nd):
            s=(k+0.5)/nd
            if nxt:
                nst='r' if nxt=='l' else 'l'
                a=(1-s)*one(st)+s*one(nst); a=np.clip(a,0.02,1); a/=a.sum()
                z=(1-s)*cen(feet[st])+s*cen(feet[nst])
                th=th_to*mj(s); f=dict(feet); f[nxt]=heel_off(feet[nxt],th) if th>0 else feet[nxt]
                put(f,{nxt:th,nst:0.0},{nxt:th>0,nst:False},a,z)
            else:
                sm=min(1,2*s); a=(1-sm)*one(st)+sm*np.array([.5,.5]); a=np.clip(a,0.02,1); a/=a.sum()
                z=(1-sm)*cen(feet[st])+sm*0.5*(cen(feet['l'])+cen(feet['r']))
                put(feet,{'l':0.0,'r':0.0},{'l':False,'r':False},a,z)
    F={s:np.array([q[0][s] for q in seq]) for s in 'lr'}; P={s:np.array([q[1][s] for q in seq]) for s in 'lr'}
    TO=np.array([[q[2]['l'],q[2]['r']] for q in seq]); AL=np.array([q[3] for q in seq]); Z=np.array([q[4] for q in seq])
    return F,P,TO,AL,Z

def ik_track(r,F,com,pel_z,pitch=0.0,P=None):
    N=len(com); Q=np.zeros((N,r.m.nq)); q=r.q.copy(); err=0
    for k in range(N):
        ge=getattr(r,'gait_extra',None); pq=quat_pitch(pitch)
        if ge is not None:
            y=ge['yaw'][k]; pq=np.array([np.cos(y/2),0,0,np.sin(y/2)])
            q[r.m.jnt_qposadr[r.m.joint('waist_yaw').id]]=-y
            for sd,sg in (('l',1),('r',-1)): q[r.m.jnt_qposadr[r.m.joint(f'{sd}_shoulder_pitch').id]]=r.q[r.m.jnt_qposadr[r.m.joint(f'{sd}_shoulder_pitch').id]]+sg*ge['arm'][k]
        q=r.ik_com(q,{s_:(F[s_][k],0.0,0.0 if P is None else P[s_][k]) for s_ in 'lr'},com[k],pel_z[k],pq)
        r.fk(q); e=max(np.linalg.norm(r.d.xpos[r.foot[s]]-F[s][k]) for s in 'lr'); err=max(err,e)
        Q[k]=q
    return Q,err

def build_walk(r,F,AL,Z,zc,pel_z=None,pitch=0.0,iters=7,P=None):
    """LIPM preview COM, then Kajita two-stage correction: the multibody ZMP error is fed back through the preview controller."""
    N=len(Z)
    if pel_z is None: pel_z=np.full(N,PEL_Z)
    gz=AL[:,0]*(F['l'][:,2]-SOLE)+AL[:,1]*(F['r'][:,2]-SOLE)
    com,_=preview_com(Z,zc); hist=[]
    for it in range(iters):
        Q,err=ik_track(r,F,com,pel_z,pitch,P)
        V,A=diff_traj(r.m,Q); zmb=mb_zmp(r,Q,V,A,gz); e=zmb-Z
        hist.append((round(float(np.abs(e[int(0.3/DT):-int(0.3/DT)]).max()),3),round(float(np.sqrt(np.mean(e[int(0.3/DT):-int(0.3/DT)]**2))),3),round(err*1000,2)))
        if it<iters-1:
            e[:int(0.3/DT)]=0; e[-int(0.3/DT):]=0; e=np.clip(e,-0.15,0.15)
            dc,_=preview_com(-e,zc); com=com+0.7*dc
    print('  ZMP err per iteration (max m, rms m, IK err mm):',hist); r.zmp_hist=hist
    return Q,com,zmb,err

def com_height(r):
    q=r.ik_com(r.q.copy(),{'l':(np.array([0,FY,SOLE]),0.0),'r':(np.array([0,-FY,SOLE]),0.0)},np.array([FC,0]),PEL_Z,quat_pitch(0))
    return r.com()[2]

def sc_walk(carry=0.0,v=1.2,Tstep=0.45,name='walk_1p2',arm=0.0,yaw=0.0,ds=0.2,pel_z=None,swing_h=0.07):
    m=load(carry,(0.25,0.0,0.10)); r=Robot(m)
    if carry:   # box held close in front of the chest (payload rigid on torso, 0.25 m ahead of the waist axis), trunk leaned back 0.25 rad at the waist
        r.set_arms(-0.6,-1.2); r.q[m.jnt_qposadr[m.joint('waist_pitch').id]]=-0.25
    zc=com_height(r); L=v*Tstep
    lens=[0.25*L,0.5*L,0.75*L]+[L]*10+[0.75*L,0.5*L]
    steps=[]; x=0; side='r'
    for i,l in enumerate(lens):
        x+=l; steps.append((side,[x if i else x, FY if side=='l' else -FY, SOLE])); side='l' if side=='r' else 'r'
    # make feet leapfrog: each step lands at x_prev_stance + l
    xs={'l':0.0,'r':0.0}; steps=[]; side='r'; front=0.0
    for l in lens:
        front+=l; steps.append((side,[front,FY if side=='l' else -FY,SOLE])); side='l' if side=='r' else 'r'
    other='l' if steps[-1][0]=='r' else 'r'
    steps.append((other,[front,FY if other=='l' else -FY,SOLE]))
    F,P,TO,AL,Z=walk_plan(steps,Td=ds*Tstep,Ts=(1-ds)*Tstep,th_to=TH_TO,swing_h=swing_h)
    # round 2: arm swing (shoulder pitch opposite to the same-side leg) and pelvis yaw (forward hip follows forward foot), waist counter-rotates
    dl=(F['l'][:,0]-F['r'][:,0])/max(L,1e-3)
    r.gait_extra=dict(arm=arm*dl,yaw=-yaw*dl)
    if pel_z is not None: r.pel_z_walk=pel_z
    Q,com,zmp,err=build_walk(r,F,AL,Z,zc,P=P,pel_z=None if pel_z is None else np.full(len(Z),pel_z))
    r.toe=TO
    return r,Q,AL,dict(zc=zc,ik_err_m=err,v=v,Tstep=Tstep,carry=carry,step_lengths=lens),com,zmp

def sc_stairs(rise=0.18,tread=0.30,Tstep=0.9):
    m=load(); r=Robot(m); zc=com_height(r)
    steps=[]; side='r'; n=5
    for i in range(1,n+1):
        for s in (side,):
            pass
    # step-over-step: each foot goes up one tread+rise past the other
    zf={'l':SOLE,'r':SOLE}; xf={'l':0.0,'r':0.0}; side='r'
    for i in range(1,n+1):
        xf[side]=i*tread; zf[side]=SOLE+i*rise; steps.append((side,[xf[side],FY if side=='l' else -FY,zf[side]])); side='l' if side=='r' else 'r'
    steps.append((side,[n*tread,FY if side=='l' else -FY,SOLE+n*rise]))
    F,P,TO,AL,Z=walk_plan(steps,Td=0.25*Tstep,Ts=0.75*Tstep,stairs=True,th_to=TH_TO); r.toe=TO
    # pelvis height follows load-weighted support height, smoothed (0.4 s window)
    hs=AL[:,0]*(F['l'][:,2]-SOLE)+AL[:,1]*(F['r'][:,2]-SOLE)
    w=int(0.4/DT); hsm=np.convolve(np.r_[np.full(w,hs[0]),hs,np.full(w,hs[-1])],np.ones(w)/w,'same')[w:-w]
    pz0=float(os.environ.get('PELZ_ST',PEL_Z)); Q,com,zmp,err=build_walk(r,F,AL,Z,zc,pel_z=pz0+hsm,P=P); info_pz=pz0
    return r,Q,AL,dict(pelvis_z=info_pz,zc=zc,ik_err_m=err,rise=rise,tread=tread,Tstep=Tstep),com,zmp

def sc_sit_to_stand(T=1.2,seat_h=0.46):
    m=load(); r=Robot(m); feet={'l':(np.array([0,FY,SOLE]),0.0),'r':(np.array([0,-FY,SOLE]),0.0)}
    def pose(hip_x,hip_z,pitch,waist):
        q=r.q.copy(); q[m.jnt_qposadr[m.joint('waist_pitch').id]]=waist
        q[3:7]=quat_pitch(pitch); R=np.array([[np.cos(pitch),0,np.sin(pitch)],[0,1,0],[-np.sin(pitch),0,np.cos(pitch)]])
        q[0:3]=np.array([hip_x,0,hip_z])-R@np.array([0,0,-0.240])
        q=r.ik_legs(q,feet,iters=80); r.fk(q); return q,r.com()
    # seat-off: thighs ~horizontal on a 0.46 m seat, hip 0.30 m behind ankle; search trunk lean so COM is over the foot (x>=+0.01)
    best=None   # seat-off: hip 0.20 m behind the ankle, 0.04 m above a 0.46 m seat; largest trunk lean the hip ROM allows (IK exact), COM must be on the sole
    for pitch in np.radians(np.arange(0,46,1)):
        q,c=pose(-0.20,seat_h+0.04,pitch,np.radians(35))
        r.fk(q); e=max(np.linalg.norm(r.d.xpos[r.foot[s_]]-feet[s_][0]) for s_ in 'lr')
        if e<1e-4 and c[0]>=HEEL+0.02: best=(pitch,q,c)
    pitch0,q0,c0=best
    q1,c1=pose(0.0,0.90,0.0,0.0)
    N=int(T/DT); Q=np.zeros((N,m.nq))
    hip0=np.array([-0.20,seat_h+0.04]); hip1=np.array([0.0,0.90])
    for k in range(N):
        s=k/(N-1); mj=10*s**3-15*s**4+6*s**5
        # hip path: rise lags forward travel slightly (human-like), lean returns to upright
        hx=hip0[0]+(hip1[0]-hip0[0])*mj; hz=hip0[1]+(hip1[1]-hip0[1])*mj
        Q[k],_=pose(hx,hz,pitch0*(1-mj),np.radians(35)*(1-mj))
    AL=np.full((N,2),0.5)
    r.fk(Q[0]); r.pad=0.3; r.trim=(0.25,0.25); return r,Q,AL,dict(seat_h=seat_h,T=T,lean_deg=float(np.degrees(pitch0)),com_x_seatoff=float(c0[0])),None,None

def sc_push(v0=0.6,react=0.10,Tsw=0.35,Tend=1.6):
    """Forward push gives COM velocity v0 at t=0 from quiet stance; ankle ZMP to toes, quick weight shift, then a capture step with the right foot.
    COM follows LIPM x''=w^2(x-p) with p chosen by capture-point control inside the support polygon."""
    m=load(); r=Robot(m); zc=com_height(r); w=np.sqrt(G/zc)
    N=int(Tend/DT); x=np.array([FC,0.0]); xd=np.array([v0,0.0])
    feet={'l':np.array([0,FY,SOLE]),'r':np.array([0,-FY,SOLE])}; Fl=[];Fr=[];AL=[];COM=[];ZMP=[]
    land=None; pr0=feet['r'].copy()
    for k in range(N):
        t=k*DT; xi=x+xd/w
        if t<react:              # double support, ZMP to toes, shift weight left
            lo=np.array([HEEL,-FY-HALFW]); hi=np.array([TOE,FY+HALFW]); tgt=np.array([TOE,FY*0.9])
            p=np.clip(tgt,lo,hi); a=np.array([0.5+0.5*t/react,0.5-0.5*t/react])
        elif t<react+Tsw:        # single support on left, right foot swings to predicted capture point
            if land is None:
                # predict xi at touchdown with p at left toe, place right foot centre there (x), lateral at -FY
                pL=np.array([TOE,FY-HALFW]); xiT=pL+(xi-pL)*np.exp(w*Tsw)
                land=np.array([xiT[0]-FC,min(-FY,xiT[1]-0.05),SOLE]); land[0]=min(land[0],0.55); land[1]=max(land[1],-0.40)
            lo=np.array([HEEL,FY-HALFW]); hi=np.array([TOE,FY+HALFW]); p=np.clip(np.array([TOE,FY-HALFW]),lo,hi)
            s=(t-react)/Tsw; feet['r']=swing(pr0,land,s,0.06); a=np.array([1.0,0.0])
        else:                    # double support, capture-point control to mid-feet
            feet['r']=land; tgt=0.5*(np.array([FC,FY])+np.array([land[0]+FC,land[1]]))
            p=xi+1.5*(xi-tgt); lo=np.array([HEEL,land[1]-HALFW]); hi=np.array([land[0]+TOE,FY+HALFW]); p=np.clip(p,lo,hi)
            # load share from ZMP position between feet centres (x)
            s=np.clip((p[0]-FC)/max(land[0],1e-3),0,1); a=np.clip(np.array([1-s,s]),0.02,1); a/=a.sum()
        xdd=w*w*(x-p); xd=xd+xdd*DT; x=x+xd*DT
        Fl.append(feet['l'].copy()); Fr.append(feet['r'].copy()); AL.append(a); COM.append(x.copy()); ZMP.append(p)
    F={'l':np.array(Fl),'r':np.array(Fr)}; AL=np.array(AL); COM=np.array(COM)
    Q=np.zeros((N,m.nq)); q=r.q.copy(); err=0
    for k in range(N):
        q=r.ik_com(q,{'l':(F['l'][k],0.0),'r':(F['r'][k],0.0)},COM[k],PEL_Z,quat_pitch(0)); Q[k]=q
        r.fk(q); err=max(err,max(np.linalg.norm(r.d.xpos[r.foot[s]]-F[s][k]) for s in 'lr'))
    r.trim=(0.0,0.3)   # push gives the COM velocity at t=0; keep the start
    return r,Q,AL,dict(v0=v0,impulse_Ns=float(v0*m.body_subtreemass[1]),land_x=float(land[0]),land_y=float(land[1]),zc=zc,ik_err_m=err,final_com_v=float(np.linalg.norm(xd))),COM,np.array(ZMP)

SC={'walk_1p2_r2':lambda:sc_walk(v=1.2,Tstep=float(os.environ.get('TSTEP','0.5')),arm=float(os.environ.get('ARM','0.35')),yaw=float(os.environ.get('YAW','0.12')),ds=float(os.environ.get('DS','0.15')),pel_z=float(os.environ.get('PELZ','1.02'))),
    'carry_20kg_r2':lambda:sc_walk(carry=20.0,v=1.2,Tstep=float(os.environ.get('TSTEP','0.5')),yaw=float(os.environ.get('YAW','0.12')),ds=float(os.environ.get('DS','0.15')),pel_z=float(os.environ.get('PELZ','1.02'))),
    'walk_1p2':lambda:sc_walk(),'walk_0p8':lambda:sc_walk(v=0.8,Tstep=0.5),'walk_1p0':lambda:sc_walk(v=1.0,Tstep=0.47),'stairs_18cm':lambda:sc_stairs(),'carry_20kg':lambda:sc_walk(carry=20.0,name='carry_20kg'),
    'sit_to_stand':lambda:sc_sit_to_stand(),'sit_to_stand_r3':lambda:sc_sit_to_stand_r3(),'carry_20kg_0p8':lambda:sc_walk(carry=20.0,v=0.8,Tstep=0.5,name='carry_20kg_0p8'),'carry_20kg_1p0':lambda:sc_walk(carry=20.0,v=1.0,Tstep=0.47,name='carry_20kg_1p0'),'push_recover':lambda:sc_push()}
def sc_sit_to_stand_r3(T=1.4):
    '''R-012 re-plan: hip_pitch kept >= HIPMIN (default -78 deg, 2 deg inside the -80 loaded limit).
    Strategy: forward lean from the WAIST (does not add hip flexion), pelvis pitch only as far as the hip limit allows, knees/ankles take the rise.
    Searches the lowest seat (0.46..0.66 m) where seat-off has the COM over the sole with exact IK and hip >= HIPMIN.'''
    HIPMIN=np.radians(float(os.environ.get('HIPMIN','-78')))
    m=load(); r=Robot(m); feet={'l':(np.array([0,FY,SOLE]),0.0),'r':(np.array([0,-FY,SOLE]),0.0)}
    hp=[r.qa[s_+'hip_pitch'] for s_ in 'lr']
    def pose(hip_x,hip_z,pitch,waist,q0=None):
        q=(r.q if q0 is None else q0).copy(); q[m.jnt_qposadr[m.joint('waist_pitch').id]]=waist
        q[3:7]=quat_pitch(pitch); R=np.array([[np.cos(pitch),0,np.sin(pitch)],[0,1,0],[-np.sin(pitch),0,np.cos(pitch)]])
        q[0:3]=np.array([hip_x,0,hip_z])-R@np.array([0,0,-0.240])
        q=r.ik_legs(q,feet,iters=80); r.fk(q); e=max(np.linalg.norm(r.d.xpos[r.foot[s_]]-feet[s_][0]) for s_ in 'lr'); return q,r.com(),e
    best=None
    for seat_h in np.arange(0.46,0.665,0.02):
        for hip_x in (-0.20,-0.16,-0.12):
            for wd in (35,45,55,60):
                for pd in range(0,41,2):
                    q,c,e=pose(hip_x,seat_h+0.04,np.radians(pd),np.radians(wd))
                    if e<1e-4 and min(q[hp])>=HIPMIN and c[0]>=HEEL+0.02:
                        best=(seat_h,hip_x,np.radians(pd),np.radians(wd),c); break
                if best: break
            if best: break
        if best: break
    if best is None: raise RuntimeError('no feasible seat 0.46-0.66 m with hip >= %.0f deg'%np.degrees(HIPMIN))
    seat_h,hx0,p0,w0,c0=best
    N=int(T/DT); Q=np.zeros((N,m.nq)); qp=None
    for k in range(N):
        s_=k/(N-1); mj=10*s_**3-15*s_**4+6*s_**5
        Q[k],_,_=pose(hx0*(1-mj),seat_h+0.04+(0.90-seat_h-0.04)*mj,p0*(1-mj),w0*(1-mj),qp); qp=Q[k]
    AL=np.full((N,2),0.5)
    r.fk(Q[0]); r.pad=0.3; r.trim=(0.25,0.25)
    return r,Q,AL,dict(seat_h=float(seat_h),hip_x_seatoff=float(hx0),pelvis_pitch_deg=float(np.degrees(p0)),waist_lean_deg=float(np.degrees(w0)),T=T,hip_min_allowed_deg=float(np.degrees(HIPMIN)),
                       hip_min_traj_deg=float(np.degrees(Q[:,hp].min())),com_x_seatoff=float(c0[0])),None,None


TRIM=0.3   # s; first/last frames are finite-difference/preview start-up edges and are excluded from all metrics

def run(name):
    r,Q,AL,info,com,zmp=SC[name]()
    info.update(model_mass_setting=MASS or 'as built',torque_limits=LIMITS,ik_rom_margin_rad=IKM)
    tr=getattr(r,'trim',(TRIM,TRIM))
    if getattr(r,'pad',0):   # static hold before/after (sit-to-stand starts and ends at rest)
        n=int(r.pad/DT); Q=np.r_[np.repeat(Q[:1],n,0),Q,np.repeat(Q[-1:],n,0)]; AL=np.r_[np.repeat(AL[:1],n,0),AL,np.repeat(AL[-1:],n,0)]
    V,A=diff_traj(r.m,Q)
    sl=slice(int(tr[0]/DT),len(Q)-int(tr[1]/DT)); Q,V,A,AL=Q[sl],V[sl],A[sl],AL[sl]
    if getattr(r,'toe',None) is not None: r.toe=r.toe[sl]
    if com is not None: com,zmp=com[sl],zmp[sl]
    toe=getattr(r,'toe',None)
    TAU,FZ,COP,RES,FR=inverse_dynamics(r,Q,V,A,AL,toe=toe)
    TAU0,*_=inverse_dynamics(r,Q,V,A,AL,armature=False,toe=toe)
    met=metrics(r,Q,V,TAU); met0=metrics(r,Q,V,TAU0)
    for j in met: met[j]['peak_Nm_no_armature']=met0[j]['peak_Nm']
    cx=COP[:,:,0]; cy=COP[:,:,1]
    cop_ok=bool(np.nanmax(cx)<=TOE+1e-4 and np.nanmin(cx)>=HEEL-1e-4 and np.nanmax(np.abs(cy))<=HALFW+1e-4)
    info.update(residual_times_s=[round(x,3) for x in (np.where(RES>0.05*r.m.body_subtreemass[1]*G)[0]*DT+tr[0])[:60].tolist()],base_residual_p99_N=float(np.percentile(RES,99)),frames_residual_gt_5pctBW=int((RES>0.05*r.m.body_subtreemass[1]*G).sum()),zmp_iter=getattr(r,'zmp_hist',None),mass_kg=float(r.m.body_subtreemass[1]),duration_s=len(Q)*DT,base_residual_max=float(RES.max()),
        cop_x_range_m=[float(np.nanmin(cx)),float(np.nanmax(cx))],cop_y_absmax_m=float(np.nanmax(np.abs(cy))),cop_inside_sole=bool(cop_ok),
        max_friction_ratio=float(FR.max()),max_vertical_GRF_BW=float(FZ.max()/(r.m.body_subtreemass[1]*G)))
    json.dump(dict(info=info,metrics=met),open(f'{OUT}/{name}.json','w'),indent=1)
    np.savez_compressed(f'{OUT}/{name}.npz',t=np.arange(len(Q))*DT,Q=Q.astype(np.float32),V=V.astype(np.float32),TAU=TAU.astype(np.float32),FZ=FZ,COP=COP,AL=AL,
        qa=np.array([r.qa['l'+j] for j in LEG]+[r.qa['r'+j] for j in LEG]),va=np.array([r.va['l'+j] for j in LEG]+[r.va['r'+j] for j in LEG]),
        com=com if com is not None else np.zeros(1),zmp=zmp if zmp is not None else np.zeros(1))
    print(name,json.dumps(info))
    for j,v in met.items(): print(f"  {j:12s} pk {v['peak_Nm']:7.1f} rms {v['rms_Nm']:6.1f} w {v['peak_rads']:5.2f} w@30% {v['speed_at30_rads']:5.2f} P {v['peak_W']:6.0f} duty {v['duty50']:.2f} q [{v['qmin_deg']:.0f},{v['qmax_deg']:.0f}]")

if __name__=='__main__':
    for n in (sys.argv[1:] or list(SC)): run(n)
