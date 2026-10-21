#!/usr/bin/env python3
"""Parametric torso cover (CFRP shell), ID-corrected per e874653 SHOULDER_PAD.md. CadQuery. Units mm, torso frame
(x fwd, y left, z up). z 50-310; width tapers 250 (z 50) -> 340 at the shoulder pitch axis (z 220; V5 330->250
taper, held at 340 so the side walls sit at y ±170); chamfered top shoulders; Ø110 shoulder openings on the pitch
axis; Ø90 neck opening; sternum bulge 110x110, skin at x +147. Outputs torso_cover.step + torso_cover.json."""
import json, os, cadquery as cq
P = dict(x_back=-110, x_front=110, z_bot=50, z_top=310, w_bot=250, w_shoulder=340, z_shoulder=220,
         shoulder_chamfer=45, t=2.0, corner_fillet=20, shoulder_open_dia=110, neck_dia=90,
         sternum_zc=220, sternum_size=110, sternum_proud=37, sternum_core=40, sternum_blend=15)
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
    return sh
if __name__ == "__main__":
    d = os.path.dirname(os.path.abspath(__file__)); sh = build()
    cq.exporters.export(sh, os.path.join(d, "torso_cover.step"))
    bb = sh.val().BoundingBox(); vol = sh.val().Volume()
    json.dump({"source": "ID e874653 SHOULDER_PAD.md; V5_POLISH_PLAN row 4", "params": P,
               "bbox_mm": [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)],
               "volume_mm3": round(vol), "mass_kg_CFRP_1550": round(vol*1.55e-6, 3),
               "sternum_skin_x_mm": P["x_front"]+P["sternum_proud"]}, open(os.path.join(d, "torso_cover.json"), "w"), indent=1)
    print([round(v) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)], round(vol*1.55e-6, 3))
