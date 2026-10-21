"""D101: feasibility of the integrated knee PU stop (Legs L91 4ea8243 Option B / fallback A) against model_v4 + r116b housing.
Checks: (1) where the r116b housing actually sits relative to the knee axis and the tongue-neck over knee 0..143.6 (CAD distances);
(2) relative travel housing<->shank points between contact 130 and top-out 143.6 (housing pivots about the trunnion with the screw axis);
(3) PU thickness needed (25 % strain) vs the available gap. Gates: 92.5 J in 25 %, 44.1 J design, contact 130, top-out 143.6."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
T=(-130.0,270.0); kz=M.P['knee_z']
def pin(q): t=math.radians(q); return(-47.5*math.sin(t),-47.5*math.cos(t))
def phi(q): p=pin(q); return math.atan2(p[1]-T[1],p[0]-T[0])
def shank_pt(q,r,t):
    a=math.radians(q); return(r*-math.sin(a)+t*-math.cos(a), r*-math.cos(a)+t*math.sin(a))
def in_h(q,P):
    f=-phi(q); d=(P[0]-T[0],P[1]-T[1]); return(d[0]*math.cos(f)-d[1]*math.sin(f), d[0]*math.sin(f)+d[1]*math.cos(f))
trav={}
for r in (50,60,100,150,200,250,280):
    a=in_h(130,shank_pt(130,r,25)); b=in_h(143.6,shank_pt(143.6,r,25)); d=math.hypot(b[0]-a[0],b[1]-a[1])
    trav[r]=dict(travel_mm=round(d,1),PU_t_25pct_mm=round(4*d),PU_area_mm2_for_62cm3=round(62000/(4*d)),F25_kN=round(11.65*62000/(4*d)/1000,1))
cad={}
for q in (0,90,130,143.6):
    ps=M.build({'L_knee':q}); g=lambda s:[p for p in ps if p['name'].startswith('L_') and s in p['name']][0]['solid']
    h=g('knee twin housing'); hb=h.BoundingBox()
    cad[q]=dict(housing_to_tongue_neck=round(h.distance(g('tongue neck')),1),housing_to_lever=round(h.distance(g('knee lever')),1),
                housing_to_tibia=round(h.distance(g('tibia tube')),1),housing_zmin_above_knee=round(hb.zmin-kz),
                housing_volume_cm3=round(h.Volume()/1000,1))
res=dict(rev='D101',source='Legs L91 4ea8243',travel_vs_r=trav,cad=cad,phi_deg={q:round(math.degrees(phi(q)),2) for q in (0,130,143.6)},
 verdict='NO-GO: hard conflict. The r116b housing is >=161 mm from every shank part near the knee (lowest face 185 mm above the knee axis); '
         'there is no housing underside at r50/r60. The only shank part that reaches the housing is the tibia tube at r~200-280 '
         '(gap 66 mm at 130 -> 8 mm at 143.6), where the relative travel is ~44-66 mm -> PU 175-265 mm thick needed. The housing also pivots '
         'about the trunnion and is held by the screws, so a strike on it bends the screws unless its line passes through the trunnion.')
json.dump(res,open(f'{HERE}/results/knee_stop_pu_d101.json','w'),indent=1); print(json.dumps(res,indent=1))
