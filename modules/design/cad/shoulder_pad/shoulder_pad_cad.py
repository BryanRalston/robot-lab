"""Lightweight parametric shoulder-pad envelope CAD (no deps; ASCII STL per body + assembly).
Frame (Arms R14): X = roll axis, Y outboard, Z up; origin on roll axis at bearing plane. Housing COAXIAL WITH X (R14 fix).
Stand-off/pad placement ON HOLD pending Arbiter R-12x: they intersect the housing as placed. Simple solids only, for the section G clash checks (Arms runs them).
CadQuery is not installed on the RL box (1 GB free RAM); for STEP, run shoulder_pad_cad.py --step on the bryan PC (needs cadquery)."""
import json, math, sys, os
G = json.load(open(os.path.join(os.path.dirname(__file__), "geometry.json")))
def box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return [(v[a],v[b],v[c]) for a,b,c,d in q] + [(v[a],v[c],v[d]) for a,b,c,d in q]
def ring(axis, c, ro, ri, a0, a1, n=48):
    """annulus/cylinder along axis ('x' or 'y'), centre c=(.,.,.), from a0 to a1 along axis."""
    def P(r, t, a):
        u, w = r*math.cos(t), r*math.sin(t)
        return (a, c[1]+u, c[2]+w) if axis == 'x' else (c[0]+u, a, c[2]+w)
    T = []
    for i in range(n):
        t0, t1 = 2*math.pi*i/n, 2*math.pi*(i+1)/n
        for r in [ro] + ([ri] if ri > 0 else []):
            T += [(P(r,t0,a0),P(r,t1,a0),P(r,t1,a1)), (P(r,t0,a0),P(r,t1,a1),P(r,t0,a1))]
        for a in (a0, a1):
            if ri > 0: T += [(P(ri,t0,a),P(ro,t0,a),P(ro,t1,a)), (P(ri,t0,a),P(ro,t1,a),P(ri,t1,a))]
            else: T += [((c[0],a,c[2]) if axis=='y' else (a,c[1],c[2]), P(ro,t0,a), P(ro,t1,a))]
    return T
def stl(name, tris):
    with open(name + ".stl", "w") as f:
        f.write(f"solid {name}\n")
        for a, b, c in tris:
            f.write(" facet normal 0 0 0\n  outer loop\n" + "".join(f"   vertex {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}\n" for p in (a,b,c)) + "  endloop\n endfacet\n")
        f.write(f"endsolid {name}\n")
s, h, p, c, cv = G["standoff_R11"], G["housing"], G["pad"], G["core"], G["cover"]
bodies = {
 "housing_7013": ring('x', (0,0,0), h["bearing_ro"], h["bearing_ri"], *h["bearing_x"]),
 "housing_flange_OD108": ring('x', (0,0,0), h["flange_ro"], h["flange_ri"], *h["flange_x"]),
 "standoff_flange": ring('y', (0,0,0), s["flange_OD"]/2, s["bore_under_box"]/2, -s["flange_t"], 0),
 "standoff_box": box(-s["box"]/2, s["box"]/2, 0, s["box_H"], s["box_zc"]-s["box"]/2, s["box_zc"]+s["box"]/2),
 "standoff_plate": box(-31, 31, s["box_H"], s["box_H"]+s["plate_t"], -20-31, -20+31),
 "tray": box(-31, 31, 27, 27.5, -51, 11),
 "pad_core": box(-c["side"]/2, c["side"]/2, 27.5, 27.5+c["h"], -20-c["side"]/2, -20+c["side"]/2),
 "pad_face_EPP": box(-c["side"]/2, c["side"]/2, 27.5+c["h"], 27.5+c["h"]+6.5, -20-c["side"]/2, -20+c["side"]/2),
 "cover_local_shell": box(-cv["half_x"], cv["half_x"], cv["y_inner"], cv["y_inner"]+cv["t"], -cv["half_z"], cv["half_z"]),
}
out = os.path.dirname(os.path.abspath(__file__)); os.chdir(out)
allt = []
for k, t in bodies.items(): stl(k, t); allt += t
stl("assembly", allt)
print("wrote", len(bodies), "bodies; cover window", cv["window"], "(not cut in STL; check visually)")
if "--step" in sys.argv:
    import cadquery as cq  # bryan PC only
    print("STEP export: implement with cq.Workplane boxes/cylinders from geometry.json")
