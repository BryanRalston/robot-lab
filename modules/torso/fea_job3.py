#!/usr/bin/env python3
"""FEA job 3: torso pocketing. Builds parametric torso (gmsh OCC), fragments all parts into one
conformal mesh (shared interface nodes), exports torso_r1.step, writes a CalculiX deck per load case,
runs ccx, parses .dat for max von Mises -> SF per material, land deflection, frequency (LC6) and
buckling factor (LC1), and writes PASS/FAIL per criterion to results.json.

SF uses the max integration-point von Mises outside a fixed 5 mm band on support and re-entrant
lines (fixed pelvis face, post junctions, land-step perimeter, hole walls, rib root). The raw
peak and its centroid are stored beside that value so a non-convergent corner can be reported
as a singularity. Modal stresses from *FREQUENCY / *BUCKLE are not included.

Usage: python fea_job3.py --cfg fea_job3.yaml --out fea/job3 [--coarse] [--no-solve] [--ccx PATH]
       [--mesh-size H] [--cases LC1_chest_pad,LC6_stand]
"""
import argparse, json, math, os, re, shutil, subprocess, time
import yaml, gmsh

SING_BAND = 5.0  # mm, fixed physical band (same at every mesh size)

def build(c):
    g = c["geometry"]; occ = gmsh.model.occ
    b, L, R, sf = g["bulkhead"], g["land"], g["rib"], g["shoulder_flange"]
    zc0 = b["z0"] + b["height_z"]/2
    al = [occ.addBox(b["x0"], -b["width_y"]/2, b["z0"], b["t"], b["width_y"], b["height_z"]),
          occ.addBox(b["x0"]+b["t"], -L["size"]/2, L["z_c"]-L["size"]/2, L["t"], L["size"], L["size"]),
          ] + ([occ.addBox(b["x0"]-R["h"], -R["t"]/2, L["z_c"]-L["size"]/2, R["h"], R["t"], L["size"])] if R["h"] > 0 else [])
    P = g["posts"]
    for y in P["y"]:
        al.append(occ.addBox(b["x0"], y-P["w_y"]/2, 0, b["t"], P["w_y"], b["z0"]))
    bx = g.get("bay_box")   # job 3c: closed sternum/pack-bay torsion box replacing the posts
    if bx:
        Y, xf_, xr_, z0_, z1_ = bx["y"], bx["x_front"], bx["x_rear"], bx["z0"], bx["z1"]
        for sg in (-1, 1):
            al.append(occ.addBox(xr_, sg*Y - (bx["t_side"] if sg > 0 else 0), z0_, xf_-xr_, bx["t_side"], z1_-z0_))
        al.append(occ.addBox(xf_-bx["t_web"], -Y, z0_, bx["t_web"], 2*Y, z1_-z0_))
        al.append(occ.addBox(xr_, -Y, z0_, bx["t_web"], 2*Y, z1_-z0_))
        al.append(occ.addBox(xr_, -Y, z1_-bx["t_lid"], xf_-xr_, 2*Y, bx["t_lid"]))
        if bx.get("t_floor"): al.append(occ.addBox(xr_, -Y, z0_, xf_-xr_, 2*Y, bx["t_floor"]))
        if bx.get("land_web"):   # 4 mm local webs under the land (side walls of the land window), R3 fillets via fillet_r
            lw = bx["land_web"]
            for yy in (-lw["y"], lw["y"]-lw["t"]):
                al.append(occ.addBox(b["x0"], yy, lw["z0"], xf_-b["x0"], lw["t"], lw["z1"]-lw["z0"]))
        if bx.get("notch_floor"):   # Option A: socket floor under the pad core (box follows the notched pack)
            nf = bx["notch_floor"]; al.append(occ.addBox(nf["x0"], -nf["y"], nf["z0"], xf_-nf["x0"], 2*nf["y"], nf["t"]))
    sb = g.get("sternum_box")   # job 3c: closed sternum box behind the bulkhead (webs + top cap) tied to the bay rear web
    if sb:
        for yy in sb["web_y"]:
            al.append(occ.addBox(sb["x_rear"], yy - sb["t"]/2, b["z0"], b["x0"] - sb["x_rear"] + 0.01, sb["t"], b["height_z"]))
        al.append(occ.addBox(sb["x_rear"], -b["width_y"]/2, b["z0"] + b["height_z"] - sb["t_cap"], b["x0"] - sb["x_rear"] + 0.01, b["width_y"], sb["t_cap"]))
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
    if bx and bx.get("front_window"):   # land/core window through the front web
        fw = bx["front_window"]; cuts.append((3, occ.addBox(bx["x_front"]-bx["t_web"]-1, -fw["y"], fw["z0"], bx["t_web"]+2, 2*fw["y"], fw["z1"]-fw["z0"])))
    if bx and bx.get("vent"):   # UL 2271 vent/burst port in the rear web, aimed down/rearward
        vt = bx["vent"]
        if vt.get("on") == "floor":   # vent through the floor, outlet down into the pelvis open top
            cuts.append((3, occ.addCylinder(vt["x"], vt["y"], bx["z0"]-1, 0, 0, bx.get("t_floor", 8)+2, vt["dia"]/2)))
        else:
            cuts.append((3, occ.addCylinder(bx["x_rear"]-1, vt["y"], vt["z"], bx["t_web"]+2, 0, 0, vt["dia"]/2)))
    if bx and bx.get("inbox_cut"):   # Option A: bulkhead web cannot pass through the cells; keep wings |y|>=Y-t_side and the strip above the lid
        cuts.append((3, occ.addBox(b["x0"]-0.5, -(bx["y"]-bx["t_side"]), bx["z0"]-1, b["t"]+0.5, 2*(bx["y"]-bx["t_side"]), bx["z1"]-bx["z0"]+1)))
        if bx.get("thor_cut"):   # Thor bay footprint above the lid: no bulkhead strip there
            tc_ = bx["thor_cut"]; cuts.append((3, occ.addBox(b["x0"]-0.5, -tc_["y"], bx["z1"]-0.01, b["t"]+1, 2*tc_["y"], b["z0"]+b["height_z"]-bx["z1"]+1)))
    bulk, _ = occ.cut(bulk, cuts)
    p = g["partition"]; part = occ.addBox(p["x0"], -p["width_y"]/2, p["z0"], p["t"], p["width_y"], p["height_z"])
    pv = g["pelvis"]; w = pv["wall"]
    po = occ.addBox(-pv["depth_x"]/2, -pv["width_y"]/2, pv["z0"], pv["depth_x"], pv["width_y"], pv["height_z"])
    pi_ = occ.addBox(-pv["depth_x"]/2+w, -pv["width_y"]/2+w, pv["z0"]+w, pv["depth_x"]-2*w, pv["width_y"]-2*w, pv["height_z"]-2*w)
    pel, _ = occ.cut([(3, po)], [(3, pi_)])
    if pv.get("deck_t"):   # waist/hip-yaw deck (model_v4 160 x 364 x 8) on the pelvis top
        dz_ = pv.get("deck_ztop", pv["z0"]+pv["height_z"])
        dk = occ.addBox(-pv["deck_x"]/2, -pv["deck_y"]/2, dz_-pv["deck_t"], pv["deck_x"], pv["deck_y"], pv["deck_t"])
        pel, _ = occ.fuse(pel, [(3, dk)])
    wv = []
    W = g.get("waist")   # model_v4 waist interface: yaw housing + yoke + -y cheek + pitch housing/output + torso bracket cheek (+y) to the floor
    if W:
        wl = [occ.addCylinder(0, 0, W["yaw_z0"], 0, 0, W["yaw_z1"]-W["yaw_z0"], W["yaw_d"]/2),
              occ.addBox(-60, -70, W["yoke_z0"], 120, 140, 8),
              occ.addBox(-35, -W["cheek_y"]-8, W["yoke_z0"]+8, 70, 8, W["pitch_z"]+30-(W["yoke_z0"]+8)),
              occ.addCylinder(0, -W["cheek_y"], W["pitch_z"], 0, 2*W["cheek_y"], 0, W["pitch_d"]/2),
              occ.addCylinder(0, W["cheek_y"]-0.01, W["pitch_z"], 0, W["flange_t"]+0.01, 0, W["pitch_d"]/2),
              ] + ([occ.addBox(-35, W["cheek_y"]+W["flange_t"]-0.01, W["pitch_z"]-30, 70, W["bracket_t"]+0.01, W["floor_z"]-(W["pitch_z"]-30))] if not W.get("yoke2") else [])
        Y2 = W.get("yoke2")   # two-sided yoke: box side walls carried down as cheeks; +y output flange + spacer, -y support bearing (THK RB7013) + spacer
        if Y2:
            yi, tc, D = Y2["y_in"], Y2["t"], Y2["D"]
            wl += [occ.addCylinder(0, W["cheek_y"]+W["flange_t"]-0.01, W["pitch_z"], 0, yi-(W["cheek_y"]+W["flange_t"])+0.02, 0, Y2["hub_d"]/2),
                   occ.addCylinder(0, -W["cheek_y"]-8-Y2["brg_w"], W["pitch_z"], 0, Y2["brg_w"]+0.01, 0, Y2["brg_od"]/2),
                   occ.addCylinder(0, -yi-0.01, W["pitch_z"], 0, yi-(W["cheek_y"]+8+Y2["brg_w"])+0.02, 0, Y2["hub_d"]/2)]
            for sg in (1, -1):
                y0 = yi if sg > 0 else -yi-tc
                wl.append(occ.addBox(-D/2, y0, Y2["z_bot"], D, tc, W["floor_z"]-Y2["z_bot"]))
        wv, _ = occ.fuse([(3, wl[0])], [(3, t) for t in wl[1:]])
    out, fmap = occ.fragment(bulk + pel + wv, [(3, part)])   # conformal: shared faces -> shared nodes
    occ.synchronize()
    wset = {t for i in range(len(bulk)+len(pel), len(bulk)+len(pel)+len(wv)) for _, t in fmap[i]}
    tags = {"bulkhead": [], "partition": [], "pelvis": [], "waist": []}
    for d, t in gmsh.model.getEntities(3):
        if t in wset: tags["waist"].append(t); continue
        x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(d, t)
        if x1 - x0 < 1.5 * p["t"] + 0.01: tags["partition"].append(t)
        elif z1 <= pv["z0"] + pv["height_z"] + 0.01: tags["pelvis"].append(t)
        else: tags["bulkhead"].append(t)
    for k, v in tags.items():
        if v: gmsh.model.addPhysicalGroup(3, v, name=k)
    return tags

def hole_table(c):
    """(yc, zc, radius, x0, x1) for empty holes. Peaks on the wall are mesh-dependent."""
    g = c["geometry"]; b, L, sf = g["bulkhead"], g["land"], g["shoulder_flange"]
    zc0 = b["z0"] + b["height_z"]/2
    holes = []
    x0, x1 = b["x0"] - 1.0, b["x0"] + b["t"] + 2.0
    for s in (-1, 1):
        for i in range(sf["n_bolt"]):
            a = 2*math.pi*i/sf["n_bolt"]
            yc = s*sf["y_c"] + sf["bc_dia"]/2*math.cos(a); zc = zc0 + sf["bc_dia"]/2*math.sin(a)
            if abs(yc) < b["width_y"]/2 - sf["bolt_dia"]:
                holes.append((yc, zc, sf["bolt_dia"]/2, x0, x1))
        gr = g["grommet"]
        holes.append((s*gr["y_c"], zc0+gr["z_off"], gr["dia"]/2, x0, x1))
    bi = g["bezel_inserts"]; xf = b["x0"]+b["t"]+L["t"]
    for dy in (-1, 1):
        for dz in (-1, 1):
            holes.append((dy*bi["pitch"]*0.4, L["z_c"]+dz*bi["pitch"]*0.4, bi["dia"]/2, xf-9.0, xf+1.0))
    return holes

def make_singular(c):
    g = c["geometry"]; b, L, R, pv, P = g["bulkhead"], g["land"], g["rib"], g["pelvis"], g["posts"]
    band = SING_BAND
    holes = hole_table(c)
    x_if = b["x0"] + b["t"]
    ly0, ly1 = -L["size"]/2, L["size"]/2
    lz0, lz1 = L["z_c"]-L["size"]/2, L["z_c"]+L["size"]/2
    rz0, rz1 = lz0, lz1
    post_boxes = []
    for y in P["y"]:
        post_boxes.append((b["x0"]-band, y-P["w_y"]/2-band, b["x0"]+b["t"]+band, y+P["w_y"]/2+band))
    def near(pt):
        x, y, z = pt
        if z <= pv["z0"] + band:
            return True
        for x0, y0, x1, y1 in post_boxes:
            if x0 <= x <= x1 and y0 <= y <= y1 and (abs(z) <= band or abs(z - b["z0"]) <= band):
                return True
        for yc, zc, r, hx0, hx1 in holes:
            if hx0 - band <= x <= hx1 + band and math.hypot(y-yc, z-zc) - r < band:
                return True
        if abs(x - x_if) <= band:
            if ly0 <= y <= ly1 and lz0 <= z <= lz1:
                d_edge = min(y-ly0, ly1-y, z-lz0, lz1-z)
            else:
                cy = min(max(y, ly0), ly1); cz = min(max(z, lz0), lz1)
                d_edge = math.hypot(y-cy, z-cz)
            if d_edge <= band:
                return True
        if rz0 - band <= z <= rz1 + band:
            for ys in (-R["t"]/2, R["t"]/2):
                if math.hypot(x - b["x0"], y - ys) < band:
                    return True
        return False
    return near

def nodes():
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    return {int(t): (xyz[3*i], xyz[3*i+1], xyz[3*i+2]) for i, t in enumerate(nt)}

def tet_vol(a, b, c, d):
    return ((b[0]-a[0])*((c[1]-a[1])*(d[2]-a[2])-(c[2]-a[2])*(d[1]-a[1]))
           -(b[1]-a[1])*((c[0]-a[0])*(d[2]-a[2])-(c[2]-a[2])*(d[0]-a[0]))
           +(b[2]-a[2])*((c[0]-a[0])*(d[1]-a[1])-(c[1]-a[1])*(d[0]-a[0])))/6.0

def node_set(N, box, used):
    x0, y0, z0, x1, y1, z1 = box
    return [n for n, (x, y, z) in N.items() if n in used and x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1]

def elements(tags):
    out = {}; skipped = 0
    for part, vols in tags.items():
        el = []
        for v in vols:
            et, ei, en = gmsh.model.mesh.getElements(3, v)
            for typ, ids, conn in zip(et, ei, en):
                if typ != 11:
                    skipped += len(ids); continue
                for k, e in enumerate(ids):
                    n = [int(x) for x in conn[10*k:10*k+10]]
                    el.append((int(e), n[:8] + [n[9], n[8]]))   # gmsh -> ccx C3D10 order
        out[part] = el
    return out, skipped

def split_posts(E, N, c):
    """Posts are fused into the bulkhead solid. Split them by centroid so SF is per part."""
    P = c["geometry"]["posts"]; b = c["geometry"]["bulkhead"]
    boxes = [(b["x0"]-0.2, y-P["w_y"]/2-0.2, -0.2, b["x0"]+b["t"]+0.2, y+P["w_y"]/2+0.2, b["z0"]-0.2) for y in P["y"]]
    posts, bulk = [], []
    for e, ns in E.get("bulkhead", []):
        p = [N[i] for i in ns[:4]]
        cx = sum(q[0] for q in p)/4; cy = sum(q[1] for q in p)/4; cz = sum(q[2] for q in p)/4
        if any(x0 <= cx <= x1 and y0 <= cy <= y1 and z0 <= cz <= z1 for x0, y0, z0, x1, y1, z1 in boxes):
            posts.append((e, ns))
        else:
            bulk.append((e, ns))
    E["bulkhead"] = bulk
    E["posts"] = posts
    W = c["geometry"].get("waist") or {}
    if W.get("yoke2"):   # torso yoke cheeks (two-sided) reported as their own part
        Y2 = W["yoke2"]; yk, rest = [], []
        for e, ns in E.get("waist", []):
            p = [N[i] for i in ns[:4]]
            cy = sum(q[1] for q in p)/4; cz = sum(q[2] for q in p)/4
            (yk if abs(cy) >= Y2["y_in"]-0.2 and cz >= Y2["z_bot"]-0.2 else rest).append((e, ns))
        E["waist"] = rest; E["yoke"] = yk
    return E

def element_info(E, N):
    rec = {}
    for part, els in E.items():
        for e, ns in els:
            p = [N[i] for i in ns[:4]]
            ctd = (sum(q[0] for q in p)/4, sum(q[1] for q in p)/4, sum(q[2] for q in p)/4)
            vol = abs(tet_vol(*p))
            edges = [math.dist(p[i], p[j]) for i in range(4) for j in range(i+1, 4)]
            L = max(edges) if edges else 1.0
            ve = math.sqrt(2)/12 * L**3
            rec[e] = {"part": part, "c": ctd, "vol": vol, "q": (vol/ve if ve else 0.0), "vm": 0.0}
    return rec

def loads(N, tgt, lc):
    F = lc.get("F", [0, 0, 0]); M = lc.get("M", [0, 0, 0]); n = len(tgt)
    if n == 0:
        raise SystemExit(f"empty target node set for {lc}")
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
        f.write("*HEADING\n" + name + "\n")
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
        f.write("*STEP\n*STATIC\n" + cl + "*NODE PRINT,NSET=LAND\nU\n*NODE PRINT,NSET=FIXED\nRF\n")
        for part, el in E.items():
            if el: f.write(f"*EL PRINT,ELSET={part.upper()}\nS\n")
        f.write("*END STEP\n")
        if name == c["post"]["freq_case"]:
            f.write("*STEP\n*FREQUENCY\n3\n*NODE FILE\nU\n*END STEP\n")
        if name == c["post"]["buckle_case"]:
            f.write("*STEP\n*BUCKLE\n2\n" + cl + "*END STEP\n")

def parse_dat(path, rec):
    r = {"U": [], "freq": [], "buckle": [], "RF": [0.0, 0.0, 0.0]}
    if not os.path.exists(path): return r
    step = 0; mode = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            s = ln.strip()
            if not s: continue
            if "S T E P" in s and "INCREMENT" not in s:
                tok = s.split()
                if tok and tok[-1].isdigit(): step = int(tok[-1])
                mode = None
                continue
            lo = s.lower()
            spaced = lo.replace(" ", "")
            if "eigenvalueoutput" in spaced and "number" not in spaced:
                mode = "F"; continue
            if "bucklingfactor" in spaced:
                mode = "B"; continue
            if "participationfactor" in spaced or "eigenvaluenumber" in spaced:
                mode = None; continue
            if lo.startswith("stresses") or lo.startswith("displacements") or lo.startswith("forces"):
                if step == 1 and lo.startswith("stresses"): mode = "S"
                elif step == 1 and lo.startswith("displacements"): mode = "U"
                elif step == 1 and lo.startswith("forces"): mode = "RF"
                else: mode = None
                continue
            tok = s.split()
            try: v = [float(t) for t in tok]
            except ValueError: continue
            if mode == "S" and len(v) >= 8:
                sx, sy, sz, txy, txz, tyz = v[2:8]
                vm = math.sqrt(0.5*((sx-sy)**2+(sy-sz)**2+(sz-sx)**2)+3*(txy**2+txz**2+tyz**2))
                info = rec.get(int(v[0]))
                if info is not None and vm > info["vm"]: info["vm"] = vm
            elif mode == "U" and len(v) == 4:
                r["U"].append(math.sqrt(v[1]**2+v[2]**2+v[3]**2))
            elif mode == "RF" and len(v) == 4:
                r["RF"][0] += v[1]; r["RF"][1] += v[2]; r["RF"][2] += v[3]
            elif mode == "F" and len(v) == 5:
                r["freq"].append(v[3])
            elif mode == "B" and len(v) == 2:
                r["buckle"].append(v[1])
    return r

def part_stats(rec, near, part):
    raw = 0.0; loc = None; eid = None
    struct = 0.0; sloc = None; n_struct = 0
    lig = 0.0; lloc = None; n_lig = 0
    for e, info in rec.items():
        if info["part"] != part: continue
        vm = info["vm"]
        if vm >= raw:
            raw = vm; loc = info["c"]; eid = e
        if not near(info["c"]):
            n_struct += 1
            if vm >= struct:
                struct = vm; sloc = info["c"]
        if part == "posts":
            z = info["c"][2]
            if 40.0 <= z <= 100.0:
                n_lig += 1
                if vm >= lig:
                    lig = vm; lloc = info["c"]
    def rnd(p):
        return None if p is None else [round(p[0], 2), round(p[1], 2), round(p[2], 2)]
    return {"vm_max": raw, "vm_loc": rnd(loc), "eid": eid,
            "vm_struct": struct if n_struct else raw, "vm_struct_loc": rnd(sloc if n_struct else loc),
            "n_struct": n_struct, "vm_ligament": lig, "vm_ligament_loc": rnd(lloc), "n_ligament": n_lig}

def resolve_ccx(arg):
    if arg and os.path.exists(arg): return arg
    w = shutil.which("ccx") or shutil.which("ccx.exe")
    if w: return w
    cand = os.path.expanduser(r"~\micromamba\root\envs\ccx\Library\bin\ccx.exe")
    if os.path.exists(cand): return cand
    return arg

def ccx_env(ccx):
    env = os.environ.copy()
    n = str(os.cpu_count() or 1)
    env["OMP_NUM_THREADS"] = n
    env["CCX_NPROC_EQUATION_SOLVER"] = n
    ccx_dir = os.path.dirname(os.path.abspath(ccx))
    extra = [ccx_dir, os.path.normpath(os.path.join(ccx_dir, "..", "mingw-w64", "bin"))]
    root = os.path.normpath(os.path.join(ccx_dir, "..", ".."))
    extra += [root, os.path.join(root, "Library", "bin"), os.path.join(root, "Library", "mingw-w64", "bin")]
    env["PATH"] = os.pathsep.join(extra + [env.get("PATH", "")])
    return env

def cleanup(deck):
    for ext in (".frd", ".cvg", ".12d"):
        p = deck + ext
        if os.path.exists(p):
            try: os.remove(p)
            except OSError: pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--coarse", action="store_true"); ap.add_argument("--no-solve", action="store_true")
    ap.add_argument("--ccx"); ap.add_argument("--mesh-size", type=float, default=0.0)
    ap.add_argument("--cases", default="", help="comma-separated load case names; default all")
    a = ap.parse_args(); c = yaml.safe_load(open(a.cfg)); os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    try: gmsh.option.setNumber("General.NumThreads", os.cpu_count() or 1)
    except Exception: pass
    gmsh.model.add("torso_r1")
    tags = build(c); gmsh.write(os.path.join(a.out, "torso_r1.step"))
    h = a.mesh_size if a.mesh_size > 0 else c["mesh"]["size_coarse" if a.coarse else "size"]
    gmsh.option.setNumber("Mesh.MeshSizeMax", h); gmsh.option.setNumber("Mesh.MeshSizeMin", h/4)
    gmsh.option.setNumber("Mesh.SecondOrderLinear", 1)  # straight-sided tets: no negative jacobians on coarse curved edges
    print(f"MESH h={h}", flush=True)
    gmsh.model.mesh.generate(3); gmsh.model.mesh.setOrder(2)
    N = nodes(); E, skipped = elements(tags); E = split_posts(E, N, c)
    used = {n for el in E.values() for _, ns in el for n in ns}
    rec = element_info(E, N)
    g = c["geometry"]; b, L, pv, p, e = g["bulkhead"], g["land"], g["pelvis"], g["partition"], g["ethercat_bosses"]
    B = 1e4; xf = b["x0"]+b["t"]+L["t"]; zt = pv["z0"]+pv["height_z"]; t = 0.05
    sets = {
        "fixed": node_set(N, (-B, -B, pv["z0"]-t, B, B, pv["z0"]+t), used),
        "land": node_set(N, (xf-t, -L["size"]/2-t, L["z_c"]-L["size"]/2-t, xf+t, L["size"]/2+t, L["z_c"]+L["size"]/2+t), used),
        "land_off": node_set(N, (xf-t, -0.5-t, L["z_c"]-0.5-t, xf+t, L["size"]/2+t, L["z_c"]+L["size"]/2+t), used),   # LC1b: 51x51 quadrant patch, centroid offset +25 y / +25 z
        "shoulder_flange_L": node_set(N, (-B, b["width_y"]/2-t, b["z0"]-t, B, B, B), used),
        "pelvis_top": node_set(N, (-B, -B, zt-t, B, B, zt+t), used),
        "partition": node_set(N, (p["x0"]-t, -B, p["z0"]+t, p["x0"]+t, B, B), used),
        "ethercat_bosses": node_set(N, (p["x0"]-t, -e["dx"], e["z_c"]-e["dz"], p["x0"]+t, e["dx"], e["z_c"]+e["dz"]), used),
    }
    gmsh.finalize()
    node_sets = {k: {n for _, ns in el for n in ns} for k, el in E.items()}
    shared = {}
    keys = [k for k in node_sets if node_sets[k]]
    for i, k in enumerate(keys):
        for m in keys[i+1:]:
            shared[f"{k}|{m}"] = len(node_sets[k] & node_sets[m])
    def npair(a, b):
        return shared.get(f"{a}|{b}", shared.get(f"{b}|{a}", 0))
    pairs = (([("waist", "pelvis")] + ([("yoke", "waist"), ("yoke", "bulkhead")] if c["geometry"]["waist"].get("yoke2") else [("waist", "bulkhead")])) if c["geometry"].get("waist") else []) + [("posts", "pelvis"), ("posts", "bulkhead"), ("partition", "bulkhead")] + ([] if c["geometry"].get("bay_box") else [("partition", "pelvis")]) + ([("bulkhead", "pelvis")] if c["geometry"].get("bay_box") and not c["geometry"]["posts"]["y"] and not c["geometry"].get("waist") else [])
    for a_, b_ in pairs:
        if not node_sets.get(a_) or not node_sets.get(b_):
            continue   # part absent in this config (e.g. 3c has no posts)
        if npair(a_, b_) <= 0:
            raise SystemExit(f"disconnected mesh: {a_}-{b_} shared={npair(a_, b_)}")
    masses = {}
    for part, el in E.items():
        if not el: continue
        mat = c["geometry"][part]["mat"]; rho = c["materials"][mat]["rho"]
        vol = sum(rec[e]["vol"] for e, _ in el)
        masses[part] = {"mat": mat, "volume_mm3": round(vol, 1), "kg": round(vol*rho*1000, 4)}
    qs = [info["q"] for info in rec.values()]
    res = {"mesh_h": h, "element": "C3D10", "solver": "calculix",
           "nodes": len(used), "elements_skipped_not_tet10": skipped,
           "parts": {k: len(v) for k, v in E.items()},
           "set_sizes": {k: len(v) for k, v in sets.items()},
           "shared_nodes": shared,
           "mass_kg": {k: v["kg"] for k, v in masses.items()},
           "mass_kg_total": round(sum(v["kg"] for v in masses.values()), 4),
           "mass_detail": masses,
           "quality_min": round(min(qs), 5) if qs else None,
           "quality_lt_0.01": sum(1 for q in qs if q < 0.01),
           "singularity_band_mm": SING_BAND,
           "criteria": c["criteria"], "cases": {}}
    print(f"MESHED h={h} nodes={res['nodes']} elems={sum(res['parts'].values())} qmin={res['quality_min']} qlt={res['quality_lt_0.01']} mass={res['mass_kg_total']}", flush=True)
    ccx = None if a.no_solve else resolve_ccx(a.ccx)
    if not a.no_solve and not ccx:
        raise SystemExit("ccx not found (pass --ccx)")
    cr = c["criteria"]; allpass = True
    near = make_singular(c)
    want = [s.strip() for s in a.cases.split(",") if s.strip()] if a.cases else list(c["load_cases"])
    for name in want:
        lc = c["load_cases"][name]
        for req in ("fixed", lc["target"]):
            if not sets.get(req):
                raise SystemExit(f"empty node set {req} for {name}")
        deck = os.path.join(a.out, name); write_deck(deck + ".inp", c, N, E, sets, name, lc)
        for info in rec.values(): info["vm"] = 0.0
        r = {"deck": deck + ".inp", "solved": False}
        print(f"SOLVE {name}", flush=True)
        if ccx and not a.no_solve:
            t1 = time.time()
            log_path = deck + ".log"
            with open(log_path, "w", encoding="utf-8", errors="replace") as logf:
                p_ = subprocess.run([ccx, "-i", name], cwd=a.out, stdout=logf, stderr=subprocess.STDOUT,
                                    env=ccx_env(ccx))
            log = open(log_path, encoding="utf-8", errors="replace").read()
            d = parse_dat(deck + ".dat", rec)
            cleanup(deck)
            bad = ("ERROR" in log) or ("Job finished" not in log) or p_.returncode not in (0, None)
            r["solved"] = (not bad) and any(info["vm"] > 0 for info in rec.values())
            r["seconds"] = round(time.time()-t1, 1)
            r["ccx_rc"] = p_.returncode
            if not r["solved"]: r["log_tail"] = log[-800:]
            F = lc.get("F", [0, 0, 0])
            rf = d["RF"]
            fres = math.sqrt(sum((F[i]+rf[i])**2 for i in range(3)))
            fmag = math.sqrt(sum(v*v for v in F))
            r["applied_F"] = F
            r["reaction_F"] = [round(v, 3) for v in rf]
            r["force_residual_N"] = round(fres, 4)
            r["equilibrium_pass"] = bool(fres < 5.0 or (fmag > 0 and fres/fmag < 0.02))
            chk = {}
            for part, el in E.items():
                if not el: continue
                gp = g[part]; Mt = c["materials"][gp["mat"]]
                if gp.get("path") == "single" and "allowable" not in gp and Mt["Sy"] > 300:
                    raise SystemExit(f"R-128: single-path {part} needs a per-part allowable")
                Sy = gp.get("allowable", Mt.get("allowable", Mt["Sy"]))
                Sy = lc.get("allowables", {}).get(part, Sy)   # per-case (T&R b1fe48f fall/ultimate allowables)
                st = part_stats(rec, near, part)
                vm_gate = st["vm_struct"] if st["vm_struct"] else st["vm_max"]
                sf = Sy/vm_gate if vm_gate else float("inf")
                sf_raw = Sy/st["vm_max"] if st["vm_max"] else float("inf")
                entry = {"path": gp.get("path"), "allowable": Sy,
                         "vm_max": round(st["vm_max"], 2), "vm_loc_mm": st["vm_loc"],
                         "vm_struct": round(st["vm_struct"], 2), "vm_struct_loc_mm": st["vm_struct_loc"],
                         "SF": round(sf, 3), "SF_raw": round(sf_raw, 3), "pass": bool(sf >= lc.get("SF_min", cr["SF_min"]))}
                if part == "posts":
                    entry["vm_ligament"] = round(st["vm_ligament"], 2)
                    entry["vm_ligament_loc_mm"] = st["vm_ligament_loc"]
                    entry["n_ligament"] = st["n_ligament"]
                    if st["vm_ligament"]:
                        entry["SF_ligament"] = round(Sy/st["vm_ligament"], 3)
                if "allowable" not in gp:
                    entry["SF_vs_320"] = round(320.0/vm_gate, 3) if vm_gate else None
                chk[f"SF_{part}"] = entry
            if d["U"]:
                um = max(d["U"])
                lim = lc.get("defl_max", cr["land_defl_max"])
                chk["land_defl"] = {"mm": round(um, 5), "limit_mm": lim, "pass": (bool(um <= lim) if name.startswith("LC1") else None)}
            if d["freq"]:
                pos = [f for f in d["freq"] if f > 1e-3]
                f1 = min(pos) if pos else min(d["freq"])
                chk["mode1_hz"] = {"hz": round(f1, 2), "all_hz": [round(f, 2) for f in d["freq"]],
                                   "pass": bool(f1 >= cr["mode1_min_hz"])}
            if d["buckle"]:
                posb = [b_ for b_ in d["buckle"] if b_ > 0]
                fac = min(posb) if posb else min(d["buckle"])
                chk["buckling"] = {"factor": round(fac, 3), "all": [round(b_, 3) for b_ in d["buckle"]],
                                   "pass": bool(fac >= cr["buckling_min"])}
            chk["equilibrium"] = {"residual_N": r["force_residual_N"], "pass": r["equilibrium_pass"]}
            r["checks"] = chk
            allpass &= r["solved"] and r["equilibrium_pass"] and all(v["pass"] is not False for v in chk.values())
            print(f"DONE {name} solved={r['solved']} eq={r['force_residual_N']} s={r['seconds']}", flush=True)
        res["cases"][name] = r
        json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    res["overall"] = "PASS" if (allpass and ccx and not a.no_solve) else ("FAIL" if ccx and not a.no_solve else "NOT_SOLVED")
    res["wall_s"] = round(time.time()-t0, 1)
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    print(res["overall"], res["nodes"], res["mass_kg_total"], json.dumps(res["set_sizes"]), flush=True)

if __name__ == "__main__":
    main()
