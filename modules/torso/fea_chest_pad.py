#!/usr/bin/env python3
"""Chest-pad crush job (T-031 / R-146). Modes:
  screen  : 1-DOF plateau-force model per case and lot bound -> force-stroke, pack g, rail load, PASS/FAIL (runs anywhere).
  radioss : writes complete OpenRadioss decks (<case>_c<cell>_0000.rad starter + _0001.rad engine) per case x mesh level:
            honeycomb block (LAW28 with plateau yield curves from the lot bound), bonded land (fixed BCS), moving rigid
            wall with impactor mass and initial velocity, rigid-wall force time history; runs them if --radioss DIR given.
Post: fea_chest_pad_post.py turns the TH CSVs into pass/fail JSON.
Usage: python fea_chest_pad.py --cfg fea_chest_pad.yaml --out fea/chest_pad [--mode screen|radioss] [--radioss /path/OpenRadioss]"""
import argparse, json, os, subprocess
import yaml
G = 9.81

def plateau_N(c, angle, lot, dyn):
    af = c["core"]["angle_factor"]; return lot*1e3*af[angle]/af[0]*dyn

def screen_case(c, cs, lot, dyn, dt=1e-5):
    F = plateau_N(c, cs["angle"], lot, dyn); m = cs["m_kg"]; h = c["core"]["size_mm"][2]/1e3
    smax = h*c["core"]["densification_strain"]
    if "F_peak_kN" in cs:   # force-driven case (from sim): elastic if below plateau
        Fp = cs["F_peak_kN"]*1e3; g = Fp/m/G
        return {"plateau_kN": round(F/1e3, 2), "F_kN": cs["F_peak_kN"], "elastic": Fp < F, "stroke_mm": 0.0, "stroke_avail_mm": round(smax*1e3, 1),
                "margin": 1.0, "bottomed": False, "peak_g": round(g, 1), "rail_load_kN": round(c["pack_mass_kg"]*g*G/1e3, 2), "force_stroke": []}
    v = cs["v_ms"]; x = t = 0.0; hist = []
    while v > 0 and x < smax:
        v -= F/m*dt; x += max(v, 0)*dt; t += dt
        if int(t/dt) % 200 == 0: hist.append((round(x*1e3, 1), round(F/1e3, 2)))
    g = F/m/G
    return {"plateau_kN": round(F/1e3, 2), "F_kN": round(F/1e3, 2), "elastic": False, "stroke_mm": round(x*1e3, 1), "stroke_avail_mm": round(smax*1e3, 1),
            "margin": round(1-x/smax, 3), "bottomed": x >= smax, "pulse_ms": round(t*1e3, 1), "peak_g": round(g, 1),
            "rail_load_kN": round(c["pack_mass_kg"]*g*G/1e3, 2), "force_stroke": hist}

def checks(c, cs, soft, hard):
    cr = c["criteria"]; af = c["core"]["angle_factor"]; Fmax = max(soft["F_kN"], hard["F_kN"])
    return {"stroke_margin": soft["margin"] >= cr["stroke_margin_min"] and not soft["bottomed"],
            "ceiling_quasistatic": c["lot_plateau_0deg_kN"][1]*af[cs["angle"]]/af[0] <= cr["ceiling_kN"],
            "pack_g": hard["peak_g"] <= cr["pack_g_allow"],
            "land_stress": Fmax*cr["land_MPa_per_kN"] <= cr["land_allow_MPa"],
            "rail_stress": hard["rail_load_kN"]*cr["rail_MPa_per_kN"] <= cr["rail_allow_MPa"],
            "pack_dv_enveloped_by_T4": cs.get("v_ms", 0) <= cr["pack_dv_allow_ms"]}

def f10(*v): return "".join(f"{x:>10}" for x in v) + "\n"
def f20(*v): return "".join(f"{x:>20}" for x in v) + "\n"

def radioss_deck(base, c, cs, cell, lot):
    """Units: Mg, mm, s (N, MPa). Core block 0..a x 0..b in y,z; crush axis = x (pad normal), land at x=0, face at x=h."""
    a, b, h = c["core"]["size_mm"][0], c["core"]["size_mm"][1], c["core"]["size_mm"][2]
    nx, ny, nz = max(2, round(h/cell)), max(2, round(a/cell)), max(2, round(b/cell))
    sig = plateau_N(c, cs["angle"], lot, 1.0)/(a*b)   # MPa, quasi-static plateau from lot bound
    rho = 72.0e-12                                    # 4.5 pcf = 72 kg/m3 -> Mg/mm3
    m = cs["m_kg"]*1e-3; v = cs.get("v_ms", 3.0)*1e3  # Mg, mm/s
    name = os.path.basename(base)
    ids = {}; nid = 0
    with open(base + "_0000.rad", "w") as f:
        f.write(f"#RADIOSS STARTER\n/BEGIN\n{name}\n      2022         0\n                  Mg                  mm                   s\n                  Mg                  mm                   s\n")
        f.write("/NODE\n")
        for k in range(nz+1):
            for j in range(ny+1):
                for i in range(nx+1):
                    nid += 1; ids[(i, j, k)] = nid
                    f.write(f"{nid:>10}" + f20(f"{i*h/nx:.4f}", f"{j*a/ny-a/2:.4f}", f"{k*b/nz-b/2:.4f}"))
        f.write("/BRICK/1\n"); e = 0
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    e += 1; q = [ids[(i,j,k)], ids[(i+1,j,k)], ids[(i+1,j+1,k)], ids[(i,j+1,k)], ids[(i,j,k+1)], ids[(i+1,j,k+1)], ids[(i+1,j+1,k+1)], ids[(i,j+1,k+1)]]
                    f.write(f10(e, *q))
        land = [ids[(0, j, k)] for j in range(ny+1) for k in range(nz+1)]
        face = [ids[(nx, j, k)] for j in range(ny+1) for k in range(nz+1)]
        f.write("/GRNOD/NODE/1\nland\n" + "".join(f10(*land[i:i+10]) for i in range(0, len(land), 10)))
        f.write("/GRNOD/NODE/2\nface\n" + "".join(f10(*face[i:i+10]) for i in range(0, len(face), 10)))
        # LAW28 honeycomb: E11 (crush axis) from HEX_CRIII stabilized modulus 150 ksi = 1034 MPa; transverse weak.
        f.write("/MAT/LAW28/1\nHexWeb_CRIII_5052_4p5pcf\n" + f20(f"{rho:.4e}"))
        f.write(f20("1034.0", "1.0", "1.0") + f20("483.0", "1.0", "214.0"))   # E11 E22 E33 ; G12 G23 G31 (L 70 ksi, W 31 ksi)
        f.write(f10(1, 2, 2, 1, 1, 1) + f20("1.0", "1.0", "1.0") + f20("1.0", "1.0", "1.0"))   # yield fct ids + scale factors (sig11 uses fct 1)
        f.write(f20("0.70", "0.70", "0.70"))   # strain at full compaction (densification)
        f.write(f"/FUNCT/1\nplateau_axial_{lot}kN\n" + f20("0.0", f"{sig:.4f}") + f20("0.60", f"{sig:.4f}") + f20("0.70", f"{sig*1.5:.4f}") + f20("0.80", f"{sig*20:.4f}"))
        f.write("/FUNCT/2\ntransverse_weak\n" + f20("0.0", "0.10") + f20("1.0", "0.10"))
        f.write("/PROP/SOLID/1\ncore\n" + f10(0, 0, 0, 0, 0, 0) + f20("0", "0", "0") + "\n")
        f.write("/PART/1\ncore\n" + f10(1, 1, 0))
        f.write("/BCS/1\nland_bonded\n   111 111         0         1\n")
        # moving plane rigid wall = impactor (effective mass m at v toward -x), starts at the face
        f.write("/RWALL/PLANE/1\nimpactor\n" + f10(0, 0, 0, 2) + f20("0.0", "0.0") + f20(f"{m:.6e}", f"{-v:.4f}") +
                f20(f"{h+0.05:.4f}", "0.0", "0.0") + f20(f"{h+1.05:.4f}", "0.0", "0.0"))
        f.write("/TH/RWALL/1\nrwall\nDEF\n         1\n/TH/NODE/1\nface\nDEF\n" + f10(face[len(face)//2], 0))
        f.write("/END\n")
    tend = 0.06 if "v_ms" in cs else 0.03
    with open(base + "_0001.rad", "w") as f:
        f.write(f"/RUN/{name}/1\n{tend}\n/TFILE/0\n1.0e-5\n/ANIM/DT\n0.0 0.002\n/ANIM/ELEM/EPSP\n/DT/NODA/CST/0\n0.67 1.0e-8\n/END\n")
    return nx*ny*nz

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cfg", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="screen", choices=["screen", "radioss"]); ap.add_argument("--radioss", help="OpenRadioss root (has exec/)")
    ap.add_argument("--only", help="run only this case name"); ap.add_argument("--cells", help="comma list overriding mesh_study")
    a = ap.parse_args(); c = yaml.safe_load(open(a.cfg)); os.makedirs(a.out, exist_ok=True)
    lo, hi = c["lot_plateau_0deg_kN"]; dlo, dhi = c["core"]["dyn_factor"]; res = {"mode": a.mode, "cases": {}}
    cells = [float(x) for x in a.cells.split(",")] if a.cells else c["mesh_study"]["cell_mm"]
    for cs in c["cases"]:
        if a.only and cs["name"] != a.only: continue
        soft, hard = screen_case(c, cs, lo, dlo), screen_case(c, cs, hi, dhi)
        ch = checks(c, cs, soft, hard)
        r = {"soft_lot": soft, "hard_lot_dyn": hard, "checks": ch, "pass": all(v for k, v in ch.items() if k != "pack_dv_enveloped_by_T4"),
             "note": "Δv beyond UN T4 envelope -> TP-G5-17 drop test" if not ch["pack_dv_enveloped_by_T4"] else ""}
        if a.mode == "radioss" and "v_ms" in cs:
            r["decks"] = []
            for cell in cells:
                for tag, lot in (("lo", lo), ("hi", hi)):
                    base = os.path.join(a.out, f"{cs['name']}_{tag}_c{int(cell)}")
                    n = radioss_deck(base, c, cs, cell, lot); r["decks"].append({"base": base, "elems": n})
                    if a.radioss:
                        ex = os.path.join(a.radioss, "exec"); env = {**os.environ, "RAD_CFG_PATH": os.path.join(a.radioss, "hm_cfg_files"),
                              "LD_LIBRARY_PATH": os.path.join(a.radioss, "extlib", "hm_reader", "linux64") + ":" + os.path.join(a.radioss, "extlib", "h3d", "lib", "linux64")}
                        d = os.path.dirname(base) or "."; nm = os.path.basename(base)
                        for exe, sfx in (("starter_linux64_gf", "_0000.rad"), ("engine_linux64_gf", "_0001.rad")):
                            subprocess.run([os.path.join(ex, exe), "-i", nm + sfx, "-nt", "4"], cwd=d, env=env, capture_output=True)
                        subprocess.run([os.path.join(ex, "th_to_csv_linux64_gf"), nm + "T01"], cwd=d, env=env, capture_output=True)
        res["cases"][cs["name"]] = r
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    for k, v in res["cases"].items(): print(k, "PASS" if v["pass"] else "FAIL", {kk: vv for kk, vv in v["checks"].items() if not vv})

if __name__ == "__main__":
    main()
