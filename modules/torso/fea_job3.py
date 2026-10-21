#!/usr/bin/env python3
"""FEA job 3: torso pocketing. Builds parametric torso (gmsh OCC), fragments all parts into one
conformal mesh (shared interface nodes), exports torso_r1.step, writes a CalculiX deck per load case,
runs ccx, parses .dat for max von Mises -> SF per material, land deflection, frequency (LC6) and
buckling factor (LC1), and writes PASS/FAIL per criterion to results.json.
Usage: python fea_job3.py --cfg fea_job3.yaml --out fea/job3 [--coarse] [--no-solve] [--ccx PATH]"""
import argparse, json, math, os, re, shutil, subprocess
import yaml, gmsh

def build(c):
    g = c["geometry"]; occ = gmsh.model.occ
    b, L, R, sf = g["bulkhead"], g["land"], g["rib"], g["shoulder_flange"]
    zc0 = b["z0"] + b["height_z"]/2
    al = [occ.addBox(b["x0"], -b["width_y"]/2, b["z0"], b["t"], b["width_y"], b["height_z"]),
          occ.addBox(b["x0"]+b["t"], -L["size"]/2, L["z_c"]-L["size"]/2, L["t"], L["size"], L["size"]),
          occ.addBox(b["x0"]-R["h"], -R["t"]/2, L["z_c"]-L["size"]/2, R["h"], R["t"], L["size"])]
    P = g["posts"]
    for y in P["y"]:
        al.append(occ.addBox(b["x0"], y-P["w_y"]/2, 0, b["t"], P["w_y"], b["z0"]))
    bulk, _ = occ.fuse([(3, al[0])], [(3, t) for t in al[1:]])
    cuts = []
    for s in (-1, 1):
        for i in range(sf["n_bolt"]):
            a = 2*math.pi*i/sf["n_bolt"]
            yc = s*sf["y_c"] + sf["bc_dia"]/2*math.cos(a); zc = zc0 + sf["bc_dia"]/2*math.sin(a)
            if abs(yc) < b["width_y"]/2 - sf["bolt_dia"]:
                cuts.append((3, occ.addCylinder(b["x0"]-1, yc, zc, b["t"]+2, 0, 0, sf["bolt_dia"]/2)))
        gr = g["grommet"]
        cuts.append((3, occ.addCylinder(b["x0"]-1, s*gr["y_c"], zc0+gr["z_off"], b["t"]+2, 0, 0, gr["dia"]/2)))
    bi = g["bezel_inserts"]; xf = b["x0"]+b["t"]+L["t"]
    for dy in (-1, 1):
        for dz in (-1, 1):
            cuts.append((3, occ.addCylinder(xf+1, dy*bi["pitch"]*0.4, L["z_c"]+dz*bi["pitch"]*0.4, -9, 0, 0, bi["dia"]/2)))
    bulk, _ = occ.cut(bulk, cuts)
    p = g["partition"]; part = occ.addBox(p["x0"], -p["width_y"]/2, p["z0"], p["t"], p["width_y"], p["height_z"])
    pv = g["pelvis"]; w = pv["wall"]
    po = occ.addBox(-pv["depth_x"]/2, -pv["width_y"]/2, pv["z0"], pv["depth_x"], pv["width_y"], pv["height_z"])
    pi_ = occ.addBox(-pv["depth_x"]/2+w, -pv["width_y"]/2+w, pv["z0"]+w, pv["depth_x"]-2*w, pv["width_y"]-2*w, pv["height_z"]-2*w)
    pel, _ = occ.cut([(3, po)], [(3, pi_)])
    occ.fragment(bulk + pel, [(3, part)])   # conformal: shared faces -> shared nodes
    occ.synchronize()
    tags = {"bulkhead": [], "partition": [], "pelvis": []}
    for d, t in gmsh.model.getEntities(3):
        x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(d, t)
        if x1 - x0 < 1.5 * p["t"] + 0.01: tags["partition"].append(t)
        elif z1 <= pv["z0"] + pv["height_z"] + 0.01: tags["pelvis"].append(t)
        else: tags["bulkhead"].append(t)
    for k, v in tags.items():
        if v: gmsh.model.addPhysicalGroup(3, v, name=k)
    return tags

def nodes():
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    return {int(t): (xyz[3*i], xyz[3*i+1], xyz[3*i+2]) for i, t in enumerate(nt)}

def node_set(N, box, used):
    x0, y0, z0, x1, y1, z1 = box
    return [n for n, (x, y, z) in N.items() if n in used and x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1]

def elements(tags):
    out = {}
    for part, vols in tags.items():
        el = []
        for v in vols:
            et, ei, en = gmsh.model.mesh.getElements(3, v)
            for typ, ids, conn in zip(et, ei, en):
                if typ != 11: continue
                for k, e in enumerate(ids):
                    n = [int(x) for x in conn[10*k:10*k+10]]
                    el.append((int(e), n[:8] + [n[9], n[8]]))   # gmsh -> ccx C3D10 order
        out[part] = el
    return out

def loads(N, tgt, lc):
    F = lc.get("F", [0, 0, 0]); M = lc.get("M", [0, 0, 0]); n = len(tgt)
    cx = sum(N[i][0] for i in tgt)/n; cy = sum(N[i][1] for i in tgt)/n
    sxx = sum((N[i][0]-cx)**2 for i in tgt) or 1.0; syy = sum((N[i][1]-cy)**2 for i in tgt) or 1.0
    out = []
    for i in tgt:
        fx, fy, fz = F[0]/n, F[1]/n, F[2]/n
        fz += -M[1]*(N[i][0]-cx)/sxx + M[0]*(N[i][1]-cy)/syy   # couple from My, Mx
        out.append((i, fx, fy, fz))
    return out

def write_deck(path, c, N, E, sets, name, lc):
    used = sorted({n for el in E.values() for _, ns in el for n in ns})
    with open(path, "w") as f:
        f.write("*NODE\n" + "".join(f"{n},{N[n][0]:.5f},{N[n][1]:.5f},{N[n][2]:.5f}\n" for n in used))
        for part, el in E.items():
            if not el: continue
            f.write(f"*ELEMENT,TYPE=C3D10,ELSET={part.upper()}\n")
            f.write("".join(f"{e}," + ",".join(map(str, ns)) + "\n" for e, ns in el))
        for part, el in E.items():
            if not el: continue
            m = c["geometry"][part]["mat"]; M = c["materials"][m]
            f.write(f"*MATERIAL,NAME=M_{part.upper()}\n*ELASTIC\n{M['E']},{M['nu']}\n*DENSITY\n{M['rho']}\n")
            f.write(f"*SOLID SECTION,ELSET={part.upper()},MATERIAL=M_{part.upper()}\n")
        for k, ns in sets.items():
            f.write(f"*NSET,NSET={k.upper()}\n" + "".join(f"{n},\n" for n in ns))
        f.write("*BOUNDARY\nFIXED,1,3\n")
        cl = "*CLOAD\n" + "".join(f"{i},{j+1},{v:.6g}\n" for i, *fv in loads(N, sets[lc["target"]], lc)
                                   for j, v in enumerate(fv) if v)
        f.write("*STEP\n*STATIC\n" + cl + "*NODE PRINT,NSET=LAND\nU\n")
        for part, el in E.items():
            if el: f.write(f"*EL PRINT,ELSET={part.upper()}\nS\n")
        f.write("*END STEP\n")
        if name == c["post"]["freq_case"]:
            f.write("*STEP\n*FREQUENCY\n3\n*END STEP\n")
        if name == c["post"]["buckle_case"]:
            f.write("*STEP\n*BUCKLE\n2\n" + cl + "*END STEP\n")

def parse_dat(path):
    r = {"S": {}, "U": [], "freq": [], "buckle": []}
    if not os.path.exists(path): return r
    mode = None; part = None; txt = open(path).read().splitlines()
    for ln in txt:
        s = ln.strip(); lo = s.lower()
        if lo.startswith("stresses"):
            mode = "S"; part = re.search(r"for set (\S+)", s).group(1); continue
        if lo.startswith("displacements"): mode = "U"; continue
        if "eigenvalue output" in lo.replace(" ", "").replace("eigenvalueoutput", "eigenvalue output") or "E I G E N V A L U E   O U T P U T" in s:
            mode = "F"; continue
        if "B U C K L I N G   F A C T O R" in s: mode = "B"; continue
        if "P A R T I C I P A T I O N" in s or "E I G E N V A L U E   N U M B E R" in s or "T O T A L" in s: mode = None; continue
        tok = s.split()
        try: v = [float(t) for t in tok]
        except ValueError: continue
        if not v: continue
        if mode == "S" and len(v) == 8:
            sx, sy, sz, txy, txz, tyz = v[2:]
            vm = math.sqrt(0.5*((sx-sy)**2+(sy-sz)**2+(sz-sx)**2)+3*(txy**2+txz**2+tyz**2))
            r["S"][part] = max(r["S"].get(part, 0.0), vm)
        elif mode == "U" and len(v) == 4: r["U"].append(math.sqrt(v[1]**2+v[2]**2+v[3]**2))
        elif mode == "F" and len(v) == 5: r["freq"].append(v[3])
        elif mode == "B" and len(v) == 2: r["buckle"].append(v[1])
    return r

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cfg", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--coarse", action="store_true"); ap.add_argument("--no-solve", action="store_true"); ap.add_argument("--ccx")
    a = ap.parse_args(); c = yaml.safe_load(open(a.cfg)); os.makedirs(a.out, exist_ok=True)
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.model.add("torso_r1")
    tags = build(c); gmsh.write(os.path.join(a.out, "torso_r1.step"))
    h = c["mesh"]["size_coarse" if a.coarse else "size"]
    gmsh.option.setNumber("Mesh.MeshSizeMax", h); gmsh.option.setNumber("Mesh.MeshSizeMin", h/4)
    gmsh.option.setNumber("Mesh.SecondOrderLinear", 1)  # straight-sided tets: no negative jacobians on coarse curved edges
    gmsh.model.mesh.generate(3); gmsh.model.mesh.setOrder(2)
    N = nodes(); E = elements(tags); used = {n for el in E.values() for _, ns in el for n in ns}
    g = c["geometry"]; b, L, pv, p, e = g["bulkhead"], g["land"], g["pelvis"], g["partition"], g["ethercat_bosses"]
    B = 1e4; xf = b["x0"]+b["t"]+L["t"]; zt = pv["z0"]+pv["height_z"]; t = 0.05
    sets = {
        "fixed": node_set(N, (-B, -B, pv["z0"]-t, B, B, pv["z0"]+t), used),
        "land": node_set(N, (xf-t, -L["size"]/2-t, L["z_c"]-L["size"]/2-t, xf+t, L["size"]/2+t, L["z_c"]+L["size"]/2+t), used),
        "shoulder_flange_L": node_set(N, (-B, b["width_y"]/2-t, -B, B, B, B), used),
        "pelvis_top": node_set(N, (-B, -B, zt-t, B, B, zt+t), used),
        "partition": node_set(N, (p["x0"]-t, -B, p["z0"]+t, p["x0"]+t, B, B), used),
        "ethercat_bosses": node_set(N, (p["x0"]-t, -e["dx"], e["z_c"]-e["dz"], p["x0"]+t, e["dx"], e["z_c"]+e["dz"]), used),
    }
    gmsh.finalize()
    res = {"mesh_h": h, "nodes": len(used), "parts": {k: len(v) for k, v in E.items()},
           "set_sizes": {k: len(v) for k, v in sets.items()}, "criteria": c["criteria"], "cases": {}}
    ccx = a.ccx or shutil.which("ccx")
    cr = c["criteria"]; allpass = True
    for name, lc in c["load_cases"].items():
        deck = os.path.join(a.out, name); write_deck(deck + ".inp", c, N, E, sets, name, lc)
        r = {"deck": deck + ".inp", "solved": False}
        if ccx and not a.no_solve:
            p_ = subprocess.run([ccx, "-i", name], cwd=a.out, capture_output=True, text=True,
                                env={**os.environ, "OMP_NUM_THREADS": str(os.cpu_count() or 1)})
            d = parse_dat(deck + ".dat"); r["solved"] = bool(d["S"]) and p_.returncode == 0
            if not r["solved"]: r["log_tail"] = p_.stdout[-800:]
            chk = {}
            for part, vm in d["S"].items():
                Mt = c["materials"][g[part.lower()]["mat"]]; Sy = Mt.get("allowable", Mt["Sy"]); sf = Sy/vm if vm else float("inf")  # R-123: SF vs static allowable where given
                chk[f"SF_{part.lower()}"] = {"vm_max": round(vm, 2), "SF": round(sf, 3), "pass": sf >= cr["SF_min"]}
            if d["U"]: um = max(d["U"]); chk["land_defl"] = {"mm": round(um, 5), "pass": (um <= cr["land_defl_max"]) if name == "LC1_chest_pad" else None}
            if d["freq"]: chk["mode1_hz"] = {"hz": round(d["freq"][0], 2), "pass": d["freq"][0] >= cr["mode1_min_hz"]}
            if d["buckle"]: chk["buckling"] = {"factor": round(d["buckle"][0], 3), "pass": d["buckle"][0] >= cr["buckling_min"]}
            r["checks"] = chk
            allpass &= r["solved"] and all(v["pass"] is not False for v in chk.values())
        res["cases"][name] = r
    res["overall"] = "PASS" if (allpass and ccx and not a.no_solve) else ("FAIL" if ccx and not a.no_solve else "NOT_SOLVED")
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    print(res["overall"], res["nodes"], json.dumps(res["set_sizes"]))

if __name__ == "__main__":
    main()
