"""Thigh-clamp retention: DP490 bond shear (axisymmetric) and Kt of a Ø6 hole in the 1.2 mm wall.

Bond: collar ID 50.20, adhesive 0.10 mm, E 2500 MPa, ν 0.40, over the Ø50 × 1.2 tube,
plus the 47.6/43.6 sleeve. Kt coupon is plane stress, P2 triangles, checked against Kt = 3
for a wide plate before the walking load is applied.
"""
import os, sys, json
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
import gmsh, meshio
from skfem import MeshTri, Basis, ElementTriP2, ElementVector, asm, LinearForm
from skfem.models.elasticity import linear_elasticity, lame_parameters

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F


def C_axi(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    # order ε_r, ε_z, ε_θ, γ_rz
    C = np.zeros((4, 4))
    C[0, 0] = C[1, 1] = C[2, 2] = lam + 2 * mu
    C[0, 1] = C[1, 0] = C[0, 2] = C[2, 0] = C[1, 2] = C[2, 1] = lam
    C[3, 3] = mu
    return C


def bond_model(Fax, nr_col=4, nz=28):
    """Axisymmetric. z = 0..34 is the bond. Tube runs z = -12..46. Full 2π integration."""
    # regions as (r0, r1, z0, z1, E, nu, name) with a simple grid per region
    # Build one structured grid: r stations and z stations, then drop elements outside parts.
    rs = np.array([21.8, 23.7, 23.8, 25.0, 25.10, 27.0, 29.0, 31.0])
    # z = 0 and z = 34 are the collar ends and must be nodes
    zs = np.unique(np.round(np.concatenate([
        np.linspace(-12, 0, 5), np.linspace(0, 34, nz), np.linspace(34, 46, 5)]), 6))

    def nid(ir, iz):
        return iz * len(rs) + ir

    nodes = np.array([(r, z) for z in zs for r in rs])  # wait, nid assumes ir fastest? 
    # redefine: ir fastest
    nodes = np.zeros((len(rs) * len(zs), 2))
    for iz, z in enumerate(zs):
        for ir, r in enumerate(rs):
            nodes[nid(ir, iz)] = (r, z)
    quads, mats = [], []
    # material id by the r-interval of the element and whether z is inside the collar/sleeve
    mats_of = {
        'sleeve': (F.E_AL, F.NU_AL),
        'glue_in': (F.E_AD, F.NU_AD),
        'tube': (F.E_AL, F.NU_AL),
        'glue_out': (F.E_AD, F.NU_AD),
        'collar': (F.E_AL, F.NU_AL),
    }
    for iz in range(len(zs) - 1):
        zc = 0.5 * (zs[iz] + zs[iz + 1])
        for ir in range(len(rs) - 1):
            rc = 0.5 * (rs[ir] + rs[ir + 1])
            name = None
            if 21.8 <= rc < 23.7 and 0 <= zc <= 34:
                name = 'sleeve'
            elif 23.7 <= rc < 23.8 and 0 <= zc <= 34:
                name = 'glue_in'
            elif 23.8 <= rc < 25.0 and -12 <= zc <= 46:
                name = 'tube'
            elif 25.0 <= rc < 25.10 and 0 <= zc <= 34:
                name = 'glue_out'
            elif 25.10 <= rc <= 31.0 and 0 <= zc <= 34:
                name = 'collar'
            if name is None:
                continue
            quads.append([nid(ir, iz), nid(ir + 1, iz), nid(ir + 1, iz + 1), nid(ir, iz + 1)])
            mats.append(name)
    quads = np.array(quads)
    nd = 2 * len(nodes)
    K = lil_matrix((nd, nd))
    G = 1 / np.sqrt(3)
    gps = ((-G, -G), (G, -G), (G, G), (-G, G))
    for e, q in enumerate(quads):
        xy = nodes[q]          # r, z
        C = C_axi(*mats_of[mats[e]])
        ke = np.zeros((8, 8))
        for xi, eta in gps:
            xs = np.array([-1, 1, 1, -1.0])
            es = np.array([-1, -1, 1, 1.0])
            N = 0.25 * (1 + xs * xi) * (1 + es * eta)
            dxi = 0.25 * xs * (1 + es * eta)
            deta = 0.25 * es * (1 + xs * xi)
            J = np.vstack((dxi, deta)) @ xy
            det = float(np.linalg.det(J))
            dN = np.linalg.inv(J) @ np.vstack((dxi, deta))  # d/dr, d/dz
            r = float(N @ xy[:, 0])
            B = np.zeros((4, 8))
            for k in range(4):
                B[0, 2 * k] = dN[0, k]       # ε_r
                B[1, 2 * k + 1] = dN[1, k]   # ε_z
                B[2, 2 * k] = N[k] / r       # ε_θ
                B[3, 2 * k] = dN[1, k]       # γ_rz
                B[3, 2 * k + 1] = dN[0, k]
            ke += (B.T @ C @ B) * det * (2 * np.pi * r)
        dof = np.array([2 * n + c for n in q for c in (0, 1)])
        K[np.ix_(dof, dof)] += ke
    # nodes that no element uses would leave a zero row
    used = set(int(i) for i in quads.ravel())
    fixed = []
    for i in range(len(nodes)):
        if i not in used:
            fixed += [2 * i, 2 * i + 1]
    # fix the tube bottom (z < -11.5, tube radii)
    for i, (r, z) in enumerate(nodes):
        if z < -11.5 and 23.8 - 0.05 <= r <= 25.0 + 0.05:
            fixed += [2 * i, 2 * i + 1]
    # axial traction on the collar top, z max of collar nodes
    top = [i for i, (r, z) in enumerate(nodes) if abs(z - 34) < 1e-6 and r >= 25.10 - 0.01]
    # distribute Fax by the annular area of each node (trapezoid). Use nodal r spacing.
    f = np.zeros(nd)
    top = sorted(top, key=lambda i: nodes[i, 0])
    for a, b in zip(top[:-1], top[1:]):
        r0, r1 = nodes[a, 0], nodes[b, 0]
        dA = np.pi * (r1 ** 2 - r0 ** 2)
        # split the force on this ring equally to the two nodes (z component)
        f[2 * a + 1] += 0.5 * Fax * dA / (np.pi * (nodes[top[-1], 0] ** 2 - nodes[top[0], 0] ** 2))
        f[2 * b + 1] += 0.5 * Fax * dA / (np.pi * (nodes[top[-1], 0] ** 2 - nodes[top[0], 0] ** 2))
    # The loop double counts. Do it once properly.
    f[:] = 0.0
    Atot = np.pi * (nodes[top[-1], 0] ** 2 - nodes[top[0], 0] ** 2)
    for a, b in zip(top[:-1], top[1:]):
        r0, r1 = nodes[a, 0], nodes[b, 0]
        dF = Fax * np.pi * (r1 ** 2 - r0 ** 2) / Atot
        f[2 * a + 1] += 0.5 * dF
        f[2 * b + 1] += 0.5 * dF
    free = np.setdiff1d(np.arange(nd), np.array(fixed))
    u = np.zeros(nd)
    u[free] = spsolve(csr_matrix(K)[free][:, free], f[free])
    # adhesive shear τ_rz in glue_out elements
    tau, zc = [], []
    sz_below, sz_mid, sz_above = [], [], []
    Cglue = C_axi(F.E_AD, F.NU_AD)
    Cal = C_axi(F.E_AL, F.NU_AL)
    for e, q in enumerate(quads):
        xy = nodes[q]
        zmid = float(xy[:, 1].mean())
        if mats[e] == 'tube':
            xs = np.array([-1., 1, 1, -1])
            es = np.array([-1., -1, 1, 1])
            N = np.full(4, 0.25)
            dxi = 0.25 * xs
            deta = 0.25 * es
            J = np.vstack((dxi, deta)) @ xy
            dN = np.linalg.inv(J) @ np.vstack((dxi, deta))
            r = float(N @ xy[:, 0])
            B = np.zeros((4, 8))
            for k in range(4):
                B[0, 2 * k] = dN[0, k]
                B[1, 2 * k + 1] = dN[1, k]
                B[2, 2 * k] = N[k] / r
                B[3, 2 * k] = dN[1, k]
                B[3, 2 * k + 1] = dN[0, k]
            ue = np.concatenate([u[2 * n:2 * n + 2] for n in q])
            sz = float((Cal @ (B @ ue))[1])
            if zmid < -1.0:
                sz_below.append(sz)
            elif 8.0 < zmid < 26.0:
                sz_mid.append(sz)
            elif zmid > 36.0:
                sz_above.append(sz)
        if mats[e] != 'glue_out':
            continue
        xy = nodes[q]
        xs = np.array([-1., 1, 1, -1])
        es = np.array([-1., -1, 1, 1])
        N = np.full(4, 0.25)
        dxi = 0.25 * xs
        deta = 0.25 * es
        J = np.vstack((dxi, deta)) @ xy
        dN = np.linalg.inv(J) @ np.vstack((dxi, deta))
        r = float(N @ xy[:, 0])
        B = np.zeros((4, 8))
        for k in range(4):
            B[0, 2 * k] = dN[0, k]
            B[1, 2 * k + 1] = dN[1, k]
            B[2, 2 * k] = N[k] / r
            B[3, 2 * k] = dN[1, k]
            B[3, 2 * k + 1] = dN[0, k]
        ue = np.concatenate([u[2 * n:2 * n + 2] for n in q])
        sig = Cglue @ (B @ ue)
        tau.append(abs(float(sig[3])))
        zc.append(float(xy[:, 1].mean()))
    tau, zc = np.array(tau), np.array(zc)
    A_bond = np.pi * 50.0 * 34.0
    rec = dict(Fax_N=Fax, n_elem=len(quads), n_glue=int(len(tau)),
               tau_peak_MPa=float(tau.max()), tau_mean_MPa=float(tau.mean()),
               tau_hand_average_MPa=Fax / A_bond,
               z_of_peak_mm=float(zc[int(np.argmax(tau))]),
               tau_at_ends_MPa=float(max(tau[zc < 2].max(), tau[zc > 32].max())),
               allowable_23C=11.5, allowable_82C=4.75,
               sz_tube_below_MPa=float(np.mean(sz_below)) if sz_below else None,
               sz_tube_midbond_MPa=float(np.mean(sz_mid)) if sz_mid else None,
               sz_tube_above_MPa=float(np.mean(sz_above)) if sz_above else None,
               sz_hand_tube_MPa=Fax / (np.pi * (25.0 ** 2 - 23.8 ** 2)))
    # The element touching the collar end rises under refinement (bimaterial corner).
    # Shear one and two millimetres in is the value to compare with the allowable.
    for z0, key in ((1.0, 'tau_near_1mm'), (2.0, 'tau_near_2mm')):
        i = int(np.argmin(np.abs(zc - z0)))
        rec[key + '_MPa'] = float(tau[i])
        rec[key + '_z_mm'] = float(zc[i])
    rec['SF_23C'] = round(11.5 / rec['tau_peak_MPa'], 3)
    rec['SF_82C'] = round(4.75 / rec['tau_peak_MPa'], 3)
    rec['SF_23C_2mm'] = round(11.5 / rec['tau_near_2mm_MPa'], 3)
    rec['SF_82C_2mm'] = round(4.75 / rec['tau_near_2mm_MPa'], 3)
    print('bond', Fax, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    return rec


def kt_coupon(W=80.0, H=48.0, R=3.0, t=1.2, sigma=1.0, h=0.6):
    """Wide plate, remote tension sigma. Returns σ_max / sigma at the hole (Kt vs 3)."""
    gmsh.initialize()
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.model.add('kt')
    disk = gmsh.model.occ.addDisk(0, 0, 0, R, R)
    rect = gmsh.model.occ.addRectangle(-W / 2, -H / 2, 0, W, H)
    gmsh.model.occ.cut([(2, rect)], [(2, disk)])
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax', h)
    gmsh.option.setNumber('Mesh.MeshSizeMin', h * 0.25)
    gmsh.model.mesh.generate(2)
    path = os.path.join(F.TMP, 'kt.msh')
    gmsh.write(path)
    gmsh.finalize()
    mm = meshio.read(path)
    tri = mm.cells_dict['triangle']
    m = MeshTri(mm.points[:, :2].T.copy(), tri.T.copy())
    # plane stress via scaled lame? linear_elasticity is 3D. Use a 2D form instead.
    # ElementVector of a tri element in skfem is 2D when the mesh is 2D.
    e = ElementVector(ElementTriP2())
    ib = Basis(m, e, intorder=2)
    # plane stress λ*, μ with E, ν replaced so the 2D isotropic operator matches plane stress.
    # For 2D, skfem lame uses the 2D strain. Check: models.elasticity in 2D uses the 2×2 sym grad.
    # The lame pair that reproduces plane stress is not the 3D one.
    # C_11 = E/(1-ν²) = λ + 2μ, C_12 = ν E/(1-ν²) = λ, μ = E/2(1+ν)
    # λ = ν E / (1-ν²), μ = E/2(1+ν)
    nu, E = F.NU_AL, F.E_AL
    lam = nu * E / (1 - nu ** 2)
    mu = E / (2 * (1 + nu))
    K = asm(linear_elasticity(lam, mu), ib)
    # fix left edge x < -W/2+0.2, pull right edge
    fix = ib.get_dofs(m.facets_satisfying(lambda x: x[0] < -W / 2 + 0.3)).all()
    # also kill rigid y: one node
    right = m.facets_satisfying(lambda x: x[0] > W / 2 - 0.3)
    fb_area = float(asm(LinearForm(lambda v, w: v[0]), __import__('skfem').FacetBasis(m, ib.elem, facets=right)).sum())
    Force = sigma * H * t   # but the model is per unit thickness if we don't multiply. Keep t=1 in the 2D model
    # 2D model is per unit thickness. Remote stress = Force_per_thickness / H.
    Fline = sigma * H
    from skfem import FacetBasis
    fb = FacetBasis(m, ib.elem, facets=right)
    area = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
    vv = np.array([Fline / area, 0.0])
    f = asm(LinearForm(lambda v, w, vv=vv: v[0] * vv[0] + v[1] * vv[1]), fb)
    free = np.setdiff1d(np.arange(ib.N), fix)
    u = np.zeros(ib.N)
    u[free] = spsolve(K[free][:, free], f[free])
    # hoop / von Mises at elements near the hole, at the equator (x~0, |y|~R)
    from skfem.helpers import sym_grad
    basis = Basis(m, e, intorder=2)
    sg = basis.interpolate(u)
    # sg.grad shape (2,2,nqp,nelem) 
    g = sg.grad
    eps = 0.5 * (g + np.transpose(g, (1, 0, 2, 3)))
    sig_x = lam * (eps[0, 0] + eps[1, 1]) + 2 * mu * eps[0, 0]
    vm = np.sqrt(sig_x ** 2 + (lam * (eps[0, 0] + eps[1, 1]) + 2 * mu * eps[1, 1]) ** 2
                 - sig_x * (lam * (eps[0, 0] + eps[1, 1]) + 2 * mu * eps[1, 1]) + 3 * (2 * mu * eps[0, 1]) ** 2)
    # element centroids
    c = m.p[:, m.t].mean(1)
    r = np.hypot(c[0], c[1])
    near = (r < R + 1.5) & (np.abs(c[0]) < 1.0)   # equator, beside the hole
    vm_e = vm.max(1) if vm.shape[0] == m.t.shape[1] else vm.max(0)
    sig_max = float(vm_e[near].max()) if near.any() else float(vm_e.max())
    rec = dict(W=W, H=H, R=R, h=h, sigma_remote=sigma, sigma_max=sig_max, Kt=sig_max / sigma,
               n_tri=int(m.t.shape[1]), area_right=area)
    print('kt', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
    return rec


def main():
    kt = kt_coupon()
    if not (2.6 <= kt['Kt'] <= 3.4):
        raise SystemExit('Kt coupon failed: %.3f' % kt['Kt'])
    # walking: 0.52 × the axial design load, tube wall only (bond failed) and shared (bond intact).
    # Gross axial stress in the 1.2 mm tube from Fax over the tube area, then × Kt.
    A_tube = np.pi * (25.0 ** 2 - 23.8 ** 2)
    Fax, Fproof = 8763.86, 13100.0
    walk = 0.52 * Fax
    out = {'kt_coupon': kt, 'bond': {}}
    for name, Fax_ in (('both_screws', Fax), ('walk_0p52', walk), ('proof_13kN', Fproof)):
        out['bond'][name] = bond_model(Fax_)
    out['bond_refine_8764N'] = {str(nz): bond_model(Fax, nz=nz) for nz in (14, 28, 56)}
    sig_walk = walk / A_tube
    out['hole'] = dict(
        A_tube_mm2=A_tube,
        sigma_walk_gross_MPa=sig_walk,
        sigma_walk_Kt_MPa=sig_walk * kt['Kt'],
        SF_yield=F.SY / (sig_walk * kt['Kt']),
        goodman_rev=F.SE / (sig_walk * kt['Kt']),
        note='Bond-failed membrane. The pin bearing is the separate hand/FEA bearing check. Gross stress uses the 1.2 mm tube area and 0.52×8.76 kN.',
    )
    print('hole', out['hole'], flush=True)
    F.save('fea_retain', out)
    print('RETAIN_DONE', flush=True)


if __name__ == '__main__':
    main()
