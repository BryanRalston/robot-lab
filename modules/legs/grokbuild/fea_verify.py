"""Solver checks. A failure here stops the production runs.

1. Cantilever 100 x 10 x 10, tip shear 100 N. Beam theory: tip 0.558 mm, root bending 60 MPa.
2. Quarter ring, bore pressure 60 MPa. Lame hoop at the bore 141.7 MPa (tongue section).
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F

def cantilever():
    s = F.box(0, 100, 0, 10, 0, 10)
    m = F.mesh_solid(s, 5.0, 'verify_beam')
    reg, _ = F._regions(m, [])
    ib, K = F.assemble(m, reg)
    fix = ib.get_dofs(m.facets_satisfying(lambda x: x[0] < 0.01, boundaries_only=True)).all()
    f, area, _ = F.facet_load(m, ib, lambda x: x[0] > 99.99, [0, 0, -100.0])
    u, _, iters, ok = F._solve_reduced(K, f, fix)
    # tip displacement: nodes with x>98, mean uz
    tips = np.where(m.p[0] > 98)[0]
    # P2 nodal dofs for vertices only live in ib.nodal_dofs
    uz = u[ib.nodal_dofs[2, tips]]
    dtip = float(-uz.mean())
    vm = F.stress_al(m, ib, u, reg['al'])
    # bending check away from the root singularity and the tip load: x in [15, 25], top fibers z>8
    c = m.p[:, m.t].mean(1)
    band = np.where((c[0] > 15) & (c[0] < 25) & (c[2] > 7.5))[0]
    # beam sigma at x=20 is M*c/I = (100*80)*5/833.333 = 48 MPa
    sig = float(np.median(vm[band])) if len(band) else float('nan')
    I = 10 * 10 ** 3 / 12
    d_ref = 100 * 100 ** 3 / (3 * F.E_AL * I)
    s_ref = (100 * 80) * 5 / I
    rec = dict(dtip_mm=dtip, d_ref_mm=d_ref, d_err=abs(dtip - d_ref) / d_ref,
               sigma_band_MPa=sig, sigma_ref_MPa=s_ref, s_err=abs(sig - s_ref) / s_ref,
               tets=int(m.t.shape[1]), dofs=int(ib.N), iters=iters, converged=bool(ok), tip_area=area)
    print('CANTILEVER', {k: round(v, 4) if isinstance(v, float) else v for k, v in rec.items()}, flush=True)
    return rec

def lame():
    # quarter of OD 55 / ID 35, length 8, bore pressure 60 MPa. Plane-strain-ish via u_y=0 on both ends.
    tube = F.cq.Workplane('XZ').circle(27.5).circle(17.5).extrude(-8)  # y = 0..8
    s = tube.intersect(F.box(0, 40, -0.1, 8.1, 0, 40))
    print('lame volume', s.val().Volume(), 'expected', 3.14159265 / 4 * (27.5 ** 2 - 17.5 ** 2) * 8, flush=True)
    m = F.mesh_solid(s, 1.5, 'verify_lame')
    reg, cent = F._regions(m, [])
    ib, K = F.assemble(m, reg)
    D = ib.get_dofs(m.facets_satisfying(lambda x: x[0] < 0.05, boundaries_only=True)).all(['u^1'])
    D = np.union1d(D, ib.get_dofs(m.facets_satisfying(lambda x: x[2] < 0.05, boundaries_only=True)).all(['u^3']))
    D = np.union1d(D, ib.get_dofs(m.facets_satisfying(lambda x: (x[1] < 0.05) | (x[1] > 7.95), boundaries_only=True)).all(['u^2']))
    # pressure on the bore, outward normal is -radial, so the traction on the solid is +p in the outward direction
    # of the bore surface, i.e. pointing out of the material, which is -e_r. Traction vector = -p e_r.
    # Apply a uniform radial traction by splitting the bore into facets and summing.
    fac = m.facets_satisfying(lambda x: np.hypot(x[0], x[2]) < 17.7, boundaries_only=True)
    e = ib.elem
    from skfem import FacetBasis, asm, LinearForm
    f = np.zeros(ib.N)
    # one basis, traction direction from the facet midpoint
    fp = m.p[:, m.facets[:, fac]].mean(1)   # (3, nfac) midpoints of corner nodes; good enough to bin
    # integrate in 8 angular bins so the traction direction is nearly constant
    ang = np.arctan2(fp[2], fp[0])
    for b0 in np.linspace(0, np.pi / 2, 8, endpoint=False):
        sel = fac[(ang >= b0 - 1e-6) & (ang < b0 + np.pi / 16 + 1e-6)]
        if len(sel) == 0:
            continue
        th = b0 + np.pi / 32
        # traction on the metal is inward-normal * p? Internal pressure pushes the wall OUTWARD, +e_r.
        tr = 60.0 * np.array([np.cos(th), 0.0, np.sin(th)])
        fb = FacetBasis(m, e, facets=sel)
        area = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
        vv = tr  # pressure already per area; the form integrates vv·v dA, so pass traction not force
        f += asm(LinearForm(lambda v, w: v[0] * vv[0] + v[1] * vv[1] + v[2] * vv[2]), fb)
        del fb
    u, _, iters, ok = F._solve_reduced(K, f, D)
    vm = F.stress_al(m, ib, u, reg['al'])
    c = m.p[:, m.t].mean(1)
    r = np.hypot(c[0], c[2])
    bore = np.where(r < 19.2)[0]
    # Lame hoop 141.7, radial ~ -60, vm = sqrt(hoop^2 + radial^2 - hoop*radial) roughly
    # plane strain more careful; the hand number quoted in r5 is the hoop 141.7
    rec = dict(vm_bore_median=float(np.median(vm[bore])), vm_bore_mean=float(vm[bore].mean()),
               hoop_hand=141.7, tets=int(m.t.shape[1]), iters=iters, converged=bool(ok), n_bore=int(len(bore)))
    print('LAME', {k: round(v, 3) if isinstance(v, float) else v for k, v in rec.items()}, flush=True)
    return rec

if __name__ == '__main__':
    c = cantilever()
    L = lame()
    ok = c['d_err'] < 0.08 and c['s_err'] < 0.20 and c['converged'] and L['converged']
    # hoop is not vm; vm for (141.7, -60) plane stress is about 173. Accept vm within 25% of that.
    # plane stress, σθ=141.7, σr=−60, σa=0 → √(σθ²+σr²−σθ σr)
    vm_ref = float(np.sqrt(141.7 ** 2 + 60 ** 2 + 141.7 * 60))
    L['vm_ref'] = vm_ref
    L['vm_err'] = abs(L['vm_bore_median'] - vm_ref) / vm_ref
    ok = ok and L['vm_err'] < 0.25
    out = dict(cantilever=c, lame=L, ok=bool(ok), vm_ref=vm_ref)
    F.save('verify_solver', out)
    print('VERIFY', 'PASS' if ok else 'FAIL', flush=True)
    sys.exit(0 if ok else 1)
