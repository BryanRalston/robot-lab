import numpy as np,trimesh,math,json
from scipy.spatial import cKDTree
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'hip_skirt_r8g_chk.py')).read().split("q=(42.5")[0])
def axes(q):
    p,r,yw=q; Rz=R('z',yw); o=(np.array([0,0,1045.]))@Rz.T+[0,130,0]; return o,Rz@[1,0,0]
def lev(pt,q):
    o,u=axes(q); v=np.array(pt)-o; roll=np.linalg.norm(v-np.dot(v,u)*u); yaw=math.hypot(pt[0]-0,pt[1]-130); return round(float(roll),1),round(float(yaw),1)
h=json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'hem.json'))); l=json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'lr2.json')))
out={}
for k in ('hem_panel','hem_shroud'): out[k]=dict(pose=h[k]['pose'],point=h[k]['point'],lever_roll_yaw_mm=lev(h[k]['point'],h[k]['pose']))
for k in ('panel_yr86','shroud_yr86','panel_yr150'):
    out['LR_'+k]=dict(pose=l[k]['L'],point_L=l[k]['pL'],lever_roll_yaw_mm=lev(l[k]['pL'],l[k]['L']))
# nominal ROM symmetric-pair check (no overtravel)
nom=[(p,r,y) for p in range(-105,41,5) for r in (-12,-8,-4,0,5,10,15) for y in (-35,-17,0,22,45)]
for nm,S in (('panel',PAN[::6]),('shroud',SHR)):
    b=min((float(cKDTree(pose(S,*q)).query(pose(mir(S),*q,side=-1))[0].min()),q) for q in nom)
    out['LR_nominal_sym_'+nm]=[round(b[0],1),b[1]]
print(json.dumps(out)); json.dump(out,open('lev.json','w'),indent=1)
