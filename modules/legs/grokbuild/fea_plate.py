"""Mindlin Q4 plate buckling. Verifies uniaxial k=4, then the foot skin bay.

Units mm, N, MPa. 7075-T6. Simply supported: w = 0 on the boundary, rotations free.
Shear is one-point reduced integration; bending and geometric stiffness are 2×2.
"""
import os, sys, json
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import eigsh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F

G = 1.0 / np.sqrt(3.0)


def _N(xi, eta):
    xs = np.array([-1.0, 1.0, 1.0, -1.0])
    es = np.array([-1.0, -1.0, 1.0, 1.0])
    N = 0.25 * (1.0 + xs * xi) * (1.0 + es * eta)
    dxi = 0.25 * xs * (1.0 + es * eta)
    deta = 0.25 * es * (1.0 + xs * xi)
    return N, dxi, deta


def _grad(xy, xi, eta):
    N, dxi, deta = _N(xi, eta)
    J = np.vstack((dxi, deta)) @ xy
    det = float(np.linalg.det(J))
    dN = np.linalg.inv(J) @ np.vstack((dxi, deta))
    return N, dN, det


def analytic_k(E, nu, a, b, t, k):
    """Uniaxial σ_cr, compression along x, plate width b (the unloaded side)."""
    return k * np.pi ** 2 * E / (12.0 * (1.0 - nu ** 2)) * (t / b) ** 2


def buckle(a, b, t, nx, ny, Nx, Ny, Nxy, support='ss', E=F.E_AL, nu=F.NU_AL, nmodes=4, shear='reduced'):
    """Lowest positive eigenvalues of K = λ Kg. Nx, Ny, Nxy are membrane forces, N/mm.
    Compression is positive. Returns λ such that the critical forces are λ times the input.
    """
    xs = np.linspace(0.0, a, nx + 1)
    ys = np.linspace(0.0, b, ny + 1)
    X, Y = np.meshgrid(xs, ys, indexing='xy')
    nodes = np.column_stack((X.ravel(), Y.ravel()))
    nn = nodes.shape[0]
    nd = 3 * nn
    ix = lambda i, j: j * (nx + 1) + i
    quads = []
    for j in range(ny):
        for i in range(nx):
            quads.append([ix(i, j), ix(i + 1, j), ix(i + 1, j + 1), ix(i, j + 1)])
    Db = E * t ** 3 / (12.0 * (1.0 - nu ** 2)) * np.array(
        [[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1.0 - nu) / 2.0]])
    Ds = (5.0 / 6.0) * (E / (2.0 * (1.0 + nu))) * t
    Kb = lil_matrix((nd, nd))
    Kg = lil_matrix((nd, nd))
    gps = ((-G, -G), (G, -G), (G, G), (-G, G))
    for q in quads:
        xy = nodes[q]
        kb = np.zeros((12, 12))
        kg = np.zeros((12, 12))
        for xi, eta in gps:
            N, dN, det = _grad(xy, xi, eta)
            wgt = det * 1.0
            # bending: κ = [θx,x, θy,y, θx,y + θy,x]
            Bb = np.zeros((3, 12))
            for k in range(4):
                Bb[0, 3 * k + 1] = dN[0, k]
                Bb[1, 3 * k + 2] = dN[1, k]
                Bb[2, 3 * k + 1] = dN[1, k]
                Bb[2, 3 * k + 2] = dN[0, k]
            kb += (Bb.T @ Db @ Bb) * wgt
            # geometric: slopes of w
            Gw = np.zeros((2, 12))
            for k in range(4):
                Gw[0, 3 * k] = dN[0, k]
                Gw[1, 3 * k] = dN[1, k]
            S = np.array([[Nx, Nxy], [Nxy, Ny]])
            kg += (Gw.T @ S @ Gw) * wgt
        # shear. Reduced (center, weight 4) for thin plates; 2×2 when b/t is small,
        # because one-point shear then leaves hourglass modes below the real eigenvalue.
        shear_pts = ((0.0, 0.0, 4.0),) if shear == 'reduced' else tuple((xi, eta, 1.0) for xi, eta in gps)
        for xi, eta, sw in shear_pts:
            N, dN, det = _grad(xy, xi, eta)
            Bs = np.zeros((2, 12))
            for k in range(4):
                Bs[0, 3 * k] = dN[0, k]
                Bs[0, 3 * k + 1] = N[k]
                Bs[1, 3 * k] = dN[1, k]
                Bs[1, 3 * k + 2] = N[k]
            kb += (Bs.T @ (Ds * np.eye(2)) @ Bs) * det * sw
        dof = np.array([3 * n + c for n in q for c in range(3)])
        Kb[np.ix_(dof, dof)] += kb
        Kg[np.ix_(dof, dof)] += kg
    edge = np.zeros(nn, dtype=bool)
    edge[nodes[:, 0] < 1e-8] = True
    edge[nodes[:, 0] > a - 1e-8] = True
    edge[nodes[:, 1] < 1e-8] = True
    edge[nodes[:, 1] > b - 1e-8] = True
    fixed = []
    for n in np.where(edge)[0]:
        fixed.append(3 * n)          # w
        if support == 'clamped':
            fixed.append(3 * n + 1)
            fixed.append(3 * n + 2)
    free = np.setdiff1d(np.arange(nd), np.array(fixed, dtype=int))
    Kb = csr_matrix(Kb)[free][:, free]
    Kg = csr_matrix(Kg)[free][:, free]
    # K φ = λ Kg φ  →  largest eigenpairs of Kg φ = μ K φ, λ = 1/μ
    mu, vec = eigsh(Kg, k=nmodes, M=Kb, which='LA')
    order = np.argsort(-mu)
    lam = 1.0 / mu[order]
    return lam, nodes.shape[0], len(quads)


def main():
    E, nu = F.E_AL, F.NU_AL
    out = {'material': dict(E=E, nu=nu), 'cases': {}}
    # thin square, SS, uniaxial. k=4 is the Kirchhoff value.
    a = b = 100.0
    t = 1.0
    Nx = 1.0
    lam, nn, ne = buckle(a, b, t, 32, 32, Nx, 0.0, 0.0, 'ss')
    sig = lam[0] * Nx / t
    sig_k = analytic_k(E, nu, a, b, t, 4.0)
    k_fea = sig / (sig_k / 4.0)
    rec = dict(a=a, b=b, t=t, nx=32, lam=float(lam[0]), sigma_cr=float(sig),
               sigma_k4=float(sig_k), k_fea=float(k_fea), nodes=int(nn), elements=int(ne),
               modes=[float(x) for x in lam])
    print('thin SS', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    out['cases']['thin_ss_k4'] = rec
    if not (3.6 <= k_fea <= 4.4):
        raise SystemExit('plate buckling verification failed: k_fea=%.3f' % k_fea)
    # stocky bay, the foot clear span between 4 mm webs (center spacing 32 mm)
    a = b = 28.0
    t = 3.5
    for nx, tag in ((16, 'bay16'), (24, 'bay24')):
        lam, nn, ne = buckle(a, b, t, nx, nx, 1.0, 0.0, 0.0, 'ss', shear='full')
        sig = float(lam[0] / t)
        rec = dict(a=a, b=b, t=t, nx=nx, sigma_cr_ss=sig, sigma_k4=float(analytic_k(E, nu, a, b, t, 4.0)),
                   k_fea=float(sig / (analytic_k(E, nu, a, b, t, 4.0) / 4.0)), nodes=int(nn), shear='full',
                   note='b/t=8. Full 2x2 shear. Kirchhoff k=4 is an upper reference; Mindlin is slightly lower.')
        lam_c, _, _ = buckle(a, b, t, nx, nx, 1.0, 0.0, 0.0, 'clamped', shear='full')
        rec['sigma_cr_clamped'] = float(lam_c[0] / t)
        print(tag, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
        out['cases'][tag] = rec
    # biaxial, equal compression, SS square. Analytic k = 2 (N = 2 * π² D / b², so σ uses k=2).
    lam, _, _ = buckle(100.0, 100.0, 1.0, 24, 24, 1.0, 1.0, 0.0, 'ss')
    sig = float(lam[0] / 1.0)
    sig2 = float(analytic_k(E, nu, 100.0, 100.0, 1.0, 2.0))
    out['cases']['thin_ss_biaxial'] = dict(sigma_cr=sig, sigma_k2=sig2, ratio=sig / sig2)
    print('biaxial', out['cases']['thin_ss_biaxial'], flush=True)
    F.save('plate_buckling', out)
    print('PLATE_PASS', flush=True)


if __name__ == '__main__':
    main()
