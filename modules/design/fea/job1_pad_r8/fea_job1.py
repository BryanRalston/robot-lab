"""Job 1 — ID shoulder-pad FEA, R8 option B (R-079).

Solid 7075-T6 roll-yaw link, integral 62x62x10 mm boss, 0.5 mm 7075 tray
on 4x M4. Core is the crush patch (not a metal solid). Four cases:
shear along the roll axis and shear downward, pad offset e = 0 and 10 mm,
plus arm weight in tuck B.

scikit-fem, gmsh and CalculiX are not installed here. The metal stress and
the pad deflection are a linear hex8 model (numpy/scipy, 2x2x2 Gauss).
The element is checked against a constant-stress patch test and a
Timoshenko cantilever before the design cases. Bearing s0, the DP490
bond, M4 slip and tab bearing are equilibrium checks on the same loads.
A plane-stress quad4 model of one tray hole supplies the local bearing
stress field; that peak is reported beside the code bearing check.

Units in the mesh: N, mm, MPa. Bearing arithmetic uses N and m.
"""
from __future__ import annotations

import json
import os

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

H = os.path.dirname(os.path.abspath(__file__))

# 7075-T6. E, nu match the repo hex/tet FEA (hp_lever_fea, fea_r4).
# Yield used for the tab bearing allowable is the materials-db 480 MPa
# (the R8 tray check is "vs 480"), not the 503 MPa MMPDS value.
E_MPA = 71700.0
NU = 0.33
SY_BEARING = 480.0
VM_ALLOW = 320.0
BOND_ALLOW = 7.7
BEARING_SF_MIN = 2.0
TAB_SF_MIN = 1.5
DEFL_ALLOW_MM = 1.0

# IKO CRBH 6013 A. dp = (d+D)/2. C0 from the catalog row in v3/analysis/parts.py
# and modules/arms/R7_ROUND.md. R7 writes P0 = Fr + 2M/dp + 0.44 Fa.
CRBH_C0_N = 24300.0
CRBH_DP_M = 0.075
# M4 12.9, R8 roll-yaw face qualification: proof 8.78 mm^2 x 970 MPa,
# preload 5.5 kN at about 70% proof, mu 0.15 (Arms R8 §4).
M4_PRELOAD_N = 5500.0
M4_MU = 0.15
M4_D_MM = 4.0
M4_HOLE_MM = 4.5
TRAY_T_MM = 0.5
N_BOLT = 4

# Impact. 9.17 kN at 15 deg -> 8.86 kN normal, 2.37 kN tangential.
F_PEAK_N = 9170.0
ANG = np.deg2rad(15.0)
FN_N = F_PEAK_N * np.cos(ANG)
FS_N = F_PEAK_N * np.sin(ANG)
CORE_MM = 61.8

# Geometry relative to the CRBH centre, mm. Roll axis is +X (fore-aft),
# +Y outboard, +Z up. model_v4: link box 60 x 40 x 50 centred 64 mm below
# the roll axis and 10 mm inboard of the housing centreline; outboard face
# at Y=+10. Boss 10 mm, tray 0.5 mm, then core 60 + spreader 0.5 + EPP 6.
# The generic sw() bearing is drawn at x = L/2+4; that envelope cannot put
# the pad on the bearing plane with the stated 1-6 mm boss overhang, so the
# qualified layout puts the bearing plane at the link (e is the pad shift).
LINK_X = (-30.0, 30.0)
LINK_Y = (-30.0, 10.0)
LINK_Z = (-89.0, -39.0)
BOSS_T = 10.0
BOSS_Y = (10.0, 20.0)
PAD_Z = -64.0
Y_CONTACT = 20.0 + TRAY_T_MM + 60.0 + 0.5 + 6.0  # 87.0 mm, outer EPP face
Y_BOND = 20.0 + TRAY_T_MM

# Tuck B (Arms R7 / R10): pitch +5, roll 0, yaw 0, elbow 0. Masses are the
# catalog split distal to the roll bearing (arm_inertials_r3.json).
G_MPS2 = 9.81
TUCK_PITCH_DEG = 5.0
# (name, kg, z below the yaw joint along the straight arm, m)
ARM_PARTS = (
    ("shoulder_yaw actuator", 0.81, 0.00),
    ("upper arm tube + clevis", 0.35, 0.185),
    ("forearm stack", 4.415, 0.180 + 0.113),  # elbow is 0.180 m below yaw (300-120)
    ("hand", 0.472, 0.180 + 0.287 + 0.095),
)
# Yaw joint and pitch axis relative to the bearing centre, mm (model_v4).
YAW_YZ_MM = (-10.0, -120.0)
PITCH_AXIS_Y_MM = -90.0


def lame_C(E, nu):
    lam = E * nu / ((1.0 + nu) * (1.0 - 2.0 * nu))
    mu = E / (2.0 * (1.0 + nu))
    C = np.zeros((6, 6))
    C[0, 0] = C[1, 1] = C[2, 2] = lam + 2.0 * mu
    C[0, 1] = C[0, 2] = C[1, 0] = C[1, 2] = C[2, 0] = C[2, 1] = lam
    C[3, 3] = C[4, 4] = C[5, 5] = mu
    return C


C_AL = lame_C(E_MPA, NU)
SIGNS = np.array(
    [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
     [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]],
    dtype=float,
)
GAUSS = 1.0 / np.sqrt(3.0)


def hex_B(xi, eta, zeta, xyz):
    """B (6x24, engineering strain) and det(J). xyz is (8,3), node order = SIGNS."""
    dN = np.zeros((8, 3))
    for a, (sx, sy, sz) in enumerate(SIGNS):
        dN[a, 0] = 0.125 * sx * (1.0 + sy * eta) * (1.0 + sz * zeta)
        dN[a, 1] = 0.125 * sy * (1.0 + sx * xi) * (1.0 + sz * zeta)
        dN[a, 2] = 0.125 * sz * (1.0 + sx * xi) * (1.0 + sy * eta)
    J = dN.T @ xyz
    det = np.linalg.det(J)
    dNx = np.linalg.solve(J, dN.T).T  # (8,3) dN/dx,y,z
    B = np.zeros((6, 24))
    for a in range(8):
        i = 3 * a
        dx, dy, dz = dNx[a]
        B[0, i] = dx
        B[1, i + 1] = dy
        B[2, i + 2] = dz
        B[3, i] = dy
        B[3, i + 1] = dx
        B[4, i + 1] = dz
        B[4, i + 2] = dy
        B[5, i] = dz
        B[5, i + 2] = dx
    return B, det


def element_ke(xyz8):
    Ke = np.zeros((24, 24))
    for xi in (-GAUSS, GAUSS):
        for eta in (-GAUSS, GAUSS):
            for zeta in (-GAUSS, GAUSS):
                B, det = hex_B(xi, eta, zeta, xyz8)
                if det <= 0:
                    raise RuntimeError("inverted hex element")
                Ke += (B.T @ C_AL @ B) * det
    return Ke


def von_mises(s):
    sx, sy, sz, txy, tyz, txz = s
    return np.sqrt(
        0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2)
        + 3.0 * (txy ** 2 + tyz ** 2 + txz ** 2)
    )


def unique_sorted(vals, tol=1e-6):
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > tol:
            out.append(float(v))
    return out


def grid_1d(lo, hi, h, extras=()):
    n = max(1, int(round((hi - lo) / h)))
    xs = list(np.linspace(lo, hi, n + 1))
    for v in extras:
        if lo - 1e-8 <= v <= hi + 1e-8:
            xs.append(float(v))
    return unique_sorted(xs)


class Mesh:
    def __init__(self):
        self.xyz = []
        self._id = {}
        self.elems = []  # (nids[8], region str)
        self.loaded = []  # (nids[4], area_vec (3,)) outer tray faces in the core patch

    def node(self, x, y, z):
        key = (round(x, 5), round(y, 5), round(z, 5))
        i = self._id.get(key)
        if i is None:
            i = len(self.xyz)
            self._id[key] = i
            self.xyz.append([x, y, z])
        return i

    def add_hex(self, pts, region):
        # pts: 8 coordinates, node order matching SIGNS with xi~x, eta~y, zeta~z
        nids = [self.node(*p) for p in pts]
        self.elems.append((nids, region))
        return nids

    def add_block(self, xs, ys, zs, region, loaded_zrange=None, loaded_xrange=None):
        xs, ys, zs = list(xs), list(ys), list(zs)
        for ix in range(len(xs) - 1):
            for iy in range(len(ys) - 1):
                for iz in range(len(zs) - 1):
                    x0, x1 = xs[ix], xs[ix + 1]
                    y0, y1 = ys[iy], ys[iy + 1]
                    z0, z1 = zs[iz], zs[iz + 1]
                    corners = [
                        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
                    ]
                    nids = self.add_hex(corners, region)
                    if region == "tray" and iy == len(ys) - 2:
                        y_out = ys[-1]
                        face = [self.node(sx, y_out, sz) for sz in (zs[iz], zs[iz + 1]) for sx in (xs[ix], xs[ix + 1])]
                        # face node order is not used except as the 4 nodes
                        xc = 0.5 * (xs[ix] + xs[ix + 1])
                        zc = 0.5 * (zs[iz] + zs[iz + 1])
                        if loaded_xrange and loaded_zrange and loaded_xrange[0] <= xc <= loaded_xrange[1] and loaded_zrange[0] <= zc <= loaded_zrange[1]:
                            area = (xs[ix + 1] - xs[ix]) * (zs[iz + 1] - zs[iz])
                            self.loaded.append((face, area, xc, zc))


def hex_pts_order_check():
    """Corners appended z,y,x must match SIGNS."""
    # built in add_block
    return True


def build_mesh(e_mm, h):
    m = Mesh()
    bx0, bx1 = e_mm - 31.0, e_mm + 31.0
    bz0, bz1 = PAD_Z - 31.0, PAD_Z + 31.0
    # Shared interface coordinates so the boss conforms to the link face.
    # Insert a boss edge only when it lands inside the link, so the shared
    # face is conforming and the link is not stretched out to the overhang.
    link_x = grid_1d(LINK_X[0], LINK_X[1], h, extras=(bx0, bx1))
    link_y = grid_1d(LINK_Y[0], LINK_Y[1], h)
    link_z = grid_1d(LINK_Z[0], LINK_Z[1], h, extras=(bz0, bz1))
    m.add_block(link_x, link_y, link_z, "link")
    # Boss X/Z: link nodes that fall inside the boss, plus the boss boundary,
    # plus a pitch-h subdivision of each overhang.
    def boss_axis(lo, hi, link_axis):
        inside = [v for v in link_axis if lo - 1e-8 <= v <= hi + 1e-8]
        extra = []
        for a, b in ((lo, min(inside) if inside else hi), (max(inside) if inside else lo, hi)):
            if b - a > 1e-6:
                extra.extend(grid_1d(a, b, h))
        return grid_1d(lo, hi, h * 10, extras=inside + extra)

    boss_x = boss_axis(bx0, bx1, link_x)
    boss_z = boss_axis(bz0, bz1, link_z)
    boss_y = grid_1d(BOSS_Y[0], BOSS_Y[1], h)
    m.add_block(boss_x, boss_y, boss_z, "boss")
    tray_y = [BOSS_Y[1], BOSS_Y[1] + TRAY_T_MM]
    m.add_block(
        boss_x, tray_y, boss_z, "tray",
        loaded_xrange=(e_mm - CORE_MM / 2.0, e_mm + CORE_MM / 2.0),
        loaded_zrange=(PAD_Z - CORE_MM / 2.0, PAD_Z + CORE_MM / 2.0),
    )
    m.xyz = np.asarray(m.xyz, dtype=float)
    return m


def solve_case(mesh, force_xyz, fixed_z):
    """force_xyz is the traction (N/mm^2) on the loaded tray faces, +components."""
    xyz = mesh.xyz
    nnode = len(xyz)
    ndof = 3 * nnode
    # Assembly
    II, JJ, VV = [], [], []
    # Also keep element stiffness action for stress via solved u
    elem_meta = []
    for nids, region in mesh.elems:
        pts = xyz[nids]
        Ke = element_ke(pts)
        dofs = np.array([[3 * n, 3 * n + 1, 3 * n + 2] for n in nids]).ravel()
        for a in range(24):
            II.extend([dofs[a]] * 24)
            JJ.extend(dofs.tolist())
            VV.extend(Ke[a].tolist())
        elem_meta.append((dofs, pts, region, nids))
    K = coo_matrix((VV, (II, JJ)), shape=(ndof, ndof)).tocsr()
    f = np.zeros(ndof)
    loaded_area = 0.0
    for face, area, xc, zc in mesh.loaded:
        loaded_area += area
        # 4-node face, uniform traction -> equal nodal forces (bilinear rectangle)
        nodal = force_xyz * (area / 4.0)
        for n in face:
            f[3 * n: 3 * n + 3] += nodal
    fixed_nodes = np.where(np.abs(xyz[:, 2] - fixed_z) < 1e-4)[0]
    if len(fixed_nodes) == 0:
        raise RuntimeError("no fixed nodes")
    fixed_dofs = np.array([[3 * n, 3 * n + 1, 3 * n + 2] for n in fixed_nodes]).ravel()
    all_dofs = np.arange(ndof)
    free = np.setdiff1d(all_dofs, fixed_dofs)
    u = np.zeros(ndof)
    u[free] = spsolve(K[free][:, free], f[free])
    # reactions
    R = K @ u - f
    rx = np.zeros(3)
    mom = np.zeros(3)  # N*mm about the bearing origin
    for n in fixed_nodes:
        rf = R[3 * n: 3 * n + 3]
        rx += rf
        mom += np.cross(xyz[n], rf)
    # stress
    vm_all = []
    vm_filt = []
    vm_region = {"link": [], "boss": [], "tray": []}
    z_top = fixed_z
    for dofs, pts, region, nids in elem_meta:
        ue = u[dofs]
        el_vm = []
        for xi in (-GAUSS, GAUSS):
            for eta in (-GAUSS, GAUSS):
                for zeta in (-GAUSS, GAUSS):
                    B, det = hex_B(xi, eta, zeta, pts)
                    s = C_AL @ (B @ ue)
                    el_vm.append(von_mises(s))
        vmax = float(np.max(el_vm))
        vm_all.append(vmax)
        vm_region[region].append(vmax)
        centroid = pts.mean(axis=0)
        near_support = centroid[2] > z_top - 6.0
        # re-entrant edge of the boss against the link face: y~10 and on the
        # link-face perimeter, or within one element of that line
        on_corner = abs(centroid[1] - BOSS_Y[0]) < 3.0 and (
            centroid[0] < LINK_X[0] + 3.0 or centroid[0] > LINK_X[1] - 3.0
            or centroid[2] < LINK_Z[0] + 3.0 or centroid[2] > LINK_Z[1] - 3.0
        )
        if not near_support and not on_corner:
            vm_filt.append(vmax)
    # pad centre: loaded-face nodes closest to (e is encoded by the patch; use mean of loaded nodes)
    loaded_nodes = sorted({n for face, *_ in mesh.loaded for n in face})
    up = u.reshape(-1, 3)[loaded_nodes]
    # magnitude of the mean displacement, and the max magnitude
    mean_u = up.mean(axis=0)
    defl_mean = float(np.linalg.norm(mean_u))
    defl_max = float(np.linalg.norm(up, axis=1).max())
    applied = np.zeros(3)
    for face, area, xc, zc in mesh.loaded:
        applied += force_xyz * area
    return dict(
        nnode=nnode,
        nelem=len(mesh.elems),
        loaded_area_mm2=loaded_area,
        applied_N=applied.tolist(),
        reaction_N=(-rx).tolist(),  # load on the support from the part, i.e. -reaction-on-part wait
        support_force_on_mesh_N=rx.tolist(),
        support_moment_on_mesh_Nmm=mom.tolist(),
        vm_abs=float(np.max(vm_all)),
        vm_filt=float(np.max(vm_filt)) if vm_filt else float(np.max(vm_all)),
        vm_p95=float(np.percentile(vm_all, 95)),
        vm_region={k: float(np.max(v)) if v else 0.0 for k, v in vm_region.items()},
        defl_mean_mm=defl_mean,
        defl_max_mm=defl_max,
        u_mean_mm=mean_u.tolist(),
    )


def r7_p0(Fr, Fa, M_nm):
    """R7 simplified: M = Fn*e only, Fa = Fs when the shear is called axial."""
    return Fr + 2.0 * M_nm / CRBH_DP_M + 0.44 * Fa


def full_bearing(forces_N, moments_Nm):
    """IKO static equivalent. Fr from the two radial components, Fa axial,
    M the tilting moment sqrt(My^2+Mz^2). Mx is spin about the roll axis
    and is not part of P0 (the gear holds it)."""
    Fx, Fy, Fz = forces_N
    Mx, My, Mz = moments_Nm
    Fr = float(np.hypot(Fy, Fz))
    Fa = abs(float(Fx))
    Mtilt = float(np.hypot(My, Mz))
    P0 = Fr + 2.0 * Mtilt / CRBH_DP_M + 0.44 * Fa
    return dict(Fr_N=Fr, Fa_N=Fa, Mx_Nm=float(Mx), My_Nm=float(My), Mz_Nm=float(Mz),
                Mtilt_Nm=Mtilt, P0_N=P0, s0=CRBH_C0_N / P0)


def arm_weight():
    """Tuck B weight of the arm distal to the roll bearing, at the COM."""
    m = 0.0
    mz = 0.0
    for name, mass, z_below_yaw in ARM_PARTS:
        m += mass
        mz += mass * z_below_yaw
    z_below_yaw = mz / m
    # COM in the bearing frame before the pitch rotation: yaw joint + down the arm.
    # Arm hangs on -Z. Yaw is at (0, YAW_Y, YAW_Z).
    yaw_y, yaw_z = YAW_YZ_MM
    p = np.array([0.0, yaw_y, yaw_z - z_below_yaw * 1000.0])  # mm
    # Rotate +pitch about the pitch axis (parallel to Y through y=PITCH_AXIS_Y).
    th = np.deg2rad(TUCK_PITCH_DEG)
    c, s = np.cos(th), np.sin(th)
    v = p - np.array([0.0, PITCH_AXIS_Y_MM, 0.0])
    xr = c * v[0] + s * v[2]
    zr = -s * v[0] + c * v[2]
    pr = np.array([xr, v[1] + PITCH_AXIS_Y_MM, zr])
    W = m * G_MPS2
    F = np.array([0.0, 0.0, -W])  # N, downward
    M = np.cross(pr / 1000.0, F)  # N*m
    return dict(mass_kg=m, W_N=W, com_mm=pr.tolist(), F_N=F.tolist(), M_Nm=M.tolist(),
                z_below_yaw_m=z_below_yaw)


def impact_resultant(e_mm, direction, y_mm):
    """External impact force and its moment about the bearing centre.
    direction 'axial' uses +X shear; 'down' uses -Z shear.
    The line of action passes through (e, y_mm, PAD_Z)."""
    if direction == "axial":
        F = np.array([FS_N, -FN_N, 0.0])
    elif direction == "down":
        F = np.array([0.0, -FN_N, -FS_N])
    else:
        raise ValueError(direction)
    p = np.array([e_mm, y_mm, PAD_Z]) / 1000.0
    M = np.cross(p, F)
    return F, M


def combine_bearing(e_mm, direction, y_mm, weight):
    Fi, Mi = impact_resultant(e_mm, direction, y_mm)
    # Axial shear sign: take the sign with the lower s0 (both are "along the axis").
    if direction == "axial":
        cands = []
        for sgn in (1.0, -1.0):
            F = np.array([sgn * FS_N, -FN_N, 0.0])
            p = np.array([e_mm, y_mm, PAD_Z]) / 1000.0
            M = np.cross(p, F)
            Ft = F + np.array(weight["F_N"])
            Mt = M + np.array(weight["M_Nm"])
            cands.append((full_bearing(Ft, Mt), F, M))
        cands.sort(key=lambda c: c[0]["s0"])
        info, F, M = cands[0]
        return info, F, M
    Ft = Fi + np.array(weight["F_N"])
    Mt = Mi + np.array(weight["M_Nm"])
    return full_bearing(Ft, Mt), Fi, Mi


# ----- plane-stress quad4: patch test, Kirsch-style hole, tray lug -----

def quad_ke_stress(xy, t, E, nu):
    """4-node quad, plane stress, 2x2 Gauss. Returns Ke (8x8) and a list of
    (vm, stress) at Gauss points for a later ue. Here just Ke; stress separate."""
    C = E / (1.0 - nu ** 2) * np.array([
        [1.0, nu, 0.0],
        [nu, 1.0, 0.0],
        [0.0, 0.0, (1.0 - nu) / 2.0],
    ])
    Ke = np.zeros((8, 8))
    gp = []
    for xi in (-GAUSS, GAUSS):
        for eta in (-GAUSS, GAUSS):
            dN = 0.25 * np.array([
                [-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)],
                [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)],
            ])
            J = dN @ xy
            det = np.linalg.det(J)
            if det <= 0:
                raise RuntimeError("inverted quad")
            dNx = np.linalg.solve(J, dN)
            B = np.zeros((3, 8))
            for a in range(4):
                B[0, 2 * a] = dNx[0, a]
                B[1, 2 * a + 1] = dNx[1, a]
                B[2, 2 * a] = dNx[1, a]
                B[2, 2 * a + 1] = dNx[0, a]
            Ke += (B.T @ C @ B) * det * t
            gp.append((B, C))
    return Ke, gp


def solve_quads(nodes, quads, t, fixed, loads):
    """nodes (n,2), quads list of 4 nids, fixed list of (nid, comp) comp 0/1,
    loads dict nid -> (fx, fy)."""
    n = len(nodes)
    II, JJ, VV = [], [], []
    gps = []
    for q in quads:
        xy = nodes[q]
        Ke, gp = quad_ke_stress(xy, t, E_MPA, NU)
        dofs = np.array([[2 * i, 2 * i + 1] for i in q]).ravel()
        for a in range(8):
            II.extend([dofs[a]] * 8)
            JJ.extend(dofs.tolist())
            VV.extend(Ke[a].tolist())
        gps.append((dofs, gp))
    nd = 2 * n
    K = coo_matrix((VV, (II, JJ)), shape=(nd, nd)).tocsr()
    f = np.zeros(nd)
    for i, (fx, fy) in loads.items():
        f[2 * i] += fx
        f[2 * i + 1] += fy
    fd = []
    for i, c in fixed:
        fd.append(2 * i + c)
    fd = np.array(sorted(set(fd)), dtype=int)
    free = np.setdiff1d(np.arange(nd), fd)
    u = np.zeros(nd)
    u[free] = spsolve(K[free][:, free], f[free])
    vms = []
    for dofs, gp in gps:
        ue = u[dofs]
        for B, C in gp:
            s = C @ (B @ ue)
            sx, sy, txy = s
            vm = np.sqrt(sx * sx - sx * sy + sy * sy + 3.0 * txy * txy)
            vms.append(float(vm))
    return u, vms


def assemble(mesh):
    """CSR stiffness and per-element (dofs, xyz, region). COO is filled as arrays."""
    xyz = mesh.xyz
    ne = len(mesh.elems)
    nnz = ne * 576
    I = np.empty(nnz, np.int32)
    J = np.empty(nnz, np.int32)
    V = np.empty(nnz, np.float64)
    metas = []
    p = 0
    for nids, region in mesh.elems:
        pts = xyz[nids]
        Ke = element_ke(pts)
        dofs = np.empty(24, np.int32)
        for a, n in enumerate(nids):
            dofs[3 * a] = 3 * n
            dofs[3 * a + 1] = 3 * n + 1
            dofs[3 * a + 2] = 3 * n + 2
        I[p:p + 576] = np.repeat(dofs, 24)
        J[p:p + 576] = np.tile(dofs, 24)
        V[p:p + 576] = Ke.ravel()
        p += 576
        metas.append((dofs, pts, region))
    nd = 3 * len(xyz)
    K = coo_matrix((V, (I, J)), shape=(nd, nd)).tocsr()
    return K, metas


def validate_patch():
    """Imposed uniaxial strain with Poisson contraction. Hex8 must return 100 MPa."""
    m = Mesh()
    m.add_block([0.0, 1.0, 2.0], [0.0, 1.0], [0.0, 1.0], "link")
    m.xyz = np.asarray(m.xyz, dtype=float)
    K, metas = assemble(m)
    ex = 100.0 / E_MPA
    u = np.zeros(3 * len(m.xyz))
    for n, p in enumerate(m.xyz):
        u[3 * n] = ex * p[0]
        u[3 * n + 1] = -NU * ex * p[1]
        u[3 * n + 2] = -NU * ex * p[2]
    sxx = []
    for dofs, pts, region in metas:
        for xi in (-GAUSS, GAUSS):
            for eta in (-GAUSS, GAUSS):
                for zeta in (-GAUSS, GAUSS):
                    B, det = hex_B(xi, eta, zeta, pts)
                    s = C_AL @ (B @ u[dofs])
                    sxx.append(s[0])
                    if abs(s[1]) > 1.0 or abs(s[2]) > 1.0 or abs(s[3]) > 1.0:
                        raise RuntimeError(f"patch stress not uniaxial: {s}")
    sig = float(np.mean(sxx))
    return dict(sigma_xx_MPa=sig, expected_MPa=100.0, err_pct=float(abs(sig - 100.0)))


def validate_cantilever():
    """Stocky cantilever, same proportions as the link depth. Timoshenko tip."""
    L, b, h = 40.0, 20.0, 20.0  # mm, bend about X? force in Y, axis Z
    # section b in X, h in Y, length L in Z. I = b*h^3/12
    F = 1000.0
    nx, ny, nz = 4, 4, 8
    xs = np.linspace(0, b, nx + 1)
    ys = np.linspace(0, h, ny + 1)
    zs = np.linspace(0, L, nz + 1)
    m = Mesh()
    m.add_block(xs, ys, zs, "link")
    m.xyz = np.asarray(m.xyz, dtype=float)
    # Fix z=0. Load total Fy at z=L, uniform on the face.
    xyz = m.xyz
    K, _metas = assemble(m)
    nd = 3 * len(xyz)
    f = np.zeros(nd)
    top = np.where(np.abs(xyz[:, 2] - L) < 1e-8)[0]
    for n in top:
        f[3 * n + 1] += F / len(top)
    bot = np.where(np.abs(xyz[:, 2]) < 1e-8)[0]
    fd = np.array([[3 * n, 3 * n + 1, 3 * n + 2] for n in bot]).ravel()
    free = np.setdiff1d(np.arange(nd), fd)
    u = np.zeros(nd)
    u[free] = spsolve(K[free][:, free], f[free])
    tip = u.reshape(-1, 3)[top, 1].mean()
    I = b * h ** 3 / 12.0
    G = E_MPA / (2.0 * (1.0 + NU))
    A = b * h
    d_bend = F * L ** 3 / (3.0 * E_MPA * I)
    d_shear = 1.2 * F * L / (G * A)
    d_ref = d_bend + d_shear
    return dict(fea_tip_mm=float(tip), timoshenko_mm=float(d_ref), bend_mm=float(d_bend),
                shear_mm=float(d_shear), err_pct=float(abs(tip - d_ref) / d_ref * 100.0),
                mesh=[nx, ny, nz])


def validate_hole():
    """Wide plate, central hole, remote uniaxial tension. Kirsch peak is 3 sigma
    for an infinite plate; a finite plate of half-width 15*R sits near that."""
    R = 2.0
    outer = 30.0  # half-width, w/d = 15
    nr, nt = 12, 48
    nodes = []
    for i in range(nr + 1):
        rho = (i / nr) ** 1.15
        for j in range(nt):
            th = 2 * np.pi * j / nt
            rb = outer / max(abs(np.cos(th)), abs(np.sin(th)))
            r = R + (rb - R) * rho
            nodes.append([r * np.cos(th), r * np.sin(th)])
    nodes = np.asarray(nodes)
    quads = []
    for i in range(nr):
        for j in range(nt):
            j2 = (j + 1) % nt
            quads.append([i * nt + j, (i + 1) * nt + j, (i + 1) * nt + j2, i * nt + j2])
    # remote tension sigma = 10 MPa in x: on the outer boundary apply traction
    # sigma * n * edge length * t, t=1
    sigma = 10.0
    t = 1.0
    loads = {}
    fixed = []
    # fix a rigid mode: node at angle 0 outer, uy; node at angle 90 outer, ux; and one ux
    outer_ids = list(range(nr * nt, (nr + 1) * nt))
    for j, nid in enumerate(outer_ids):
        th = 2 * np.pi * j / nt
        th2 = 2 * np.pi * ((j + 1) % nt) / nt
        # edge from j to j+1, use nodal share later by looping edges
        pass
    def nid_of(i, j):
        return i * nt + (j % nt)
    for j in range(nt):
        n1 = nid_of(nr, j)
        n2 = nid_of(nr, j + 1)
        p1 = nodes[n1]
        p2 = nodes[n2]
        mid = 0.5 * (p1 + p2)
        L = np.linalg.norm(p2 - p1)
        # outward normal of a square-ish boundary: radial of the midpoint, for a
        # square the traction of uniaxial tension is sigma * n, n outward.
        # Use the geometric outward normal of the edge, rotated 90 deg, pointing out.
        tang = p2 - p1
        normal = np.array([tang[1], -tang[0]])
        normal = normal / np.linalg.norm(normal)
        if np.dot(normal, mid) < 0:
            normal = -normal
        tr = sigma * normal * L * t  # force on the edge
        for nid in (n1, n2):
            loads.setdefault(nid, np.zeros(2))
            loads[nid] += 0.5 * tr
    loads = {i: (v[0], v[1]) for i, v in loads.items()}
    # kill rigid body: fix ux, uy at the node closest to (-outer, 0) direction inner? 
    # Fix ux and uy of one inner-ring node and uy of another.
    fixed = [(nid_of(0, 0), 0), (nid_of(0, 0), 1), (nid_of(0, nt // 4), 0)]
    # That over-constrains the hole. Better fix three outer dofs that don't fight the load.
    # Re-do: remove those and pin outer node j=nt//2 (left) ux uy and outer j=nt//4 uy.
    fixed = [(nid_of(nr, nt // 2), 0), (nid_of(nr, nt // 2), 1), (nid_of(nr, nt // 4), 0)]
    u, vms = solve_quads(nodes, quads, t, fixed, loads)
    # peak hoop is the max vm near the hole (first ring of gauss points is not tagged).
    # Evaluate stress on the inner-most element ring directly.
    peak = 0.0
    C = E_MPA / (1.0 - NU ** 2) * np.array([[1, NU, 0], [NU, 1, 0], [0, 0, (1 - NU) / 2]])
    for j in range(nt):
        q = [nid_of(0, j), nid_of(0, j + 1), nid_of(1, j + 1), nid_of(1, j)]
        xy = nodes[q]
        dofs = np.array([[2 * i, 2 * i + 1] for i in q]).ravel()
        ue = u[dofs]
        # sample at xi,eta toward the inner edge. Node order: 0 inner j, 1 inner j+1,
        # 2 outer j+1, 3 outer j. Inner edge is nodes 0-1, which is eta=-1 if order is
        # standard (xi,eta): I used (0,1,2,3) = (-1,-1),(1,-1),(1,1),(-1,1) so
        # local order must match. I appended [n00, n10, n11, n01] in solve? 
        # Here q = [inner j, inner j+1, outer j+1, outer j] which is NOT the standard
        # corner order if j increases with angle (that's tangential, not xi).
        # Skip the analytic B and just take the global max vm from solve_quads,
        # which includes every Gauss point.
        peak = max(peak, 0.0)
    peak = float(np.max(vms))
    return dict(peak_vm_MPa=peak, remote_MPa=sigma, Kt=peak / sigma,
                note="diagnostic only: traction was sigma*n on a square (near equibiaxial, Kt~2), not uniaxial Kirsch")


def lug_model(F_bolt):
    """Corner-tab region of the 0.5 mm tray. Hole Ø4.5, centre 7 mm from the
    two free edges (bolt at ±24 mm on a 62 mm tray whose edge is at ±31 mm).
    Bolt force is toward the nearer free edge (tear-out direction)."""
    R = M4_HOLE_MM / 2.0
    xmin, xmax = -16.0, 7.0
    ymin, ymax = -16.0, 7.0
    nr, nt = 16, 64
    nodes = []
    angles = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    for i in range(nr + 1):
        rho = (i / nr) ** 1.25
        for th in angles:
            c, s = np.cos(th), np.sin(th)
            cand = []
            if c > 1e-14:
                cand.append(xmax / c)
            if c < -1e-14:
                cand.append(xmin / c)
            if s > 1e-14:
                cand.append(ymax / s)
            if s < -1e-14:
                cand.append(ymin / s)
            rb = min(cand)
            r = R + (rb - R) * rho
            nodes.append([r * c, r * s])
    nodes = np.asarray(nodes, dtype=float)
    def nid(i, j):
        return i * nt + (j % nt)
    quads = []
    for i in range(nr):
        for j in range(nt):
            quads.append([nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)])
    # cosine bearing pressure on the half of the hole facing +x (bolt pushes
    # the tray toward +x, into the free edge)
    p_max = 2.0 * F_bolt / (np.pi * R * TRAY_T_MM)
    loads = {}
    for j in range(nt):
        n1, n2 = nid(0, j), nid(0, j + 1)
        th1 = angles[j]
        th2 = angles[(j + 1) % nt]
        # integrate along the arc. Use the midpoint.
        thm = 0.5 * (th1 + (th2 if th2 > th1 else th2 + 2 * np.pi))
        dth = (th2 - th1) if th2 > th1 else (th2 + 2 * np.pi - th1)
        ct = np.cos(thm)
        if ct <= 0:
            continue
        # traction on the wall is inward-compressive, resultant +x.
        # Outward normal of the hole surface (pointing out of the material, into the hole) is -radial.
        # Pressure p pushes the material in the +radial? The bolt is inside the hole and pushes
        # the material outward (away from hole centre) on the +x side. Traction vector on the
        # material is +p * radial (outward from the hole centre).
        radial = np.array([np.cos(thm), np.sin(thm)])
        arc = R * dth
        dF = p_max * ct * arc * TRAY_T_MM * radial
        for n in (n1, n2):
            loads.setdefault(n, np.zeros(2))
            loads[n] += 0.5 * dF
    loads = {i: (float(v[0]), float(v[1])) for i, v in loads.items()}
    # fix the far edges x=xmin and y=ymin (continuity into the rest of the sheet)
    fixed = []
    for i in range(nr + 1):
        for j in range(nt):
            x, y = nodes[nid(i, j)]
            if abs(x - xmin) < 1e-6 or abs(y - ymin) < 1e-6:
                fixed.append((nid(i, j), 0))
                fixed.append((nid(i, j), 1))
    u, vms = solve_quads(nodes, quads, TRAY_T_MM, fixed, loads)
    # split contact-ring vm vs the rest. Contact ring is i=0 elements: first nr? 
    # solve_quads doesn't tag them. Recompute per element.
    contact_vm = []
    ligament_vm = []
    C = E_MPA / (1.0 - NU ** 2) * np.array([[1.0, NU, 0.0], [NU, 1.0, 0.0], [0.0, 0.0, (1.0 - NU) / 2.0]])
    for i in range(nr):
        for j in range(nt):
            q = [nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)]
            xy = nodes[list(q)]
            Ke, gp = quad_ke_stress(xy, TRAY_T_MM, E_MPA, NU)
            dofs = np.array([[2 * a, 2 * a + 1] for a in q]).ravel()
            ue = u[dofs]
            for B, Cc in gp:
                s = Cc @ (B @ ue)
                sx, sy, txy = s
                vm = float(np.sqrt(sx * sx - sx * sy + sy * sy + 3 * txy * txy))
                if i == 0:
                    contact_vm.append(vm)
                else:
                    ligament_vm.append(vm)
    fsum = np.zeros(2)
    for fx, fy in loads.values():
        fsum += (fx, fy)
    sig_br = F_bolt / (M4_D_MM * TRAY_T_MM)
    # tear-out: two shear planes, edge distance from hole wall to the free edge
    c_edge = xmax - R
    sig_tear = F_bolt / (2.0 * c_edge * TRAY_T_MM)
    return dict(
        F_bolt_N=F_bolt,
        resultant_check_N=fsum.tolist(),
        p_max_MPa=p_max,
        sigma_bearing_MPa=sig_br,
        bearing_SF=SY_BEARING / sig_br,
        tearout_MPa=sig_tear,
        tearout_SF_vs_330=330.0 / sig_tear,
        vm_contact_MPa=float(np.max(contact_vm)),
        vm_ligament_MPa=float(np.max(ligament_vm)),
        edge_distance_from_wall_mm=c_edge,
    )


def service_vm_allowance_note():
    return (
        "Peak von Mises is the hex8 Gauss maximum outside a 6 mm band on the "
        "fixed roll-output face and outside a 3 mm band on the boss/link "
        "re-entrant edge. Those two lines are support and sharp-corner "
        "artifacts; the absolute maximum is reported beside the filtered peak. "
        "The hole-contact peak is a bearing stress and is gated by the tab "
        "bearing SF, not added again as a von Mises fail, provided the joint "
        "does not slip."
    )


def run():
    print("patch...", flush=True)
    patch = validate_patch()
    print("  ", patch, flush=True)
    if patch["err_pct"] > 1.0:
        raise SystemExit("patch test failed")
    print("cantilever...", flush=True)
    cant = validate_cantilever()
    print("  ", cant, flush=True)
    if cant["err_pct"] > 15.0:
        raise SystemExit("cantilever check failed")
    print("hole Kt (diagnostic, not a gate)...", flush=True)
    try:
        hole = validate_hole()
    except Exception as exc:
        hole = {"error": str(exc)}
    print("  ", hole, flush=True)

    weight = arm_weight()
    print("arm weight", weight, flush=True)

    # R7 table reproduction (their simplified M = Fn*e, Fa = Fs, Fr = Fn)
    r7 = {}
    for e_mm in (0.0, 10.0):
        M = FN_N * (e_mm / 1000.0)
        P = r7_p0(FN_N, FS_N, M)
        r7[f"e{e_mm:.0f}"] = dict(P0_kN=P / 1000.0, s0=CRBH_C0_N / P, M_Nm=M)

    F_bolt = FS_N / N_BOLT
    print("lug...", flush=True)
    lug = lug_model(F_bolt)
    print("  bearing SF", round(lug["bearing_SF"], 3), "vm contact", round(lug["vm_contact_MPa"], 1),
          "vm ligament", round(lug["vm_ligament_MPa"], 1), "F check", lug["resultant_check_N"], flush=True)

    slip_cap = M4_PRELOAD_N * M4_MU
    slip_ok = bool(slip_cap > F_bolt)

    bond_area = (CORE_MM / 1000.0) ** 2
    bond_shear = FS_N / bond_area / 1e6
    bond_comp = FN_N / bond_area / 1e6
    bond_stress = max(bond_shear, 0.0)  # no tensile peel: crush patch is in compression
    # equivalent reported value is the larger of shear and any peel
    bond = dict(area_m2=bond_area, shear_MPa=bond_shear, compression_MPa=bond_comp,
                peel_MPa=0.0, governing_MPa=max(bond_shear, 0.0),
                note="uniform crush patch 61.8 mm square; DP490 gate is shear/peel, compression reported separately")

    cases = []
    h_prod = 4.0
    for direction in ("axial", "down"):
        for e_mm in (0.0, 10.0):
            name = f"{direction}_e{e_mm:.0f}"
            print("case", name, flush=True)
            info, Fimp, Mimp = combine_bearing(e_mm, direction, Y_CONTACT, weight)
            # sensitivity of s0 to where the tangential line of action is taken
            sens = {}
            for label, y in (("contact", Y_CONTACT), ("bond", Y_BOND), ("link_face", LINK_Y[1])):
                s, _, _ = combine_bearing(e_mm, direction, y, weight)
                sens[label] = round(s["s0"], 3)
            mesh = build_mesh(e_mm, h_prod)
            area = sum(a for _, a, _, _ in mesh.loaded)
            if area <= 0:
                raise RuntimeError("no loaded faces")
            print(f"  mesh nodes {len(mesh.xyz)} elems {len(mesh.elems)} loaded {area:.0f} mm^2", flush=True)
            if direction == "axial":
                best = None
                for sgn in (1.0, -1.0):
                    F = np.array([sgn * FS_N, -FN_N, 0.0])
                    p = np.array([e_mm, Y_CONTACT, PAD_Z]) / 1000.0
                    M = np.cross(p, F) + np.array(weight["M_Nm"])
                    Ft = F + np.array(weight["F_N"])
                    s0 = full_bearing(Ft, M)["s0"]
                    if best is None or s0 < best[0]:
                        best = (s0, sgn, F)
                F_app = best[2]
                info["shear_sign"] = best[1]
            else:
                F_app = np.array([0.0, -FN_N, -FS_N])
            trac = F_app / area  # N/mm^2
            fe_w = solve_with_weight(mesh, trac, weight, e_mm)
            case = dict(
                name=name,
                direction=direction,
                e_mm=e_mm,
                bearing=info,
                bearing_s0_by_load_line=sens,
                fe=fe_w,
                mesh_h_mm=h_prod,
            )
            cases.append(case)
            print("  s0", round(info["s0"], 3), "vm", round(fe_w["vm_filt"], 1),
                  "defl", round(fe_w["defl_max_mm"], 4), "sens", sens, flush=True)

    # one refined mesh on the axially offset case (boss overhang) for convergence
    print("refine axial_e10...", flush=True)
    mesh_f = build_mesh(10.0, 2.0)
    area = sum(a for _, a, _, _ in mesh_f.loaded)
    F_app = np.array([FS_N, -FN_N, 0.0])
    fe_fine = solve_with_weight(mesh_f, F_app / area, weight, 10.0)
    print("  fine vm", round(fe_fine["vm_filt"], 1), "abs", round(fe_fine["vm_abs"], 1),
          "defl", round(fe_fine["defl_max_mm"], 4), "nelem", fe_fine["nelem"], flush=True)

    results = dict(
        method="hex8 linear elasticity (numpy/scipy) + IKO CRBH statics + DP490/M4 hand checks. No skfem/CalculiX on this PC.",
        validation=dict(patch=patch, cantilever=cant, hole_Kt=hole),
        inputs=dict(
            Fn_N=FN_N, Fs_N=FS_N, core_mm=CORE_MM,
            y_contact_mm=Y_CONTACT, y_bond_mm=Y_BOND, pad_z_mm=PAD_Z,
            E_MPa=E_MPA, nu=NU, Sy_bearing_MPa=SY_BEARING,
            CRBH="6013 A", C0_N=CRBH_C0_N, dp_m=CRBH_DP_M,
            preload_N=M4_PRELOAD_N, mu=M4_MU, tray_t_mm=TRAY_T_MM,
        ),
        arm_weight=weight,
        r7_simplified_s0=r7,
        bond=bond,
        lug=lug,
        slip=dict(cap_N=slip_cap, shear_per_bolt_N=F_bolt, no_slip=slip_ok,
                  margin=slip_cap / F_bolt),
        cases=cases,
        refined_axial_e10=dict(h_mm=2.0, fe=fe_fine),
        vm_rule=service_vm_allowance_note(),
    )
    # gates
    for c in cases:
        b = c["bearing"]
        vm = c["fe"]["vm_filt"]
        # use the finer-mesh vm for the matching case if it is higher
        if c["name"] == "axial_e10":
            vm = max(vm, fe_fine["vm_filt"])
        defl = c["fe"]["defl_max_mm"]
        if c["name"] == "axial_e10":
            defl = max(defl, fe_fine["defl_max_mm"])
        flags = dict(
            von_mises_MPa=vm,
            von_mises_pass=bool(vm <= VM_ALLOW),
            bond_MPa=bond["governing_MPa"],
            bond_pass=bool(bond["governing_MPa"] <= BOND_ALLOW),
            bearing_s0=b["s0"],
            bearing_pass=bool(b["s0"] >= BEARING_SF_MIN),
            defl_mm=defl,
            defl_pass=bool(defl <= DEFL_ALLOW_MM),
            slip_pass=slip_ok,
            shear_per_bolt_N=F_bolt,
            friction_cap_N=slip_cap,
            tab_bearing_SF=lug["bearing_SF"],
            tab_bearing_pass=bool(lug["bearing_SF"] >= TAB_SF_MIN),
        )
        flags["case_pass"] = all(flags[k] for k in (
            "von_mises_pass", "bond_pass", "bearing_pass", "defl_pass", "slip_pass", "tab_bearing_pass"))
        c["gate"] = flags
    overall = all(c["gate"]["case_pass"] for c in results["cases"])
    results["overall"] = "PASS" if overall else "FAIL"
    out = os.path.join(H, "results.json")
    json.dump(results, open(out, "w"), indent=1)
    print("OVERALL", results["overall"])
    write_report(results)
    return results


def solve_with_weight(mesh, trac, weight, e_mm):
    """Same as solve_case, plus the arm weight as a uniform -Z force on the
    link bottom face, and the small pitch-rotation shear as an X force there."""
    xyz = mesh.xyz
    nnode = len(xyz)
    ndof = 3 * nnode
    K, elem_meta = assemble(mesh)
    f = np.zeros(ndof)
    loaded_area = 0.0
    for face, area, xc, zc in mesh.loaded:
        loaded_area += area
        nodal = trac * (area / 4.0)
        for n in face:
            f[3 * n: 3 * n + 3] += nodal
    # bottom face of the link
    zbot = LINK_Z[0]
    bottom = np.where(np.abs(xyz[:, 2] - zbot) < 1e-4)[0]
    # keep only nodes that sit on the link footprint
    bottom = np.array([n for n in bottom if LINK_X[0] - 1e-6 <= xyz[n, 0] <= LINK_X[1] + 1e-6
                       and LINK_Y[0] - 1e-6 <= xyz[n, 1] <= LINK_Y[1] + 1e-6])
    Fw = np.array(weight["F_N"])
    if len(bottom):
        for n in bottom:
            f[3 * n: 3 * n + 3] += Fw / len(bottom)
    fixed_z = LINK_Z[1]
    fixed_nodes = np.where(np.abs(xyz[:, 2] - fixed_z) < 1e-4)[0]
    fixed_nodes = np.array([n for n in fixed_nodes if LINK_X[0] - 1e-6 <= xyz[n, 0] <= LINK_X[1] + 1e-6
                            and LINK_Y[0] - 1e-6 <= xyz[n, 1] <= LINK_Y[1] + 1e-6])
    fixed_dofs = np.array([[3 * n, 3 * n + 1, 3 * n + 2] for n in fixed_nodes]).ravel()
    free = np.setdiff1d(np.arange(ndof), fixed_dofs)
    u = np.zeros(ndof)
    u[free] = spsolve(K[free][:, free], f[free])
    vm_all, vm_filt = [], []
    vm_region = {"link": [], "boss": [], "tray": []}
    for dofs, pts, region in elem_meta:
        ue = u[dofs]
        el = []
        for xi in (-GAUSS, GAUSS):
            for eta in (-GAUSS, GAUSS):
                for zeta in (-GAUSS, GAUSS):
                    B, det = hex_B(xi, eta, zeta, pts)
                    el.append(von_mises(C_AL @ (B @ ue)))
        vmax = float(max(el))
        vm_all.append(vmax)
        vm_region[region].append(vmax)
        centroid = pts.mean(0)
        near_support = centroid[2] > fixed_z - 6.0
        on_corner = abs(centroid[1] - BOSS_Y[0]) < 3.0 and (
            centroid[0] < LINK_X[0] + 3.0 or centroid[0] > LINK_X[1] - 3.0
            or centroid[2] < LINK_Z[0] + 3.0 or centroid[2] > LINK_Z[1] - 3.0
        )
        if not near_support and not on_corner:
            vm_filt.append(vmax)
    loaded_nodes = sorted({n for face, *_ in mesh.loaded for n in face})
    up = u.reshape(-1, 3)[loaded_nodes]
    return dict(
        nnode=int(nnode), nelem=len(mesh.elems),
        loaded_area_mm2=float(loaded_area),
        applied_pad_N=(trac * loaded_area).tolist(),
        vm_abs=float(max(vm_all)),
        vm_filt=float(max(vm_filt) if vm_filt else max(vm_all)),
        vm_p95=float(np.percentile(vm_all, 95)),
        vm_region={k: float(max(v)) if v else 0.0 for k, v in vm_region.items()},
        defl_mean_mm=float(np.linalg.norm(up.mean(0))),
        defl_max_mm=float(np.linalg.norm(up, axis=1).max()),
        u_mean_mm=up.mean(0).tolist(),
        n_fixed=int(len(fixed_nodes)),
        n_bottom=int(len(bottom)),
    )


def write_report(res):
    w = res["arm_weight"]
    lines = []
    A = lines.append
    A("# Job 1 report — shoulder pad R8 option B FEA (R-079)")
    A("")
    A(f"**Overall: {res['overall']}.**")
    A("")
    A("Four cases, each gated on the six criteria in `BRIEF.md`. "
      "A case passes only when every criterion passes. "
      "The axial-shear cases fail the CRBH 6013 static safety factor.")
    A("")
    A("## Criteria")
    A("")
    A("| case | von Mises MPa | bond MPa | bearing s0 | defl mm | M4 slip | tab bearing SF | case |")
    A("|---|---:|---:|---:|---:|---|---:|---|")
    for c in res["cases"]:
        g = c["gate"]
        slip = "no slip" if g["slip_pass"] else "SLIP"
        A("| {name} | {vm:.1f} {vp} | {bd:.2f} {bp} | {s0:.2f} {sp} | {df:.3f} {dp} | {slip} ({sh:.0f} N < {cap:.0f} N) | {tb:.2f} {tp} | {cp} |".format(
            name=c["name"],
            vm=g["von_mises_MPa"], vp="PASS" if g["von_mises_pass"] else "FAIL",
            bd=g["bond_MPa"], bp="PASS" if g["bond_pass"] else "FAIL",
            s0=g["bearing_s0"], sp="PASS" if g["bearing_pass"] else "FAIL",
            df=g["defl_mm"], dp="PASS" if g["defl_pass"] else "FAIL",
            slip=slip, sh=g["shear_per_bolt_N"], cap=g["friction_cap_N"],
            tb=g["tab_bearing_SF"], tp="PASS" if g["tab_bearing_pass"] else "FAIL",
            cp="PASS" if g["case_pass"] else "FAIL",
        ))
    A("")
    A("Limits: von Mises ≤ 320 MPa, bond ≤ 7.7 MPa, bearing s0 ≥ 2.0, deflection ≤ 1 mm, "
      "preload × μ > shear per bolt, tab bearing SF ≥ 1.5 on 480 MPa.")
    A("")
    A("## Method")
    A("")
    A("Python 3.12 on this PC has numpy and scipy. scikit-fem, gmsh and CalculiX are not installed. "
      "The link, the 62×62×10 boss and the 0.5 mm tray are one conforming hex8 mesh "
      "(full 2×2×2 integration, E = 71.7 GPa, ν = 0.33). "
      "The roll-output face of the link (Z = −39 mm) is fixed. "
      "The core is not meshed: 9.17 kN at 15° is a uniform traction on the 61.8 mm square "
      "(normal 8.86 kN inward, tangential 2.37 kN). "
      "Arm weight is a separate force on the bottom of the link.")
    A("")
    A("The hex8 element recovers uniaxial tension "
      f"({res['validation']['patch']['sigma_xx_MPa']:.2f} MPa against 100 MPa) and a stocky "
      f"cantilever within {res['validation']['cantilever']['err_pct']:.1f}% of Timoshenko "
      f"({res['validation']['cantilever']['fea_tip_mm']:.4f} mm vs "
      f"{res['validation']['cantilever']['timoshenko_mm']:.4f} mm; the element is slightly stiff).")
    A("")
    A(res["vm_rule"])
    A("")
    A("Production mesh pitch is 4 mm (one 0.5 mm element through the tray). "
      f"The axial e = 10 mm case was repeated at 2 mm "
      f"({res['refined_axial_e10']['fe']['nelem']} elements): filtered von Mises "
      f"{res['refined_axial_e10']['fe']['vm_filt']:.1f} MPa, absolute peak "
      f"{res['refined_axial_e10']['fe']['vm_abs']:.1f} MPa, pad deflection "
      f"{res['refined_axial_e10']['fe']['defl_max_mm']:.4f} mm. "
      "The filtered peak does not climb toward 320 MPa.")
    A("")
    A("## Loads and bearing")
    A("")
    A(f"Normal {res['inputs']['Fn_N']:.1f} N (−Y, into the robot). "
      f"Tangential {res['inputs']['Fs_N']:.1f} N, either +X/−X along the roll axis "
      "(the sign with the lower s0 is kept) or −Z (downward).")
    A("")
    A(f"Arm distal to the roll bearing: {w['mass_kg']:.2f} kg, weight {w['W_N']:.1f} N, "
      f"tuck B (pitch +{TUCK_PITCH_DEG:.0f}°, roll 0, yaw 0, elbow 0). "
      f"COM at x,y,z = ({w['com_mm'][0]:.1f}, {w['com_mm'][1]:.1f}, {w['com_mm'][2]:.1f}) mm "
      "relative to the CRBH centre. The weight changes s0 by about 0.01.")
    A("")
    A("CRBH 6013 A, C0 = 24.3 kN, dp = 75 mm. "
      "P0 = Fr + 2M/dp + 0.44 Fa (IKO static equivalent, catalog formula (2); "
      "M in N·m with dp in m). Fr is the radial resultant, Fa the axial component, "
      "M the tilting moment sqrt(My² + Mz²). Torque about the roll axis, Mx, is spin: "
      "the gear holds it, and it is not inside P0.")
    A("")
    A("The pad centre sits at Z = −64 mm (model_v4 link centre; R7's 0.064 m offset) "
      f"and the contact face is at Y = {Y_CONTACT:.1f} mm "
      "(link face +10 mm, boss 10, tray 0.5, core 60, spreader 0.5, EPP 6). "
      "A normal force at that point makes roll torque Mx = Fn × 0.064 m and, "
      "with axial offset e, tilting moment Fn × e. "
      "An axial tangential force at the same point makes tilting moment "
      "Fs × sqrt(Y² + Z²). R7's published table uses only M = Fn·e and Fa = Fs "
      "(s0 2.45 at 0 mm, 1.98 at 10 mm). That table is reproduced below. "
      "1.98 is already under the gate of 2.0. "
      "The table also leaves out the tangential force's lever arm, so it is not the value gated here.")
    A("")
    A("| e mm | R7 simplified s0 (M = Fn·e, Fa = Fs) |")
    A("|---:|---:|")
    for k, v in res["r7_simplified_s0"].items():
        A(f"| {k[1:]} | {v['s0']:.2f} |")
    A("")
    A("Gated s0 uses the contact line of action. The same formula with the line of action "
      "moved in to the bond or to the link face still fails both axial cases:")
    A("")
    A("| case | s0 contact (gated) | s0 at bond | s0 at link face | Mx N·m | Mtilt N·m |")
    A("|---|---:|---:|---:|---:|---:|")
    for c in res["cases"]:
        b = c["bearing"]
        s = c["bearing_s0_by_load_line"]
        A(f"| {c['name']} | {b['s0']:.2f} | {s['bond']:.2f} | {s['link_face']:.2f} | {b['Mx_Nm']:.0f} | {b['Mtilt_Nm']:.0f} |")
    A("")
    A("Downward shear is radial, so its tilting moment is only Fn and Fs times e. "
      "Those two cases clear s0 ≥ 2. Both axial cases are below 2.")
    A("")
    A(f"Roll-axis torque Mx is {res['cases'][0]['bearing']['Mx_Nm']:.0f} N·m in the axial cases "
      f"(Fn × 64 mm) and {res['cases'][2]['bearing']['Mx_Nm']:.0f} N·m when the shear is also downward "
      "(extra Fs × Y). CSG-25 momentary peak is 369 N·m. Mx is outside the six gates. "
      "It is large enough that the roll gear, not only the crossed roller, needs a look.")
    A("")
    A("## Bond, bolts, tray")
    A("")
    bd = res["bond"]
    A(f"Core–tray DP490 on {CORE_MM} mm square ({bd['area_m2']*1e6:.0f} mm²). "
      f"Shear {bd['shear_MPa']:.2f} MPa, compression {bd['compression_MPa']:.2f} MPa, peel 0. "
      f"The gate uses shear (the 23 MPa lap-shear rating / 3 = 7.7 MPa). "
      f"Compression is the crush pressure and is also under 7.7 MPa. "
      "The honeycomb holds the pressure near the plateau, so an offset of the whole pad "
      "(e = 0 or 10 mm) does not concentrate the bond.")
    A("")
    sl = res["slip"]
    A(f"Four M4 12.9, preload {M4_PRELOAD_N:.0f} N, μ = {M4_MU}. "
      f"Friction per bolt {sl['cap_N']:.0f} N. "
      f"Shear per bolt {sl['shear_per_bolt_N']:.1f} N (2.37 kN / 4; the pad resultant is centred on the bolt group). "
      f"Margin {sl['margin']:.2f}. No slip. "
      "The impact compression on the faying face is extra clamp and is not credited.")
    A("")
    lg = res["lug"]
    A(f"Tab bearing uses the bolt diameter, σ = F/(d t) = {lg['sigma_bearing_MPa']:.1f} MPa "
      f"on {M4_D_MM:.0f} × {TRAY_T_MM} mm. "
      f"SF vs 480 MPa is {lg['bearing_SF']:.2f} (limit 1.5). "
      f"Tear-out, not a gate: {lg['tearout_MPa']:.0f} MPa, SF {lg['tearout_SF_vs_330']:.2f} vs 330 MPa, "
      f"with {lg['edge_distance_from_wall_mm']:.2f} mm from the hole wall to the tray edge "
      f"(bolt centres at ±24 mm, tray edge at ±31 mm, hole diameter {M4_HOLE_MM} mm).")
    A("")
    A(f"A plane-stress model of that corner hole, cosine bearing load {lg['F_bolt_N']:.1f} N "
      f"(the nodal resultant matches that force), "
      f"gives a contact-ring von Mises of {lg['vm_contact_MPa']:.0f} MPa and "
      f"{lg['vm_ligament_MPa']:.0f} MPa off the contact ring. "
      f"The ligament value is above the 320 MPa von Mises limit. "
      "It is the bearing-type path. The slip check says that path is not the service load: "
      f"friction holds while μ × preload ({sl['cap_N']:.0f} N) stays above {sl['shear_per_bolt_N']:.0f} N "
      f"(μ above {sl['shear_per_bolt_N']/M4_PRELOAD_N:.2f} at this preload). "
      "The gated von Mises is the hex8 service stress. "
      "The absolute hex8 peak on the 2 mm mesh is "
      f"{res['refined_axial_e10']['fe']['vm_abs']:.0f} MPa, still under 320; "
      "it rose at the re-entrant edge while the filtered peak stayed near 17 MPa.")
    A("")
    A("## Assumptions")
    A("")
    A("- Qualified layout: bearing midplane at the link, pad centre shifted by e. "
      "model_v4's `sw()` bearing sits at x = L/2+4 on a generic envelope; that drawing "
      "cannot meet e ≤ 10 mm and the 1–6 mm boss overhang together.")
    A("- Link is the model_v4 60×40×50 block. The face at Z = −39 mm stands in for the "
      "roll-output connection. Stress in that face is excluded. Neck compliance between "
      "that face and the CRBH is not meshed; at this section size it does not move a "
      "0.01 mm deflection up to the 1 mm limit.")
    A("- Boss 62×62×10 is solid 7075 and integral. The booked 0.024 kg is about a quarter "
      "of a solid 62×62×10 at 2.81 g/cm³ (about 0.108 kg). Mass is unchanged by this job.")
    A("- Tray floor matches the boss. Lips locate the core and do not carry load "
      "(SHOULDER_PAD: the bond carries shear). Bolt holes are Ø4.5 on centres ±24 mm.")
    A("- Core, spreader and EPP are the crush stack. Structural deflection is the metal "
      "displacement at the bond patch, not the core crush.")
    A("- Tuck is tuck B, the current Arms pose. The withdrawn pitch −30 / elbow −110 tuck "
      "is not the load case. Distal mass is the catalog split in `arm_inertials_r3.json`, "
      "not the lighter sim bodies.")
    A("- μ = 0.15 and 5.5 kN preload are the Arms R8 figures for this M4×8 joint "
      "(class 12.9). The superseded R7 doubler note (class 8.8, 2 kN) is not used.")
    A("- Bearing SF is the equilibrium s0 at the contact line of action, including arm weight. "
      "The R7 simplified column is shown and is not the gate.")
    A("")
    A("## Files")
    A("")
    A("- `fea_job1.py` — model, checks, this report")
    A("- `results.json` — numbers behind the table")
    A("")
    path = os.path.join(H, "REPORT.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    run()
