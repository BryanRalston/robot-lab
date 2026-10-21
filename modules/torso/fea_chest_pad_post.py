#!/usr/bin/env python3
"""Post-process OpenRadioss chest-pad runs: reads <base>T01.csv (th_to_csv), extracts rigid-wall force vs impactor
displacement, peak force, stroke, pack g (= F/m), rail load (= pack mass x g), mesh convergence (last two levels <= 5 %),
and writes pass/fail JSON. Usage: python fea_chest_pad_post.py --cfg fea_chest_pad.yaml --dir fea/chest_pad"""
import argparse, csv, glob, json, os, re
import yaml
G = 9.81

def read_th(path):
    rows = list(csv.reader(open(path)))
    hdr = [h.strip().upper() for h in rows[0]]; data = [[float(x) for x in r] for r in rows[1:] if r]
    col = lambda pat: next(i for i, h in enumerate(hdr) if re.search(pat, h))
    t = [r[0] for r in data]; F = [abs(r[col(r"RWALL.*(FNX|FN|FX)")]) for r in data]
    try: X = [abs(r[col(r"(DX|X).*NODE|NODE.*(DX|X)")]) for r in data]
    except StopIteration: X = [0.0]*len(t)
    return t, F, X

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cfg", required=True); ap.add_argument("--dir", required=True); a = ap.parse_args()
    c = yaml.safe_load(open(a.cfg)); cr = c["criteria"]; h = c["core"]["size_mm"][2]; smax = h*c["core"]["densification_strain"]
    cases = {cs["name"]: cs for cs in c["cases"]}; out = {"runs": {}, "cases": {}}
    for f in sorted(glob.glob(os.path.join(a.dir, "*T01.csv"))):
        base = os.path.basename(f)[:-7]; m = re.match(r"(.+)_(lo|hi)_c(\d+)$", base)
        if not m: continue
        name, lot, cell = m.group(1), m.group(2), int(m.group(3)); cs = cases[name]
        t, F, X = read_th(f); Fpk = max(F)/1e3; stroke = max(X)
        g = Fpk*1e3/cs["m_kg"]/G
        out["runs"][base] = {"case": name, "lot": lot, "cell": cell, "F_peak_kN": round(Fpk, 2), "stroke_mm": round(stroke, 1),
                             "pack_g": round(g, 1), "rail_kN": round(c["pack_mass_kg"]*g*G/1e3, 2),
                             "force_stroke": [(round(X[i], 1), round(F[i]/1e3, 2)) for i in range(0, len(t), max(1, len(t)//200))]}
    for name in cases:
        runs = [r for r in out["runs"].values() if r["case"] == name]
        if not runs: continue
        res = {}
        for lot in ("lo", "hi"):
            rr = sorted([r for r in runs if r["lot"] == lot], key=lambda r: -r["cell"])
            if len(rr) >= 2:
                d = abs(rr[-1]["F_peak_kN"] - rr[-2]["F_peak_kN"])/rr[-1]["F_peak_kN"]; ds = abs(rr[-1]["stroke_mm"] - rr[-2]["stroke_mm"])/max(rr[-1]["stroke_mm"], 1e-6)
                res[f"converged_{lot}"] = max(d, ds) <= c["mesh_study"]["max_change"]
            if rr: res[f"fine_{lot}"] = rr[-1]
        lo, hi = res.get("fine_lo"), res.get("fine_hi")
        chk = {}
        if lo: chk["stroke_margin"] = 1 - lo["stroke_mm"]/smax >= cr["stroke_margin_min"]
        if hi: chk.update({"ceiling": hi["F_peak_kN"] <= cr["ceiling_kN"]*max(c["core"]["dyn_factor"]), "pack_g": hi["pack_g"] <= cr["pack_g_allow"],
                           "land": hi["F_peak_kN"]*cr["land_MPa_per_kN"] <= cr["land_allow_MPa"], "rail": hi["rail_kN"]*cr["rail_MPa_per_kN"] <= cr["rail_allow_MPa"]})
        chk.update({k: v for k, v in res.items() if k.startswith("converged")})
        out["cases"][name] = {"checks": chk, "pass": bool(chk) and all(chk.values())}
    json.dump(out, open(os.path.join(a.dir, "post_results.json"), "w"), indent=1)
    print({k: v["pass"] for k, v in out["cases"].items()} or "no T01.csv found")

if __name__ == "__main__":
    main()
