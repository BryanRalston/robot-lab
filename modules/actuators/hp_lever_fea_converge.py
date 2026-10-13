"""Mesh-convergence study for the needle hip_pitch lever (O13).

Runs hp_lever_fea.py at h = 4, 3, 2.5, 2 mm and at h = 2 mm with a gmsh
Field Box of 1.5 mm on the arm/cheek junctions. Richardson-extrapolates the
symmetric phi -60 peak. If SF_yield on that peak is below 1.5, increases d0
by 1 mm and repeats. Writes one JSON per mesh, a convergence plot, the
updated results/hp_lever_fea_r4.json, and the O13 report.
"""
import json, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
PY = os.environ.get("FEA_PYTHON", sys.executable)
SCRIPT = os.path.join(H, "hp_lever_fea.py")
RES = os.path.join(H, "results")
SY = 503.0
CASES = [f"{k}_phi{ph:+d}" for ph in (-90, -60, -30, 0, 30, 60, 90) for k in ("sym", "fault")]


def _name(h, h_local, d0):
    hs = f"{h:g}".replace(".", "p")
    loc = f"_local{h_local:g}".replace(".", "p") if h_local else ""
    d0s = "" if abs(d0 - 25) < 1e-9 else f"_d0{d0:g}".replace(".", "p")
    return f"hp_lever_fea_h{hs}{loc}{d0s}.json"


def run_one(b, d0, d1, fr, h, h_local=None, export=False):
    dest = os.path.join(RES, _name(h, h_local, d0))
    env = os.environ.copy()
    env["HUB"] = "needle"
    env["ROOT"] = "37.5,26"
    env["FEATAG"] = _name(h, h_local, d0).replace(".json", "")
    env.setdefault("NTHREADS", "8")
    env.setdefault("OMP_NUM_THREADS", "8")
    env.setdefault("MKL_NUM_THREADS", "8")
    env.setdefault("OPENBLAS_NUM_THREADS", "8")
    env.pop("HLOCAL", None)
    cmd = [PY, "-u", SCRIPT, str(b), str(d0), str(d1), str(fr), str(h), "--out", dest]
    if h_local:
        env["HLOCAL"] = str(h_local)
    if export:
        env["STEPNAME"] = "hip_pitch_lever_B_needle_sf15"
        cmd.append("--export")
    print("RUN", " ".join(cmd), "HLOCAL", env.get("HLOCAL"), flush=True)
    p = subprocess.run(cmd, env=env, cwd=os.path.dirname(H))
    if p.returncode != 0 or not os.path.isfile(dest):
        raise SystemExit(f"FEA failed h={h} h_local={h_local} d0={d0} rc={p.returncode}")
    return json.load(open(dest))


def _three(series):
    """Three finest (h, value) points, smallest h first."""
    pts = sorted((float(h), float(v)) for h, v in series)
    if len(pts) < 3:
        raise ValueError("need at least 3 uniform meshes")
    return pts[:3]


def richardson(series):
    """vm = vm0 + C h^p from the three finest uniform meshes.

    Returns a dict. p is solved from the ratio of successive differences.
    If the three values are not monotone, or p falls outside [0.4, 4], the
    fit is reported as not asymptotic and vm0 is left None.
    """
    (h3, f3), (h2, f2), (h1, f1) = _three(series)  # h3 < h2 < h1
    d32, d21 = f3 - f2, f2 - f1
    out = dict(h=[h1, h2, h3], f=[f1, f2, f3], monotone=d32 * d21 > 0 and d32 != 0)
    if not out["monotone"]:
        out.update(p=None, C=None, vm0=None, note="three finest values are not monotone")
        return out
    target = (f1 - f2) / (f2 - f3)

    def ratio(p):
        return (h1 ** p - h2 ** p) / (h2 ** p - h3 ** p)

    # ratio(p) decreases from h1/h2 (as p->0, by L'Hopital it's ln ratio) toward 1? 
    # For h1>h2>h3>0 and p>0, ratio > 0. Scan p.
    lo, hi = 0.05, 8.0
    rlo, rhi = ratio(lo), ratio(hi)
    if not (min(rlo, rhi) <= target <= max(rlo, rhi)):
        out.update(p=None, C=None, vm0=None, note=f"no p in ({lo},{hi}) matches difference ratio {target:.4g}")
        return out
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if (ratio(mid) - target) * (rlo - target) > 0:
            lo, rlo = mid, ratio(mid)
        else:
            hi = mid
    p = 0.5 * (lo + hi)
    C = (f2 - f3) / (h2 ** p - h3 ** p)
    vm0 = f3 - C * h3 ** p
    if not (0.4 <= p <= 4.0) or vm0 <= 0:
        out.update(p=p, C=C, vm0=None, note=f"p={p:.3f} outside [0.4, 4] or non-positive intercept")
        return out
    out.update(p=p, C=C, vm0=vm0, note="three-point Richardson on the finest uniform meshes")
    return out


def case_pair(doc, name):
    c = doc["cases"][name]
    return c["vm_max_MPa"], c["vm_p999_MPa"]


def series_for(docs, name, key):
    out = []
    for d in docs:
        if d["params"].get("h_local"):
            continue
        out.append((d["params"]["h"], d["cases"][name][key]))
    return out


def main():
    b, d0, d1, fr = 25.0, 25.0, 15.0, 0.0
    meshes = [(4.0, None), (3.0, None), (2.5, None), (2.0, None), (2.0, 1.5)]
    history = []
    while True:
        docs = []
        for i, (h, hl) in enumerate(meshes):
            docs.append(run_one(b, d0, d1, fr, h, hl, export=(i == len(meshes) - 1)))
        uniform = [d for d in docs if not d["params"].get("h_local")]
        local = [d for d in docs if d["params"].get("h_local")]
        rx = richardson(series_for(docs, "sym_phi-60", "vm_max_MPa"))
        rx999 = richardson(series_for(docs, "sym_phi-60", "vm_p999_MPa"))
        computed = [d["cases"]["sym_phi-60"]["vm_max_MPa"] for d in docs]
        peak_candidates = list(computed)
        if rx["vm0"] is not None:
            peak_candidates.append(rx["vm0"])
        # Pass/fail uses the higher of the extrapolated peak and every computed
        # peak, so an optimistic extrapolation cannot clear the 1.5 line.
        peak = max(peak_candidates)
        sf = SY / peak
        rec = dict(d0=d0, docs=docs, richardson_max=rx, richardson_p999=rx999, peak_MPa=peak, SF_yield=sf)
        history.append(rec)
        print(f"d0={d0:g} Richardson vm0={rx['vm0']} p={rx['p']} governing peak={peak:.2f} SF={sf:.3f}", flush=True)
        if sf >= 1.5 - 1e-9:
            break
        if os.environ.get("FEA_D0_STEP", "0") != "1":
            print(f"SF_yield {sf:.3f} < 1.5 at d0={d0:g}. d0 step is off (set FEA_D0_STEP=1 to continue).", flush=True)
            break
        d0 += 1.0
        if d0 > 36:
            print("stopped: d0 exceeded 36 mm without SF_yield >= 1.5", flush=True)
            break
        print(f"SF_yield {sf:.3f} < 1.5, increasing d0 to {d0:g}", flush=True)
    summary = dict(history=[{k: v for k, v in rec.items() if k != "docs"} | {
        "meshes": [{kk: dd[kk] for kk in ("params", "nodes", "ndof", "tets", "mass_7075_kg", "mass_kg", "worst_sym", "SF_sym", "SF_fault")} | {
            "sym_phi-60": dd["cases"]["sym_phi-60"]
        } for dd in rec["docs"]]
    } for rec in history])
    json.dump(summary, open(os.path.join(RES, "hp_lever_fea_convergence.json"), "w"), indent=1)
    print("wrote", os.path.join(RES, "hp_lever_fea_convergence.json"), flush=True)


if __name__ == "__main__":
    main()
