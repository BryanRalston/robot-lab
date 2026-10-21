"""P-156 rev 4d STL (thigh frame): skin grille/inlet/outlet plate, fin-tip baffle, chimney duct walls, inlet floor, outlet passage.
thigh_knee_vents.json is the rev 4d record (thigh_knee_vents.py = rev 4b base; do not re-run it over the json)."""
import os
def box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]; q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return [(v[a], v[b], v[c]) for a, b, c, d in q] + [(v[a], v[c], v[d]) for a, b, c, d in q]
B = [box(-84.0, -82.5, 104, 156, 643, 860),            # skin: inlet 643-681, grille 688-792, outlet 822-860
     box(-57.0, -56.0, 104, 156, 688, 792),            # fin-tip baffle
     box(-57.0, -34.5, 102.9, 104.1, 643, 860), box(-57.0, -34.5, 155.9, 157.1, 643, 860),   # chimney duct walls
     box(-82.5, -57.0, 104, 156, 687.4, 688.6),        # inlet plenum floor (separates the grille space)
     box(-82.5, -57.0, 104, 156, 816.4, 817.6),        # outlet passage floor (above the housing top ~815)
     box(-57.0, -56.0, 104, 156, 792, 817)]            # chimney front wall to the outlet turn
H = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(H, "thigh_knee_vents.stl"), "w") as f:
    f.write("solid v\n")
    for tris in B:
        for t in tris: f.write(" facet normal 0 0 0\n  outer loop\n" + "".join("   vertex %.2f %.2f %.2f\n" % p for p in t) + "  endloop\n endfacet\n")
    f.write("endsolid v\n")
print("ok")
