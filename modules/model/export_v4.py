"""Tessellate model_v4 to a light GLB (one mesh per part, colour by status/group) + parts json."""
import json,os,sys,numpy as np,trimesh
import model_v4 as M
COL={'actuator':(70,110,200),'bearing':(225,170,40),'linkage':(60,170,170),'stop':(220,40,40),'sensor':(120,120,120),'power':(90,90,90),'electronics':(90,90,90),'structure':(185,190,198)}
def tess(solid,tol=0.6):
    v,f=solid.tessellate(tol,0.5); return np.array([(p.x,p.y,p.z) for p in v])/1000.0, np.array(f)
def export(out_glb,out_json,pose=None):
    parts=M.build(pose); sc=trimesh.Scene(); meta=[]
    for i,p in enumerate(parts):
        v,f=tess(p['solid'])
        if not len(f): continue
        c=COL.get(p['group'],(180,180,180))
        if p['est'] and p['group'] in ('structure',): c=(235,150,70)   # placeholder structure = orange
        if p['est'] and p['group']=='actuator': c=(240,120,60)
        m=trimesh.Trimesh(v[:,[0,2,1]]*[1,1,-1],f,process=False)   # z-up -> glTF y-up
        m.visual.face_colors=list(c)+[255]
        nm=f'p{i:03d}'; sc.add_geometry(m,node_name=nm,geom_name=nm)
        meta.append(dict(node=nm,name=p['name'],seg=p['seg'],group=p['group'],est=p['est'],joints=sorted(M.chain(p['seg']))))
    sc.export(out_glb); json.dump(meta,open(out_json,'w'),indent=0); return parts
if __name__=='__main__':
    ROOT=M.ROOT; export(os.path.join(ROOT,'site/cad/bhl_v4.glb'),os.path.join(ROOT,'site/cad/parts_v4.json'))
    print(os.path.getsize(os.path.join(ROOT,'site/cad/bhl_v4.glb'))/1e6,'MB')
