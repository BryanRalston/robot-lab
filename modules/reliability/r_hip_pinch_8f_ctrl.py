"""T&R rev 8c: (a) panel-only hem gap (sphere R141.5 about C1, JCH 3) at nominal/2.5/3.6/5.8 deg roll overtravel on the 2240(+ovt) grid;
(b) rev 8c geometry (ID r8c_fix panel R152 y86 chamfer phi0 45, JCH 3) L<->R through Controls hip_pinch.py (d941ca6: rev 8b geometry, trip 33 stopgap AND original 28):
any 8c pose < 28 mm that the Controls model reports >= 28 is an untripped closure. Right leg in T&R mirrored convention -> sim (p,-r,-y)."""
import numpy as np, sys, os, json
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(H+'/../..'); D=ROOT+'/modules/design/cad/covers'
src=open(D+'/hip_skirt_r8c_fix.py').read().split("S=np.vstack")[0]; ns={'__file__':D+'/hip_skirt_r8c_fix.py'}; exec(src,ns)
T,C1=ns['T'],ns['C1']; P8=ns['panel'](); JCH=3.0
sys.path.insert(0,ROOT+'/modules/controls/arm'); import hip_pinch as Hc
mir=lambda X:X*[1,-1,1]; R=np.radians
pit=list(range(-105,41,5))+[-107.5,42.5]; yaw=(-37.5,-35,-17,0,22,45,47.5)
OT={'nominal':(-12,15),'ovt2.5':(-14.5,17.5),'ovt3.6':(-15.6,18.6)}
o={}
for k,(lo,hi) in OT.items():
    G=[(p,r,y) for p in pit for r in sorted({lo,-8,-4,0,5,10,hi,-12,15}) if lo<=r<=hi for y in yaw]
    h=min((float(np.linalg.norm(T(P8,*q)-C1,axis=1).min())-141.5-JCH,q) for q in G)
    o['hem_panel_'+k]=[round(h[0],1),list(h[1]),'tol2',round(h[0]-2,1)]
rng=np.random.default_rng(7); AX=np.array([[0,130,z] for z in np.linspace(500,900,9)])
for k in ('nominal','ovt2.5','ovt3.6'):
    lo,hi=OT[k]; n=0; below=0; untr=[]; worst=(1e9,None)
    for _ in range(8000):
        a=np.r_[rng.uniform(-107.5,42.5),rng.uniform(lo,hi),rng.uniform(-37.5,47.5)]; b=np.r_[rng.uniform(-107.5,42.5),rng.uniform(lo,hi),rng.uniform(-37.5,47.5)]
        if float(np.linalg.norm(T(AX,*a)[:,None]-mir(T(AX,*b))[None],axis=2).min())<60: continue
        n+=1; g=float(cKDTree(T(P8,*a)).query(mir(T(P8,*b)))[0].min())-JCH
        if g<worst[0]: worst=(g,(a.round(1).tolist(),b.round(1).tolist()))
        if g<28:
            below+=1; gc=Hc.gaps({'l_hip_pitch':R(a[0]),'l_hip_roll':R(a[1]),'l_hip_yaw':R(a[2]),'r_hip_pitch':R(b[0]),'r_hip_roll':R(-b[1]),'r_hip_yaw':R(-b[2])})['lr']
            inrom= bool(-12<=a[1]<=15 and -12<=b[1]<=15)
            if gc>=min(Hc.TRIP,28): untr.append(dict(a=a.round(1).tolist(),b=b.round(1).tolist(),g8c=round(g,1),ctrl=round(gc,1),in_contract_roll=bool(inrom)))
            else: untr_ok=True
    o['LR_'+k]=dict(feasible=n,below28_8c=below,worst=[round(worst[0],1),worst[1]],ctrl_trip=Hc.TRIP,untripped_by_ctrl_model=len(untr),untripped_at_ctrl_trip=int(sum(u['ctrl']>=Hc.TRIP for u in untr)),note='untripped_by_ctrl_model counts ctrl>=28 (nominal trip); untripped_at_ctrl_trip uses the live stopgap',examples=untr[:6],
        untripped_in_contract_roll=int(sum(u["in_contract_roll"] for u in untr)))
print(json.dumps(o,indent=1)); json.dump(o,open(H+'/r_hip_pinch_8f_ctrl.json','w'),indent=1)
