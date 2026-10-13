"""RL Legs gait library: reference trajectories (LIPM ZMP preview / capture point), whole-leg IK,
and floating-base inverse dynamics (mj_inverse + explicit foot-wrench distribution) on sim/v3/humanoid_v3.xml."""
import os, json, numpy as np, mujoco
from scipy.linalg import solve_discrete_are
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
XML=os.path.join(ROOT,'sim','v3','humanoid_v3.xml')
LEG=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll']
G=9.81; DT=0.005
SOLE=0.080            # ankle axis height above sole (foot box bottom at -0.080 in foot frame)
HEEL,TOE,HALFW=-0.060,0.180,0.050   # sole extents in foot frame (x from ankle, half width)

def load(carry=0.0, carry_pos=(0.32,0.0,0.12)):
    xml=open(XML).read()
    if carry>0:   # payload rigidly attached to torso (two-handed carry in front of torso)
        tag='<geom name="torso" type="box"'
        xml=xml.replace(tag,f'<body name="payload" pos="{carry_pos[0]} {carry_pos[1]} {carry_pos[2]}"><inertial pos="0 0 0" mass="{carry}" diaginertia="0.2 0.15 0.2"/></body>'+tag,1)
    m=mujoco.MjModel.from_xml_path(XML) if carry<=0 else mujoco.MjModel.from_xml_string(xml)
    return m

class Robot:
    def __init__(s,m):
        s.m=m; s.d=mujoco.MjData(m)
        s.qa={}; s.va={}
        for side in 'lr':
            for j in LEG:
                jid=m.joint(f'{side}_{j}').id; s.qa[side+j]=m.jnt_qposadr[jid]; s.va[side+j]=m.jnt_dofadr[jid]
        s.legq={side:np.array([s.qa[side+j] for j in LEG]) for side in 'lr'}
        s.legv={side:np.array([s.va[side+j] for j in LEG]) for side in 'lr'}
        s.foot={'l':m.body('L_foot').id,'r':m.body('R_foot').id}
        s.q=np.zeros(m.nq); s.q[3]=1
        for side in 'lr':
            s.q[s.qa[side+'hip_pitch']]=-0.3; s.q[s.qa[side+'knee']]=0.6; s.q[s.qa[side+'ankle_pitch']]=-0.3
        for side in 'lr': s.q[m.jnt_qposadr[m.joint(f'{side}_elbow').id]]=-0.3
        s.q[2]=1.06
    def set_arms(s,sp,el):
        for side in 'lr':
            s.q[s.m.jnt_qposadr[s.m.joint(f'{side}_shoulder_pitch').id]]=sp
            s.q[s.m.jnt_qposadr[s.m.joint(f'{side}_elbow').id]]=el
    def fk(s,q):
        s.d.qpos[:]=q; mujoco.mj_kinematics(s.m,s.d); mujoco.mj_comPos(s.m,s.d)
    def com(s): return s.d.subtree_com[1].copy()
    def ik_legs(s,q,feet,iters=60,tol=1e-16):
        """feet: {'l':(pos_ankle(3), yaw), 'r':...}. Pelvis pose in q is held; solve 6 leg joints/side."""
        m,d=s.m,s.d
        for side,ft in feet.items():
            p,yaw=ft[0],ft[1]; th=ft[2] if len(ft)>2 else 0.0
            Rt=np.array([[np.cos(yaw),-np.sin(yaw),0],[np.sin(yaw),np.cos(yaw),0],[0,0,1]])@np.array([[np.cos(th),0,np.sin(th)],[0,1,0],[-np.sin(th),0,np.cos(th)]])
            for it in range(iters):
                s.fk(q); b=s.foot[side]
                ep=p-d.xpos[b]; R=d.xmat[b].reshape(3,3)
                Re=Rt@R.T; er=0.5*np.array([Re[2,1]-Re[1,2],Re[0,2]-Re[2,0],Re[1,0]-Re[0,1]])
                e=np.r_[ep,er]
                if e@e<tol: break
                jp=np.zeros((3,m.nv)); jr=np.zeros((3,m.nv)); mujoco.mj_jacBody(m,d,jp,jr,b)
                J=np.r_[jp,jr][:,s.legv[side]]
                dq=np.linalg.solve(J.T@J+1e-6*np.eye(6),J.T@e)
                n=np.abs(dq).max()
                if n>0.2: dq*=0.2/n
                q[s.legq[side]]+=dq
                q[s.legq[side][3]]=max(q[s.legq[side][3]],0.02)   # keep knee on the flexed branch
                jr_=s.m.jnt_range[[s.m.joint(f'{side}_{j}').id for j in LEG]]   # IK may exceed model ROM by <=15 deg (reported as a ROM need)
                q[s.legq[side]]=np.clip(q[s.legq[side]],jr_[:,0]-0.26,jr_[:,1]+0.26)

        return q
    def ik_com(s,q,feet,com_xy,pel_z,pel_quat,iters=6):
        q[3:7]=pel_quat; q[2]=pel_z
        for k in range(iters):
            q=s.ik_legs(q,feet); c=s.com()
            e=com_xy-c[:2]
            if e@e<1e-12: break
            q[0:2]+=e
        return q

def quat_pitch(th): return np.array([np.cos(th/2),0,np.sin(th/2),0])

def preview_gains(zc,dt=DT,NL=320,Qe=1.0,R=1e-6):
    A=np.array([[1,dt,dt*dt/2],[0,1,dt],[0,0,1]]); B=np.array([[dt**3/6],[dt*dt/2],[dt]]); C=np.array([[1,0,-zc/G]])
    Ab=np.block([[np.eye(1),C@A],[np.zeros((3,1)),A]]); Bb=np.r_[C@B,B]; Ib=np.r_[[[1.0]],np.zeros((3,1))]
    Q=np.zeros((4,4)); Q[0,0]=Qe
    P=solve_discrete_are(Ab,Bb,Q,R*np.eye(1))
    K=np.linalg.solve(R+Bb.T@P@Bb,Bb.T@P@Ab); Gi=K[0,0]; Gx=K[0,1:]
    Ac=Ab-Bb@K; X=-Ac.T@P@Ib; Gd=[-Gi]
    for i in range(1,NL): Gd.append(float(np.linalg.solve(R+Bb.T@P@Bb,Bb.T@X)[0,0])); X=Ac.T@X
    return A,B,C,Gi,Gx,np.array(Gd)

def preview_com(zmp_ref,zc,dt=DT):
    """Kajita 2003 ZMP preview control. zmp_ref: (N,2). returns com (N,2), zmp actual (N,2)."""
    A,B,C,Gi,Gx,Gd=preview_gains(zc); NL=len(Gd); N=len(zmp_ref)
    ref=np.r_[zmp_ref,np.repeat(zmp_ref[-1:],NL,0)]
    out=np.zeros((N,2)); zout=np.zeros((N,2))
    for ax in range(2):
        x=np.array([ref[0,ax],0,0]); esum=0
        for k in range(N):
            p=(C@x)[0]; esum+=p-ref[k,ax]
            u=-Gi*esum-Gx@x-Gd@ref[k+1:k+1+NL,ax]
            x=A@x+B[:,0]*u; out[k,ax]=x[0]; zout[k,ax]=p
    return out,zout

def swing(p0,p1,s,h,z_clear=None):
    """swing foot point at phase s in [0,1]: min-jerk horizontal, vertical lift profile."""
    mj=10*s**3-15*s**4+6*s**5
    p=p0+(p1-p0)*mj
    if z_clear is None:
        p[2]=p0[2]+(p1[2]-p0[2])*mj+h*64*s**3*(1-s)**3
    else:  # stairs: lift first, move, then lower
        zt=max(p0[2],p1[2])+z_clear
        if s<0.3: p[2]=p0[2]+(zt-p0[2])*(10*(s/.3)**3-15*(s/.3)**4+6*(s/.3)**5); p[:2]=p0[:2]
        elif s<0.8: u=(s-.3)/.5; mm=10*u**3-15*u**4+6*u**5; p[:2]=p0[:2]+(p1[:2]-p0[:2])*mm; p[2]=zt
        else: u=(s-.8)/.2; p[:2]=p1[:2]; p[2]=zt+(p1[2]-zt)*(10*u**3-15*u**4+6*u**5)
    return p

def diff_traj(m,Q,dt=DT):
    N=len(Q); V=np.zeros((N,m.nv)); A=np.zeros((N,m.nv))
    for k in range(1,N-1):
        v=np.zeros(m.nv); mujoco.mj_differentiatePos(m,v,2*dt,Q[k-1],Q[k+1]); V[k]=v
    V[0]=V[1]; V[-1]=V[-2]
    A[1:-1]=(V[2:]-V[:-2])/(2*dt); A[0]=A[1]; A[-1]=A[-2]
    return V,A

MU=0.8   # friction coefficient used for the wrench-distribution feasibility constraints

def _foot_cons(nw):
    """linear inequality rows G w >= 0 in foot-local wrench coords. flat: [Fx Fy Fz Mx My Mz] about ankle; toe line: [Fx Fy Fz Mx Mz] at toe edge."""
    if nw==6:
        G=[[0,0,1,0,0,0],[-SOLE,0,-HEEL,0,-1,0],[SOLE,0,TOE,0,1,0],[0,SOLE,HALFW,-1,0,0],[0,-SOLE,HALFW,1,0,0],
           [-1,0,MU,0,0,0],[1,0,MU,0,0,0],[0,-1,MU,0,0,0],[0,1,MU,0,0,0],[0,0,0.05,0,0,-1],[0,0,0.05,0,0,1]]
    else:
        G=[[0,0,1,0,0],[0,0,HALFW,-1,0],[0,0,HALFW,1,0],[-1,0,MU,0,0],[1,0,MU,0,0],[0,-1,MU,0,0],[0,1,MU,0,0],[0,0,0.03,0,-1],[0,0,0.03,0,1]]
    return np.array(G,float)

def distribute(Ab,f,alphas,nws,mg,JL=None,fl=None):
    """min  1e3*|Ab w - f|^2 (base wrench balance, soft) + |w|^2_W + share penalty + leg joint torque^2/100^2, s.t. CoP-in-sole, friction cone (pyramid), Fz>=0."""
    from scipy.optimize import minimize
    n=Ab.shape[1]; Wd=[]; Gs=[]; fz=[]; o=0
    for nw in nws:
        Wd+=[1,1,1,30,30,30][:nw] if nw==6 else [1,1,1,30,30]; Gb=np.zeros((len(_foot_cons(nw)),n)); Gb[:,o:o+nw]=_foot_cons(nw); Gs.append(Gb); fz.append(o+2); o+=nw
    G=np.vstack(Gs); S=np.diag(Wd)/mg**2*1e-2
    Ftot=np.zeros(n); 
    for i in fz: Ftot[i]=1
    Pm=np.zeros((len(fz),n))
    for k,i in enumerate(fz): Pm[k]=np.eye(n)[i]-alphas[k]*Ftot
    sc=1.0/mg
    H=2*(1e3*sc*sc*Ab.T@Ab+S+0.3*sc*sc*Pm.T@Pm); g=-2*1e3*sc*sc*Ab.T@f
    if JL is not None:   # among feasible splits prefer the one with least leg joint torque (no internal squeeze forces)
        c=1.0/100.0**2; H=H+2*c*JL@JL.T; g=g-2*c*JL@fl
    w0=np.linalg.lstsq(Ab,f,rcond=None)[0]
    res=minimize(lambda w:0.5*w@H@w+g@w,w0,jac=lambda w:H@w+g,constraints=[dict(type='ineq',fun=lambda w:G@w,jac=lambda w:G)],method='SLSQP',options=dict(maxiter=200,ftol=1e-12))
    return res.x

def inverse_dynamics(r,Q,V,A,alpha,armature=True,toe=None):
    """Floating-base ID. mj_inverse with contacts off gives the generalized force needed; the 6 base rows must be supplied by the feet.
    Foot wrenches come from a small QP (CoP inside sole, friction 0.8, Fz>=0, load share follows the plan); joint torque = qfrc_inverse - sum J^T w.
    Any base wrench the feet cannot supply (dynamically infeasible plan) is reported as residual."""
    m=r.m; d=r.d
    m.opt.disableflags|=mujoco.mjtDisableBit.mjDSBL_CONTACT|mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS|mujoco.mjtDisableBit.mjDSBL_LIMIT
    arm0=m.dof_armature.copy()
    if not armature: m.dof_armature[:]=0
    mg=m.body_subtreemass[1]*G
    N=len(Q); TAU=np.zeros((N,m.nv)); FZ=np.zeros((N,2)); COP=np.full((N,2,2),np.nan); RES=np.zeros(N); FR=np.zeros(N)
    for k in range(N):
        d.qpos[:]=Q[k]; d.qvel[:]=V[k]; d.qacc[:]=A[k]; mujoco.mj_inverse(m,d)
        f=d.qfrc_inverse.copy(); Js=[]; als=[]
        for i,side in enumerate('lr'):
            if alpha[k,i]>1e-6:
                b=r.foot[side]; jp=np.zeros((3,m.nv)); jr=np.zeros((3,m.nv))
                istoe=bool(toe is not None and toe[k,i]); R=d.xmat[b].reshape(3,3)
                pt=d.xpos[b]+R@np.array([TOE,0,-SOLE]) if istoe else d.xpos[b].copy()
                mujoco.mj_jac(m,d,jp,jr,pt,b)
                Rw=np.zeros((6,6)); Rw[:3,:3]=R; Rw[3:,3:]=R; J=Rw.T@np.r_[jp,jr]
                if istoe: J=J[[0,1,2,3,5]]
                Js.append((J,istoe,i,R)); als.append(alpha[k,i])
        als=np.array(als)/sum(als)
        Ab=np.hstack([J[0][:,:6].T for J in Js])
        legd=np.r_[r.legv['l'],r.legv['r']]
        JL=np.vstack([J[0][:,legd] for J in Js])
        W=distribute(Ab,f[:6],als,[J[0].shape[0] for J in Js],mg,JL,f[legd])
        tau=f.copy(); o=0
        for (J,istoe,i,R) in Js:
            nw=J.shape[0]; w=W[o:o+nw]; o+=nw; tau-=J.T@w
            Fl=w[:3]; Fw=R@Fl; FZ[k,i]=Fw[2]
            if Fl[2]>1: COP[k,i]=[TOE,w[3]/Fl[2]] if istoe else [(-w[4]-SOLE*Fl[0])/Fl[2],(w[3]-SOLE*Fl[1])/Fl[2]]
            FR[k]=max(FR[k],np.hypot(Fl[0],Fl[1])/max(Fl[2],1e-6))
        RES[k]=np.abs(tau[:6]).max(); TAU[k]=tau
    m.dof_armature[:]=arm0
    m.opt.disableflags&=~(mujoco.mjtDisableBit.mjDSBL_CONTACT|mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS|mujoco.mjtDisableBit.mjDSBL_LIMIT)
    return TAU,FZ,COP,RES,FR

def metrics(r,Q,V,TAU,dt=DT):
    out={}
    for j in LEG:
        rows=[]
        for side in 'lr':
            t=TAU[:,r.va[side+j]]; w=V[:,r.va[side+j]]; p=t*w
            pk=np.abs(t).max()
            rows.append(dict(peak_Nm=pk,rms_Nm=np.sqrt(np.mean(t*t)),peak_rads=np.abs(w).max(),
                             speed_at30_rads=float(np.abs(w[np.abs(t)>=0.3*pk]).max()) if pk>0 else 0.0,
                             peak_W=np.abs(p).max(),peak_pos_W=max(p.max(),0),peak_neg_W=-min(p.min(),0),mean_pos_W=np.mean(np.clip(p,0,None)),
                             duty50=float(np.mean(np.abs(t)>=0.5*pk)),
                             qmin_deg=np.degrees(Q[:,r.qa[side+j]].min()),qmax_deg=np.degrees(Q[:,r.qa[side+j]].max())))
        o={k:float(max(a[k],b[k])) for (a,b) in [rows] for k in rows[0]}
        o['qmin_deg']=float(min(rows[0]['qmin_deg'],rows[1]['qmin_deg']))
        out[j]=o
    return out

def mb_zmp(r,Q,V,A,ground_z):
    """whole-body ZMP from the floating-base residual of mj_inverse (contact off)."""
    m=r.m; d=r.d
    m.opt.disableflags|=mujoco.mjtDisableBit.mjDSBL_CONTACT|mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS|mujoco.mjtDisableBit.mjDSBL_LIMIT
    Z=np.zeros((len(Q),2))
    for k in range(len(Q)):
        d.qpos[:]=Q[k]; d.qvel[:]=V[k]; d.qacc[:]=A[k]; mujoco.mj_inverse(m,d)
        F=d.qfrc_inverse[:3]; M=d.xmat[1].reshape(3,3)@d.qfrc_inverse[3:6]; o=d.xpos[1].copy(); oz=o[2]-ground_z[k]
        rx=(M[1]+oz*F[0])/F[2]; ry=(oz*F[1]-M[0])/F[2]; Z[k]=[o[0]-rx,o[1]-ry]
    m.opt.disableflags&=~(mujoco.mjtDisableBit.mjDSBL_CONTACT|mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS|mujoco.mjtDisableBit.mjDSBL_LIMIT)
    return Z
