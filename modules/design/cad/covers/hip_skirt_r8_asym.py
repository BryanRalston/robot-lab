"""P-023 rev 8 L<->R thigh-panel re-sweep with ASYMMETRIC both-leg poses (Controls 164eeab finding), Legs pivots (as hip_skirt_r8.py).
Region: pitch -10..+45, yaw -45..45 (both signs: toe-in/out), roll -20..+20, each leg independent; 20k random pairs + Controls' worst.
Variants: inboard edge y0 and an inboard-rear corner chamfer (cut where y < y0 + c*(phi-phi0)/(60-phi0)). Shroud spans y 86-150, so y0 <= 86."""
import numpy as np, math, json, os
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__))
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def T(X,p,r,yw):
    P=(X-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
def panel(y0=60,c=0,phi0=35):
    P=[]
    for ph in np.linspace(35,60,26):
        for y in np.linspace(y0,200,36):
            if c and y < y0 + c*max(0,(ph-phi0))/(60-phi0): continue
            r=math.radians(ph); P.append([-150*math.sin(r),y,920-150*math.cos(r)])
    return np.array(P)
rng=np.random.default_rng(0); N=20000
Q=np.c_[rng.uniform(-10,45,(N,2)),rng.uniform(-20,20,(N,2)),rng.uniform(-45,45,(N,2))]
def sweep(P):
    worst=(1e9,None); bad=0
    for pl,pr,rl,rr,yl,yr in Q:
        g=float(cKDTree(T(P,pl,rl,yl)).query(T(P,pr,rr,yr)*[1,-1,1])[0].min())
        if g<3: bad+=1
        if g<worst[0]: worst=(g,(pl,pr,rl,rr,yl,yr))
    return round(worst[0],1),[round(v,1) for v in worst[1]],bad
res={}
for name,kw in [("rev8",dict()),("y0=70",dict(y0=70)),("y0=80",dict(y0=80)),("y0=86",dict(y0=86)),("y0=86+ch40",dict(y0=86,c=40,phi0=45))]:
    res[name]=sweep(panel(**kw)); print(name,res[name],flush=True)
json.dump(res,open(os.path.join(H,'hip_skirt_r8_asym.json'),'w'),indent=1)
