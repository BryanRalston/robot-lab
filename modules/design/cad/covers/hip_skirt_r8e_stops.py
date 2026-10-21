"""P-023 rev 8e option (a): stop tip -> rigid cup, contact pose (panels parallel, inboard faces 110 mm apart, y=+-55, local frame
x fwd/z up at the phi40/phi70 stations). L panel: stop at phi40, cup at phi70; R mirrored (cup phi40, stop phi70).
Stop: PA66-GF30 tube d25/d17, 95 mm from face. Cup: OD35/bore 29 (2 mm radial entry gap), 45 mm tall (5 past 40 mm foam), floor 15 from face,
45 deg lead-in to d45 at the mouth. Panels simplified to 3 mm plates 160x110 for the contact model."""
import cadquery as cq, json, os
H=os.path.dirname(os.path.abspath(__file__))
def xz(y0,d,dy): return cq.Workplane("XZ").workplane(offset=-y0)  # normal -y
ZS={'p40':-55,'p70':55}
def plate(ys): return cq.Workplane("XY").box(110,3,160).translate((0,ys,0))
def stop(ys,z,sg):
    s=cq.Workplane("XZ").center(0,z).circle(12.5).circle(8.5).extrude(95)
    return s.translate((0,ys+(0 if sg<0 else 95),0)) if sg<0 else s.mirror("XZ").translate((0,ys-95,0)).translate((0,95,0))
def tube(z,ro,ri,L): return cq.Workplane("XZ").center(0,z).circle(ro).circle(ri).extrude(L)
parts={}
# L panel at y=+55: stop toward -y at p40, cup toward -y at p70
parts['L_panel']=plate(56.5)
parts['L_stop_p40']=tube(ZS['p40'],12.5,8.5,95).translate((0,55,0))       # XZ extrude goes -y
parts['L_cup_p70']=tube(ZS['p70'],17.5,14.5,45).translate((0,55,0)).union(tube(ZS['p70'],22.5,17.5,3).translate((0,55-42,0))).union(cq.Workplane('XZ').center(0,ZS['p70']).circle(14.6).extrude(15).translate((0,55,0)))
parts['R_panel']=plate(-56.5)
parts['R_cup_p40']=tube(ZS['p40'],17.5,14.5,45).mirror("XZ").translate((0,-55,0)).union(tube(ZS['p40'],22.5,17.5,3).mirror("XZ").translate((0,-55+42,0))).union(cq.Workplane('XZ').center(0,ZS['p40']).circle(14.6).extrude(15).mirror('XZ').translate((0,-55,0)))
parts['R_stop_p70']=tube(ZS['p70'],12.5,8.5,95).mirror("XZ").translate((0,-55,0))
a=cq.Assembly()
for k,v in parts.items(): a.add(v,name=k)
a.save(os.path.join(H,'hip_skirt_r8e_stops.step'))
c=cq.Compound.makeCompound([v.val() for v in parts.values()]); cq.exporters.export(c,os.path.join(H,'hip_skirt_r8e_stops.stl'),tolerance=0.3)
bb=c.BoundingBox(); print([round(v,1) for v in (bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax)])

import math
rho=1.36e-3
m_stop=math.pi*(12.5**2-8.5**2)*95*rho; m_cup=(math.pi*(17.5**2-14.5**2)*45+math.pi*14.6**2*15+math.pi*(22.5**2-17.5**2)*3)*rho
json.dump(dict(rev="P-023 rev 8e option (a)",frame="contact-pose local: panels parallel, inboard faces y=+-55 (110 rigid), x fwd, z up; z=-55 phi40 station, +55 phi70",
 contact_pose="limp adduction with equal pitch/roll/yaw both legs (the only family where the tip lands in the cup)",
 stop=dict(mat="PA66-GF30",od=25,id=17,len_from_face=95,station="L phi40 / R phi70"),
 cup=dict(mat="PA66-GF30",od=35,bore=29,radial_entry_gap=2.0,height=45,floor_from_face=15,engagement=30,lead_in="45 deg to d45 mouth (capture +-8 mm)"),
 foam_gaps=dict(foam_face_gap_mm=30,cup_proud_of_foam_mm=5,trap="none: 5 mm step <=5, 30 mm open >=25"),
 alignment=dict(poses=57600,closing_past_stand=16668,seated_capture8=101,seated_capture16=365,lateral_miss_p50_mm=87,p90=153,max=245,stop_axis_angle_p50_deg=44,
   verdict="FAIL: tip lands off-cup on the other panel/foam in ~98% of closing poses; seats only when the two legs' pitch and roll match within ~+-5 deg/+-3 deg (EST from grid)"),
 strength=dict(axial_165N_MPa=0.8,lat_165N_at44deg_bend_MPa=9.0,powered_2200N_axial_MPa=10.4,powered_2200N_at44deg_bend_MPa=120,fall_1000N_EST_at44deg_MPa=55,
   PA12_d16_solid_powered_bend_MPa=361,verdict="PA12 fails powered; PA66-GF30 d25/d17 tube 120 MPa vs ~130-180 conditioned UTS (SF 1.1-1.5) MARGINAL; specify breakaway: 2x M4 PA66 shear screws at the base, release ~1.0 kN lateral"),
 mass_kg_side=round((m_stop+m_cup)/1000,3),mass_delta_vs_8d=round((m_stop+m_cup)/1000-0.010,3)),open(os.path.join(H,'hip_skirt_r8e_stops.json'),'w'),indent=1)
