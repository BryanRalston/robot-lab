import numpy as np, math
p='/tmp/rla/modules/design/cad/covers/hip_skirt_r8.py'
src=open(p).read().split("single=[b for b")[0]
src=src.replace("POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]",
 "POSES=[(p,r,y) for p in list(range(-105,41,5))+[-107.5,42.5] for r in (-20,-14.5,-12,-8,-4,0,5,10,15,17.5) for y in (-37.5,-35,-17,0,22,45,47.5)]")
src=src.replace("R1=dmin[0]-25","R1=144.0")
src=src.replace("P=cyl(150,35,60,y0=60)","""P=[]
for ph in np.linspace(35,60,26):
    for y in np.linspace(86,200,36):
        if y < 86 + 40*max(0,(ph-35))/25: continue
        r=math.radians(ph); P.append([-150*math.sin(r),y,920-150*math.cos(r)])
P=np.array(P)""")
src=src.split("lr=[];lr_bad=[]")[0]
ns={'__file__':p}; exec(compile(src,'x','exec'),ns)
hem=ns['hem']; T=ns['T']; P=ns['P']; mir=ns['mir']
inrom=[(g,q) for g,q in hem if -12<=q[1]<=15 and -35<=q[2]<=45 and -105<=q[0]<=40]
ovt=[(g,q) for g,q in hem if -14.5<=q[1]<=17.5]
print('hem min ROM',min(inrom),'ovt',min(ovt),'band ROM/ovt',sum(5<g<25 for g,q in inrom),sum(5<g<25 for g,q in ovt),'max',max(inrom)[0])
from scipy.spatial import cKDTree
rng=np.random.default_rng(1); N=6000
def samp(n): return np.c_[rng.uniform(-107.5,42.5,n),rng.uniform(-14.5,17.5,n),rng.uniform(-37.5,47.5,n)]
A=samp(N); B=samp(N); worst=(1e9,None); bad3=0; bad28=0; deep=0
AX=np.array([[0,130,z] for z in np.linspace(500,900,9)])
for a,b in zip(A,B):
    ta=T(P,*a); tb=mir(T(P,*b))
    g=float(cKDTree(ta).query(tb)[0].min())
    legs=float(np.linalg.norm(T(AX,*a)[:,None]-mir(T(AX,*b))[None],axis=2).min())
    if legs<60: continue
    if g<3: bad3+=1; deep+= (min(a[0],b[0])< -10)
    if g<28: bad28+=1
    if g<worst[0]: worst=(g,(a.round(1),b.round(1)))
print('asym feasible pairs N',N,'<3mm',bad3,'(of which a leg flexed beyond -10:',deep,') <28mm',bad28,'worst',worst)
