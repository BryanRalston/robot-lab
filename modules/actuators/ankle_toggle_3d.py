"""D96 (R-146/P-157, Legs L73): ankle screw toggle in 3D. Geometry from model_v4 P (D60): trunnion (ankle_tx 90, +-ankle_dy 45, ankle_tz 450)
on the shank; instep pin (ankle_lever 73, +-45, ankle_z+ankle_ez = 100) on the foot; ankle cross at (0, 0, 80): pitch about y (shank->cross),
roll about x (cross->foot), model_v4 joint order. Sign as model_v4/Legs: q<0 dorsiflexion. Per-screw pitch moment arm = |((P-A) x u) . y_pitch|.
F per screw 2218 N [EST, Legs: 323.8 N.m /(2 x 0.073)]."""
import json,math,numpy as np
A=np.array([0.,0.,80.]); T={s:np.array([90.,s*45.,450.]) for s in (1,-1)}; P0={s:np.array([73.,s*45.,100.]) for s in (1,-1)}
def Ry(q):  # same as Legs 2D R(q) on (x,z)
    c,s=math.cos(q),math.sin(q); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rx(f): c,s=math.cos(f),math.sin(f); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
F=323.8/2/0.073; out={}
for fd in (0,18,-18):
    rows=[]
    for qd in np.arange(-40,-66.01,-0.25):
        q=math.radians(qd); f=math.radians(fd); arms={}
        for s in (1,-1):
            # pin: foot frame -> roll about x at A -> pitch about y at A ; trunnion is on the shank (fixed frame here)
            p=A+Ry(q)@(Rx(f)@(P0[s]-A)); u=(p-T[s])/np.linalg.norm(p-T[s]); r=p-A
            arms[s]=float(np.cross(r,u)[1])   # signed moment arm about the pitch axis (+y in this frame), mm
        rows.append(dict(q=round(qd,2),arm_p=round(arms[1],2),arm_m=round(arms[-1],2),tau=round(F*(abs(arms[1])*np.sign(arms[1])+arms[-1])/1000*np.sign(arms[1]+arms[-1]),1)))
    sgn=lambda r,k: r[k]>0
    tog={k:next((r['q'] for a,r in zip(rows,rows[1:]) if (a[k]>0)!=(r[k]>0)),None) for k in ('arm_p','arm_m')}
    out[f'roll_{fd}']=dict(toggle_deg=tog,at={str(x):next(r for r in rows if r['q']==x) for x in (-45,-50,-52.5,-55,-57.5,-60)})
json.dump(out,open('results/ankle_toggle_3d.json','w'),indent=1); print(json.dumps(out,indent=1))
# --- 2-DOF parallel singularity: J = d(L+,L-)/d(q,phi); det(J)=0 is the true 3D toggle. Also torque capacity:
# max pitch torque with |F|<=F each and zero net roll moment (static: tau = J^T F).
def L(q,f,s): p=A+Ry(q)@(Rx(f)@(P0[s]-A)); return np.linalg.norm(p-T[s])
def J(q,f,h=1e-5):
    return np.array([[(L(q+h,f,s)-L(q-h,f,s))/2/h,(L(q,f+h,s)-L(q,f-h,s))/2/h] for s in (1,-1)])  # mm/rad
grid=[]
for fd in (0,5,10,12,15,18):
    for qd in (-45,-50,-52.5,-55,-57.5,-60):
        Jm=J(math.radians(qd),math.radians(fd))
        # tau = J^T F (N.mm), want max tau_pitch with tau_roll=0, |F_i|<=F
        best=0
        for f1 in np.linspace(-F,F,401):
            # tau_roll = J[0,1]f1 + J[1,1]f2 = 0
            if abs(Jm[1,1])<1e-9: continue
            f2=-Jm[0,1]*f1/Jm[1,1]
            if abs(f2)<=F: best=max(best,abs(Jm[0,0]*f1+Jm[1,0]*f2)/1000)
        grid.append(dict(roll=fd,q=qd,detJ=round(float(np.linalg.det(Jm)),0),tau_pitch_max_Nm=round(best,1)))
out['parallel']=grid
json.dump(out,open('results/ankle_toggle_3d.json','w'),indent=1)
for g in grid: print(g)
