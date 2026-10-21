"""Export ID head shell (p100) and torso shell/cover (p009) from site/cad/bhl_v4.glb to STL + faceted STEP (AP214
surface model (OPEN_SHELL; torso shell is open-bottom), no CAD kernel). Frame/units: glTF of site v4 (Y up, metres) converted to mm and to the Arms frame
X fore-aft? -> NO re-orientation applied: coordinates kept as site v4 world, x1000 (mm). Arms: apply your sim->CAD transform.
For a sewn B-rep solid run export_covers_occ.py on the bryan PC (needs cadquery/OCP)."""
import json, struct, numpy as np, os, sys
R = os.path.dirname(os.path.abspath(__file__)); GLB = os.path.join(R, "../../../../site/cad/bhl_v4.glb")
b = open(GLB, "rb").read(); L = struct.unpack("<I", b[12:16])[0]; g = json.loads(b[20:20+L])
bin0 = 20+L+8
CT = {5126: "f4", 5125: "u4", 5123: "u2", 5121: "u1"}; NC = {"SCALAR": 1, "VEC3": 3}
def acc(i):
    a = g["accessors"][i]; v = g["bufferViews"][a["bufferView"]]
    off = bin0+v.get("byteOffset", 0)+a.get("byteOffset", 0)
    return np.frombuffer(b, dtype="<"+CT[a["componentType"]], count=a["count"]*NC[a["type"]], offset=off).reshape(a["count"], -1)
def mesh(name):
    n = next(n for n in g["nodes"] if n.get("name") == name); assert "matrix" not in n and "translation" not in n
    V, F = [], []
    for p in g["meshes"][n["mesh"]]["primitives"]:
        v = acc(p["attributes"]["POSITION"])*1000.0; f = acc(p["indices"]).reshape(-1, 3)+len(np.concatenate(V) if V else [])
        V.append(v); F.append(f)
    return np.concatenate(V), np.concatenate(F)
def stl(fn, V, F):
    with open(fn, "w") as o:
        o.write("solid s\n")
        for t in F:
            o.write(" facet normal 0 0 0\n  outer loop\n" + "".join(f"   vertex {V[i][0]:.4f} {V[i][1]:.4f} {V[i][2]:.4f}\n" for i in t) + "  endloop\n endfacet\n")
        o.write("endsolid s\n")
def step(fn, V, F, label):
    L = []; k = [0]
    def e(s): k[0] += 1; L.append(f"#{k[0]}={s};"); return k[0]
    pts = [e(f"CARTESIAN_POINT('',({x:.4f},{y:.4f},{z:.4f}))") for x, y, z in V]
    faces = [e(f"FACE_OUTER_BOUND('',#{e('POLY_LOOP(%s,(%s))' % (repr(''), ','.join('#%d' % pts[i] for i in t)))},.T.)") for t in F]
    faces = [e(f"FACE('',(#{f}))") for f in faces]
    sh = e(f"OPEN_SHELL('',({','.join('#%d' % f for f in faces)}))"); br = e(f"SHELL_BASED_SURFACE_MODEL('{label}',(#{sh}))")
    ctx = e("( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNIT_ASSIGNED_CONTEXT((#%d,#%d,#%d)) REPRESENTATION_CONTEXT('','') )" % (
        e("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )"), e("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )"), e("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")))
    o0 = e("CARTESIAN_POINT('',(0.,0.,0.))"); ax = e(f"AXIS2_PLACEMENT_3D('',#{o0},$,$)")
    app = e("APPLICATION_CONTEXT('automotive_design')"); e(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{app})")
    pc = e(f"PRODUCT_CONTEXT('',#{app},'mechanical')"); pr = e(f"PRODUCT('{label}','{label}','',(#{pc}))")
    pdf = e(f"PRODUCT_DEFINITION_FORMATION('','',#{pr})"); pdc = e(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app},'design')")
    pd = e(f"PRODUCT_DEFINITION('design','',#{pdf},#{pdc})"); pds = e(f"PRODUCT_DEFINITION_SHAPE('','',#{pd})")
    rep = e(f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#{ax},#{br}),#{ctx})"); e(f"SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})")
    hdr = "ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('faceted cover export'),'2;1');\nFILE_NAME('%s','2026-10-21',('RL Industrial Design'),(''),'','','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n" % os.path.basename(fn)
    open(fn, "w").write(hdr + "\n".join(L) + "\nENDSEC;\nEND-ISO-10303-21;\n")
info = {}
for node, nm in (("p100", "head_shell"), ("p009", "torso_cover")):
    V, F = mesh(node); stl(os.path.join(R, nm+".stl"), V, F); step(os.path.join(R, nm+".step"), V, F, nm)
    info[nm] = {"node": node, "verts": len(V), "tris": len(F), "bbox_mm": [V.min(0).round(1).tolist(), V.max(0).round(1).tolist()]}
json.dump(info, open(os.path.join(R, "covers.json"), "w"), indent=1); print(json.dumps(info))
