#!/usr/bin/env python3
"""Parametric torso cover (CFRP shell) for ID shoulder-sweep re-check. CadQuery. Units mm, robot frame
(origin waist centre, x fwd, y left, z up). Outputs torso_cover.step + torso_cover.json. [EST] dims from R1 §25."""
import json, cadquery as cq
P = dict(x_back=-110, x_front=110, half_w=170, z_bot=0, z_top=470, t=2.0, fillet=25,
         sternum_c=(360,), sternum_size=110, sternum_proud=37, sternum_core=40, sternum_blend=15,
         shoulder_y=170, shoulder_z=380, shoulder_open_dia=130, neck_dia=90, waist_open=(200, 280))
def build(p=P):
    L, W, H = p["x_front"]-p["x_back"], 2*p["half_w"], p["z_top"]-p["z_bot"]
    outer = cq.Workplane("XY").box(L, W, H).translate(((p["x_front"]+p["x_back"])/2, 0, (p["z_top"]+p["z_bot"])/2)).edges("|Z").fillet(p["fillet"])
    s = p["sternum_size"]; zc = p["sternum_c"][0]
    bulge = (cq.Workplane("YZ").workplane(offset=p["x_front"]-1).center(0, zc).rect(s, s)
             .extrude(p["sternum_proud"]+1).edges("|X").fillet(p["sternum_blend"]))
    solid = outer.union(bulge)
    shell = solid.faces(">Z or <Z").shell(-p["t"])
    sh = cq.Workplane("XZ").workplane(offset=-p["half_w"]-50).center(0, p["shoulder_z"]).circle(p["shoulder_open_dia"]/2).extrude(W+100)
    shell = shell.cut(sh.translate((0, 0, 0)))
    return shell
if __name__ == "__main__":
    import os; d = os.path.dirname(os.path.abspath(__file__)); sh = build()
    cq.exporters.export(sh, os.path.join(d, "torso_cover.step"))
    bb = sh.val().BoundingBox(); vol = sh.val().Volume()
    json.dump({"params": P, "bbox_mm": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
               "volume_mm3": vol, "mass_kg_CFRP_1550": round(vol*1.55e-6, 3),
               "sternum_skin_x_mm": P["x_front"]+P["sternum_proud"]}, open(os.path.join(d, "torso_cover.json"), "w"), indent=1)
    print(bb.xmax, round(vol*1.55e-6, 3))
