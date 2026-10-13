"""CAD mass + inertia per segment vs budget (v2/analysis summary_final.json). Writes out/mass.md, out/mass.json"""
import model, json, numpy as np
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
model.build_upper(); model.build_leg(1); model.build_leg(-1)
bud=dict(mass=model.V3['m'])
def grp(seg):
    b=seg.split('_',1)[-1]
    if b in ('foot','shank','thigh'): return b
    if b in ('pelvis','hipY','hipR'): return 'pelvis'
    return 'upper'
S={}
for p in model.PARTS:
    sh=p['solid'].val(); g=GProp_GProps(); BRepGProp.VolumeProperties_s(sh.wrapped,g)
    v=g.Mass(); rho=model.MAT[p['mat']] if p['mass'] is None else p['mass']/v
    m=v*rho; c=g.CentreOfMass(); c=np.array([c.X(),c.Y(),c.Z()]); M=g.MatrixOfInertia()
    I=np.array([[M.Value(i,j) for j in (1,2,3)] for i in (1,2,3)])*rho   # about part COM, kg*mm^2
    s=S.setdefault(p['seg'],dict(m=0,parts=[]));s['m']+=m;s['parts'].append((m,c,I,p['name'],p['mat']))
out={};tot=0
for seg,s in S.items():
    m=s['m'];com=sum(pm*c for pm,c,_,_,_ in s['parts'])/m;I=np.zeros((3,3))
    for pm,c,Ic,_,_ in s['parts']:
        d=c-com;I+=Ic+pm*(d@d*np.eye(3)-np.outer(d,d))
    out[seg]=dict(mass=round(m,3),com_mm=[round(x,1) for x in com],I_kgm2=[round(x*1e-6,5) for x in np.diag(I)],n=len(s['parts']))
    tot+=m
G={}
for seg,o in out.items(): G[grp(seg)]=G.get(grp(seg),0)+o['mass']
nleg={'foot':2,'shank':2,'thigh':2,'pelvis':1,'upper':1}
L=['# v3 CAD mass and inertia vs v3 catalog rollup','',f'CAD total: **{tot:.1f} kg**; catalog-part rollup (v3/analysis): **{bud["mass"]:.1f} kg**; difference {tot-bud["mass"]:+.1f} kg ({(tot/bud["mass"]-1)*100:+.1f} %).','',
 'Densities: 7075 2810, CFRP 1550, steel 7850, Ti 4430, PA12 1010 kg/m³. Motors, gears, battery, compute and bearings use catalog/[EST] mass overrides applied over their envelope volume.','',
 ]
L+=['','| segment | mass kg | COM mm (world, standing) | Ixx Iyy Izz about COM kg·m² |','|---|---|---|---|']
for seg in sorted(out):o=out[seg];L.append(f"| {seg} | {o['mass']:.2f} | {o['com_mm']} | {o['I_kgm2']} |")
open('out/mass.md','w').write('\n'.join(L));json.dump(dict(total=tot,groups=G,segments=out),open('out/mass.json','w'),indent=1)
print('\n'.join(L[:14]))
