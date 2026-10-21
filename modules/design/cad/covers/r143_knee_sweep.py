"""R-143 + T&R 447aa8e guard: envelope = guard outer face 24.5 proud of the plate (x -59.0), sides at the 100x48 window.
R-143 (a01b3e6): knee heat-plate rev 3 (Actuators D91 194f615: 100x48 plate, 8 fins 13x1.0 @6.0 pitch, fins out) ROM sweep.
No assembly CAD places the plate (Actuators note), so the plate is placed from committed Legs data (thigh frame = world at zero pose):
 - L51 box on the femur rear, z 688-792, 26 deep from the band clamp face x -8.5 -> plate outer face x -34.5; fins to x -47.5;
   y 130 +-24 (plate W 48), z 690-790 (L 100). Our merged drive-bay rear panel (L58 tabs to x -38) gets the 100x48 window.
 - Knee axis y at (x 0, z 500) (model_v4 knee_z); flexion = +Ry, 1 deg steps 0-145 (Legs sweeps 0-135; 145 is R-143).
 - Moving neighbours: Legs shank keep-out point sets (shin fairing, ankle boot; shank frame), knee lever eye at r 47.5 behind the
   axis at 0 deg [EST], RV12 rods dia 12 from the housing trunnion (x -130, z 770) to the eye, at y 130 +-22.5 (overlap with the plate in y,
   so the 2D x-z distance is used: conservative), knee twin housing front fin tips r 42.5+9 about the trunnion (rev B; pivots in place).
 - Hip pitch -105..+40 (Legs poses), 1 deg: plate fins vs hip skirt keep-out points (pelvis frame), hip axis (x 0, z 920).
 - Seated/kneeling: seat plane tangent to the rear-most thigh hardware (housing rear fins x -197 / fairing x -181) at hip 90;
   kneeling = knee 145 (shank under thigh, covered by the knee sweep)."""
import numpy as np, json, os
H = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(H, '../../../legs/results/v5')
ld = lambda f: np.load(os.path.join(V, f+'_pts.npy'))
# fin envelope (tips plane + sides), sampled
fy, fz = np.meshgrid(np.linspace(106, 154, 9), np.linspace(690, 790, 21))
FIN = np.c_[np.full(fy.size, -59.0), fy.ravel(), fz.ravel()]
FIN = np.vstack([FIN] + [np.c_[np.full(fz.size, x), fy.ravel(), fz.ravel()] for x in (-34.5, -41.0, -47.5, -53.0)])
def Ry(P, th, c):
    t = np.radians(th); x, z = P[:, 0]-c[0], P[:, 2]-c[1]
    return np.c_[x*np.cos(t)+z*np.sin(t)+c[0], P[:, 1], -x*np.sin(t)+z*np.cos(t)+c[1]]
def seg_d(Pxz, a, b):
    ab = b-a; t = np.clip(((Pxz-a)@ab)/(ab@ab), 0, 1); return np.linalg.norm(Pxz-(a+t[:, None]*ab), axis=1)
def mind(A, B):
    from scipy.spatial import cKDTree; return float(cKDTree(B).query(A)[0].min())
shank = np.vstack([ld('shin_fairing'), ld('ankle_boot')])
knee = []
for a in range(0, 146):
    S = Ry(shank, a, (0, 500)); eye = Ry(np.array([[-47.5, 130, 500]]), a, (0, 500))[0][[0, 2]]
    rod = float(seg_d(FIN[:, [0, 2]], np.array([-130., 770.]), eye).min() - 6)
    knee.append(dict(deg=a, shank_keepouts=round(mind(FIN, S), 1), rods=round(rod, 1)))
hous = round(float(-59.0 - (-130 + 42.5 + 9)), 1)
hip = []   # pelvis-fixed hardware: pelvis shell underside z 1126 (model_v4 pelvis_bot); hip skirt is flexible P-023 fabric over the thigh
for a in range(-105, 41):
    hip.append(dict(deg=a, hip_skirt=round(float(1126 - Ry(FIN, a, (0, 920))[:, 2].max()), 1)))
kmin = min(knee, key=lambda r: min(r['shank_keepouts'], r['rods'])); hmin = min(hip, key=lambda r: r['hip_skirt'])
out = dict(assumptions=__doc__, knee_min=kmin, hip_min=hmin, housing_fin_tips_static_mm=hous,
           seated_fin_above_seat_mm=round(-59.0 - (-197), 1), A35_static_cover_inner_face_to_fins="n/a: fins pass through a sealed window (no cover over them); window edge seal to plate base",
           gate_mm=3, knee=knee, hip=hip)
json.dump(out, open(os.path.join(H, 'r143_knee_sweep.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('knee_min', 'hip_min', 'housing_fin_tips_static_mm', 'seated_fin_above_seat_mm')}))
