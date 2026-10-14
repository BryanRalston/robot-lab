"""Plane-strain press fit of the 16MnCr5 shaft in the 7075 tongue.

Ø35/Ø30 shaft, 0.141 mm diametral interference, friction μ = 0.15.
The 2D slice checks hoop, contact pressure, gapping under a needle line load,
and the tangential micro-slip. The tilting moment is axial and is reported from
the 3D tongue solve, not from this slice.
+60 K drops the diametral interference by 0.0254 mm.
"""
import os, sys, json
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F

E_S, NU_S = 210000.0, 0.30
MU = 0.15
DIAM = 0.141          # mm, structure_r5
D_HOT = 0.0254        # mm diametral lost at +60 K
R_SHAFT_NOM = 17.5
R_BORE = 15.0
R_HUB = 27.5


def C_plane(E, nu):
    a = E * (1 - nu) / ((1 + nu) * (1 - 2 * nu))
    b = E * nu / ((1 + nu) * (1 - 2 * nu))
    c = E / (2 * (1 + nu))
    return np.array([[a, b, 0.0], [b, a, 0.0], [0.0, 0.0, c]])


def mesh(nth, n_sh, n_hub, delta_rad):
    """Shaft r = 15 .. 17.5+δ, hub r = 17.5 .. 27.5. Separate interface nodes."""
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    r_s = np.linspace(R_BORE, R_SHAFT_NOM + delta_rad, n_sh + 1)
    r_h = np.linspace(R_SHAFT_NOM, R_HUB, n_hub + 1)
    # node blocks: shaft (n_sh+1)*nth, then hub (n_hub+1)*nth
    ns = (n_sh + 1) * nth
    nodes = []
    for r in r_s:
        for t in th:
            nodes.append((r * np.cos(t), r * np.sin(t)))
    for r in r_h:
        for t in th:
            nodes.append((r * np.cos(t), r * np.sin(t)))
    nodes = np.array(nodes)
    quads, mat = [], []

    def qid(block, ir, ith):
        return block + ir * nth + (ith % nth)

    for ir in range(n_sh):
        for ith in range(nth):
            quads.append([qid(0, ir, ith), qid(0, ir, ith + 1), qid(0, ir + 1, ith + 1), qid(0, ir + 1, ith)])
            mat.append(0)
    base = ns
    for ir in range(n_hub):
        for ith in range(nth):
            quads.append([qid(base, ir, ith), qid(base, ir, ith + 1), qid(base, ir + 1, ith + 1), qid(base, ir + 1, ith)])
            mat.append(1)
    # contact pairs (shaft outer, hub inner) at the same angle. Initial gap is -δ.
    pairs = [(qid(0, n_sh, ith), qid(base, 0, ith)) for ith in range(nth)]
    return nodes, np.array(quads), np.array(mat), pairs, th


def shape_grad(xy, xi, eta):
    xs = np.array([-1.0, 1.0, 1.0, -1.0])
    es = np.array([-1.0, -1.0, 1.0, 1.0])
    dxi = 0.25 * xs * (1 + es * eta)
    deta = 0.25 * es * (1 + xs * xi)
    J = np.vstack((dxi, deta)) @ xy
    det = float(np.linalg.det(J))
    dN = np.linalg.inv(J) @ np.vstack((dxi, deta))
    return dN, det


def assemble(nodes, quads, mat):
    nd = 2 * len(nodes)
    K = lil_matrix((nd, nd))
    Cs = (C_plane(E_S, NU_S), C_plane(F.E_AL, F.NU_AL))
    G = 1.0 / np.sqrt(3.0)
    gps = ((-G, -G), (G, -G), (G, G), (-G, G))
    for e, q in enumerate(quads):
        xy = nodes[q]
        ke = np.zeros((8, 8))
        C = Cs[int(mat[e])]
        for xi, eta in gps:
            dN, det = shape_grad(xy, xi, eta)
            B = np.zeros((3, 8))
            for k in range(4):
                B[0, 2 * k] = dN[0, k]
                B[1, 2 * k + 1] = dN[1, k]
                B[2, 2 * k] = dN[1, k]
                B[2, 2 * k + 1] = dN[0, k]
            ke += (B.T @ C @ B) * det
        dof = np.array([2 * n + c for n in q for c in (0, 1)])
        K[np.ix_(dof, dof)] += ke
    return csr_matrix(K)


def solve_case(delta_rad, F_line, tag, nth=72, n_sh=4, n_hub=6, kn=2.0e5, kt=2.0e5):
    """F_line is the resultant radial force per mm of shaft length, along +y. 0 = pure interference."""
    nodes, quads, mat, pairs, th = mesh(nth, n_sh, n_hub, delta_rad)
    K = assemble(nodes, quads, mat)
    # kill rigid body: pin shaft-bore node 0 in x and y, and one more in x (θ = 90°)
    fixed = [0, 1, 2 * (nth // 4)]
    nd = K.shape[0]
    dθ = 2 * np.pi / nth
    arc = (R_SHAFT_NOM + 0.5 * delta_rad) * dθ
    # cosine traction on the shaft bore, resultant F_line along +y
    f_ext = np.zeros(nd)
    if abs(F_line) > 0:
        # p = p0 cos(φ), φ from +y, resultant ∫ p cos φ * R dφ = p0 * R * π
        p0 = F_line / (np.pi * R_BORE)
        for ith, t in enumerate(th):
            # bore node ir=0
            n = ith
            # traction = -p0 cos(φ) * e_r with φ measured so +y is the loaded side
            cy, sy = np.cos(t), np.sin(t)
            # φ=0 at +y: cos φ = sin(t) if t from +x? t=π/2 is +y, sin(t)=1. Use sin(t).
            pr = p0 * np.sin(t)
            f_ext[2 * n] += -pr * cy * (R_BORE * dθ) * 0.0  # replaced below
            # inward cosine: the load pushes the bore wall toward +y, so traction on the
            # metal is in the +y direction, distributed as cos about +y.
        # rebuild cleanly
        f_ext[:] = 0.0
        for ith, t in enumerate(th):
            cφ = np.sin(t)  # +1 at +y
            if cφ <= 0:
                continue
            er = np.array([np.cos(t), np.sin(t)])
            tr = p0 * cφ * er   # into the metal? the bore pressure from a roller above pushes down
            # resultant should be +y. er at +y is +y, so +p*er gives +y. Good.
            f_ext[2 * ith:2 * ith + 2] += tr * (R_BORE * dθ)
    free = np.setdiff1d(np.arange(nd), fixed)
    # One bonded penalty solve. The spring closes the initial overlap; contact pressure
    # is the hub bore radial stress, which stays finite as the penalty gets stiffer.
    g0 = -delta_rad
    Kc = K.tolil()
    f = f_ext.copy()
    for ia, ib_ in pairs:
        er = nodes[ib_] / np.linalg.norm(nodes[ib_])
        et = np.array([-er[1], er[0]])
        k = kn * arc
        kt_ = kt * arc
        for nA, sA in ((ia, -1.0), (ib_, 1.0)):
            for nB, sB in ((ia, -1.0), (ib_, 1.0)):
                Kc[2 * nA:2 * nA + 2, 2 * nB:2 * nB + 2] += (k * sA * sB) * np.outer(er, er)
                Kc[2 * nA:2 * nA + 2, 2 * nB:2 * nB + 2] += (kt_ * sA * sB) * np.outer(et, et)
        f[2 * ia:2 * ia + 2] += k * g0 * er
        f[2 * ib_:2 * ib_ + 2] += -k * g0 * er
    u = np.zeros(nd)
    u[free] = spsolve(csr_matrix(Kc)[free][:, free], f[free])
    Cs = (C_plane(E_S, NU_S), C_plane(F.E_AL, F.NU_AL))
    hoop, prad = [], []
    for e, q in enumerate(quads):
        if mat[e] != 1:
            continue
        xy = nodes[q]
        rc = xy.mean(0)
        if np.linalg.norm(rc) > R_SHAFT_NOM + 1.2:
            continue
        dN, det = shape_grad(xy, 0.0, 0.0)
        ue = np.concatenate([u[2 * n:2 * n + 2] for n in q])
        B = np.zeros((3, 8))
        for k in range(4):
            B[0, 2 * k] = dN[0, k]
            B[1, 2 * k + 1] = dN[1, k]
            B[2, 2 * k] = dN[1, k]
            B[2, 2 * k + 1] = dN[0, k]
        sig = Cs[1] @ (B @ ue)
        er = rc / np.linalg.norm(rc)
        et = np.array([-er[1], er[0]])
        S = np.array([[sig[0], sig[2]], [sig[2], sig[1]]])
        hoop.append(float(et @ S @ et))
        prad.append(float(-er @ S @ er))
    hoop, prad = np.array(hoop), np.array(prad)
    slips = []
    for ia, ib_ in pairs:
        er = nodes[ib_] / np.linalg.norm(nodes[ib_])
        et = np.array([-er[1], er[0]])
        da = u[2 * ia:2 * ia + 2]
        db = u[2 * ib_:2 * ib_ + 2]
        slips.append(float((db - da) @ et))
    slips = np.array(slips)
    # gross slip where the bonded shear |kt * slip| exceeds μ p. p is the bore radial stress
    # sampled at the same angle (prad is one value per sector, same order as pairs for a structured mesh).
    p_at = prad if len(prad) == len(pairs) else np.full(len(pairs), float(np.median(prad)))
    tau = kt * slips
    rec = dict(
        tag=tag, delta_rad_mm=delta_rad, F_line_N_per_mm=F_line,
        p_median_MPa=float(np.median(prad)), p_min_MPa=float(prad.min()), p_max_MPa=float(prad.max()),
        hoop_bore_median_MPa=float(np.median(hoop)), hoop_bore_max_MPa=float(hoop.max()),
        slip_peak_mm=float(np.max(np.abs(slips))),
        slip_p95_mm=float(np.percentile(np.abs(slips), 95)),
        n_open=int(np.sum(prad <= 0.0)), n_pairs=len(pairs),
        n_gross_slip=int(np.sum(np.abs(tau) > MU * np.maximum(p_at, 0.0))),
        hand_p_MPa=60.0 * (delta_rad / (DIAM / 2)),
        hand_hoop_MPa=141.7 * (delta_rad / (DIAM / 2)),
        note='Bonded penalty, one solve. p is -σ_rr at the hub bore. A non-positive p is lift-off; the bonded shear is then not a friction solution.',
    )
    rec['gapped'] = bool(rec['p_min_MPa'] <= 0.0)
    print(tag, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items() if k != 'pressure_history'}, flush=True)
    return rec


def main():
    d0 = DIAM / 2
    d_hot = d0 - D_HOT / 2
    # needle line load: 9.1 kN over a 10 mm axial patch → 910 N/mm. Also the mean 10.06 kN / 27 mm.
    out = {
        'interference': solve_case(d0, 0.0, 'interference_60'),
        'hot_60K': solve_case(d_hot, 0.0, 'hot_plus60K'),
        'needle_9kN': solve_case(d0, 9100.0 / 10.0, 'needle_910N_per_mm'),
        'needle_hot': solve_case(d_hot, 9100.0 / 10.0, 'needle_hot'),
        'mean_10kN': solve_case(d0, 10063.0 / 27.0, 'mean_373N_per_mm'),
    }
    # gates: pure interference pressure within 15% of 60, hoop within 20% of 142
    p = out['interference']['p_median_MPa']
    h = out['interference']['hoop_bore_median_MPa']
    if not (50 < p < 70) or not (110 < h < 175):
        raise SystemExit('press-fit verification failed p=%.2f hoop=%.2f' % (p, h))
    F.save('fea_press', out)
    print('PRESS_PASS', flush=True)


if __name__ == '__main__':
    main()
