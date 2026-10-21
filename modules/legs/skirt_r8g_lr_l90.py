import numpy as np,trimesh,math,json,time
from scipy.spatial import cKDTree
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'../design/cad/covers/r8g/hip_skirt_r8g_chk.py')).read().replace('/workspace/rl-id-wt','/workspace/rl-p153').split("q=(42.5")[0])
PI=[-107.5,-90,-70,-50,-30,-10,0,15,30,42.5]; RO=[-15.6,-12,-6,0,8,18.6]; YA=[-38.6,-35,-17.5,0,20,40,43.6]
Q=[(p,r,y) for p in PI for r in RO for y in YA]
Pn=PAN[np.random.default_rng(0).choice(len(PAN),2500,replace=False)]
res={}
for yr in (86,):
  for nm,S in (('panel',Pn[Pn[:,1]>=yr]),('shroud',SHR),('panel_shroud',np.vstack([Pn[Pn[:,1]>=yr],SHR]))):
    if nm=='shroud' and yr!=86: continue
    t=time.time(); Lt=[cKDTree(pose(S,*q)) for q in Q]; Rr=[pose(mir(S),*q,side=-1) for q in Q]
    best=(1e9,0,0); cnt=0
    for i in range(len(Q)):
      for j in range(len(Q)):
        d=float(Lt[i].query(Rr[j],distance_upper_bound=40)[0].min())
        if d<31: cnt+=1
        if d<best[0]: best=(d,i,j)
    i,j=best[1],best[2]; Lp=pose(S,*Q[i]); k=cKDTree(Lp).query(Rr[j])[1]; jj=int(np.argmin(np.linalg.norm(Lp[k]-Rr[j],axis=1)))
    res[f'{nm}_yr{yr}']=dict(raw=round(best[0],1),L=Q[i],R=Q[j],n_raw_lt31=cnt,pL=Lp[k[jj]].round(1).tolist(),pR=Rr[j][jj].round(1).tolist())
    print(nm,yr,res[f'{nm}_yr{yr}'],round(time.time()-t),flush=True)
json.dump(res,open(__import__('os').path.join(__import__('os').path.dirname(__file__),'../../../../legs/results/r031/skirt_r8g_lr_l90.json'),'w'),indent=1)
