# T&R TORSO_BC_P160_REVIEW: free-body inertia-relief waist loads vs fixed pelvis. Mass props: modules/legs/rl/humanoid_mjx.xml (68.0 kg). Run: git show origin/main:modules/legs/rl/humanoid_mjx.xml > /tmp/h.xml; python3 this.py
# NOTE: printed "waist moment" lines from the lower side are superseded; use the "from upper side" / V1 / V3 lines (sign fix).
import xml.etree.ElementTree as E, numpy as np
r=E.parse('/tmp/h.xml').getroot()
pts=[]
def walk(b,p0,tag):
    p=p0+np.array([float(x) for x in (b.get('pos') or '0 0 0').split()])
    n=b.get('name'); t=tag
    if n=='torso': t='upper'
    i=b.find('inertial')
    if i is not None:
        c=p+np.array([float(x) for x in (i.get('pos') or '0 0 0').split()])
        d=i.get('diaginertia'); Iyy=float(d.split()[1]) if d else 0
        pts.append((n,float(i.get('mass')),c,Iyy,t))
    for ch in b.findall('body'): walk(ch,p,t)
for b in r.find('worldbody').findall('body'): walk(b,np.zeros(3),'lower')
m=np.array([q[1] for q in pts]); c=np.array([q[2] for q in pts]); I=np.array([q[3] for q in pts]); up=np.array([q[4]=='upper' for q in pts])
M=m.sum(); zc=(m*c[:,2]).sum()/M; xc=(m*c[:,0]).sum()/M
Iy=(I+m*((c[:,2]-zc)**2+(c[:,0]-xc)**2)).sum()
zaxis=[q[2][2] for q in pts if q[0]=='torso'][0]  # torso COM approx; use torso body origin below
print('M',M,'upper',m[up].sum(),'zc',zc,'Iy',Iy)
import sys
F=29.0; zw=1.16+0.028+0.092; zp=zw+0.150   # waist pitch axis at torso origin [EST], pad 150 mm above
for label,Fext in (('free',1),):
    alpha=F*(zp-zc)/Iy  # rad/s^2 per kN... (kN*m/kg m2)
    a=F/M + alpha*(c[:,2]-zc)  # x-accel kN/kg (sign: force +x at zp)
    lo=~up
    V=(m[lo]*a[lo]).sum()
    Mw=(m[lo]*a[lo]*(zw-c[lo,2])).sum() + (I[lo]*alpha).sum()
    print('waist shear kN',V,'waist moment kNm',Mw,'fixed: 29 /',F*0.15)
    # pelvis at hips pinned? knee contact variant: legs pinned at knees in kneel -> report
print('--- variant: legs pinned at hips (no moment), lumped at hip joint z=1.16')
names=[q[0] for q in pts]
legs=np.array([any(s in q[0] for s in ('hip','thigh','shank','shin','knee','ankle','foot','calf','tib')) and q[0] not in('pelvis',) for q in pts])
print('leg mass',m[legs].sum())
m2=m.copy(); c2=c.copy(); I2=I.copy()
c2[legs,2]=1.16; c2[legs,0]=0; I2[legs]=0
M=m2.sum(); zc=(m2*c2[:,2]).sum()/M; Iy=(I2+m2*(c2[:,2]-zc)**2).sum()
for zpad in (zp,):
  alpha=F*(zpad-zc)/Iy; a=F/M+alpha*(c2[:,2]-zc); lo=~up
  V=(m2[lo]*a[lo]).sum(); Mw=(m2[lo]*a[lo]*(zw-c2[lo,2])).sum()+(I2[lo]*alpha).sum()
  print('zc',zc,'Iy',Iy,'shear',V,'moment',Mw, 'upper only accel frac', (m2[up]*a[up]).sum()/F)
print('--- variant: pivot at knees (L2 kneel tip), knee z rel', )
lo=~up
print('lower items',[(names[k],round(m2[k],2),round(c2[k,2],3),I2[k]) for k in range(len(names)) if lo[k]])
Mu=F*(zp-zw)-(m2[up]*a[up]*(c2[up,2]-zw)).sum()-(I2[up]*alpha).sum()
print('moment from upper side',Mu,'shear upper side',F-(m2[up]*a[up]).sum())
for lab,legsin in (('rigid locked legs',None),):
  pass
# variant 1 upper-side check (rigid whole body, original c,I)
M=m.sum(); zc0=(m*c[:,2]).sum()/M; Iy0=(I+m*((c[:,2]-zc0)**2+(c[:,0]-xc)**2)).sum()
al=F*(zp-zc0)/Iy0; a0=F/M+al*(c[:,2]-zc0)
print('V1 rigid: shear',F-(m[up]*a0[up]).sum(),'moment',F*(zp-zw)-(m[up]*a0[up]*(c[up,2]-zw)).sum()-(I[up]*al).sum())
# variant 3: torso+pelvis+waistY pinned at hip pitch axis zh (legs grounded via knees), legs excluded
zh=1.045; keep=~legs
Ih=(I[keep]+m[keep]*(c[keep,2]-zh)**2).sum(); al=F*(zp-zh)/Ih; a3=al*(c[:,2]-zh)
Vw=F-(m[up]*a3[up]).sum(); Mw=F*(zp-zw)-(m[up]*a3[up]*(c[up,2]-zw)).sum()-(I[up]*al).sum()
R=F-(m[keep]*a3[keep]).sum()
print('V3 hip-pinned: shear',Vw,'moment',Mw,'hip reaction',R)
