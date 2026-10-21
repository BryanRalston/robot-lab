#!/usr/bin/env python3
"""FEA job 3: torso pocketing. Builds parametric torso (gmsh OCC), exports torso_r1.step,
meshes C3D10, writes one CalculiX deck per load case, runs ccx if on PATH, writes results.json.
Usage: python fea_job3.py --cfg fea_job3.yaml --out fea/job3 [--coarse] [--no-solve]"""
import argparse, json, os, shutil, subprocess, re
import yaml, gmsh

def build(c, coarse):
    g = c["geometry"]; occ = gmsh.model.occ; tags = {}
    b = g["bulkhead"]
    bk = occ.addBox(b["x0"], -b["width_y"]/2, b["z0"], b["t"], b["width_y"], b["height_z"])
    L = g["land"]; land = occ.addBox(b["x0"]+b["t"], -L["size"]/2, L["z_c"]-L["size"]/2, L["t"], L["size"], L["size"])
    R = g["rib"]; rib = occ.addBox(b["x0"]-R["h"], -R["t"]/2, L["z_c"]-L["size"]/2, R["h"], R["t"], L["size"])
    vol, _ = occ.fuse([(3, bk)], [(3, land), (3, rib)])
    cuts = []
    sf = g["shoulder_flange"]
    for s in (-1, 1):
        import math
        for i in range(sf["n_bolt"]):
            a = 2*math.pi*i/sf["n_bolt"]
            yc = s*sf["y_c"] + sf["bc_dia"]/2*math.cos(a); zc = b["z0"]+b["height_z"]/2 + sf["bc_dia"]/2*math.sin(a)
            if abs(yc) < b["width_y"]/2 - 5:
                cuts.append((3, occ.addCylinder(b["x0"]-1, yc, zc, b["t"]+2, 0, 0, sf["bolt_dia"]/2)))
        gr = g["grommet"]
        cuts.append((3, occ.addCylinder(b["x0"]-1, s*gr["y_c"], b["z0"]+b["height_z"]/2+gr["z_off"], b["t"]+2, 0, 0, gr["dia"]/2)))
    bi = g["bezel_inserts"]
    for dy in (-1, 1):
        for dz in (-1, 1):
            cuts.append((3, occ.addCylinder(b["x0"]+b["t"]+L["t"]+1, dy*bi["pitch"]/2*0.8, L["z_c"]+dz*bi["pitch"]/2*0.8, -10, 0, 0, bi["dia"]/2)))
    blk, _ = occ.cut(vol, cuts)
    p = g["partition"]; part = occ.addBox(p["x0"], -p["width_y"]/2, p["z0"], p["t"], p["width_y"], p["height_z"])
    pv = g["pelvis"]; po = occ.addBox(-pv["depth_x"]/2, -pv["width_y"]/2, pv["z0"], pv["depth_x"], pv["width_y"], pv["height_z"])
    w = pv["wall"]; pi_ = occ.addBox(-pv["depth_x"]/2+w, -pv["width_y"]/2+w, pv["z0"]+w, pv["depth_x"]-2*w, pv["width_y"]-2*w, pv["height_z"])
    pel, _ = occ.cut([(3, po)], [(3, pi_)])
    occ.synchronize()
    tags = {"bulkhead": [t for d, t in blk], "partition": [part], "pelvis": [t for d, t in pel]}
    for k, v in tags.items():
        gmsh.model.addPhysicalGroup(3, v, name=k)
    return tags

def node_set(box):
    x0, y0, z0, x1, y1, z1 = box
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    out = []
    for i, t in enumerate(tags):
        x, y, z = xyz[3*i:3*i+3]
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1: out.append(int(t))
    return out

def write_deck(path, c, tags, lc_name, lc, sets):
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    with open(path, "w") as f:
        f.write("*NODE\n")
        for i, t in enumerate(nt): f.write(f"{int(t)},{xyz[3*i]:.4f},{xyz[3*i+1]:.4f},{xyz[3*i+2]:.4f}\n")
        for part, vols in tags.items():
            f.write(f"*ELEMENT,TYPE=C3D10,ELSET={part}\n")
            for v in vols:
                et, ei, en = gmsh.model.mesh.getElements(3, v)
                for typ, ids, conn in zip(et, ei, en):
                    if typ != 11: continue
                    for k, e in enumerate(ids):
                        n = [int(x) for x in conn[10*k:10*k+10]]
                        n = n[:8] + [n[9], n[8]]  # gmsh->ccx C3D10 order
                        f.write(f"{int(e)}," + ",".join(map(str, n)) + "\n")
        for part in tags:
            m = c["geometry"][part]["mat"]; M = c["materials"][m]
            f.write(f"*MATERIAL,NAME={m}_{part}\n*ELASTIC\n{M['E']},{M['nu']}\n*DENSITY\n{M['rho']}\n")
            f.write(f"*SOLID SECTION,ELSET={part},MATERIAL={m}_{part}\n")
        for k, ns in sets.items():
            f.write(f"*NSET,NSET={k}\n"); [f.write(f"{n}\n") for n in ns]
        f.write("*BOUNDARY\nfixed,1,3\n*STEP\n*STATIC\n*CLOAD\n")
        F = lc.get("F", [0, 0, 0]); tgt = sets[lc["target"]]
        if lc.get("M"):  # moment as couple: +/- Fz on ends in x
            My = lc["M"][1]; d = 120.0; F = [0, 0, My/d]
        for j, comp in enumerate(F):
            if comp: [f.write(f"{n},{j+1},{comp/len(tgt):.6g}\n") for n in tgt]
        f.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")
        f.write("*STEP\n*FREQUENCY\n3\n*END STEP\n" if lc_name == "LC1_chest_pad" else "")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cfg", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--coarse", action="store_true"); ap.add_argument("--no-solve", action="store_true")
    a = ap.parse_args(); c = yaml.safe_load(open(a.cfg)); os.makedirs(a.out, exist_ok=True)
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.model.add("torso_r1")
    tags = build(c, a.coarse)
    gmsh.write(os.path.join(a.out, "torso_r1.step"))
    h = c["mesh"]["size_coarse" if a.coarse else "size"]
    gmsh.option.setNumber("Mesh.MeshSizeMax", h); gmsh.option.setNumber("Mesh.MeshSizeMin", h/4)
    gmsh.model.mesh.generate(3); gmsh.model.mesh.setOrder(2)
    g = c["geometry"]; b = g["bulkhead"]; L = g["land"]; pv = g["pelvis"]; p = g["partition"]; e = g["ethercat_bosses"]
    BIG = 1e4
    sets = {
        "fixed": node_set((-BIG, -BIG, pv["z0"]-0.1, BIG, BIG, pv["z0"]+0.1)),
        "land": node_set((b["x0"]+b["t"]+L["t"]-0.1, -L["size"]/2, L["z_c"]-L["size"]/2, BIG, L["size"]/2, L["z_c"]+L["size"]/2)),
        "shoulder_flange_L": node_set((-BIG, b["width_y"]/2-0.1, -BIG, BIG, BIG, BIG)),
        "pelvis_top": node_set((-BIG, -BIG, pv["z0"]+pv["height_z"]-0.1, BIG, BIG, pv["z0"]+pv["height_z"]+0.1)),
        "partition": node_set((p["x0"]-0.1, -BIG, p["z0"], p["x0"]+p["t"]+0.1, BIG, p["z0"]+p["height_z"])),
        "ethercat_bosses": node_set((p["x0"]-0.1, -e["dx"], e["z_c"]-e["dz"], p["x0"]+p["t"]+0.1, e["dx"], e["z_c"]+e["dz"])),
    }
    # NOTE: parts are not yet tied; on the PC add *TIE (bulkhead/partition/pelvis via shell CFRP) before trusting LC1-4 load paths.
    res = {"mesh_h": h, "nodes": len(gmsh.model.mesh.getNodes()[0]), "set_sizes": {k: len(v) for k, v in sets.items()},
           "criteria": c["criteria"], "cases": {}}
    ccx = shutil.which("ccx") or shutil.which("ccx_2.21") or shutil.which("ccx_static")
    for name, lc in c["load_cases"].items():
        deck = os.path.join(a.out, name); write_deck(deck + ".inp", c, tags, name, lc, sets)
        r = {"deck": deck + ".inp", "solved": False}
        if ccx and not a.no_solve:
            subprocess.run([ccx, "-i", deck], cwd=a.out, check=False); r["solved"] = os.path.exists(deck + ".frd")
        res["cases"][name] = r
    gmsh.finalize()
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1); print(json.dumps(res["set_sizes"]), res["nodes"])

if __name__ == "__main__":
    main()
