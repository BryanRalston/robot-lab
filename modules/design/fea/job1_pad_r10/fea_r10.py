"""Pad R10 / Arms R13 stand-off FEA (R-120, R-121). CASE.md 00ff254, R7_ROUND.md §G 1ee8d73.
Reuses the job1_pad_r8 hex8 element (fea_job1.py), IKO static P0, and gates. numpy/scipy only.
Frame: origin on the roll axis at the bearing plane; +X roll axis, +Y outboard, +Z up. mm, N, MPa.
Stand-off (ID 00ff254 + Arms R13): ribs 2 x (30 X x 5 Z) Y 0..23 at Z [-5,0] and [-20,-15];
face plate 62x62 Y 23..27 centred Z -20, rear pocket to 2 mm floor (4 mm rim, 8 mm M4 bosses
at +-24, rib lands kept solid); 0.5 mm tray Y 27..27.5; core patch 54.8^2 centred (e, -20).
Rib roots (Y=0) fixed = roll-output hub/flange (flange joint by hand calc from FE reactions)."""
import os, sys, json, numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "..", "job1_pad_r8"))
import fea_job1 as J  # hex_B, C_AL, von_mises, GAUSS, arm_weight, grid_1d

C0, DP = 27700.0, 0.085          # CRBH 7013 A
F = 7000.0; A = np.deg2rad(15.0)
FN, FS = F*np.cos(A), F*np.sin(A)  # 6761, 1812
FS_MU = 0.15*FN                    # mu 0.15 sensitivity (not credited)
PZ, YC = -20.0, 102.3
CORE = 54.8
VM320, VM335 = 320.0, 335.0
E_PT = [0.0]
RIB_Z = ((-5.0, 0.0), (-20.0, -15.0))

def in_part(xc, yc, zc):
    if yc < 23.0:
        return "rib" if abs(xc) <= 15.0 and any(a <= zc <= b for a, b in RIB_Z) else None
    if abs(xc) > 31.0 or abs(zc-PZ) > 31.0: return None
    if yc < 25.0:  # pocketed rear layer
        rim = abs(xc) >= 27.0 or abs(zc-PZ) >= 27.0
        boss = any(abs(xc-sx*24) <= 4.0 and abs(zc-PZ-sz*24) <= 4.0 for sx in (-1,1) for sz in (-1,1))
        land = abs(xc) <= 15.0 and any(a <= zc <= b for a, b in RIB_Z)
        return "plate_rim" if (rim or boss or land) else None
    if yc < 27.0: return "plate_floor"
    return "tray"

def build(h, e):
    ex = [-31,-28,-27,-20,-15,15,20,27,28,31, e-CORE/2, e+CORE/2]
    ez = [PZ+v for v in (-31,-28,-27,-20,-4,4,20,27,28,31)] + [-5,0,-15, PZ-CORE/2, PZ+CORE/2]
    xs = np.array(J.grid_1d(-31, 31, h, extras=ex)); zs = np.array(J.grid_1d(PZ-31, PZ+31, h, extras=ez))
    ys = np.array(J.grid_1d(0, 23, max(h, 1.0)*1.15) + [23.667, 24.333, 25.0, 25.667, 26.333, 27.0, 27.5]); ys = np.unique(np.round(ys, 6))
    nid = -np.ones((len(xs), len(ys), len(zs)), int); elems, reg, loaded = [], [], []
    def node(i, j, k):
        if nid[i, j, k] < 0: nid[i, j, k] = node.n; node.n += 1
        return nid[i, j, k]
    node.n = 0
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            for k in range(len(zs)-1):
                xc, yc, zc = (xs[i]+xs[i+1])/2, (ys[j]+ys[j+1])/2, (zs[k]+zs[k+1])/2
                r = in_part(xc, yc, zc)
                if r is None: continue
                c = [(i,j,k),(i+1,j,k),(i+1,j+1,k),(i,j+1,k),(i,j,k+1),(i+1,j,k+1),(i+1,j+1,k+1),(i,j+1,k+1)]
                elems.append([node(*q) for q in c]); reg.append(r)
                if r == "tray" and abs(xc-e) <= CORE/2 and abs(zc-PZ) <= CORE/2:
                    loaded.append(([node(i,j+1,k), node(i+1,j+1,k), node(i,j+1,k+1), node(i+1,j+1,k+1)],
                                   (xs[i+1]-xs[i])*(zs[k+1]-zs[k])))
    xyz = np.zeros((node.n, 3))
    for i in range(len(xs)):
        for j in range(len(ys)):
            for k in range(len(zs)):
                if nid[i,j,k] >= 0: xyz[nid[i,j,k]] = (xs[i], ys[j], zs[k])
    return xyz, np.array(elems), np.array(reg), loaded

_kc = {}
def ke(pts):
    d = tuple(np.round(pts[6]-pts[0], 6))
    if d not in _kc:
        K = np.zeros((24, 24)); Bs = []
        for a in (-J.GAUSS, J.GAUSS):
            for b in (-J.GAUSS, J.GAUSS):
                for c in (-J.GAUSS, J.GAUSS):
                    B, det = J.hex_B(a, b, c, pts - pts[0]); K += B.T @ J.C_AL @ B * det; Bs.append(B)
        _kc[d] = (K, np.array(Bs))
    return _kc[d]

def solve(xyz, el, reg, loaded, Fvec):
    n = len(xyz); dofs = (3*el[:, :, None] + np.arange(3)).reshape(len(el), 24)
    Ks = np.array([ke(xyz[e])[0] for e in el])
    K = coo_matrix((Ks.ravel(), (np.repeat(dofs, 24, 1).ravel(), np.tile(dofs, (1, 24)).ravel())), shape=(3*n, 3*n)).tocsr()
    # Core load transfer to the tray: shears Fx, Fz uniform; normal Fy as a linear field a + b x' + c z'
    # whose resultant sits at (e, PZ) and whose moments carry Fs over the core height (YC - Y_tray).
    area = sum(a for _, a in loaded); f = np.zeros(3*n)
    cen = np.array([xyz[face].mean(0)[[0, 2]] for face, _ in loaded]); ar = np.array([a for _, a in loaded])
    cp = (cen*ar[:, None]).sum(0)/area; d = cen - cp
    Ixx = (ar*d[:, 0]**2).sum(); Izz = (ar*d[:, 1]**2).sum(); Ixz = (ar*d[:, 0]*d[:, 1]).sum()
    dY = YC - xyz[loaded[0][0][0], 1]
    tx = Fvec[1]*(E_PT[0]-cp[0]) - dY*Fvec[0]; tz = Fvec[1]*(PZ-cp[1]) - dY*Fvec[2]
    b, c = np.linalg.solve([[Ixx, Ixz], [Ixz, Izz]], [tx, tz])
    py = Fvec[1]/area + b*d[:, 0] + c*d[:, 1]
    for (face, a), p in zip(loaded, py):
        for q in face: f[3*q:3*q+3] += np.array([Fvec[0]/area, p, Fvec[2]/area])*a/4
    peel = float(max(0.0, py.max()))  # Fy is -Y (compression); +py means tension on the bond
    comp = float(-py.min())
    fixed = np.where(xyz[:, 1] < 1e-6)[0]; fd = (3*fixed[:, None]+np.arange(3)).ravel()
    free = np.setdiff1d(np.arange(3*n), fd); u = np.zeros(3*n)
    u[free] = spsolve(K[free][:, free].tocsc(), f[free])
    R = K @ u - f; Rf = R.reshape(-1, 3)[fixed]
    Mroot = np.cross(xyz[fixed]/1000, Rf).sum(0)   # N.m about origin (roll axis) of support reactions
    vm = np.array([max(J.von_mises(J.C_AL @ (B @ u[d])) for B in ke(xyz[e])[1]) for e, d in zip(el, dofs)])
    cy = xyz[el].mean(1)[:, 1]
    out = {"nelem": int(len(el)), "ndof": int(3*n), "area_mm2": float(area),
           "support_F_N": (-Rf.sum(0)).tolist(), "support_M_Nm": (-Mroot).tolist(), "vm_abs": float(vm.max()), "bond_peel_MPa": peel, "bond_comp_max_MPa": comp, "bond_shear_MPa": float(np.hypot(Fvec[0], Fvec[2])/area)}
    for r in ("rib", "plate_rim", "plate_floor", "tray"):
        m = reg == r
        out[f"vm_{r}_abs"] = float(vm[m].max())
        if r == "rib":  # exclude the fixed-root singular band (3 mm) and rib/plate re-entrant line (2 mm)
            mm = m & (cy > 3.0) & (cy < 21.0); out["vm_rib_filt"] = float(vm[mm].max())
        if r in ("plate_rim", "plate_floor"):
            cx = xyz[el].mean(1); near = (np.abs(np.abs(cx[:, 0]) - 15) < 2.5) | np.array([any(abs(z-v) < 2.5 for v in (-5, 0, -15, -20)) for z in cx[:, 2]])
            mm = m & ~(near & (np.abs(cx[:, 0]) < 17.5)); out[f"vm_{r}_filt"] = float(vm[mm].max())
            out[f"vm_{r}_p99"] = float(np.percentile(vm[m], 99))
    ln = sorted({q for face, _ in loaded for q in face}); U = u.reshape(-1, 3)[ln]
    out["defl_max_mm"] = float(np.linalg.norm(U, axis=1).max()); out["defl_mean_mm"] = float(np.linalg.norm(U.mean(0)))
    return out

def bearing(Fimp, e, w):
    M = np.cross(np.array([e, YC, PZ])/1000, Fimp) + np.array(w["M_Nm"]); Ft = Fimp + np.array(w["F_N"])
    Fr = np.hypot(Ft[1], Ft[2]); Fa = abs(Ft[0]); Mt = np.hypot(M[1], M[2]); P0 = Fr + 2*Mt/DP + 0.44*Fa
    Mx_raw = np.cross(np.array([e, YC, PZ])/1000, Fimp)[0]
    return {"Fr_N": Fr, "Fa_N": Fa, "Mtilt_Nm": Mt, "P0_N": P0, "s0": C0/P0, "Mx_raw_Nm": float(Mx_raw),
            "gear_SF_fault": 369.0/(1.05*abs(Mx_raw))}

def arms_scalar_s0(fs, e):  # Arms R13 / R-120 conservative scalar sum
    M = fs*np.hypot(YC, -PZ)/1000 + FN*e/1000; return C0/(FN + 2*M/DP + 0.44*fs)

def flange_joint(Fsup, Msup):
    # 8 x M4 12.9 PCD 62 + 2 x dia4 m6 dowels on PCD 62, flange 5 mm 7075. Loads: support resultant at roll axis.
    V = np.hypot(Fsup[1], Fsup[2]) if False else np.linalg.norm([Fsup[1], Fsup[2]])  # in-plane shear (flange plane YZ)
    T = abs(Msup[0]); r = 0.031
    bolt = V/8 + T/(8*r); dowel = V/2 + T/(2*r)
    Mb = np.hypot(Msup[1], Msup[2]); Fa = Fsup[0]
    # bolt tension from tilt on 8 bolts PCD62: max = Fa/8 + Mb/(4 r) (sum r_i^2 = 4 r^2)
    tens = abs(Fa)/8 + Mb/(4*r)
    return {"shear_V_N": V, "torque_Nm": T, "per_bolt_shear_if_bolts_share_N": bolt, "bolt_SF_vs_5kN": 5000/bolt,
            "per_dowel_shear_if_dowels_only_N": dowel, "dowel_tau_MPa": dowel/(np.pi*4), "dowel_SF_vs_600MPa": 600/(dowel/(np.pi*4)),
            "dowel_flange_bearing_MPa": dowel/(4*5), "dowel_bearing_SF_vs_480": 480/(dowel/(4*5)),
            "bolt_tension_max_N": tens, "preload_N": 4600.0, "separation_SF": 4600.0/tens}

def run(h=1.0, h_check=2.0):
    w = J.arm_weight(); res = {"weight": w, "cases": []}
    for tag, fs in (("15deg", FS), ("mu015", FS_MU)):
        for d in ("axial", "down"):
            for e in (0.0, 5.0, 10.0):
                cands = [np.array([s*fs, -FN, 0.0]) for s in (1, -1)] if d == "axial" else [np.array([0.0, -FN, -fs])]
                Fi = min(cands, key=lambda v: bearing(v, e, w)["s0"])
                b = bearing(Fi, e, w); c = {"name": f"{tag}_{d}_e{e:.0f}", "Fs_N": fs, "F_imp": Fi.tolist(), "bearing": b,
                                           "arms_scalar_s0": arms_scalar_s0(fs, e)}
                if tag == "15deg":
                    E_PT[0] = e; mesh = build(h, e); c["fe"] = solve(*mesh, Fi); c["flange"] = flange_joint(c["fe"]["support_F_N"], c["fe"]["support_M_Nm"])
                print(c["name"], round(b["s0"], 3), round(b["Mx_raw_Nm"]), c.get("fe", {}).get("vm_rib_filt"), flush=True)
                res["cases"].append(c)
    E_PT[0] = 10.0; mesh = build(h_check, 10.0); Fi = np.array([0.0, -FN, -FS])
    res["conv_down_e10_h2"] = solve(*mesh, Fi); print("conv", res["conv_down_e10_h2"]["vm_rib_filt"], flush=True)
    json.dump(res, open(os.path.join(H, "results.json"), "w"), indent=1, default=float)
    return res

if __name__ == "__main__":
    run()
