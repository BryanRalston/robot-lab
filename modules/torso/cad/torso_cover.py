#!/usr/bin/env python3
"""Parametric torso cover (CFRP shell), ID-corrected per e874653 SHOULDER_PAD.md. CadQuery. Units mm, torso frame
(x fwd, y left, z up). z 50-310; width tapers 250 (z 50) -> 340 at the shoulder pitch axis (z 220; V5 330->250
taper, held at 340 so the side walls sit at y ±170); chamfered top shoulders; Ø110 shoulder openings on the pitch
axis; Ø90 neck opening; sternum bulge 110x110, skin at x +147. Outputs torso_cover.step + torso_cover.json."""
import json, os, cadquery as cq
P = dict(x_back=-110, x_front=110, z_bot=50, z_top=310, w_bot=250, w_shoulder=340, z_shoulder=220,
         shoulder_chamfer=45, t=2.0, corner_fillet=20, shoulder_open_dia=110, neck_dia=90,
         sternum_zc=220, slot_w=3.5, slot_pitch=6.0,
         vent_in=dict(z=(105, 155), x_cols=((-60, -24), (-18, 18), (24, 60))),
         vent_out=dict(z=(160, 214), x_cols=((-102, -62), (62, 102))), sternum_size=110, sternum_proud=65, sternum_core=68, sternum_blend=15)
def build(p=P):
    L = p["x_front"]-p["x_back"]; xc = (p["x_front"]+p["x_back"])/2
    hb, hs, c = p["w_bot"]/2, p["w_shoulder"]/2, p["shoulder_chamfer"]
    prof = [(-hb, p["z_bot"]), (hb, p["z_bot"]), (hs, p["z_shoulder"]), (hs, p["z_top"]-c), (hs-c, p["z_top"]),
            (-(hs-c), p["z_top"]), (-hs, p["z_top"]-c), (-hs, p["z_shoulder"])]
    body = cq.Workplane("YZ").workplane(offset=p["x_back"]).polyline(prof).close().extrude(L)
    sh = body.faces("<Z").shell(-p["t"])
    s, t, xf = p["sternum_size"], p["t"], p["x_front"]
    def blk(size, x0, dx, f):
        w = cq.Workplane("YZ").workplane(offset=x0).center(0, p["sternum_zc"]).rect(size, size).extrude(dx)
        return w.edges("|X").fillet(f) if f > 0 else w
    bulge = blk(s, xf - t, p["sternum_proud"] + t, p["sternum_blend"]).cut(blk(s - 2*t, xf - t - 1, p["sternum_proud"] + 1, p["sternum_blend"] - t))
    sh = sh.union(bulge).cut(blk(s - 2*t, xf - t - 1, t + 2, p["sternum_blend"] - t))   # open wall behind bulge (pad pocket, core 40)
    sh = sh.cut(cq.Workplane("XZ").workplane(offset=-hs-20).center(0, p["z_shoulder"]).circle(p["shoulder_open_dia"]/2).extrude(-(2*hs+40)))
    sh = sh.cut(cq.Workplane("XY").workplane(offset=p["z_top"]-10).center(xc, 0).circle(p["neck_dia"]/2).extrude(20))
    for v in (p["vent_in"], p["vent_out"]):   # horizontal slots through the sloped side panel, both sides
        z = v["z"][0] + p["slot_w"]/2
        while z <= v["z"][1] - p["slot_w"]/2 + 1e-6:
            for x0, x1 in v["x_cols"]:
                for sg in (-1, 1):
                    cut = cq.Workplane("XY").box(x1-x0, 80, p["slot_w"]).translate(((x0+x1)/2, sg*160, z))
                    sh = sh.cut(cut)
            z += p["slot_pitch"]
    return sh
def vent_area(v, p=P):
    n = int((v["z"][1]-v["z"][0]-p["slot_w"])//p["slot_pitch"]) + 1
    return n, round(n*sum((b-a) for a, b in v["x_cols"])*p["slot_w"]/100, 1)   # cm2 per side (projected on x-z; true area on the 14.8 deg slope is larger)
THOR = {"basis": "electronics R1 §(duct routing): Thor cold-plate fin stack bay 130 x 200 (y 200 [EST orientation]) + 1 mm PC duct walls; Thor at z ~0.29; Sunon PF40281B1 40x40x28 inside the bay",
        "y_extent_above_z265_mm": 101, "chamfer_inner_y_at_z308_mm": 125 + 2,
        "chamfer_line": "|y| = 170 - (z - 265) outer; at |y| 101 the chamfer is at z 334 > top 310",
        "margin_to_|y|<125_mm": 24, "verdict": "clears with the 45 mm chamfer; no change to 35 mm needed"}
if __name__ == "__main__":
    d = os.path.dirname(os.path.abspath(__file__)); sh = build()
    cq.exporters.export(sh, os.path.join(d, "torso_cover.step"))
    bb = sh.val().BoundingBox(); vol = sh.val().Volume()
    json.dump({"source": "ID e874653 SHOULDER_PAD.md; V5_POLISH_PLAN row 4", "params": P,
               "bbox_mm": [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)],
               "volume_mm3": round(vol), "mass_kg_CFRP_1550": round(vol*1.55e-6, 3),
               "sternum_skin_x_mm": P["x_front"]+P["sternum_proud"],
               "vents_per_side": {"in": vent_area(P["vent_in"]), "out": vent_area(P["vent_out"]), "rule": "A35 >=25 cm2 in/out per bay; slots 3.5 mm wide (>=3 mm), IP2X: 12 mm finger cannot enter, live parts >=80 mm reach behind slots"},
               "thor_duct_check": THOR}, open(os.path.join(d, "torso_cover.json"), "w"), indent=1)
    print([round(v) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)], round(vol*1.55e-6, 3))
