import numpy as np,trimesh,math,json
from scipy.spatial import cKDTree
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'hip_skirt_r8g_chk.py')).read().split("q=(42.5")[0])
pit=list(range(-105,41,5))+[-107.5,42.5]; yaw=(-37.5,-35,-17,0,22,45,47.5)
G=[(p,r,y) for p in pit for r in (-15.6,-14.5,-12,-8,-4,0,5,10,15,17.5,18.6) for y in yaw]
out={}
for nm,S in (('hem_panel',PAN),('hem_shroud',SHR)):
    L=[]
    for q in G:
        X=pose(S,*q); d,k=KH.query(X); i=int(d.argmin()); L.append((float(d[i])-3.0,q,X[i]))
    g,q,p=min(L,key=lambda t:t[0]); band=sum(5<t[0]-2<25 for t in L)
    out[nm]=dict(min_JCH=round(g,1),min_tol2=round(g-2,1),pose=q,point=p.round(1).tolist(),n_5_25=band,poses=len(G),
      at_42_5_m14_5_m35=round(min(t[0] for t in L if t[1]==(42.5,-14.5,-35)),1))
print(json.dumps(out)); json.dump(out,open('hem.json','w'),indent=1)
