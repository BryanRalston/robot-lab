"""R5: ankle instep pin radius 70 -> 73 mm (Actuators D45). 3-D clearance sweep over ankle pitch -60..+40 (mechanical) x roll -25..+25 (v3 ranges).
Geometry from v3/cad/model.py: ankle axis (0,0,80); screws at y=±45 from body trunnions (90, ±45, 410) to instep pins (R, ±45, 100) in the foot frame.
Parts checked: screw rod (capsule r6) + rod-end eye (sphere r12 at the pin), nut housing (capsule r20.5, 27..83 mm below the trunnion) vs
tibia tube (capsule r22.5 at x=14, z 130..450), ankle fork box (x -25..37, |y|<=22, z 90..130), ankle cross (30 cube) and the other screw; instep block vs fork."""
import numpy as np,json,os,sys
H=os.path.dirname(os.path.abspath(__file__))
def Rot(p,r):
    p,r=np.radians(p),np.radians(r); Ry=np.array([[np.cos(p),0,np.sin(p)],[0,1,0],[-np.sin(p),0,np.cos(p)]]); Rx=np.array([[1,0,0],[0,np.cos(r),-np.sin(r)],[0,np.sin(r),np.cos(r)]]); return Ry@Rx
def seg_pts(a,b,n=60): return a+(b-a)*np.linspace(0,1,n)[:,None]
def d_box(P,lo,hi): q=np.maximum(np.maximum(lo-P,P-hi),0); return np.linalg.norm(q,axis=1)
def d_capz(P,x,y,z0,z1,r): zc=np.clip(P[:,2],z0,z1); return np.linalg.norm(P-np.c_[np.full(len(P),x),np.full(len(P),y),zc],axis=1)-r
A=np.array([0,0,80.]); res={}
for R in (70.0,73.0):
    worst={}; arm=[]
    for pitch in np.arange(-60,41,5):
        for roll in np.arange(-25,26,5):
            M=Rot(-pitch,roll)   # positive pitch = dorsiflexion (toe up): rotate foot about +y by -pitch in this x-forward frame
            segs=[]
            for sy in (1,-1):
                T=np.array([90,sy*45,410.]); Pn=A+M@(np.array([R,sy*45,100.])-A)
                u=(Pn-T)/np.linalg.norm(Pn-T); rod=seg_pts(T+u*83,Pn); nut=seg_pts(T+u*27,T+u*83,20)
                segs.append((sy,rod,nut,Pn,T))
                checks={'rod_vs_tibia':d_capz(rod,14,0,130,450,22.5)-6,'rod_vs_fork':d_box(rod,np.array([-25,-22,90]),np.array([37,22,130]))-6,
                        'eye_vs_fork':d_box(Pn[None],np.array([-25,-22,90]),np.array([37,22,130]))-12,'eye_vs_cross':d_box(Pn[None],A-15,A+15)-12,
                        'nut_vs_tibia':d_capz(nut,14,0,130,450,22.5)-20.5,'nut_vs_fork':d_box(nut,np.array([-25,-22,90]),np.array([37,22,130]))-20.5}
                for k,v in checks.items():
                    m=float(np.min(v))
                    if k not in worst or m<worst[k][0]: worst[k]=(round(m,1),int(pitch),int(roll))
            # instep block corners (foot frame x R-15..R+15, |y|<=45, z 10..50) vs fork
            c=np.array([[x,y,z] for x in (R-15,R+15) for y in (-45,45) for z in (10,50)]); cw=(A+(M@(c-A).T).T)
            m=float(d_box(cw,np.array([-25,-22,90]),np.array([37,22,130])).min())
            if 'instep_block_vs_fork' not in worst or m<worst['instep_block_vs_fork'][0]: worst['instep_block_vs_fork']=(round(m,1),int(pitch),int(roll))
            if roll==0:   # sagittal moment arm of the screw line about the ankle axis
                sy,rod,nut,Pn,T=segs[0]; d=Pn-T; v=A-T; arm.append((int(pitch),round(float(abs(d[0]*v[2]-d[2]*v[0])/np.hypot(d[0],d[2])),1)))
    res[f'R{R:g}']=dict(min_clearance_mm={k:dict(gap=v[0],pitch=v[1],roll=v[2]) for k,v in worst.items()},arm_min_mm=min(a for _,a in arm),arm_at=[a for a in arm if a[1]==min(x for _,x in arm)][0],arm_profile=arm)
json.dump(res,open(f'{H}/results/r5/ankle_clearance.json','w'),indent=1)
for k,v in res.items(): print(k,'arm min',v['arm_min_mm'],v['arm_at'],{a:b['gap'] for a,b in v['min_clearance_mm'].items()})
