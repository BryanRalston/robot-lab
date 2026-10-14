"""RL Arms A42: wrist fork-cheek vs palm clash over the P-026 ROM (pitch ±60 about y, yaw ±30 about x), light point-sampling check.
Geometry (model_v4.py / palm_7075.py, mm, wrist pivot = origin): roll-output fork cheeks 30(x) x 6(y) x 26(z) centred (0, ±17, +6)
-> occupy x ±15, |y| 14..20, z -7..+19. Palm envelope 32 x 86 x 90 centred z -60 -> x ±16, y ±43, z -105..-15 (top = wrist plate).
Fix searched: notch in the palm top under each cheek band (|y| in [y0, y1], full x), depth to z = -zn. Gap requirement 2 mm.
Hand order: fork -> pitch (y) -> cross -> yaw (x) -> palm, so palm points p map to fork frame as Ry(pitch) @ Rx(yaw) @ p."""
import numpy as np,json,os,itertools
H=os.path.dirname(os.path.abspath(__file__))
def Rx(a):c,s=np.cos(a),np.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a):c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
CHEEK=dict(x=(-15,15),y=(14,20),z=(-7,19)); GAP=2.0
def palm_pts(notch=None,step=1.0):
    xs=np.arange(-16,16.01,step); ys=np.arange(-43,43.01,step); P=[]
    for x in xs:
        for y in ys:
            ztop=-15.0
            if notch and notch[0]<=abs(y)<=notch[1]: ztop=-notch[2]
            for z in np.arange(ztop,ztop-12.01,-step): P.append((x,y,z))   # top 12 mm skin is enough for the clash
    return np.array(P)
def min_gap(P,pitches,yaws):
    g=1e9; worst=None
    for p,yw in itertools.product(pitches,yaws):
        Q=(Ry(np.radians(p))@Rx(np.radians(yw))@P.T).T
        for side in (1,-1):
            lo=np.array([CHEEK['x'][0],min(side*14,side*20),CHEEK['z'][0]]); hi=np.array([CHEEK['x'][1],max(side*14,side*20),CHEEK['z'][1]])
            d=np.maximum(np.maximum(lo-Q,Q-hi),0); dist=np.sqrt((d**2).sum(1)); m=dist.min()
            if m<g: g=m; worst=(p,yw)
    return round(float(g),2),worst
pit=np.arange(-60,60.1,10); yaw=np.arange(-30,30.1,10)
base=min_gap(palm_pts(step=2),pit,yaw); base_old=min_gap(palm_pts(step=2),np.arange(-40,40.1,10),np.arange(-25,25.1,12.5))
# FIX (sphere rule): every fork/cross part within radius Rf of the pivot, palm (except its lug, which lives inside the cross) at >= Rf+gap.
# Compact cheeks 20(x) x 6(y) x 20(z) at |y| 14..20 -> Rf = sqrt(10^2+20^2+10^2) = 24.5 mm. Palm top moved from z -15 to z -27.
CHEEK.update(x=(-10,10),z=(-10,10))
def palm_drop(dz,step=2.0):
    P=palm_pts(step=step); P[:,2]-=dz; return P
fix=min_gap(palm_drop(12.0),pit,yaw)
Rf=float(np.sqrt(10**2+20**2+10**2))
out=dict(current=dict(cheek='30x6x26 at |y|14..20, z -7..19',palm_top_z=-15,gap_P026=base[0],worst_P026=base[1],gap_pm40_pm25=base_old[0]),
  fix=dict(cheek='20x6x20 at |y|14..20 (pin bosses), all fork/cross parts inside r 24.5 of pivot',palm_top_z=-27,drop_mm=12,
           sampled_min_gap_P026_mm=fix[0],sphere_rule=f'palm >= 27 mm from pivot, fork <= {Rf:.1f} mm: >= {27-Rf:.1f} mm for ANY pitch/yaw'),
  consequences=dict(hand_length_mm=+12,wrist_static_Nm=round(7.4+10*9.81*0.012,2),wrist_need_Nm=round(1.5*(7.4+10*9.81*0.012),2),contract_need_Nm=14.7,D70_repeated_peak_Nm=36),
  constraint_for_D70='no wrist drive housing may sit inside the palm swept region (radius >= 27 mm from pivot, |y|<=43 band); D70 units must ride on the roll output above the pivot (z >= +27) or outboard |y| >= 45; CAD by Actuators/ID')
json.dump(out,open(os.path.join(H,'wrist_clash_r4.json'),'w'),indent=1); print(json.dumps(out,indent=0))
