"""C3D27 (triquadratic hex) tube checks: cantilever verification, section stress, dent, axial buckling.

One element through the 1.2 mm wall. Mid-side nodes are projected back onto the true radii.
Units mm, N, MPa. 7075-T6. The weighed tubes stay the M2 lengths; the mesh is a prismatic stub
long enough for Saint-Venant decay and for several buckle half-waves.
"""
import os, sys, json, gc
import numpy as np
from skfem import MeshHex1, MeshHex2, Basis, ElementVector, ElementHex2, asm, FacetBasis, LinearForm, BilinearForm
from skfem.models.elasticity import linear_elasticity, lame_parameters
import pyamg
from scipy.sparse.linalg import eigsh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F

G_MASS = 9.81
MASS = 66.5
BW3, FALL = 3 * MASS * G_MASS, 6 * MASS * G_MASS


def _lut():
    # reference (x,y,z) = (i, j, k) in {0,1}^3 → local corner index of MeshHex1
    return {(0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 2, (1, 0, 0): 3,
            (0, 1, 1): 4, (1, 0, 1): 5, (1, 1, 0): 6, (1, 1, 1): 7}


LUT = _lut()


def box_mesh(L, W, H, nx, ny, nz):
    """Box [0,L] x [-W/2,W/2] x [-H/2,H/2]. x along the beam, z vertical."""
    xs = np.linspace(0, L, nx + 1)
    ys = np.linspace(-W / 2, W / 2, ny + 1)
    zs = np.linspace(-H / 2, H / 2, nz + 1)
    nx_, ny_, nz_ = nx, ny, nz

    def nid(i, j, k):
        return (k * (ny_ + 1) + j) * (nx_ + 1) + i

    p = np.zeros((3, (nx + 1) * (ny + 1) * (nz + 1)))
    for k, z in enumerate(zs):
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                p[:, nid(i, j, k)] = (x, y, z)
    t = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                conn = [0] * 8
                for (a, b, c), loc in LUT.items():
                    # reference x=i (beam), y=j (width), z=k (height)
                    conn[loc] = nid(i + a, j + b, k + c)
                t.append(conn)
    m1 = MeshHex1(p, np.array(t, dtype=np.int32).T)
    return MeshHex2.from_mesh(m1)


def tube_mesh(Rin, Rout, L, ntheta, nz):
    """Tube axis z, one quadratic element through the wall. θ is periodic."""
    th = np.linspace(0, 2 * np.pi, ntheta, endpoint=False)
    zs = np.linspace(0, L, nz + 1)
    rs = (Rin, Rout)

    def nid(ith, iz, ir):
        return (iz * 2 + ir) * ntheta + (ith % ntheta)

    p = np.zeros((3, ntheta * (nz + 1) * 2))
    for iz, z in enumerate(zs):
        for ir, r in enumerate(rs):
            for ith, t in enumerate(th):
                p[:, nid(ith, iz, ir)] = (r * np.cos(t), r * np.sin(t), z)
    t = []
    for iz in range(nz):
        for ith in range(ntheta):
            conn = [0] * 8
            for (a, b, c), loc in LUT.items():
                # reference x = θ, y = z, z = r
                conn[loc] = nid(ith + a, iz + b, c)
            t.append(conn)
    m = MeshHex2.from_mesh(MeshHex1(p, np.array(t, dtype=np.int32).T))
    Rmid = 0.5 * (Rin + Rout)
    rr = np.hypot(m.p[0], m.p[1])
    ang = np.arctan2(m.p[1], m.p[0])
    inner = rr < 0.5 * (Rin + Rmid)
    outer = rr > 0.5 * (Rout + Rmid)
    rr = rr.copy()
    rr[inner] = Rin
    rr[outer] = Rout
    m.p[0] = rr * np.cos(ang)
    m.p[1] = rr * np.sin(ang)
    return m


def _solve(K, f, D, tol=1e-8):
    I = np.setdiff1d(np.arange(K.shape[0]), D)
    Kc = K[I][:, I].tocsr()
    ml = pyamg.smoothed_aggregation_solver(Kc, max_coarse=400, keep=False, smooth=('jacobi', {}))
    res = []
    x = ml.solve(f[I], tol=tol, accel='cg', maxiter=4000, residuals=res)
    u = np.zeros(f.shape[0])
    u[I] = x
    rel = float(res[-1] / res[0]) if res and res[0] else 1.0
    return u, len(res), rel < 1e-6


def _end_load(m, ib, z_sel, tz_of_yz):
    """Axial traction tz(y, x) on a z=const face, binned so the resultant can be checked."""
    fac = m.facets_satisfying(z_sel, boundaries_only=True)
    if len(fac) == 0:
        raise RuntimeError('end face matched nothing')
    fp = m.p[:, m.facets[:, fac]].mean(1)
    # 8 bins in y, 4 in x is enough for a linear field
    yb = np.linspace(fp[1].min() - 1e-6, fp[1].max() + 1e-6, 9)
    xb = np.linspace(fp[0].min() - 1e-6, fp[0].max() + 1e-6, 5)
    f = np.zeros(ib.N)
    area = 0.0
    for i in range(8):
        for j in range(4):
            sel = fac[(fp[1] >= yb[i]) & (fp[1] < yb[i + 1]) & (fp[0] >= xb[j]) & (fp[0] < xb[j + 1])]
            if len(sel) == 0:
                continue
            yc = 0.5 * (yb[i] + yb[i + 1])
            xc = 0.5 * (xb[j] + xb[j + 1])
            fb = FacetBasis(m, ib.elem, facets=sel)
            a = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
            tz = float(tz_of_yz(yc, xc))
            vv = np.array([0.0, 0.0, tz])
            f += asm(LinearForm(lambda v, w, vv=vv: v[0] * vv[0] + v[1] * vv[1] + v[2] * vv[2]), fb)
            area += a
    return f, area


def vm_of(m, ib, u):
    lam, mu = lame_parameters(F.E_AL, F.NU_AL)
    b = Basis(m, ib.elem, intorder=4)
    g = b.interpolate(u).grad
    eps = 0.5 * (g + np.transpose(g, (1, 0, 2, 3)))
    tr = np.einsum('iiek->ek', eps)
    sig = 2 * mu * eps + lam * np.einsum('ij,ek->ijek', np.eye(3), tr)
    v = np.sqrt(0.5 * ((sig[0, 0] - sig[1, 1]) ** 2 + (sig[1, 1] - sig[2, 2]) ** 2
                       + (sig[2, 2] - sig[0, 0]) ** 2) + 3 * (sig[0, 1] ** 2 + sig[1, 2] ** 2 + sig[0, 2] ** 2))
    return v.max(1), sig.mean(-1)


def cantilever():
    """100 x 10 x 10 beam, tip shear 100 N in -z. Bending + 6/5 shear."""
    L, W, H, P = 100.0, 10.0, 10.0, 100.0
    m = box_mesh(L, W, H, 16, 2, 2)
    e = ElementVector(ElementHex2())
    # intorder 2 under-integrates the 27-node hex (beam came out 27% stiff). 4 is exact here.
    ib = Basis(m, e, intorder=4)
    lam, mu = lame_parameters(F.E_AL, F.NU_AL)
    K = asm(linear_elasticity(lam, mu), ib)
    fix = ib.get_dofs(m.facets_satisfying(lambda x: x[0] < 0.2, boundaries_only=True)).all()
    f, area, _ = F.facet_load(m, ib, lambda x: x[0] > L - 0.3, [0, 0, -P])
    u, iters, ok = _solve(K, f, fix)
    zdof = ib.nodal_dofs[2]
    tip_uz = u[zdof][ib.doflocs[0, zdof] > L - 0.3]
    dz = float(np.mean(tip_uz))
    I = W * H ** 3 / 12.0
    Gsh = F.E_AL / (2 * (1 + F.NU_AL))
    d_bend = P * L ** 3 / (3 * F.E_AL * I)
    d_shear = 1.2 * P * L / (Gsh * W * H)
    target = d_bend + d_shear
    rec = dict(tip_uz_mm=dz, target_mm=target, bend_mm=d_bend, shear_mm=d_shear,
               error_pct=100 * (dz + target) / target,  # dz is negative
               area_mm2=area, cg_iters=iters, converged=bool(ok),
               elements=int(m.t.shape[1]), dofs=int(ib.N))
    rec['error_pct'] = 100.0 * abs(-dz - target) / target
    print('cantilever', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    if rec['error_pct'] > 5.0 or not ok:
        raise SystemExit('tube cantilever failed')
    return rec


@BilinearForm
def kg_axial(u, v, w):
    """∫ du_i/dz dv_i/dz. Paired with K φ = λ Kg φ, λ = σ_cr for unit compression."""
    return u.grad[0, 2] * v.grad[0, 2] + u.grad[1, 2] * v.grad[1, 2] + u.grad[2, 2] * v.grad[2, 2]


def section(Rin, Rout):
    A = np.pi * (Rout ** 2 - Rin ** 2)
    I = np.pi / 4.0 * (Rout ** 4 - Rin ** 4)
    return A, I


def run_tube(name, Rin, Rout, Lmesh, ntheta, nz, arm_mm):
    A, I = section(Rin, Rout)
    m = tube_mesh(Rin, Rout, Lmesh, ntheta, nz)
    e = ElementVector(ElementHex2())
    ib = Basis(m, e, intorder=4)
    lam, mu = lame_parameters(F.E_AL, F.NU_AL)
    K = asm(linear_elasticity(lam, mu), ib).tocsr()
    print(name, 'elements', m.t.shape[1], 'dofs', ib.N, 'A', round(A, 2), 'I', round(I, 1), flush=True)
    fix = ib.get_dofs(m.facets_satisfying(lambda x: x[2] < 0.15, boundaries_only=True)).all()
    cent = m.p[:, m.t].mean(1) if False else None
    # element centroids from the 8 corners (t holds corners only on MeshHex2? from_mesh keeps mesh.t as the linear connectivity)
    c = m.p[:, m.t[:8]].mean(1)
    band = np.where((c[2] > 0.35 * Lmesh) & (c[2] < 0.65 * Lmesh))[0]

    def one(tag, Force, M):
        tz = lambda y, x, Force=Force, M=M: -Force / A - (M / I) * y
        f, area = _end_load(m, ib, lambda x, L=Lmesh: x[2] > L - 0.2, tz)
        uz = np.zeros(ib.N)
        for attr in ('nodal_dofs', 'edge_dofs', 'facet_dofs', 'interior_dofs'):
            ed = getattr(ib, attr)
            if ed is None or getattr(ed, 'ndim', 0) != 2 or ed.shape[0] < 3:
                continue
            uz[np.ravel(ed[2])] = 1.0
        nF = float(f @ uz)
        if abs(Force) > 1.0 and abs(nF + Force) / abs(Force) > 0.08:
            raise RuntimeError('%s end load resultant %.1f N vs target %.1f N' % (tag, nF, -Force))
        u, iters, ok = _solve(K.copy(), f, fix)
        vm, sig = vm_of(m, ib, u)
        vb = vm[band]
        if len(vb) == 0:
            raise RuntimeError('%s mid-span band is empty' % tag)
        hand = Force / A + abs(M) * Rout / I
        rec = dict(F_N=Force, M_Nmm=M, area_mm2=round(area, 1), resultant_Fz=round(nF, 1),
                   vm_band_max=float(vb.max()), vm_band_p99=float(np.percentile(vb, 99)),
                   hand_MPa=float(hand), SF_band_max=round(F.SY / float(vb.max()), 3),
                   cg_iters=iters, converged=bool(ok))
        print(tag, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
        del u, vm, sig
        gc.collect()
        return rec

    cases = {}
    for mult, lab in ((1.0, 'bw3'), (2.0, 'fall')):
        Force = BW3 * mult
        M = Force * arm_mm
        cases[lab] = one('%s %s' % (name, lab), Force, M)

    # dent: both ends fixed, lateral patch at midspan
    fix2 = np.union1d(fix, ib.get_dofs(m.facets_satisfying(lambda x, L=Lmesh: x[2] > L - 0.15, boundaries_only=True)).all())
    for mult, lab in ((1.0, 'dent_bw3'), (2.0, 'dent_fall')):
        Force = BW3 * mult
        sel = lambda x, L=Lmesh, R=Rout: (np.abs(x[2] - L / 2) < 8.0) & (np.hypot(x[0], x[1]) > R - 0.15) & (np.abs(np.arctan2(x[1], x[0])) < np.radians(18))
        f, area, _ = F.facet_load(m, ib, sel, [Force, 0, 0])
        u, iters, ok = _solve(K.copy(), f, fix2)
        vm, _ = vm_of(m, ib, u)
        rec = dict(F_N=Force, patch_mm2=round(area, 1), vm_max=float(vm.max()),
                   SF=round(F.SY / float(vm.max()), 3), cg_iters=iters, converged=bool(ok),
                   note='both ends fixed, patch |z-L/2|<8 mm and |θ|<18° on the OD, force +x')
        print(name, lab, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
        cases[lab] = rec
        del u, vm
        gc.collect()

    # axial buckling, unit compression σ_zz. Classical thin-cylinder membrane stress.
    Kg = asm(kg_axial, ib).tocsr()
    free = np.setdiff1d(np.arange(ib.N), fix)
    Kf = K[free][:, free]
    Gf = Kg[free][:, free]
    mu, _ = eigsh(Gf, k=3, M=Kf, which='LA', tol=1e-6)
    sig_cr = float(1.0 / np.max(mu))
    Rmid = 0.5 * (Rin + Rout)
    t = Rout - Rin
    classical = F.E_AL * t / (Rmid * np.sqrt(3 * (1 - F.NU_AL ** 2)))
    buck = dict(sigma_cr_MPa=sig_cr, classical_MPa=float(classical), ratio=sig_cr / classical,
                ntheta=ntheta, nz=nz, L_mm=Lmesh)
    print(name, 'buckle', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in buck.items()}, flush=True)
    cases['axial_buckling'] = buck
    return dict(part=name, Rin=Rin, Rout=Rout, A_mm2=A, I_mm4=I, elements=int(m.t.shape[1]),
                dofs=int(ib.N), cases=cases)


def main():
    out = {'cantilever': cantilever()}
    # stubs: several buckle half-waves (λ~1.7*sqrt(R t) ~ 9 mm) and a clean mid band
    out['femur'] = run_tube('femur', 23.8, 25.0, 80.0, 36, 16, 120.0)
    out['tibia'] = run_tube('tibia', 21.3, 22.5, 80.0, 36, 16, 100.0)
    F.save('fea_tubes', out)
    print('TUBE_DONE', flush=True)


if __name__ == '__main__':
    main()
