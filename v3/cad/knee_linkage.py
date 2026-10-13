"""v3.2: knee slider-crank geometry vs required torque over the range (the v3 CAD comment claimed arm >=45 mm for 30-120 deg; it is actually 14 mm at 120 deg).
Searches lever clock angle, lever radius and trunnion position; requires arm(theta)*F_peak >= T_req(theta) [EST profile] and rod-end clearance to the femur collar
(2D, sagittal) over 0..KMAX. Writes out/knee_linkage.json"""
import math,json,itertools,sys
sys.argv=['x']
import model
P=model.P;hz,kz=P['hip_z'],P['knee_z'];ODp=model.act_dim('hip_pitch')[0];fl=hz-ODp/2-2
V=model.V3;row=[r for r in V['rows'] if r['joint']=='knee'][0];F=row['T']/V['state']['J']['knee']['arm']
ARMMAX=V['state']['J']['knee']['arm']*1000*row['speed'][0]/row['speed'][1] if isinstance(row.get('speed'),list) else 59.2
REQ={0:40,10:80,20:159,30:159,40:159,50:159,60:159,70:150,80:130,90:110,100:100,110:90,120:75,130:60}   # N·m [EST]: landing 3 BW at 20-60°, slow deep squat beyond
def prof(c,r,tx,tz,kmax):
    T=(tx,tz);res=[]
    for th in range(0,kmax+1,5):
        a=math.radians(c+th);E=(-r*math.sin(a),-r*math.cos(a));d=(T[0]-E[0],T[1]-E[1]);L=math.hypot(*d)
        arm=abs(E[0]*d[1]-E[1]*d[0])/L
        # clearance: rod-end sphere r11 vs femur collar/tube (x in [18-33,18+33], z>40) and clevis rear face (x<-23 open)
        dx=max(0,(18-33)-E[0]-11,E[0]-11-(18+33));dz=max(0,40-E[1]-11)
        clear=(dx>0 or dz>0)
        res.append((th,arm,L,clear))
    return res
def score(c,r,tx,tz,kmax):
    p=prof(c,r,tx,tz,kmax)
    if not all(x[3] for x in p): return None
    Ls=[x[2] for x in p];stroke=max(Ls)-min(Ls)
    if any(x[1]>ARMMAX for x in p if x[0]<=80): return None   # swing speed: joint speed = screw speed/arm, needs arm <= ARMMAX over 0-80°
    marg=min(x[1]/1000*F/REQ[min(REQ,key=lambda k:abs(k-x[0]))] for x in p)
    return marg,stroke,p
best={}
for kmax in (120,130,135,140):
    b=None
    for c,r,tx,tz in itertools.product(range(-20,61,5),(50,52,55,58.5,60,62,65,70),(-95,-110,-125,-140),(fl-60-kz,fl-120-kz,fl-180-kz)):
        pass
        s=score(c,r,tx,tz,kmax)
        if s and (b is None or s[0]>b[0]): b=(s[0],s[1],dict(clock=c,r=r,tx=tx,tz_rel=tz),[(x[0],round(x[1],1)) for x in s[2]])
    best[kmax]=b;print(kmax,b and (round(b[0],2),round(b[1]),b[2]),flush=True)
cur=score(30,52,-95,fl-60-kz,120)
json.dump(dict(F_peak=F,req=REQ,current=dict(margin=cur[0] if cur else None,arm=[(x[0],round(x[1],1)) for x in prof(30,52,-95,fl-60-kz,140)]),best={k:v for k,v in best.items()}),open('out/knee_linkage.json','w'),indent=1)
print('current margin', cur and round(cur[0],2))
# selected geometry (KSEL) -> geometry-only torque factor k = min_theta (arm/arm_nom)/(REQ/need); v3.py sizes the knee to T_out*k >= need
import os
KSEL=int(os.environ.get('KSEL','135'));sel=best[KSEL]
arm_nom=V['state']['J']['knee']['arm']*1000;need=row['need']
k=min(a/arm_nom/(REQ[min(REQ,key=lambda q:abs(q-t))]/need) for t,a in sel[3])
o=json.load(open('out/knee_linkage.json'));o.update(selected=dict(kmax=KSEL,geom=sel[2],arm=sel[3],k=k,arm_nom=arm_nom,armmax_swing=ARMMAX));json.dump(o,open('out/knee_linkage.json','w'),indent=1)
print('selected',KSEL,sel[2],'k=%.3f'%k)
