"""D96: ankle-roll stop carrier [EST placeholder 54x62x15 at (0,y,az-22.5), model_v4] relief vs the ankle fork cheeks (y +-24..30, z 80-136 on the shank).
Relief: top-edge step on both +-y sides: for |y-yc| >= YN, carrier top lowered by D (z 65 -> 65-D), inner corner R3 [CAD box-cut here; R3 in the drawing note].
Check: model_v4 OCC min distance carrier <-> shank parts at knee 145, ankle pitch -45..-60, roll 0/+-18 (Legs L73 (C) method). Gate >= 3 mm."""
import sys,os,json;H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(H,'../model'))
import model_v4 as M, cadquery as cq
YN=float(os.environ.get('YN',18)); D=float(os.environ.get('D',6))
_add=M.add
def add(name,seg,solid,*a,**k):
    if 'ankle-roll stop carrier' in name:
        b=solid.BoundingBox(); yc=(b.ymin+b.ymax)/2
        for sy in (1,-1):
            y0=yc+YN if sy>0 else b.ymin-1
            solid=solid.cut(cq.Solid.makeBox(b.xlen+2,(b.ymax-yc)-YN+1,D+1,pnt=cq.Vector(b.xmin-1,y0,b.zmax-D)))
        name=name.replace('[EST]',f'[EST, D96 relief |y|>={YN:g} top -{D:g}]')
    return _add(name,seg,solid,*a,**k)
M.add=add
out=[]
for f in (0,18,-18):
    for q in (-45,-50,-52.5,-55,-57.5,-60):
        pz={'L_knee':145,'L_ankle_pitch':q}
        if f: pz['L_ankle_roll']=f
        parts=M.build(pz); c=[p for p in parts if p['name'].startswith('L_ankle-roll stop carrier')][0]
        sh=[p for p in parts if p['seg']=='L_shank']
        best=(1e9,'')
        for p in sh:
            d=float(c['solid'].distance(p['solid']))
            if d<best[0]: best=(round(d,1),p['name'])
        out.append(dict(roll=f,q=q,min_mm=best[0],to=best[1])); print(out[-1],flush=True)
vol=None
json.dump(dict(YN=YN,D=D,removed_mm3=round(2*54*(31-YN)*D,0),removed_g_per_ankle=round(2*54*(31-YN)*D*2.81e-3,1),rows=out),open(f'{H}/results/ankle_carrier_relief_d96.json','w'),indent=1)
