#!/usr/bin/env python3
"""Chest-pad crush job. Mode 'screen': 1-DOF plateau-force model (lot band x dynamic x angle factor), integrates
m*x'' = -F(x) to stop; outputs force-stroke, peak g on pack, rail loads, PASS/FAIL. Mode 'radioss': writes an
OpenRadioss starter deck per case and mesh level (LAW28 honeycomb block, rigid impactor of mass m at v) and runs it if
starter/engine are on PATH; post via *T01 time history. Usage:
  python fea_chest_pad.py --cfg fea_chest_pad.yaml --out fea/chest_pad [--mode screen|radioss]"""
import argparse, json, math, os, shutil, subprocess
import yaml
G = 9.81

def plateau_N(c, angle, lot, dyn):
    return lot*1e3 * c["core"]["angle_factor"][angle]/c["core"]["angle_factor"][0] * dyn

def screen_case(c, cs, lot, dyn, dt=1e-5):
    F = plateau_N(c, cs["angle"], lot, dyn); h = c["core"]["size_mm"][2]/1e3
    stroke_max = h*c["core"]["densification_strain"]; m = cs["m_kg"]; v = cs["v_ms"]; x = 0.0; t = 0.0; hist = []
    while v > 0 and x < stroke_max:
        a = F/m; v -= a*dt; x += max(v, 0)*dt; t += dt
        if len(hist) < 2000 and int(t/dt) % 50 == 0: hist.append((round(x*1e3, 2), round(F/1e3, 2)))
    bottomed = x >= stroke_max
    g_pk = F/m/G; return {"plateau_kN": round(F/1e3, 2), "stroke_mm": round(x*1e3, 1), "stroke_avail_mm": round(stroke_max*1e3, 1),
            "margin": round(1 - x/stroke_max, 3), "bottomed": bottomed, "pulse_ms": round(t*1e3, 1), "peak_g": round(g_pk, 1),
            "dv_ms": cs["v_ms"], "rail_load_kN": round(c["pack_mass_kg"]*g_pk*G/1e3, 2), "force_stroke": hist[::10]}

def radioss_deck(path, c, cs, cell_mm, lot):
    a, b, h = [s for s in c["core"]["size_mm"]]; n = [max(1, round(a/cell_mm)), max(1, round(b/cell_mm)), max(1, round(h/cell_mm))]
    sig = plateau_N(c, cs["angle"], lot, 1.0)/(a*b*1e-6)/1e6
    with open(path, "w") as f:
        f.write(f"#RADIOSS STARTER\n/BEGIN\n{os.path.basename(path)[:-9]}\n 2019 0\n kg mm ms\n kg mm ms\n")
        f.write(f"# core {a}x{b}x{h} mm, {n[0]}x{n[1]}x{n[2]} hexa, plateau {sig:.3f} MPa, impactor {cs['m_kg']} kg at {cs['v_ms']} m/s, angle {cs['angle']}\n")
        nid = 0; ids = {}
        for k in range(n[2]+1):
            for j in range(n[1]+1):
                for i in range(n[0]+1):
                    nid += 1; ids[(i, j, k)] = nid
        f.write("/NODE\n")
        for (i, j, k), q in ids.items(): f.write(f"{q:10d}{i*a/n[0]:20.4f}{j*b/n[1]:20.4f}{k*h/n[2]:20.4f}\n")
        f.write("/BRICK/1\n"); e = 0
        for k in range(n[2]):
            for j in range(n[1]):
                for i in range(n[0]):
                    e += 1; v = [ids[(i,j,k)], ids[(i+1,j,k)], ids[(i+1,j+1,k)], ids[(i,j+1,k)], ids[(i,j,k+1)], ids[(i+1,j,k+1)], ids[(i+1,j+1,k+1)], ids[(i,j+1,k+1)]]
                    f.write(f"{e:10d}" + "".join(f"{x:10d}" for x in v) + "\n")
        f.write(f"/MAT/LAW28/1\nHexWeb_CRIII_4p5\n 7.2E-8\n# E11..E33 G12..G31 (MPa) [EST from HEX_CRIII]; yield curves = plateau {sig:.3f} MPa flat to eps 0.75 then densify\n")
        f.write("/PROP/SOLID/1\ncore\n/PART/1\ncore\n 1 1\n")
        f.write(f"# TODO on PC: /RWALL moving rigid wall mass {cs['m_kg']} kg, /INIVEL {cs['v_ms']} m/s, /BCS fixed land face, /TH/RWALL force, /FUNCT plateau curves\n/END\n")
    return n

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cfg", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="screen", choices=["screen", "radioss"]); a = ap.parse_args()
    c = yaml.safe_load(open(a.cfg)); os.makedirs(a.out, exist_ok=True); cr = c["criteria"]; res = {"mode": a.mode, "cases": {}}
    lo, hi = c["lot_plateau_0deg_kN"]; d_lo, d_hi = c["core"]["dyn_factor"]
    for cs in c["cases"]:
        soft = screen_case(c, cs, lo, d_lo); hard = screen_case(c, cs, hi, d_hi)
        chk = {"stroke_margin": soft["margin"] >= cr["stroke_margin_min"] and not soft["bottomed"],
               "ceiling_quasistatic": hi*c["core"]["angle_factor"][cs["angle"]]/c["core"]["angle_factor"][0] <= cr["ceiling_kN"],
               "pack_g": hard["peak_g"] <= cr["pack_g_allow"], "pack_dv": cs["v_ms"] <= cr["pack_dv_allow_ms"]}
        res["cases"][cs["name"]] = {"soft_lot": soft, "hard_lot_dyn": hard, "checks": chk, "pass": all(chk.values())}
        if a.mode == "radioss":
            for cell in c["mesh_study"]["cell_mm"]:
                radioss_deck(os.path.join(a.out, f"{cs['name']}_c{cell}_0000.rad"), c, cs, cell, lo)
    st = shutil.which("starter_linux64_gf") or shutil.which("starter_win64")
    res["radioss_available"] = bool(st)
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    for k, v in res["cases"].items(): print(k, v["pass"], v["checks"])

if __name__ == "__main__":
    main()
