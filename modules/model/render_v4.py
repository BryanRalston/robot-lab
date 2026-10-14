"""Matplotlib render of model_v4 (z-up) for progress images. usage: render_v4.py out.png view [pose-json] [xlim ylim zlim]"""
import sys,json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import model_v4 as M, export_v4 as E
def render(out,elev=12,azim=-60,pose=None,box=None,title='',hl=None):
    parts=M.build(pose); fig=plt.figure(figsize=(7,9),dpi=110); ax=fig.add_subplot(111,projection='3d')
    L=np.array([0.3,-0.5,0.8]); L/=np.linalg.norm(L); allv=[]
    for p in parts:
        v,f=E.tess(p['solid'],1.0); v=v*1000
        if box is not None:
            c=v.mean(0)
            if not all(box[k][0]<=c[k]<=box[k][1] for k in range(3)): continue
        tri=v[f]; n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-9
        c=np.array(E.COL.get(p['group'],(180,180,180)))/255
        if p['est'] and p['group'] in('structure','actuator'): c=np.array((240,140,60))/255
        if hl and any(h in p['name'] for h in hl): c=np.array((255,0,200))/255
        sh=0.45+0.55*np.abs(n@L); cols=np.clip(c[None]*sh[:,None],0,1)
        ax.add_collection3d(Poly3DCollection(tri,facecolors=cols,edgecolors='none')); allv.append(v)
    V=np.vstack(allv); lo,hi=V.min(0),V.max(0); c=(lo+hi)/2; r=(hi-lo).max()/2
    ax.set_xlim(c[0]-r,c[0]+r);ax.set_ylim(c[1]-r,c[1]+r);ax.set_zlim(c[2]-r,c[2]+r);ax.set_box_aspect((1,1,1))
    ax.view_init(elev,azim); ax.set_axis_off(); ax.set_title(title,fontsize=10); plt.tight_layout(); plt.savefig(out); plt.close()
if __name__=='__main__':
    render(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),json.loads(sys.argv[4]) if len(sys.argv)>4 else None,
           json.loads(sys.argv[5]) if len(sys.argv)>5 else None, sys.argv[6] if len(sys.argv)>6 else '')
