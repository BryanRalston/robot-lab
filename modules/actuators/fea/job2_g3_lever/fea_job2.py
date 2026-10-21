"""Job 2 — G3 hip-pitch lever FEA (R-031 release candidate).

Imports modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step and
solves it with hp_lever_fea_v2.mesh / hp_lever_fea_v2.solve (pressure on the
ø42 bore, yoke face fixed at |y|=13.5, pin tractions). Design load is the
v2 pin force, 4542 N/pin. The walk case is the same field scaled by
2030/4542 (linear elasticity). Fully reversed amplitude is that von Mises.

Levels: global h = 4, 3, 2 mm with Ball hloc = 1.5, 1.0, 0.6 mm.
Balls (radius 7 mm, as in v2.mesh) sit on the web/arm R8 blends, the bore
lip circle r=21 at |y|=33.5, and the ear roots. The as-built STEP has no
1x45 chamfer and no R1 lip edge; the lip is the sharp bore-end circle.

Run from WSL (Windows Smart App Control blocks the repo venv):
  LEVEL=1 python fea_job2.py          # one level, 1..3
  python fea_job2.py --all            # three levels, one process each
  python fea_job2.py --report         # REPORT.md + plot from the JSON files
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

# v2.mesh hardcodes Ball radius 7 mm and thickness 8 mm. At hloc 0.6 mm that
# support on this STEP was 661k tets (~3.0M P2 dofs) and does not fit the
# 15 GB WSL budget. Radius 5 mm was still 343k tets. Radius 4 mm / thickness
# 4 mm is the same Ball field at 235k tets (~1.1M dofs), which this PC can solve.
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

STEP_RC = os.path.join(ACT, "cad", "hip_pitch_lever_r031_mw_b30_d36_RC.step")
STEP_B35 = os.path.abspath(os.path.join(ACT, "..", "legs", "cad", "hip_pitch_lever_r031_mw_b35_d40.step"))
# Actuators also has a non-merged-web b35/d40. The L47 fallback (mass +0.242 robot)
# is the merged-web solid in legs/cad.
HI = 13.5
F_DESIGN = float(L.F)          # 4542 N
F_WALK = 2030.0
SCALE = F_WALK / F_DESIGN
ALLOW_PEAK = 503.0 / 1.5       # 335.333 MPa
ALLOW_AMP = 87.0 / 1.5         # 58 MPa
LEVELS = ((4.0, 1.5), (3.0, 1.0), (2.0, 0.6))
# Spot centres measured on the RC STEP (see REPORT). Same set is used at every level.
# R8: four web-face corner blends at |y|=38.5 plus the side-fillet centres.
# Bore lip: r=21 circle at |y|=33.5, lower arc (arm) and the +z pressure point.
# Ear root: arm/ear junction and the upper ear blend.


def lip(y, deg):
    a = np.radians(deg)
    return [round(21.0 * np.cos(a), 2), y, round(21.0 * np.sin(a), 2)]


# Level-1 scout (h 4 / 1.5, balls on the R8 corners, the lip and the ear only)
# peaked at (±15.4, ±38.8, -10.4), the upper arm/web corner, which those balls
# missed. These centres cover that corner, the R8 blends at z≈-27, the lower
# bore lip, and the ear-root / phi0 spot near |y|≈60.
SPOTS = [
    # upper arm/web corner (governing scout peak) and the R8 blends
    [15.4, 38.5, -10.4], [-15.4, 38.5, -10.4],
    [15.4, -38.5, -10.4], [-15.4, -38.5, -10.4],
    [15.09, 38.5, -27.3], [-15.09, 38.5, -27.3],
    [15.09, -38.5, -27.3], [-15.09, -38.5, -27.3],
    # bore lip, lower arc (arm side). No 1x45/R1 edge exists on this STEP.
    lip(33.5, -90), lip(33.5, -45), lip(33.5, -135),
    lip(-33.5, -90), lip(-33.5, -45), lip(-33.5, -135),
    # ear roots and the phi0 concentration on the ear rim
    [0.0, 52.0, -50.0], [0.0, -52.0, -50.0],
    [7.0, 59.0, -48.0], [-7.0, 59.0, -48.0],
    [7.0, -59.0, -48.0], [-7.0, -59.0, -48.0],
]
# b35/d40 arm is wider (b=35). The upper web edge runs x=±17.95 at z=-7.92,
# and the R8 blends sit at |x|≈17.7. Ear ø26 is unchanged.
SPOTS_B35 = [
    [17.95, 38.5, -7.92], [-17.95, 38.5, -7.92],
    [17.95, -38.5, -7.92], [-17.95, -38.5, -7.92],
    [0.0, 38.5, -7.92], [0.0, -38.5, -7.92],
    [17.74, 38.5, -25.17], [-17.74, 38.5, -25.17],
    [17.74, -38.5, -25.17], [-17.74, -38.5, -25.17],
    lip(33.5, -90), lip(33.5, -45), lip(33.5, -135),
    lip(-33.5, -90), lip(-33.5, -45), lip(-33.5, -135),
    [13.0, 51.0, -51.1], [-13.0, 51.0, -51.1],
    [13.0, -51.0, -51.1], [-13.0, -51.0, -51.1],
]
if os.environ.get("SPOTSET") == "b35":
    SPOTS = SPOTS_B35


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
    """Confirm the v2 selectors still land on this STEP before the solve."""
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
    return dict(vm_MPa=float(vm[i]), at_mm=at, p999_MPa=float(np.percentile(vm[ev], 99.9)))


def write_level(rec):
    path = os.path.join(HERE, f"level_{rec['tag']}_h{rec['h_mm']:g}_l{rec['hloc_mm']:g}.json")
    json.dump(rec, open(path, "w"), indent=1)
    print("WROTE", path, flush=True)
    print(f"PEAK {rec['governing']} {rec['peak_MPa']:.2f} MPa at {rec['peak_at_mm']}  amp {rec['amplitude_MPa']:.2f}", flush=True)
    return path


def main_level(index, step, tag):
    h, hloc = LEVELS[index]
    # wrap run so counts are captured. V.mesh prints nothing; recount by re-reading is wasteful.
    # run_level prints SOLVE/SOLVED lines. Counts are stored inside by patching below.
    shape, mass = load_shape(step)
    fn = os.path.join(tempfile.gettempdir(), f"job2_{tag}_h{h:g}_l{hloc:g}")
    print(f"MESH {tag} h={h} hloc={hloc} spots={len(SPOTS)} vol={mass['volume_mm3']:.1f}", flush=True)
    m = V.mesh(shape, h, hloc, fn, SPOTS)
    nodes, tets = int(m.p.shape[1]), int(m.t.shape[1])
    faces = facet_report(m)
    print("FACETS", json.dumps(faces), "nodes", nodes, "tets", tets, flush=True)
    if any(v == 0 for v in faces["pin_facets"].values()) or any(v == 0 for v in faces["bore_facets"].values()) or faces["yoke_facets"] == 0:
        raise RuntimeError(f"boundary selector missed a face: {faces}")
    if os.environ.get("MESH_ONLY"):
        print("MESH_ONLY", nodes, tets, flush=True)
        return
    print("SOLVE", flush=True)
    ib, U = V.solve(m)
    ndof = int(ib.N)
    print(f"SOLVED ndof={ndof}", flush=True)
    C = V.cases(U)
    # pin displacement at |y|~69 (mid pin stub), governing sym cases only
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
    del C, ib
    gc.collect()
    fault = max((k for k in out if not k.startswith("sym_")), key=lambda k: out[k]["vm_MPa"])
    sel = np.where(ev)[0]
    keep = sel[(gov_vm[sel] > 0.25 * gov_peak) | (np.arange(sel.size) % 12 == 0)]
    # cap the cloud so the npz stays small
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
    del gov_vm, m, c
    gc.collect()
    rec = dict(
        tag=tag,
        step=step.replace("\\", "/"),
        h_mm=h, hloc_mm=hloc, ball_r_mm=BALL_R, ball_t_mm=BALL_T,
        n_spots=len(SPOTS), spots=SPOTS,
        nodes=nodes, tets=tets, ndof=ndof,
        facets=faces, mass=mass,
        material=dict(name="7075-T6", E_MPa=L.E, nu=L.NU, Sy_MPa=503.0, Su_MPa=572.0, Se_MPa=87.0),
        governing=gov_name,
        fault_governing=fault,
        peak_MPa=out[gov_name]["vm_MPa"],
        peak_at_mm=out[gov_name]["at_mm"],
        p999_MPa=out[gov_name]["p999_MPa"],
        amplitude_MPa=out[gov_name]["vm_MPa"] * SCALE,
        amplitude_at_mm=out[gov_name]["at_mm"],
        fault_peak_MPa=out[fault]["vm_MPa"],
        fault_at_mm=out[fault]["at_mm"],
        fault_amplitude_MPa=out[fault]["vm_MPa"] * SCALE,
        pin_disp_mm=disp,
        scale_walk=SCALE, F_design_N=F_DESIGN, F_walk_N=F_WALK,
        allow_peak_MPa=ALLOW_PEAK, allow_amp_MPa=ALLOW_AMP,
        cases={k: dict(vm_MPa=v["vm_MPa"], at_mm=v["at_mm"], amp_MPa=v["vm_MPa"] * SCALE,
                       p999_MPa=v["p999_MPa"]) for k, v in out.items()},
    )
    write_level(rec)


if __name__ == "__main__":
    tag = os.environ.get("TAG", "rc")
    step = os.environ.get("STEP", STEP_RC)
    if "--all" in sys.argv:
        raise SystemExit("use the shell driver")
    idx = int(os.environ.get("LEVEL", "1")) - 1
    main_level(idx, step, tag)
