"""D96: knee release housing top vs L60 trunnion top plate (underside z 816, thigh-fixed): Legs L74 bbox 2.0 mm < 3 gate.
The world-top points are the REAR fin tip corners at the can end (local y +65.8, z 1, x +-40..50), not the boss or the body.
Fix: spot-trim the fin tips flat at world z <= ZT (812.5, so 3.5 mm) in the model_v4 placement; the cut is mapped back to the local frame.
Fins are not in the load path (forging net 75.7 MPa vs 211 is on the body/boss, D80), so the margin is unchanged. Area loss reported."""
import sys,os,json;H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(H,'../model'))
import model_v4 as M, cadquery as cq
ZT=float(os.environ.get('ZT',812.5))
_st=M.step; M.step=lambda n,*a,**k:_st('knee_twin_housing_release_r116' if n=='knee_twin_housing' else n)
s0=cq.importers.importStep(f'{H}/cad/knee_twin_housing_release_r116.step').val(); s1=s0
# the housing pivots on its trunnions with the knee, so sweep knee 0..145: in each pose, the L60 top plate grown by GAP (box offset)
# is mapped into the housing local frame and cut away (spot-trim of whatever fin/boss tips enter the 3 mm zone).
GAP=float(os.environ.get('GAP',3.5)); hits={}
for kq in list(range(0,146,5))+[145]:
    parts=M.build({'L_knee':kq}); hs=[p for p in parts if p['name'].startswith('L_knee twin housing')][0]['solid']; L=hs.location()
    tp=[p for p in parts if p['name'].startswith('L_knee trunnion bracket top plate')][0]['solid'].BoundingBox()
    tool=cq.Solid.makeBox(tp.xlen+2*GAP,tp.ylen+2*GAP,tp.zlen+2*GAP,pnt=cq.Vector(tp.xmin-GAP,tp.ymin-GAP,tp.zmin-GAP)).moved(L.inverse)
    v=s1.intersect(tool).Volume()
    if v>1e-6: hits[kq]=round(v,2); s1=s1.cut(tool)
ZT=None
A0,A1,V0,V1=s0.Area(),s1.Area(),s0.Volume(),s1.Volume()
cq.exporters.export(cq.Workplane().add(s1),f'{H}/cad/knee_twin_housing_release_r116b.step')
res=dict(GAP=GAP,knee_hits_mm3=hits,removed_mm3=round(V0-V1,1),removed_g=round((V0-V1)*2.81e-3,2),area_m2_before=round(A0/1e6,5),
         area_m2_after=round(A1/1e6,5),area_loss_m2=round((A0-A1)/1e6,6),fin_area_loss_pct_of_0p0703=round((A0-A1)/1e6/0.0703*100,2),valid=s1.isValid(),
         step='cad/knee_twin_housing_release_r116b.step')
json.dump(res,open(f'{H}/results/knee_housing_fin_trim_d96.json','w'),indent=1); print(res)
