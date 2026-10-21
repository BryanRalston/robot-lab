"""Job 2R — G3 hip-pitch lever FEA, brief G3-R2.

Reuses hp_lever_fea_v2.mesh / solve (gmsh Ball fields, P2 tets, pyamg CG).
Same loads as job 2: design 4542 N/pin, fatigue amplitude = that von Mises
times 2030/4542 (R = -1). No hex8 solver.

Levels: h/hloc = 4/1.5, 3/1.0, 2.5/0.6. Ball radius 4 mm, thickness 4 mm,
14 centres only (4 upper R8, 4 ear-root R5, 4 lower R8, 2 bore lips).
If a mesh exceeds 300k tets the driver drops the radius to 3 mm.

Run from the WSL venv (Windows Smart App Control blocks the repo venv):
  LEVEL=1 TAG=a python fea_job2r.py
  MESH_ONLY=1 LEVEL=3 TAG=a python fea_job2r.py
"""
from __future__ import annotations

import gc
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ACT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ACT)

import hp_lever_fea as L  # noqa: E402
import hp_lever_fea_v2 as V  # noqa: E402
import cadquery as cq  # noqa: E402
import gmsh  # noqa: E402

# v2.mesh hardcodes Ball radius 7 / thickness 8. G3-R2 uses 4 / 4.
BALL_R = float(os.environ.get("BALL_R", "4"))
BALL_T = float(os.environ.get("BALL_T", "4"))
_set_number = gmsh.model.mesh.field.setNumber


def _set_number_job(tag, name, value):
    if name == "Radius":
        value = BALL_R
    elif name == "Thickness":
        value = BALL_T
    return _set_number(tag, name, value)


gmsh.model.mesh.field.setNumber = _set_number_job

STEP_A = os.path.join(ACT, "cad", "hip_pitch_lever_g3_b34_d40_e26.step")
STEP_B = os.path.join(ACT, "cad", "hip_pitch_lever_g3_b30_d36_e26.step")
HI = 13.5
F_DESIGN = float(L.F)  # 4542 N
F_WALK = 2030.0
SCALE = F_WALK / F_DESIGN
ALLOW_PEAK = 271.0  # 7075-T651 plate, ST, 2.001-2.5 in, single path (R-128)
ALLOW_AMP = 58.0
LEVELS = ((4.0, 1.5), (3.0, 1.0), (2.5, 0.6))
TET_CAP = 300000


def _signs(x, y, z):
    return [[sx * x, sy * y, z] for sx in (1.0, -1.0) for sy in (1.0, -1.0)]


# Upper R8: 45-degree point on the explicit cylinder (axis at |x|=xa+8, |y|=46.5),
# z=-14 as specified (mid-span of z -24..-6). Probe end-arc mids match these x,y.
# Ear R5: brief centres (±13, ±48, -52), which cover the blend edges.
# Lower R8: midpoint of the filleted web/arm edge (R8 B-spline), both solids.
# Bore lip: arm-side point of the r=21 circle at |y|=33.5, one ball per cheek.
SPOTS = {
    "a": (
        _signs(19.34, 40.84, -14.0)
        + _signs(13.0, 48.0, -52.0)
        + _signs(17.37, 38.50, -25.71)
        + [[0.0, 33.5, -21.0], [0.0, -33.5, -21.0]]
    ),
    "b": (
        _signs(17.34, 40.84, -14.0)
        + _signs(13.0, 48.0, -52.0)
        + _signs(15.09, 38.50, -27.30)
        + [[0.0, 33.5, -21.0], [0.0, -33.5, -21.0]]
    ),
}
FAMILIES = {
    "upper_r8": slice(0, 4),
    "ear_r5": slice(4, 8),
    "lower_r8": slice(8, 12),
    "bore_lip": slice(12, 14),
}


def load_shape(step):
    shape = cq.importers.importStep(step)
    solids = shape.solids().vals()
    if len(solids) != 2 or not shape.val().isValid():
        raise RuntimeError(f"expected 2 valid solids, got {len(solids)}")
    vol = float(sum(x.Volume() for x in solids))
    vp = 2.0 * np.pi * 6.0 ** 2 * 25.0
    mass = dict(
        volume_mm3=vol,
        pin_stub_mm3=vp,
        mass_7075_kg=(vol - vp) * L.RHO,
        mass_pins_kg=vp * 7.85e-6,
        mass_kg=(vol - vp) * L.RHO + vp * 7.85e-6,
        rule="(V - 2*pi*6^2*25)*2.81e-6 + steel pins at 7.85 g/cm^3",
    )
    return shape, mass


def check_mask(c):
    """v2 exclusion: 2.5 mm off the fixed yoke face, and the steel pin stubs."""
    ay = np.abs(c[1])
    return (ay > HI + 2.5) & (ay < 62.0) & ~((ay > 60.5) & (np.hypot(c[0], c[2] + 50.0) < 8.0))


def facet_report(m):
    pin = {}
    for sg in (1, -1):
        fac = m.facets_satisfying(
            lambda x, sg=sg: (sg * x[1] > 62.5) & (np.hypot(x[0], x[2] + 50.0) > 5.7),
            boundaries_only=True)
        pin[str(sg)] = int(fac.size)
    bore = {}
    for cs in (1, -1):
        fac = m.facets_satisfying(
            lambda x, cs=cs: (np.abs(np.hypot(x[0], x[2]) - 21.0) < 0.2)
            & (cs * x[1] > HI - 0.01) & (cs * x[1] < 33.5 + 0.01),
            boundaries_only=True)
        bore[str(cs)] = int(fac.size)
    yoke = m.facets_satisfying(lambda x: np.abs(np.abs(x[1]) - HI) < 0.05, boundaries_only=True)
    return dict(pin_facets=pin, bore_facets=bore, yoke_facets=int(yoke.size))


def summarize_case(vm, c, ev):
    idx = np.where(ev)[0]
    i = idx[int(np.argmax(vm[ev]))]
    at = [round(float(x), 2) for x in c[:, i]]
    return dict(vm_MPa=float(vm[i]), at_mm=at, at_exact=[float(x) for x in c[:, i]],
                p999_MPa=float(np.percentile(vm[ev], 99.9)), elem=int(i))


def family_peaks(vm, c, ev, spots):
    out = {}
    for name, sl in FAMILIES.items():
        best_i = None
        best = -1.0
        for p in spots[sl]:
            d = np.linalg.norm(c - np.asarray(p, dtype=float)[:, None], axis=0)
            m = ev & (d <= BALL_R)
            if not np.any(m):
                continue
            i = int(np.where(m)[0][np.argmax(vm[m])])
            if vm[i] > best:
                best = float(vm[i])
                best_i = i
        if best_i is None:
            out[name] = None
        else:
            out[name] = dict(
                vm_MPa=best,
                amp_MPa=best * SCALE,
                at_mm=[round(float(x), 2) for x in c[:, best_i]],
            )
    return out


def surface_samples(m, c, vm, ev, peak):
    """von Mises 2 mm and 4 mm from the hot spot, inward along the surface normal."""
    p = np.asarray(peak, dtype=float)
    bf = np.asarray(m.boundary_facets())
    tri = m.facets[:, bf]
    fc = m.p[:, tri].mean(axis=1)
    j = int(np.argmin(np.linalg.norm(fc - p[:, None], axis=0)))
    pts = m.p[:, tri[:, j]]
    n = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    n = n / np.linalg.norm(n)
    fidx = int(bf[j])
    owner = m.f2t[:, fidx]
    tet = int(owner[0] if owner[0] >= 0 else owner[1])
    if np.dot(n, fc[:, j] - c[:, tet]) < 0:
        n = -n

    def nearest(q):
        dist = np.linalg.norm(c - q[:, None], axis=0)
        dist = np.where(ev, dist, np.inf)
        i = int(np.argmin(dist))
        return i, float(dist[i])

    # If the tet test pointed the wrong way, the 2 mm inward sample leaves the body.
    i_in, d_in = nearest(p - n * 2.0)
    i_out, d_out = nearest(p + n * 2.0)
    flipped = d_in > d_out + 0.5
    if flipped:
        n = -n
    samples = {}
    for dist in (2.0, 4.0):
        q = p - n * dist
        i, de = nearest(q)
        samples[f"d{dist:g}_mm"] = dict(
            vm_MPa=float(vm[i]),
            amp_MPa=float(vm[i]) * SCALE,
            at_mm=[round(float(x), 2) for x in c[:, i]],
            target_mm=[round(float(x), 2) for x in q],
            elem_dist_mm=round(de, 3),
        )
    samples["outward_normal"] = [round(float(x), 4) for x in n]
    samples["surface_gap_mm"] = round(float(np.linalg.norm(fc[:, j] - p)), 3)
    samples["normal_flipped"] = bool(flipped)
    return samples


def write_level(rec):
    path = os.path.join(HERE, f"level_{rec['tag']}_h{rec['h_mm']:g}_l{rec['hloc_mm']:g}.json")
    json.dump(rec, open(path, "w"), indent=1)
    print("WROTE", path, flush=True)
    print(
        f"PEAK {rec['tag']} {rec['governing']} {rec['peak_MPa']:.2f} MPa "
        f"at {rec['peak_at_mm']} amp {rec['amplitude_MPa']:.2f} "
        f"p999 {rec['p999_MPa']:.2f} tets {rec['tets']}",
        flush=True,
    )
    return path


def main_level(index, step, tag):
    h, hloc = LEVELS[index]
    spots = SPOTS[tag]
    if len(spots) != 14:
        raise RuntimeError(f"expected 14 balls, got {len(spots)}")
    shape, mass = load_shape(step)
    fn = os.path.join(tempfile.gettempdir(), f"job2r_{tag}_h{h:g}_l{hloc:g}")
    print(
        f"MESH {tag} h={h} hloc={hloc} ball_r={BALL_R} ball_t={BALL_T} "
        f"spots={len(spots)} vol={mass['volume_mm3']:.1f}",
        flush=True,
    )
    m = V.mesh(shape, h, hloc, fn, spots)
    nodes, tets = int(m.p.shape[1]), int(m.t.shape[1])
    print(f"TETS {tag} {tets} nodes {nodes} ball_r={BALL_R}", flush=True)
    if tets > TET_CAP and BALL_R > 3.01:
        print(f"NEED_BALL_R=3 {tag} tets={tets}", flush=True)
        raise SystemExit(2)
    faces = facet_report(m)
    print("FACETS", json.dumps(faces), flush=True)
    if any(v == 0 for v in faces["pin_facets"].values()) or any(v == 0 for v in faces["bore_facets"].values()) or faces["yoke_facets"] == 0:
        raise RuntimeError(f"boundary selector missed a face: {faces}")
    if os.environ.get("MESH_ONLY"):
        chk = os.path.join(HERE, f"meshcheck_{tag}.json")
        json.dump(dict(tag=tag, h_mm=h, hloc_mm=hloc, ball_r_mm=BALL_R, ball_t_mm=BALL_T,
                       nodes=nodes, tets=tets, facets=faces, mass=mass), open(chk, "w"), indent=1)
        print(f"MESH_ONLY {nodes} {tets}", flush=True)
        return
    print("SOLVE", flush=True)
    ib, U = V.solve(m)
    ndof = int(ib.N)
    print(f"SOLVED ndof={ndof}", flush=True)
    C = V.cases(U)
    pin = np.where(np.abs(np.abs(ib.doflocs[1]) - 69.0) < 0.6)[0]
    disp = {}
    for name in ("sym_phi+60", "sym_phi-60", "sym_phi+0"):
        if name in C and pin.size:
            disp[name] = float(np.abs(C[name][pin]).max())
    del U
    gc.collect()
    c = m.p[:, m.t].mean(1)
    ev = check_mask(c)
    out = {}
    gov_vm = None
    gov_name = None
    gov_peak = -1.0
    for k, u in list(C.items()):
        vm, _ = V.stress(ib, u)
        rec_c = summarize_case(vm, c, ev)
        out[k] = rec_c
        if k.startswith("sym_") and rec_c["vm_MPa"] > gov_peak:
            gov_peak = rec_c["vm_MPa"]
            gov_name = k
            gov_vm = vm
        else:
            del vm
        del C[k]
        del u
    del C
    gc.collect()
    fault = max((k for k in out if not k.startswith("sym_")), key=lambda k: out[k]["vm_MPa"])
    try:
        samples = surface_samples(m, c, gov_vm, ev, out[gov_name]["at_exact"])
    except Exception as exc:
        samples = dict(error=str(exc))
        print("SAMPLE_FAIL", exc, flush=True)
    try:
        families = family_peaks(gov_vm, c, ev, spots)
    except Exception as exc:
        families = dict(error=str(exc))
        print("FAMILY_FAIL", exc, flush=True)
    sel = np.where(ev)[0]
    keep = sel[(gov_vm[sel] > 0.25 * gov_peak) | (np.arange(sel.size) % 12 == 0)]
    if keep.size > 250000:
        rng = np.random.default_rng(0)
        hi = sel[gov_vm[sel] > 0.45 * gov_peak]
        rest = sel[gov_vm[sel] <= 0.45 * gov_peak]
        take = rng.choice(rest, size=min(80000, rest.size), replace=False) if rest.size else rest
        keep = np.unique(np.concatenate([hi, take]))
    np.savez_compressed(
        os.path.join(HERE, f"field_{tag}_h{h:g}_l{hloc:g}.npz"),
        c=c[:, keep].astype(np.float32),
        vm=gov_vm[keep].astype(np.float32),
        peak_at=np.array(out[gov_name]["at_mm"], dtype=np.float32),
        case=np.array(gov_name),
    )
    del gov_vm, m, c, ib
    gc.collect()
    ratio = out[gov_name]["p999_MPa"] / out[gov_name]["vm_MPa"]
    rec = dict(
        tag=tag,
        step=os.path.relpath(step, ACT).replace("\\", "/"),
        h_mm=h, hloc_mm=hloc, ball_r_mm=BALL_R, ball_t_mm=BALL_T,
        n_spots=len(spots), spots=spots,
        nodes=nodes, tets=tets, ndof=ndof,
        facets=faces, mass=mass,
        material=dict(
            name="7075-T651",
            E_MPa=L.E, nu=L.NU,
            note="E and nu are the job 2 solver values. von Mises here is force-driven, so E cancels. Pass gate is the R-128 ST band, not Sy/1.5.",
            allow_static_MPa=ALLOW_PEAK, allow_amp_MPa=ALLOW_AMP,
        ),
        solver="gmsh Ball + scikit-fem ElementTetP2 + pyamg CG (hp_lever_fea_v2)",
        governing=gov_name,
        fault_governing=fault,
        peak_MPa=out[gov_name]["vm_MPa"],
        peak_at_mm=out[gov_name]["at_mm"],
        p999_MPa=out[gov_name]["p999_MPa"],
        p999_over_peak=ratio,
        amplitude_MPa=out[gov_name]["vm_MPa"] * SCALE,
        amplitude_at_mm=out[gov_name]["at_mm"],
        fault_peak_MPa=out[fault]["vm_MPa"],
        fault_at_mm=out[fault]["at_mm"],
        fault_amplitude_MPa=out[fault]["vm_MPa"] * SCALE,
        families=families,
        surface_samples=samples,
        pin_disp_mm=disp,
        scale_walk=SCALE, F_design_N=F_DESIGN, F_walk_N=F_WALK,
        allow_peak_MPa=ALLOW_PEAK, allow_amp_MPa=ALLOW_AMP,
        cases={k: dict(vm_MPa=v["vm_MPa"], at_mm=v["at_mm"], amp_MPa=v["vm_MPa"] * SCALE,
                       p999_MPa=v["p999_MPa"]) for k, v in out.items()},
    )
    write_level(rec)


if __name__ == "__main__":
    tag = os.environ.get("TAG", "a")
    step = os.environ.get("STEP", STEP_A if tag == "a" else STEP_B)
    idx = int(os.environ.get("LEVEL", "1")) - 1
    main_level(idx, step, tag)
