"""Leg structure FEA, brief modules/legs/grokbuild/structure_fea.md (r3–r5).

  python fea_r5.py mass
  python fea_r5.py ring|clamp|clevis|ktongue|fork|tongue|foot [h_mm]

Units mm, N, MPa. 7075-T6. Body mass 66.5 kg. Results in grokbuild/results/.
Pins and the sensor flange are steel and are not in the aluminum mass.
"""
import os, sys, json, gc
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea_tet as F
from skfem import FacetBasis, asm, LinearForm

G = 9.81
MASS = 66.5
W, BW3, FALL = MASS * G, 3 * MASS * G, 6 * MASS * G
GRF = 1039.8          # worst ID vertical GRF, results/r3/structure_check.json (includes 20 kg carry)
FK, FH, FS = 7267.4, 9084.3, 4542.0
T_CARRY, T_NEED = 241.5e3, 314.0e3   # N·mm, r4 requirements at 66.5 kg (carry peak, 1.5× ID need)
LEVER, COP = 73.0, 165.0             # instep screw arm after the r5 move to 73 mm; toe patch center

def half(s, y1=80, z0=-5, z1=80, x0=-80, x1=200):
    return s.intersect(F.box(x0, x1, -0.05, y1, z0, z1))

def al_mass(solid):
    return F.volume(solid) * F.RHO_AL

# ---------------------------------------------------------------- geometry
def foot_al():
    """Closed box, r4 geometry that weighed 0.870 kg, instep shifted +3 mm (r5, 73 mm)."""
    skin, web, nweb, pad, padt, iw = 3.5, 4.0, 4, 45.0, 6.0, 5.0
    s = F.box(-60, 180, -50, 50, 0, skin).union(F.box(-60, 180, -50, 50, 18 - skin, 18))
    for y in np.linspace(-50 + web / 2, 50 - web / 2, nweb):
        s = s.union(F.box(-60, 180, y - web / 2, y + web / 2, 0, 18))
    s = s.union(F.box(-60, -56, -50, 50, 0, 18)).union(F.box(176, 180, -50, 50, 0, 18))
    inst = F.box(58, 88, -45, 45, 10, 50).cut(F.box(58 + iw, 88 - iw, -45 + iw, 45 - iw, 18, 50 - iw))
    s = s.union(inst)
    s = s.union(F.box(-pad, pad, -50, 50, 18 - padt, 18)).union(F.box(-pad, pad, -50, 50, 0, padt))
    return s

def foot_with_flange():
    """Aluminum box plus a steel ankle F/T flange (OD 60, ID 22, 8 mm) and 6 × Ø5 tied shanks on BC Ø46.

    The flange top is the support. The aluminum is loaded only through the bonded flange
    and the shanks, not through a rigid disk on the skin.
    """
    s = foot_al()
    fl = F.cyl_z(30, 18, 26).cut(F.cyl_z(11, 17.5, 26.5))
    angs = [20, 70, 130, 200, 250, 310]
    xy = [(23 * np.cos(np.radians(a)), 23 * np.sin(np.radians(a))) for a in angs]
    for x, y in xy:
        s = s.cut(F.cyl_z(2.75, 11.5, 18.2, (x, y)))
        fl = fl.cut(F.cyl_z(2.75, 17.8, 26.2, (x, y)))
        s = s.union(F.cyl_z(2.5, 12.0, 26.0, (x, y)))
    s = s.union(fl)
    return s, xy

def clamp_geom(fillet=True):
    """Split collar on the Ø50 femur, arms to y=±69, axial Ø12 eyes. r4 form, ring height 34, arm depth 30.

    Fillets (r = 1.5 mm) are the four vertical root lines and the four root arcs where each
    arm meets the collar. r = 2 mm fails on the arcs (OCC StdFail_NotDone).
    """
    b, hz, ring_t, ring_h = 12.0, 30.0, 6.0, 34.0
    s = F.cq.Workplane('XY').circle(25 + ring_t).circle(25).extrude(ring_h).translate((0, 0, -ring_h / 2))
    for sg in (1, -1):
        s = s.union(F.box(-b / 2, b / 2, min(sg * 24, sg * 57), max(sg * 24, sg * 57), -hz / 2, hz / 2))
        eye = F.box(-12, 12, sg * 69 - 12, sg * 69 + 12, -hz / 2, hz / 2)
        hole = F.cq.Workplane('YZ').center(sg * 69, 0).circle(6).extrude(30).translate((-15, 0, 0))
        s = s.union(eye.cut(hole))
    used = 0.0
    if fillet:
        lines, arcs = [], []
        for e in s.edges().vals():
            c = e.Center()
            if abs(abs(c.x) - b / 2) < 0.4 and abs(abs(c.y) - 30.41) < 0.5 and abs(c.z) < 1.0 and abs(e.Length() - hz) < 1.0:
                lines.append(e)
            if abs(c.x) < 1.2 and abs(abs(c.y) - 30.8) < 0.8 and abs(c.z) > 10.0:
                arcs.append(e)
        edges = lines + arcs
        if len(edges) != 8:
            raise RuntimeError('clamp fillet selector found %d lines + %d arcs, want 4+4' % (len(lines), len(arcs)))
        t = s.newObject(edges).fillet(1.5)
        if not (t.val().isValid() and len(t.solids().vals()) == 1):
            raise RuntimeError('clamp fillet r=1.5 did not yield one solid')
        s, used = t, 1.5
    return s, used

def hip_ring():
    """CRBH 5013 seat: OD 96, bore Ø80, length 25, neck 50×25 overlapping the ring so it is one solid.

    A neck that only touches the bore (z = −68..−48) is two solids. z = −66..−44 overlaps and weighs 0.225 kg.
    """
    ring = F.cyl_y(48, -12.5, 12.5).cut(F.cyl_y(40, -14, 14))
    neck = F.box(-25, 25, -12.5, 12.5, -66, -44)
    return ring.union(neck)

def clevis_geom():
    """v3 knee clevis. Cheeks 46×14×62, bridge 40×70×22, Ø16 pin, femur bore Ø50.

    The bore meets the bridge on a tangent, so the aluminum is two ears until the pin is unioned.
    Ear pockets (y = 23..34.5, z = 42..60) bring the aluminum to the M2 mass 0.235 kg.
    The pin ligament and the cheek faces are not pocketed.
    """
    cheek = F.box(-23, 23, 21, 35, -21, 41).union(F.box(-23, 23, -35, -21, -21, 41))
    bridge = F.box(3, 43, -35, 35, 40, 62)
    pocket = F.box(4, 42, 23, 34.5, 42, 60).union(F.box(4, 42, -34.5, -23, 42, 60))
    body = cheek.union(bridge).cut(F.cyl_y(8, -40, 40)).cut(F.cyl_z(25, 40, 80, (18, 0))).cut(pocket)
    pin = F.cyl_y(8, -36, 36)
    return body.union(pin), body

def ktongue_geom():
    """v3 knee tongue with the lever removed. R32 about the Ø16 pin, lower block to z = −50.

    The pocket sits in the lower block (x ≥ 16, |z| clear of the hole). Distance from the
    pocket corner to the pin surface is 12 mm. Target mass 0.233 kg.
    """
    tongue = F.box(-20, 30, -20, 20, -50, 10).intersect(
        F.cyl_y(32, -20, 20).union(F.box(-5, 35, -20, 20, -50, -10)))
    body = tongue.cut(F.box(16, 33, -16, 16, -48, -12)).cut(F.cyl_y(8, -25, 25))
    pin = F.cyl_y(8, -24, 24)
    return body.union(pin), body

def fork_geom():
    """v3 ankle fork. Outer 62×44×40, slot through the lower 20 mm leaving 4 mm walls, Ø12 pin.

    v3 places the solid cap on the upper 20 mm. The M2 pocket removes 30% of a 10 mm plate
    from that cap (0.158 kg). The pin crosses the walls at mid-slot.
    """
    outer = F.box(-25, 37, -22, 22, 0, 40)
    slot = F.box(-27, 39, -18, 18, -1, 20)
    # volume tuned so the aluminum matches the M2 0.158 kg line (see masses())
    pocket = F.box(-16, 28, -14, 14, 30, 36)
    body = outer.cut(slot).cut(pocket).cut(F.cyl_y(6, -26, 26, c=(0, 10)))
    pin = F.cyl_y(6, -26, 26, c=(0, 10))
    return body.union(pin), body

def tongue_geom():
    """Femur tongue OD 55 × 27 (|y|≤13.5), bore Ø35, neck 50×27 overlapping the hub. Mass 0.184 kg."""
    hub = F.cyl_y(27.5, -13.5, 13.5).cut(F.cyl_y(17.5, -15, 15))
    neck = F.box(-25, 25, -13.5, 13.5, -46.5, -26)
    return hub.union(neck)

# ---------------------------------------------------------------- loads
def z_ones(ib):
    v = np.zeros(ib.N)
    v[ib.nodal_dofs[2]] = 1.0
    ed = ib.edge_dofs
    if ed is not None and getattr(ed, 'ndim', 0) == 2 and ed.shape[0] >= 3:
        v[np.ravel(ed[2])] = 1.0
    return v

def y_ones(ib):
    v = np.zeros(ib.N)
    v[ib.nodal_dofs[1]] = 1.0
    ed = ib.edge_dofs
    if ed is not None and getattr(ed, 'ndim', 0) == 2 and ed.shape[0] >= 3:
        v[np.ravel(ed[1])] = 1.0
    return v

def resultant(ib, f):
    """Net Fz and the moment about x of a traction, from a rigid test function.

    M_x = Fz * y − Fy * z. edge_dofs for a vector P2 basis is (3, n_edges).
    """
    loc = ib.doflocs
    ed = ib.edge_dofs
    if ed is None or getattr(ed, 'ndim', 0) != 2 or ed.shape[0] < 3:
        raise RuntimeError('edge_dofs shape %s, expected (3, n_edges)' % (None if ed is None else ed.shape,))
    uz, uy = z_ones(ib), y_ones(ib)
    rot = uz * loc[1] + uy * (-loc[2])
    return float(f @ uz), float(f @ rot)

def check_load(ib, f, Fz, Mx, tag, f_tol=0.08, m_tol=0.12):
    nF, nM = resultant(ib, f)
    print(tag, 'resultant N', round(nF, 1), 'Nmm', round(nM, 1),
          'target', round(Fz, 1), round(Mx, 1), flush=True)
    if abs(Fz) > 1.0 and abs(nF - Fz) / abs(Fz) > f_tol:
        raise RuntimeError('%s force is off by %.1f pct' % (tag, 100.0 * abs(nF - Fz) / abs(Fz)))
    if abs(Mx) > 1.0 and abs(nM - Mx) / abs(Mx) > m_tol:
        raise RuntimeError('%s moment is off by %.1f pct' % (tag, 100.0 * abs(nM - Mx) / abs(Mx)))
    return nF, nM

def traction_on(m, ib, facets, traction):
    if len(facets) == 0:
        return np.zeros(ib.N), 0.0
    fb = FacetBasis(m, ib.elem, facets=facets)
    area = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
    vv = np.array(traction, float)
    f = asm(LinearForm(lambda v, w: v[0] * vv[0] + v[1] * vv[1] + v[2] * vv[2]), fb)
    return f, area

def cosine_fz(m, ib, radius, y0, y1, Fz, nbin=10):
    """Cosine bearing pressure on a y-axis bore. Resultant is Fz along +z (sign of Fz)."""
    fac = m.facets_satisfying(
        lambda x, r=radius, a=y0, b=y1: (np.abs(np.hypot(x[0], x[2]) - r) < 1.4) & (x[1] > a) & (x[1] < b),
        boundaries_only=True)
    if len(fac) == 0:
        raise RuntimeError('cosine: no bore facets')
    fp = m.p[:, m.facets[:, fac]].mean(1)
    # φ = 0 at the bottom (−z) when Fz>0, because the roller contacts the metal it pushes
    phi = np.arctan2(fp[0], -np.sign(Fz) * fp[2])
    keep = np.abs(phi) <= np.pi / 2 + 0.02
    fac, phi = fac[keep], phi[keep]
    edges = np.linspace(-np.pi / 2, np.pi / 2, nbin + 1)
    bins = []
    for i in range(nbin):
        sel = fac[(phi >= edges[i]) & (phi <= edges[i + 1] + 1e-9)]
        if len(sel) == 0:
            continue
        th = 0.5 * (edges[i] + edges[i + 1])
        fb = FacetBasis(m, ib.elem, facets=sel)
        area = float(asm(LinearForm(lambda v, w: v[0]), fb).sum())
        bins.append((th, area, sel))
    denom = sum(area * np.cos(th) ** 2 for th, area, _ in bins)
    if denom < 1e-9:
        raise RuntimeError('cosine denom is zero')
    # p_amp stays positive. A signed p0 flips the traction twice when Fz < 0
    # (once in e_r, once in the leading minus) and both halves of a couple
    # then push the same way.
    p_amp = abs(Fz) / denom
    s = 1.0 if Fz >= 0.0 else -1.0
    f = np.zeros(ib.N)
    for th, area, sel in bins:
        # e_r from the bore center out to the wall. Traction -p e_r is toward the center.
        # Contact sits on the wall opposite the force, so net Fz has the sign of Fz.
        er = np.array([np.sin(th), 0.0, -s * np.cos(th)])
        tr = -p_amp * np.cos(th) * er
        fi, _ = traction_on(m, ib, sel, tr)
        f += fi
    return f

def radial_plus_moment(m, ib, radius, y_seat, F, M):
    """Cosine radial load F over the whole seat, plus a self-calibrated ±y couple of moment M.

    The couple is two half-length cosines of opposite sign. Its scale comes from the
    measured moment of a unit pair, so the resultant is F and M regardless of the
    band centroid. A negative half means the linear traction would pull on that side.
    """
    fF = cosine_fz(m, ib, radius, -y_seat, y_seat, F)
    unit = cosine_fz(m, ib, radius, 0.05, y_seat, 1.0) + cosine_fz(m, ib, radius, -y_seat, -0.05, -1.0)
    nF_u, m_unit = resultant(ib, unit)
    print('couple unit force', round(nF_u, 4), 'moment', round(m_unit, 3), flush=True)
    if abs(M) < 1.0:
        return fF, 0.0
    if abs(m_unit) < 1e-3:
        raise RuntimeError('unit couple produced no moment (m_unit=%g, force %g)' % (m_unit, nF_u))
    if abs(nF_u) > 0.15:
        raise RuntimeError('unit couple net force %g (want ~0); the two halves are not opposed' % nF_u)
    scale = M / m_unit
    return fF + scale * unit, float(scale)

def solve_loads(m, ib, K, fix, load_vectors, al_elems, masks=None):
    """load_vectors: name -> f (assembled). Optional masks drop elements from the reported peak
    (fixture neighborhoods). The full-field percentiles are always stored."""
    out = {}
    for name, f in load_vectors.items():
        u, _, iters, ok = F._solve_reduced(K.copy(), f, fix)
        vm = F.stress_al(m, ib, u, al_elems)
        rec = F.summarize(vm, al_elems, m, u, ib, name)
        rec['cg_iters'] = iters
        rec['converged'] = bool(ok)
        if masks:
            for mk, sel in masks.items():
                sub = al_elems[sel(m.p[:, m.t[:, al_elems]].mean(1))]
                if len(sub) == 0:
                    continue
                rec[mk] = dict(vm_max=float(vm[sub].max()), vm_p999=float(np.percentile(vm[sub], 99.9)),
                               SF=round(F.SY / float(np.percentile(vm[sub], 99.9)), 3))
        out[name] = (rec, u, vm)
        gc.collect()
    return out

def pack(tag, meta, cases):
    """cases values are result dicts (no displacement arrays)."""
    F.save(tag, dict(meta, cases=cases))

# ---------------------------------------------------------------- parts
def prep(solid, h, tag, masks):
    m = F.mesh_solid(solid, h, tag)
    reg, cent = F._regions(m, masks)
    print(tag, 'tets', m.t.shape[1], 'nodes', m.p.shape[1],
          {k: int(len(v)) for k, v in reg.items()}, flush=True)
    ib, K = F.assemble(m, reg)
    ed = ib.edge_dofs
    print(tag, 'dofs', ib.N, 'edge_dofs', None if ed is None else tuple(getattr(ed, 'shape', ())), flush=True)
    return m, ib, K, reg, cent

def _fix(m, ib, sel, tag):
    fix = ib.get_dofs(m.facets_satisfying(sel, boundaries_only=True)).all()
    if len(fix) == 0:
        raise RuntimeError(tag + ' support matched no facets')
    return fix

def run_ring(h):
    s = hip_ring()
    Fphys = 2 * FS + 1.5 * W
    meta = dict(part='hip_ring', h_mm=h, mass_kg=round(al_mass(s), 4), n_solids=len(s.solids().vals()),
                F_physical_N=round(Fphys, 1), M_Nmm=192e3,
                note='OD 96, bore 80, L 25, neck 50x25 from z=-66 to -44 (one solid, 0.225 kg). '
                     'Seat |y|<=6.5. physical = radial cosine of 2*4542+1.5*66.5*g plus a calibrated '
                     'couple of 192 N·m. brief_12p4 is the r4 lumped radial load (moment added as M/D = 2.4 kN). '
                     'stacked applies 12.4 kN and 192 N·m together and double-counts the moment. Neck end fixed.')
    print('ring mass', meta['mass_kg'], 'solids', meta['n_solids'], flush=True)
    m, ib, K, reg, cent = prep(s, h, 'ring', [])
    fix = _fix(m, ib, lambda x: x[2] < -65.5, 'ring')
    specs = (
        ('physical_10kN_192Nm', Fphys, 192e3),
        ('brief_12p4kN_only', 12400.0, 0.0),
        ('stacked_12p4kN_plus_192Nm', 12400.0, 192e3),
    )
    loads = {}
    scales = {}
    for name, Fz, Mx in specs:
        f, scale = radial_plus_moment(m, ib, 40.0, 6.5, Fz, Mx)
        check_load(ib, f, Fz, Mx, name)
        loads[name] = f
        scales[name] = scale
    meta['couple_scale_N'] = scales
    solved = solve_loads(m, ib, K, fix, loads, reg['al'])
    pack('fea_ring_h%g' % h, meta, {k: v[0] for k, v in solved.items()})

def run_clamp(h):
    full, fr = clamp_geom(True)
    s = half(full, y1=90, z0=-40, z1=40, x0=-40, x1=40)
    meta = dict(part='thigh_clamp', h_mm=h, fillet_mm=fr, mass_kg=round(2 * al_mass(s), 4),
                note='Half model, uy=0 on y=0, bore fixed. One eye carries 4542 N; symmetry is both screws. '
                     'Fatigue is 0.52x fully reversed on the peak, per the brief.')
    print('clamp fillet', fr, 'mass', meta['mass_kg'], flush=True)
    m, ib, K, reg, cent = prep(s, h, 'clamp', [])
    fix = _fix(m, ib, lambda x: np.hypot(x[0], x[1]) < 25.2, 'clamp bore')
    fix = np.union1d(fix, F.sym_y(m, ib))
    hole = lambda x: (np.hypot(x[1] - 69, x[2]) < 6.3) & (np.abs(x[0]) < 12.2)
    loads = {}
    for name, Feye in (('screw_4542', FS), ('walk_0p52', 0.52 * FS)):
        fi, area, _ = F.facet_load(m, ib, hole, [0, 0, Feye])
        print(name, 'eye area', round(area, 2), flush=True)
        loads[name] = fi
    solved = solve_loads(m, ib, K, fix, loads, reg['al'])
    pack('fea_clamp_h%g' % h, meta, {k: v[0] for k, v in solved.items()})

def _pin_part(kind, h):
    if kind == 'clevis':
        fused, body = clevis_geom()
        s = half(fused, y1=50, z0=-30, z1=70, x0=-40, x1=60)
        body_h = half(body, y1=50, z0=-30, z1=70, x0=-40, x1=60)
        pin_r, gap = 7.95, (lambda x: (np.hypot(x[0], x[2]) < 8.3) & (x[1] < 20.5) & (x[1] > 0.2))
        fix_sel = lambda x: (np.abs(np.hypot(x[0] - 18.0, x[1]) - 25.0) < 1.6) & (x[2] > 42.0)
        forces = {'fall_6BW': FALL / 2, 'bw3_plus_screw': (BW3 + FK) / 2, 'op_grf_plus_screw': (GRF + FK) / 2}
        note = 'Half clevis. Ø16 steel pin tied in the hole. Support is the femur bore surface (Ø50 at x=18), not the bridge tip. Pin loaded in the cheek gap. Bridge ears pocketed.'
    elif kind == 'ktongue':
        fused, body = ktongue_geom()
        s, body_h = fused, body
        pin_r, gap = 7.95, (lambda x: (np.hypot(x[0], x[2]) < 8.3) & (np.abs(x[1]) > 20.2))
        fix_sel = lambda x: x[2] < -49.2
        forces = {'fall_6BW': FALL, 'bw3_plus_screw': BW3 + FK, 'op_grf_plus_screw': GRF + FK}
        note = 'v3 knee tongue, lever removed, Ø16 pin. Bottom face (z=-50) fixed. Pin ends loaded in double shear. Pocket leaves a 12 mm ligament.'
    else:
        fused, body = fork_geom()
        s = half(fused, y1=30, z0=-5, z1=50, x0=-40, x1=50)
        body_h = half(body, y1=30, z0=-5, z1=50, x0=-40, x1=50)
        pin_r = 5.95
        gap = lambda x: (np.hypot(x[0], x[2] - 10) < 6.4) & (x[1] < 17.5) & (x[1] > 0.2)
        fix_sel = lambda x: x[2] > 39.2
        FA = T_CARRY / LEVER
        forces = {'fall_6BW': FALL / 2, 'bw3': BW3 / 2, 'op_carry_screw': (GRF + FA) / 2}
        note = 'Half v3 ankle fork. 4 mm walls, 20 mm cap, Ø12 pin at mid-slot, cap pocketed. Top face fixed. op adds the 66.5 kg carry screw T/73 mm.'
    meta = dict(part=kind, h_mm=h, mass_al_kg=round(al_mass(body_h) * (2 if kind != 'ktongue' else 1), 4),
                pin='Ø16' if kind != 'fork' else 'Ø12', note=note)
    print(kind, 'al mass', meta['mass_al_kg'], flush=True)
    zpin = 10.0 if kind == 'fork' else 0.0
    masks = [('steel', lambda c, r=pin_r, zp=zpin: np.hypot(c[0], c[2] - zp) < r)]
    m, ib, K, reg, cent = prep(s, h, kind, masks)
    fix = _fix(m, ib, fix_sel, kind)
    if kind != 'ktongue':
        fix = np.union1d(fix, F.sym_y(m, ib))
    loads = {}
    for name, Fz in forces.items():
        fi, area, _ = F.facet_load(m, ib, gap, [0, 0, -Fz])
        print(name, 'pin area', round(area, 1), flush=True)
        loads[name] = fi
    solved = solve_loads(m, ib, K, fix, loads, reg['al'])
    pack('fea_%s_h%g' % (kind, h), meta, {k: v[0] for k, v in solved.items()})

def run_tongue(h):
    s = tongue_geom()
    meta = dict(part='femur_tongue', h_mm=h, mass_kg=round(al_mass(s), 4),
                note='OD 55 L 27 bore 35 + neck. 60 MPa is the design interference pressure (0.141 mm diametral). '
                     'Mechanical load is the D32 pair: 10063 N and 192 N·m, superposed on the pressure because '
                     'contact stays closed while radial pressure stays compressive. +60 K uses 49.2 MPa.')
    print('tongue mass', meta['mass_kg'], flush=True)
    m, ib, K, reg, cent = prep(s, h, 'tongue', [])
    fix = _fix(m, ib, lambda x: x[2] < -46.2, 'tongue')
    # pressure cases: internal pressure pushes the bore outward (+e_r). Bin it.
    def pressure(p):
        # |y| < 13.3 keeps the flat hub ends (y = ±13.5) out of the pressure. Those
        # faces sit at the bore radius and were taking a radial traction.
        fac = m.facets_satisfying(lambda x: (np.abs(np.hypot(x[0], x[2]) - 17.5) < 1.3) & (np.abs(x[1]) < 13.3), boundaries_only=True)
        fp = m.p[:, m.facets[:, fac]].mean(1)
        ang = np.arctan2(fp[0], fp[2])
        f = np.zeros(ib.N)
        edges = np.linspace(-np.pi, np.pi, 17)
        for i in range(16):
            sel = fac[(ang >= edges[i]) & (ang < edges[i + 1] + 1e-9)]
            if len(sel) == 0:
                continue
            th = 0.5 * (edges[i] + edges[i + 1])
            # ang = atan2(x, z), so e_r = (sin ang, 0, cos ang) points out of the bore into the metal
            tr = p * np.array([np.sin(th), 0.0, np.cos(th)])
            fi, _ = traction_on(m, ib, sel, tr)
            f += fi
        return f
    Fphys = 2 * FS + 1.5 * W
    # The 192 N·m couple is calibrated on the bore. One half of the linear traction goes negative
    # because 192 N·m exceeds F*(seat/4). That tension is not a contact traction; interface
    # radial stress after superposition is the gapping check, and a negative p_min means the
    # bonded result is not a contact solution.
    f_mech, sc_m = radial_plus_moment(m, ib, 17.5, 13.4, Fphys, 192e3)
    f_p = pressure(60.0)
    f_hot = pressure(49.2)
    check_load(ib, f_mech, Fphys, 192e3, 'tongue mech')
    Ff = FS + 1.5 * W
    Mf = 192e3 + FS * 69.0
    f_fault, sc_f = radial_plus_moment(m, ib, 17.5, 13.4, Ff, Mf)
    check_load(ib, f_fault, Ff, Mf, 'tongue fault')
    f_fall, _ = radial_plus_moment(m, ib, 17.5, 13.4, FALL, 0.0)
    check_load(ib, f_fall, FALL, 0.0, 'tongue fall')
    meta['couple_scale_mech'] = sc_m
    meta['couple_scale_fault'] = sc_f
    meta['fault_F_N'] = round(Ff, 1)
    meta['fault_M_Nmm'] = Mf
    loads = {'pressure_60': f_p, 'pressure_hot_49p2': f_hot, 'mech': f_mech, 'fault': f_fault, 'fall': f_fall,
             'combined': f_p + f_mech, 'combined_hot': f_hot + f_mech, 'combined_fault': f_p + f_fault, 'combined_fall': f_p + f_fall}
    solved = solve_loads(m, ib, K, fix, loads, reg['al'])
    # radial pressure at the bore from the combined displacement: -σ_rr
    bore = np.where(np.hypot(cent[0], cent[2]) < 19.0)[0]
    bore = np.intersect1d(bore, reg['al'])
    extra = {}
    for name in ('combined', 'combined_hot', 'combined_fault', 'pressure_60'):
        u = solved[name][1]
        sig = F.stress_tensor(m, ib, u, bore)
        # σ_rr = e_r · σ · e_r
        erx, erz = cent[0, bore], cent[2, bore]
        nrm = np.hypot(erx, erz) + 1e-12
        erx, erz = erx / nrm, erz / nrm
        srr = sig[0, 0] * erx ** 2 + sig[2, 2] * erz ** 2 + 2 * sig[0, 2] * erx * erz
        # e_θ = (−e_z, 0, e_x)
        stt = sig[0, 0] * erz ** 2 + sig[2, 2] * erx ** 2 - 2 * sig[0, 2] * erx * erz
        p = -srr
        mid = np.abs(cent[1, bore]) < 8.0
        extra[name] = dict(p_min_MPa=float(p.min()), p_p5_MPa=float(np.percentile(p, 5)), p_median_MPa=float(np.median(p)),
                           gap_if_p_min_neg=bool(p.min() < 0), n=int(len(bore)),
                           hoop_mid_median_MPa=float(np.median(stt[mid])) if np.any(mid) else None,
                           p_mid_median_MPa=float(np.median(p[mid])) if np.any(mid) else None)
        print(name, 'interface p', extra[name], flush=True)
    cases = {k: v[0] for k, v in solved.items()}
    for k, v in extra.items():
        cases[k]['interface'] = v
    pack('fea_tongue_h%g' % h, meta, cases)

def sole_contact(m, ib, K, fix, al_elems, sel, Ftarget, tag, kn=2.0e5):
    """Rigid flat ground on `sel`. Penalty kn [N/mm³], flange dofs already in `fix`.

    The ground approach is scaled so the upward reaction equals Ftarget. Dofs that go
    into tension are released and the contact is resolved. Springs sit on the corner
    nodes only, each with one third of its triangle's area. P2 consistent areas go
    negative and were producing multi-GPa spikes on tiny dofs.
    """
    from scipy.sparse import diags
    fac = m.facets_satisfying(sel, boundaries_only=True)
    if len(fac) == 0:
        raise RuntimeError(tag + ' contact selector matched nothing')
    verts = m.facets[:, fac]
    p0, p1, p2 = m.p[:, verts[0]], m.p[:, verts[1]], m.p[:, verts[2]]
    area_f = 0.5 * np.linalg.norm(np.cross((p1 - p0).T, (p2 - p0).T), axis=1)
    area = float(area_f.sum())
    if area <= 1.0:
        raise RuntimeError('%s contact area %.3f mm^2' % (tag, area))
    a_node = np.zeros(m.p.shape[1])
    for k in range(3):
        np.add.at(a_node, verts[k], area_f / 3.0)
    zd = np.asarray(ib.nodal_dofs[2]).ravel()
    if zd.size != a_node.size:
        raise RuntimeError('nodal z-dofs %d vs vertices %d' % (zd.size, a_node.size))
    a_lump = np.zeros(ib.N)
    a_lump[zd] = a_node
    a_lump[np.intersect1d(np.flatnonzero(a_lump > 0.0), fix)] = 0.0
    active = a_lump > 1e-6
    delta = 0.02
    u, iters, ok = None, 0, False
    released = 0
    for it in range(8):
        idx = np.flatnonzero(active)
        D = diags(np.where(active, kn * a_lump, 0.0), shape=(ib.N, ib.N), format='csr')
        f = np.where(active, kn * a_lump * delta, 0.0)
        u, _, iters, ok = F._solve_reduced((K + D).tocsr(), f, fix)
        react = kn * a_lump[idx] * (delta - u[idx])
        R = float(react.sum())
        tension = react < -1e-4 * abs(Ftarget)
        print(tag, 'iter', it, 'R', round(R, 1), 'target', round(Ftarget, 1),
              'delta', round(delta, 5), 'n', int(idx.size), 'tension', int(tension.sum()),
              'cg', iters, 'ok', bool(ok), flush=True)
        if tension.any():
            active[idx[tension]] = False
            released += int(tension.sum())
            continue
        if abs(R) < 1e-3:
            raise RuntimeError(tag + ' contact reaction is zero')
        if abs(R - Ftarget) / abs(Ftarget) < 0.02:
            break
        delta *= Ftarget / R
    else:
        raise RuntimeError(tag + ' contact did not match the target force')
    idx = np.flatnonzero(active)
    react = kn * a_lump[idx] * (delta - u[idx])
    area_i = a_lump[idx]
    p = react / area_i
    xs = ib.doflocs[0, idx]
    vm = F.stress_al(m, ib, u, al_elems)
    rec = F.summarize(vm, al_elems, m, u, ib, tag)
    rec['cg_iters'] = iters
    rec['converged'] = bool(ok)
    rec['contact'] = dict(
        area_mm2=round(area, 2), Ftarget_N=round(Ftarget, 2), R_N=round(float(react.sum()), 2),
        p_mean_MPa=float(react.sum() / area), p_max_MPa=float(p.max()),
        p_max_main_MPa=float(p[area_i >= 0.2 * np.median(area_i)].max()),
        p_p95_MPa=float(np.percentile(p, 95)), cop_x_mm=float(np.sum(react * xs) / np.sum(react)),
        n_active=int(idx.size), n_released=int(released), delta_mm=float(delta), kn_N_per_mm3=kn)
    print(tag, 'pressure', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec['contact'].items()}, flush=True)
    del u, vm, D, f
    gc.collect()
    return rec


def run_foot(h):
    try:
        full, xy = foot_with_flange()
        bolts = True
    except Exception as ex:
        print('bolt boolean failed', ex, flush=True)
        full, xy, bolts = foot_al().union(F.cyl_z(30, 18, 26).cut(F.cyl_z(11, 17.5, 26.5))), [], False
    al = foot_al()
    # z to 55 keeps the instep tower (top face at z = 50). z = 30 cut that face off.
    s = half(full, y1=55, z0=-1, z1=55, x0=-70, x1=190)
    meta = dict(part='foot', h_mm=h, mass_al_kg=round(al_mass(al), 4), bolts=bolts, bolt_xy_mm=[(round(a, 2), round(b, 2)) for a, b in xy],
                BW3_N=round(BW3, 2), FALL_N=round(FALL, 2),
                note='Half foot, uy=0 on y=0. Steel flange OD60/ID22 x 8 mm on the skin, 6xØ5 shanks on BC Ø46 '
                     '(3 in the half model) tied through the 6 mm pad. Support is the flange top, not a rigid skin disk. '
                     'Toe patch x>=165, heel patch x<=-45. Carry uses 241.5 N·m at 66.5 kg and the 73 mm arm.')
    print('foot al mass', meta['mass_al_kg'], 'bolts', bolts, flush=True)
    if xy:
        def steel_pred(c, xy=xy):
            fl = c[2] > 18.15
            shank = np.zeros(c.shape[1], dtype=bool)
            for x, y in xy:
                if y < -1:
                    continue
                shank |= (c[2] > 12.0) & ((c[0] - x) ** 2 + (c[1] - y) ** 2 < 2.6 ** 2)
            return fl | shank
        masks = [('steel', steel_pred)]
    else:
        masks = [('steel', lambda c: c[2] > 18.15)]
    m, ib, K, reg, cent = prep(s, h, 'foot', masks)
    fix = _fix(m, ib, lambda x: (x[2] > 25.7) & (np.hypot(x[0], x[1]) < 30.5), 'foot flange')
    fix = np.union1d(fix, F.sym_y(m, ib, 0.15))
    toe = lambda x: (x[2] < 0.08) & (x[0] >= 165)
    heel = lambda x: (x[2] < 0.08) & (x[0] <= -45)
    corner = lambda x: (x[2] < 0.08) & (x[0] >= 165) & (x[1] >= 30)
    inst = lambda x: x[2] > 49.5
    loads = {}
    halfF = lambda F: F / 2
    for name, sel, Fz in (
            ('fall_toe', toe, halfF(FALL)), ('fall_heel', heel, halfF(FALL)), ('fall_toe_corner', corner, halfF(FALL)),
            ('bw3_toe', toe, halfF(BW3)), ('bw3_heel', heel, halfF(BW3))):
        fi, area, _ = F.facet_load(m, ib, sel, [0, 0, Fz])
        print(name, 'patch', round(area, 1), flush=True)
        loads[name] = fi
    for name, T in (('op_carry', T_CARRY), ('op_need_1p5', T_NEED)):
        FT, FA = T / COP, T / LEVER
        fi, a1, _ = F.facet_load(m, ib, toe, [0, 0, halfF(FT)])
        fj, a2, _ = F.facet_load(m, ib, inst, [0, 0, -halfF(FA)])
        print(name, 'toe', round(a1, 1), 'instep', round(a2, 1), 'FT', round(FT, 1), 'FA', round(FA, 1), flush=True)
        loads[name] = fi + fj
    solved = solve_loads(m, ib, K, fix, loads, reg['al'])
    # membrane σ_xx in the top skin, away from the flange, for the buckling bay
    u = solved['fall_toe'][1]
    c = cent
    skin = np.where((c[2] > 16) & (c[2] < 18.2) & (c[0] > 50) & (c[0] < 150) & (np.abs(c[1] - 16) > 6))[0]
    skin = np.intersect1d(skin, reg['al'])
    sig = F.stress_tensor(m, ib, u, skin) if len(skin) else None
    membrane = None
    if sig is not None:
        membrane = dict(n=int(len(skin)), sxx_mean=float(sig[0, 0].mean()), sxx_p95=float(np.percentile(sig[0, 0], 95)),
                        szz_mean=float(sig[2, 2].mean()))
        print('top skin membrane', membrane, flush=True)
    cases = {k: v[0] for k, v in solved.items()}
    meta['top_skin_fall_toe'] = membrane
    pack('fea_foot_h%g' % h, meta, cases)
    del solved, u, sig
    gc.collect()
    # Separate file so a contact failure does not drop the linear result above.
    try:
        contact = {}
        for name, sel, Fz in (('fall_toe', toe, halfF(FALL)), ('fall_heel', heel, halfF(FALL))):
            contact[name] = sole_contact(m, ib, K, fix, reg['al'], sel, Fz, 'contact_' + name)
        F.save('fea_foot_contact_h%g' % h, dict(part='foot_contact', h_mm=h, cases=contact,
               note='Unilateral penalty on the toe or heel patch. Flange fixed. '
                    'Ground approach scaled to the half-model fall load. 3 BW is half of this while the active set stays in compression.'))
        print('SOLE_CONTACT_DONE', flush=True)
    except Exception as ex:
        print('SOLE_CONTACT_FAILED', repr(ex), flush=True)

def _solids(s):
    return len(s.solids().vals())

def masses():
    al = foot_al()
    print('foot', round(al_mass(al), 4), 'solids', _solids(al))
    cl, fr = clamp_geom(True)
    print('clamp fillet', fr, round(al_mass(cl), 4), 'solids', _solids(cl))
    ring = hip_ring()
    print('ring', round(al_mass(ring), 4), 'solids', _solids(ring))
    fused, body = clevis_geom()
    print('clevis al', round(al_mass(body), 4), 'body solids', _solids(body), 'fused solids', _solids(fused))
    fused, body = ktongue_geom()
    print('ktongue al', round(al_mass(body), 4), 'solids', _solids(body), 'fused', _solids(fused))
    fused, body = fork_geom()
    print('fork al', round(al_mass(body), 4), 'solids', _solids(body), 'fused', _solids(fused))
    tongue = tongue_geom()
    print('tongue', round(al_mass(tongue), 4), 'solids', _solids(tongue))
    print('FALL', round(FALL, 2), 'BW3', round(BW3, 2), 'carry screw', round(T_CARRY / LEVER, 1))

if __name__ == '__main__':
    cmd = sys.argv[1]
    h = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    if cmd == 'mass':
        masses()
    elif cmd == 'ring':
        run_ring(h)
    elif cmd == 'clamp':
        run_clamp(h)
    elif cmd in ('clevis', 'ktongue', 'fork'):
        _pin_part(cmd, h)
    elif cmd == 'tongue':
        run_tongue(h)
    elif cmd == 'foot':
        run_foot(h)
    else:
        raise SystemExit('unknown ' + cmd)
