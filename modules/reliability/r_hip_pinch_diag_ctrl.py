"""T&R: resolve 0.77 mm (r_hip_pinch_check_8b.py) vs 21.6 mm (Controls hip_pinch.py 36786b4). Reproduce worst pair, then evaluate
under both geometries and sign conventions."""
import numpy as np, math, sys, os, json
from scipy.spatial import cKDTree
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../..'))
sys.path.insert(0,ROOT+'/modules/controls/arm'); import hip_pinch as Hc
g=Hc.geometry(); T,mir=g['T'],g['mir']; PC=g['P']
def mypanel(phi0=35):
    P=[]
    for ph in np.linspace(35,60,26):
        for y in np.linspace(86,200,36):
            if y<86+40*max(0,(ph-phi0))/(60-phi0): continue
            r=math.radians(ph); P.append([-150*math.sin(r),y,920-150*math.cos(r)])
    return np.array(P)
PT=mypanel(35)
rng=np.random.default_rng(1); N=6000
samp=lambda n: np.c_[rng.uniform(-107.5,42.5,n),rng.uniform(-14.5,17.5,n),rng.uniform(-37.5,47.5,n)]
A=samp(N); B=samp(N); AX=np.array([[0,130,z] for z in np.linspace(500,900,9)])
best=(1e9,None)
for a,b in zip(A,B):
    if float(np.linalg.norm(T(AX,*a)[:,None]-mir(T(AX,*b))[None],axis=2).min())<60: continue
    d=float(cKDTree(T(PT,*a)).query(mir(T(PT,*b)))[0].min())
    if d<best[0]: best=(d,(a,b))
a,b=best[1]; o={'TR_worst_pair':[a.round(2).tolist(),b.round(2).tolist(),round(best[0],2)]}
lr=lambda P,a,b: round(float(cKDTree(T(P,*a)).query(mir(T(P,*b)))[0].min()),2)
o['TR_panel_phi0_35']=lr(PT,a,b); o['ctrl_panel_phi0_45_same_pose']=lr(PC,a,b)
o['TR_panel_rightsign_flipped(b_r,b_y negated)']=lr(PT,a,[b[0],-b[1],-b[2]])
R=np.radians; q=lambda a,b:{'l_hip_pitch':R(a[0]),'l_hip_roll':R(a[1]),'l_hip_yaw':R(a[2]),'r_hip_pitch':R(b[0]),'r_hip_roll':R(b[1]),'r_hip_yaw':R(b[2])}
o['ctrl_gaps_sim_input_as_TR(+r,+y)']=round(Hc.gaps(q(a,b))['lr'],2)
o['ctrl_gaps_sim_input_mirrored(-r,-y)']=round(Hc.gaps(q(a,[b[0],-b[1],-b[2]]))['lr'],2)
o['ctrl_test_pose_23_0_38_40_0_46']=round(Hc.gaps(q((23,0,38),(40,0,46)))['lr'],2)
o['panel_ymin_TR']=float(PT[:,1].min()); o['panel_ymin_ctrl']=float(PC[:,1].min()); o['n_pts']=[len(PT),len(PC)]
o['ctrl_minus_TR_points_outside']=int((cKDTree(PT).query(PC)[0]>3).sum()); o['TR_minus_ctrl']=int((cKDTree(PC).query(PT)[0]>3).sum())
print(json.dumps(o,indent=1)); json.dump(o,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'r_hip_pinch_diag_ctrl.json'),'w'),indent=1)
