"""Export STEP (assembly, standing pose) + GLB (named mesh per part) + parts.json metadata for the site viewer."""
import model, json, numpy as np, trimesh, cadquery as cq, os
model.build_upper(); model.build_leg(1); model.build_leg(-1)
COL={'7075-T6':(176,184,196),'CFRP':(45,48,54),'steel':(120,124,130),'Ti-6Al-4V':(150,140,130),'PA12':(230,230,225)}
asm=cq.Assembly(name='bhl_v2')
sc=trimesh.Scene(); meta=[]; seen={}
R=np.array([[0,1,0],[0,0,1],[1,0,0]])  # CAD (x fwd,y left,z up) -> glTF (x=left,y=up,z=fwd)
for p in model.PARTS:
    nm=p['name']; k=seen.get(nm,0); seen[nm]=k+1; nm=nm if k==0 else f'{nm} #{k+1}'
    sh=p['solid'].val(); v=sh.Volume(); m=p['mass'] if p['mass'] is not None else v*model.MAT[p['mat']]
    mat=p['mat'] if p['mat'] in COL else 'steel'
    col=COL.get(p['mat'],(200,90,40) if p['mass'] is not None else (150,150,150))
    if 'motor' in nm or 'strain-wave' in nm: col=(184,115,51)
    if 'battery' in nm: col=(40,90,160)
    if 'compute' in nm: col=(30,140,90)
    asm.add(sh,name=nm.replace('/','-'),color=cq.Color(*[c/255 for c in col]))
    vs,ts=sh.tessellate(0.6,0.5)
    V=np.array([(q.x,q.y,q.z) for q in vs])/1000.0@R.T
    tm=trimesh.Trimesh(V,np.array(ts),process=True)
    tm.visual=trimesh.visual.ColorVisuals(tm,face_colors=np.tile([*col,255],(len(tm.faces),1)))
    i=len(meta); sc.add_geometry(tm,node_name=f'p{i}',geom_name=f'p{i}')
    c=sh.Center(); meta.append(dict(id=f'p{i}',name=nm,seg=p['seg'],material=p['mat'],mass_kg=round(m,3),
        mass_src='catalog/[EST] override' if p['mass'] is not None else 'volume × density',c=[round(x/1000,4) for x in (c.y,c.z,c.x)]))
os.makedirs('export',exist_ok=True)
asm.save('export/bhl_v2_assembly.step')
sc.export('export/bhl_v2.glb')
json.dump(meta,open('export/parts.json','w'))
print(len(meta),'parts', os.path.getsize('export/bhl_v2.glb')/1e6,'MB glb', os.path.getsize('export/bhl_v2_assembly.step')/1e6,'MB step')
