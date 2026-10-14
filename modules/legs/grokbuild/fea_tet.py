"""P2 tetrahedron elasticity for the leg-structure FEA (mm, N, MPa).

Same stack as modules/legs/fea_r4.py (CadQuery, gmsh, scikit-fem, pyamg).
One part per process. 7075-T6 unless an element mask says steel or adhesive.
"""
import os, sys, json, gc, tempfile
os.environ.setdefault('OMP_NUM_THREADS', '8')
os.environ.setdefault('MKL_NUM_THREADS', '8')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '8')
if sys.platform == 'win32':
    import sysconfig
    _sp = sysconfig.get_paths()['purelib']
    for _sub in ('cadquery_ocp.libs', 'vtk.libs'):
        _p = os.path.join(_sp, _sub)
        if os.path.isdir(_p):
            os.add_dll_directory(_p)
import numpy as np
import gmsh
import meshio
import cadquery as cq
from skfem import MeshTet, ElementTetP2, ElementVector, Basis, FacetBasis, asm, LinearForm
from skfem.models.elasticity import linear_elasticity, lame_parameters
import pyamg

E_AL, NU_AL = 71700.0, 0.33
E_ST, NU_ST = 210000.0, 0.30
E_AD, NU_AD = 2500.0, 0.40          # DP490, mid of the 2–3 GPa band in the brief
RHO_AL, RHO_ST = 2.81e-6, 7.85e-6
SY, SU, SE = 503.0, 572.0, 159.0    # 7075-T6 yield, ultimate, fatigue at 5e8 fully reversed

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results')
os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(tempfile.gettempdir(), 'legs_fea')
os.makedirs(TMP, exist_ok=True)

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

def cyl_y(r, y0, y1, c=(0, 0)):
    # extrude(-h) on an XZ workplane spans y = 0..h. Shift by y0.
    h = y1 - y0
    return cq.Workplane('XZ').center(c[0], c[1]).circle(r).extrude(-h).translate((0, y0, 0))

def cyl_z(r, z0, z1, c=(0, 0)):
    return cq.Workplane('XY').circle(r).extrude(z1 - z0).translate((c[0], c[1], z0))

def goodman_pulse(vm):
    """0 → peak. sa = sm = vm/2."""
    sa = sm = 0.5 * vm
    return 1.0 / (sa / SE + sm / SU)

def goodman_rev(vm, k=0.52):
    """Fully reversed at k × the static peak. Mean is zero."""
    return SE / (k * vm)

def mesh_solid(solid, h, tag, hmin=None):
    path = os.path.join(TMP, tag)
    cq.exporters.export(solid, path + '.step')
    gmsh.initialize()
    gmsh.option.setNumber('General.NumThreads', 8)
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.model.occ.importShapes(path + '.step')
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.MeshSizeMax', h)
    gmsh.option.setNumber('Mesh.MeshSizeMin', h if hmin is None else hmin)
    gmsh.option.setNumber('Mesh.Algorithm3D', 10)   # HXT
    try:
        gmsh.model.mesh.generate(3)
    except Exception:
        gmsh.option.setNumber('Mesh.Algorithm3D', 1)
        gmsh.model.mesh.generate(3)
    gmsh.write(path + '.msh')
    gmsh.finalize()
    mm = meshio.read(path + '.msh')
    return MeshTet(mm.points.T.copy(), mm.cells_dict['tetra'].T.copy())

def _regions(m, masks):
    """masks: list of (name, predicate on element centroid (3,)). Returns index arrays."""
    c = m.p[:, m.t].mean(1)   # (3, ne)
    out = {}
    taken = np.zeros(m.t.shape[1], dtype=bool)
    for name, pred in masks:
        sel = pred(c) & ~taken
        out[name] = np.where(sel)[0]
        taken |= sel
    out['al'] = np.where(~taken)[0]
    return out, c

def assemble(m, regions):
    """regions: dict name -> element indices. Names: al, steel, adh."""
    e = ElementVector(ElementTetP2())
    mats = {'al': (E_AL, NU_AL), 'steel': (E_ST, NU_ST), 'adh': (E_AD, NU_AD)}
    ib = Basis(m, e, intorder=2)
    K = None
    for name, (Em, nu) in mats.items():
        idx = regions.get(name)
        if idx is None or len(idx) == 0:
            continue
        lam, mu = lame_parameters(Em, nu)
        b = Basis(m, e, elements=idx, intorder=2)
        Ki = asm(linear_elasticity(lam, mu), b)
        K = Ki if K is None else K + Ki
        del Ki, b
        gc.collect()
    return ib, K.tocsr()

def _solve_reduced(K, f, D, tol=1e-7, maxiter=6000):
    I = np.setdiff1d(np.arange(K.shape[0]), D, assume_unique=False)
    Kc = K[I][:, I].tocsr()
    del K
    gc.collect()
    ml = pyamg.smoothed_aggregation_solver(Kc, max_coarse=400, keep=False, smooth=('jacobi', {}))
    res = []
    x = ml.solve(f[I], tol=tol, accel='cg', maxiter=maxiter, residuals=res)
    u = np.zeros(f.shape[0])
    u[I] = x
    rel = float(res[-1] / res[0]) if res and res[0] else 1.0
    return u, I, len(res), rel < 10 * tol or (res and res[-1] < tol * (np.linalg.norm(f[I]) + 1e-30))

def stress_al(m, ib, u, al_elems, Em=E_AL, nu=NU_AL):
    """von Mises per aluminum element (max over quadrature points). Chunked."""
    lam, mu = lame_parameters(Em, nu)
    ne = m.t.shape[1]
    vm = np.zeros(ne)
    step = 8000
    for a in range(0, len(al_elems), step):
        idx = al_elems[a:a + step]
        b = Basis(m, ib.elem, elements=idx, intorder=2)
        # interpolate on the full basis, then slice: cheaper to use element-local field
        g = b.interpolate(u).grad                 # (3,3,nqp,nchunk)
        eps = 0.5 * (g + np.transpose(g, (1, 0, 2, 3)))
        tr = np.einsum('iiek->ek', eps)
        sig = 2 * mu * eps + lam * np.einsum('ij,ek->ijek', np.eye(3), tr)
        v = np.sqrt(0.5 * ((sig[0, 0] - sig[1, 1]) ** 2 + (sig[1, 1] - sig[2, 2]) ** 2
                           + (sig[2, 2] - sig[0, 0]) ** 2) + 3 * (sig[0, 1] ** 2 + sig[1, 2] ** 2 + sig[0, 2] ** 2))
        vm[idx] = v.max(1)
        del b, g, eps, sig, v
        gc.collect()
    return vm

def facet_load(m, ib, sel, vec):
    fac = m.facets_satisfying(sel, boundaries_only=True)
    if len(fac) == 0:
        raise RuntimeError('load or support selector matched no boundary facets')
    e = ib.elem
    fb = FacetBasis(m, e, facets=fac)
    # x-component shape functions partition unity, so the sum is the facet area
    area = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
    vv = np.array(vec, float) / area
    f = asm(LinearForm(lambda v, w: v[0] * vv[0] + v[1] * vv[1] + v[2] * vv[2]), fb)
    return f, area, fac

def summarize(vm, elems, m, u, ib, label):
    ve = vm[elems]
    i_local = int(np.argmax(ve))
    i = int(elems[i_local])
    c = m.p[:, m.t[:, i]].mean(1)
    # structural value: 99.9th percentile, and the max among elements whose centroid is
    # not on a Dirichlet edge (caller may pass a pre-masked vm). Both are reported.
    out = dict(
        vm_max=float(ve.max()),
        vm_p999=float(np.percentile(ve, 99.9)),
        vm_p99=float(np.percentile(ve, 99)),
        vm_p50=float(np.percentile(ve, 50)),
        at_mm=[round(float(x), 2) for x in c],
        umax_mm=float(np.max(np.abs(u))),
        n_elem=int(len(elems)),
    )
    out['SF_yield_max'] = round(SY / out['vm_max'], 3)
    out['SF_yield_p999'] = round(SY / out['vm_p999'], 3)
    out['goodman_pulse_p999'] = round(goodman_pulse(out['vm_p999']), 3)
    out['goodman_rev_0p52_p999'] = round(goodman_rev(out['vm_p999']), 3)
    out['goodman_pulse_max'] = round(goodman_pulse(out['vm_max']), 3)
    out['goodman_rev_0p52_max'] = round(goodman_rev(out['vm_max']), 3)
    # Peak that is still present 2 mm from the hottest element. A corner singularity
    # drops; a real hot spot does not.
    cents = m.p[:, m.t[:, elems]].mean(1)
    far = np.linalg.norm(cents - np.asarray(c, float).reshape(3, 1), axis=0) >= 2.0
    if np.any(far):
        off = float(ve[far].max())
        out['vm_max_2mm_off'] = off
        out['SF_yield_2mm_off'] = round(SY / off, 3)
        out['goodman_pulse_2mm_off'] = round(goodman_pulse(off), 3)
        out['goodman_rev_0p52_2mm_off'] = round(goodman_rev(off), 3)
    print(label, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items()}, flush=True)
    return out

def run_case(m, ib, K, fix_dofs, loads, al_elems):
    """loads: dict name -> list of (selector, force_vector). fix_dofs: dirichlet indices."""
    results = {}
    for name, parts in loads.items():
        f = np.zeros(ib.N)
        areas = {}
        for sel, vec in parts:
            fi, area, _ = facet_load(m, ib, sel, vec)
            f += fi
            areas[str(len(areas))] = round(area, 2)
        u, _, iters, ok = _solve_reduced(K.copy(), f, fix_dofs)
        vm = stress_al(m, ib, u, al_elems)
        rec = summarize(vm, al_elems, m, u, ib, name)
        rec['cg_iters'] = iters
        rec['converged'] = bool(ok)
        rec['load_area_mm2'] = areas
        results[name] = rec
        del u, vm, f
        gc.collect()
    return results

def stress_tensor(m, ib, u, elems, Em=E_AL, nu=NU_AL):
    """Mean stress tensor over quadrature points, aluminum (or Em). Returns (3,3,n)."""
    lam, mu = lame_parameters(Em, nu)
    out = np.zeros((3, 3, len(elems)))
    step = 4000
    for a in range(0, len(elems), step):
        idx = elems[a:a + step]
        b = Basis(m, ib.elem, elements=idx, intorder=2)
        g = b.interpolate(u).grad
        eps = 0.5 * (g + np.transpose(g, (1, 0, 2, 3)))
        tr = np.einsum('iiek->ek', eps)
        sig = 2 * mu * eps + lam * np.einsum('ij,ek->ijek', np.eye(3), tr)
        out[:, :, a:a + len(idx)] = sig.mean(-1)
        del b, g, eps, sig
        gc.collect()
    return out

def sym_y(m, ib, tol=0.08):
    return ib.get_dofs(m.facets_satisfying(lambda x: np.abs(x[1]) < tol, boundaries_only=True)).all(['u^2'])

def save(tag, payload):
    path = os.path.join(OUT, tag + '.json')
    json.dump(payload, open(path, 'w'), indent=1)
    print('wrote', path, flush=True)
    return path

def volume(solid):
    return float(sum(s.Volume() for s in solid.solids().vals()))
