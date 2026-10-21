"""T&R independent verification of Controls hip_pinch.py (9d96058/54ca3de, ID rev 8f STLs) toward 35/30/28.
T&R geometry: r8c_fix analytic panel R152 (y86+40 chamfer phi0 45) and the 8f notched hem STL, JCH 3. Large random sweep
(N pairs per roll range: contract ROM, +2.5, +3.6 deg) of asymmetric both-leg poses; every pair with a gap < 60 mm is stored so results are reported for the old yaw ROM (-35..45 / +ovt) and the Legs 3f4164b yaw ROM (T&R mirrored: both legs -35..+40) + single-leg hem grid. Also hem STL audit."""
import numpy as np, sys, os, json, trimesh
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(H+'/../..'); D=ROOT+'/modules/design/cad/covers'
src=open(D+'/hip_skirt_r8c_fix.py').read().split("S=np.vstack")[0]; ns={'__file__':D+'/hip_skirt_r8c_fix.py'}; exec(src,ns)
T,C1=ns['T'],ns['C1']; P8=ns['panel'](); JCH=3.0; mir=lambda X:X*[1,-1,1]
sys.path.insert(0,ROOT+'/modules/controls/arm'); import hip_pinch as Hc; Hc._G.clear(); Hc.REV='8f'
hm=trimesh.load(D+'/hip_skirt_r8f_pelvis_notched.stl',force='mesh'); KH=cKDTree(np.vstack([hm.vertices,hm.triangles_center]))
r=np.linalg.norm(hm.vertices-C1,axis=1)
o={'hem_stl':dict(verts=len(hm.vertices),r_from_C1_min=round(float(r.min()),1),r_max=round(float(r.max()),1),
   n_within_1mm_of_R141p5=int((abs(r-141.5)<1).sum()),bbox=[hm.bounds[0].round(1).tolist(),hm.bounds[1].round(1).tolist()])}
# direction of the analytic 30.2 mm closest point
q0=(42.5,-12,-37.5); X=T(P8,*q0); i=np.argmin(np.linalg.norm(X-C1,axis=1)); u=(X[i]-C1)/np.linalg.norm(X[i]-C1)
o['hem_sphere_closest']=dict(pose=q0,panel_pt=X[i].round(1).tolist(),sphere_pt=(C1+141.5*u).round(1).tolist(),
   stl_dist_to_sphere_pt=round(float(KH.query(C1+141.5*u)[0]),1),stl_gap_at_pose=round(float(KH.query(X)[0].min())-JCH,1))
R=np.radians; rng=np.random.default_rng(11); AX=np.array([[0,130,z] for z in np.linspace(500,900,9)])
N=int(sys.argv[1]) if len(sys.argv)>1 else 4000
for k,(lo,hi) in {'ROM':(-12,15),'ovt2.5':(-14.5,17.5),'ovt3.6':(-15.6,18.6)}.items():
    rec=[];err=[];miss=[];below=0;n=0;herr=[];hmiss=[]
    yl,yh=(-35,45) if k=='ROM' else (-37.5,47.5); pl,ph=(-105,40) if k=='ROM' else (-107.5,42.5)
    for _ in range(N):
        a=np.r_[rng.uniform(pl,ph),rng.uniform(lo,hi),rng.uniform(yl,yh)]; b=np.r_[rng.uniform(pl,ph),rng.uniform(lo,hi),rng.uniform(yl,yh)]
        if float(np.linalg.norm(T(AX,*a)[:,None]-mir(T(AX,*b))[None],axis=2).min())<60: continue
        n+=1; XA=T(P8,*a); g=float(cKDTree(XA).query(mir(T(P8,*b)))[0].min())-JCH; gh=float(KH.query(XA)[0].min())-JCH
        G=Hc.gaps({'l_hip_pitch':R(a[0]),'l_hip_roll':R(a[1]),'l_hip_yaw':R(a[2]),'r_hip_pitch':R(b[0]),'r_hip_roll':R(-b[1]),'r_hip_yaw':R(-b[2])})
        if g<60 or gh<60: rec.append(dict(a=a.round(2).tolist(),b=b.round(2).tolist(),tr=round(g,2),ctrl=round(G['lr'],2),htr=round(gh,2),hctrl=round(G['hem_l'],2)))
        if g<60: err.append(G['lr']-g)
        if gh<60: herr.append(G['hem_l']-gh)
        if g<28:
            below+=1
            if G['lr']>=28: miss.append(dict(a=a.round(2).tolist(),b=b.round(2).tolist(),tr=round(g,2),ctrl=round(G['lr'],2)))
        if gh<28 and G['hem_l']>=28: hmiss.append(dict(a=a.round(2).tolist(),tr=round(gh,2),ctrl=round(G['hem_l'],2)))
    e=np.array(err); he=np.array(herr) if herr else np.zeros(1)
    o['sweep_'+k]=dict(pairs=n,lr_below28_TR=below,lr_err_ctrl_minus_TR_mm=dict(n=len(e),max=round(float(e.max()),2),min=round(float(e.min()),2),p99=round(float(np.percentile(e,99)),2)),
       lr_untripped_at_28=miss,hem_err=dict(n=len(herr),max=round(float(he.max()),2),min=round(float(he.min()),2)),hem_untripped_at_28=hmiss,records=rec)
    print(k,{x:v for x,v in o['sweep_'+k].items() if 'untripped' not in x and x!='records'},len(miss),len(hmiss),flush=True)
json.dump(o,open(H+'/r_hip_pinch_8f_verify_ctrl.json','w'),indent=1); print(json.dumps(o['hem_stl']),json.dumps(o['hem_sphere_closest']))
