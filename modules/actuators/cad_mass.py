"""RL Actuators round 2: CadQuery mass properties for leg actuator housings and twin-screw linkages (R-001 items 1-2).
Geometry from drawing values: Kollmorgen TBM2G stator OD/stack (datasheets/tbm2g_manual.pdf §9), Harmonic Drive CSG-2A Table 8
(OD A, axial length B; datasheets/hd_csf_csg_catalog.pdf), Rollvis RV12 nut D1 26 / flange D4 46 / L1 36 (datasheets/rollvis_rv_tables.pdf p.25),
IKO CRBH 6013 A 60x90x13 (datasheets/iko_crb_catalog.pdf). Run: python3 cad_mass.py -> results/cad_mass.json, results/cad_mass.md, cad/*.step"""
import cadquery as cq, json, math, os
H=os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{H}/cad',exist_ok=True)
RHO={'7075':2810,'steel':7850,'Ti6Al4V':4430}
def kg(s,mat): return s.val().Volume()*1e-9*RHO[mat]
def tube(od,idd,L): return cq.Workplane('XY').circle(od/2).circle(idd/2).extrude(L)
def disc(od,t,idd=0):
    w=cq.Workplane('XY').circle(od/2)
    if idd: w=w.circle(idd/2)
    return w.extrude(t)
WALL=2.0      # 7075-T6 wall; torque/bending stress check below (machining minimum, not strength, governs)
# stator OD, stack length (TBM2G drawing: OD from model number, stack 14.76 / 19.26 mm + end-turns -> manual "overall length" column)
MOT={'TBM2G-06008':(60,17.71),'TBM2G-08508':(85,19.34),'TBM2G-07613':(76,23.09),'TBM2G-06013':(60,22.21)}
CSG={'CSG-17-100':(60,32.5),'CSG-25-100':(85,37.0)}           # Table 8: øA, B (CSG)
CRB={'CRBH 6013 A':(60,90,13)}
def rotary(motor,gear,bear='CRBH 6013 A'):
    mod,ml=MOT[motor]; god,gB=CSG[gear]; bd,bD,bB=CRB[bear]
    D=max(mod,bD)+2*WALL+2; L=ml+8+gB+bB+6            # motor + 8 mm encoder/rotor hub gap + gear + bearing + 6 mm output flange
    body=tube(D,D-2*WALL,L)
    rear=disc(D,2.5,idd=D*0.35)                         # rear cap with cable/encoder bore
    seat=tube(bD+8,bD,bB).translate((0,0,L-bB))          # bearing outer-ring seat (4 mm radial)
    flange=disc(D+14,4,idd=D-2*WALL).translate((0,0,L-4))
    for k in range(8):
        a=2*math.pi*k/8; flange=flange.cut(cq.Workplane('XY').circle(2.75).extrude(4).translate(((D+7)/2*math.cos(a),(D+7)/2*math.sin(a),L-4)))
    stator_land=tube(mod+2*WALL,mod,4).translate((0,0,4))   # stator bond land
    s=body.union(rear).union(seat).union(flange).union(stator_land)
    return s,dict(D=D,L=L)
def linear_body(motor,fins=0,bosses='both',web=0.0,eye=False):
    """One screw unit body: motor can (stator OD) + necked nut housing (nut D1 26 + 2 x 7202 angular-contact pair OD 35) + trunnion bosses.
    v4 audit (D59-D62): bosses 'both' | 'outer' (local +x only) | 'none'; web>0 = half of a shared centre web to local x=-web (knee twin housing,
    screw half-spacing 45 -> web to the mid-plane); eye=True = axial GE 12 C eye lug behind the rear cap (centre z -15, bore along local x)."""
    mod,ml=MOT[motor]; D=mod+2*WALL+2; Lm=ml+20                # motor section incl. rotor support bearing + encoder
    Dn=35+2*WALL+2; Ln=36+20                                   # nut section: RV12 nut L1 36 + bearing pair 2 x 10 mm
    m=tube(D,D-2*WALL,Lm).union(disc(D,2.5,idd=D*0.35))
    cone=cq.Workplane('XY').circle(D/2).workplane(offset=6).circle(Dn/2).loft().cut(cq.Workplane('XY').circle(D/2-WALL).workplane(offset=6).circle(Dn/2-WALL).loft()).translate((0,0,Lm))
    n=tube(Dn,Dn-2*WALL,Ln).translate((0,0,Lm+6)).union(disc(Dn,3,idd=14).translate((0,0,Lm+6+Ln-3)))
    s=m.union(cone).union(n)
    for sgn in ((1,-1) if bosses=='both' else (1,) if bosses=='outer' else ()):
        s=s.union(cq.Workplane('YZ').circle(10).extrude(7).translate((sgn*(D/2)-1 if sgn>0 else -(D/2)-6,0,Lm/2)))   # trunnion bosses (v4: sunk 1 mm into the can wall so the boss fuses; was tangent -> separate solid)
    if web:   # shared centre web (rib 6 mm, fore-aft depth 24, over the motor section) + top/bottom flanges 3 mm
        x0,x1=-web,-(D/2-WALL)
        s=s.union(cq.Workplane('XY').box(x1-x0,6,Lm).translate(((x0+x1)/2,0,Lm/2)))
        for zc in (1.5,Lm-1.5): s=s.union(cq.Workplane('XY').box(x1-x0,24,3).translate(((x0+x1)/2,0,zc)))
    if eye:   # GE 12 C (D 22, C 7) in a 10 mm lug, centre 15 mm behind the rear cap; replaces the trunnion bosses
        lug=cq.Workplane('YZ').center(0,-15).circle(15).extrude(10).translate((-5,0,0)).union(cq.Workplane('XY').box(10,30,15).translate((0,0,-7.5)))
        s=s.union(lug.cut(cq.Workplane('YZ').center(0,-15).circle(11).extrude(12).translate((-6,0,0))))
    for k in range(fins): s=s.union(tube(D+16,D-1,3).translate((0,0,6+k*9)))
    return s,dict(D=D,L=Lm+6+Ln)
def knee_twin(dy=45):
    h=linear_body('TBM2G-07613',bosses='outer',web=dy)[0]
    return h.translate((dy,0,0)).union(h.mirror('YZ').translate((-dy,0,0)))
def hub():   # nut-rotor hub: 7075 sleeve rotor->nut flange (RV12 flange ø46, 6 x M5 per Rollvis p.25); 2.0 mm wall, 14 mm engagement
    s=tube(30.2,26.2,14).union(disc(46,4,idd=26.2))
    for k in range(6):
        a=2*math.pi*k/6; s=s.cut(cq.Workplane('XY').circle(2.75).extrude(5).translate((18*math.cos(a),18*math.sin(a),0)))
    return s
def pins(): return cq.Workplane('XZ').circle(8).circle(4.5).extrude(12).union(cq.Workplane('XZ').circle(8).circle(4.5).extrude(12).translate((0,40,0)))   # 2 x ø16/ø9 x12 hollow steel (v3 model.py stubs were solid)
def lever(r_mm,dy=45,h=24,t=12,taper=True):
    """Twin-screw crossbar + 2 outboard cheeks (v3 model.py l.158 form), pivot boss ø32, scaled to lever radius r."""
    # crossbar: moment is max at the pivot web and zero at the cheeks -> section tapers 24 -> 12 mm (same SF at the root)
    half=lambda sg: cq.Workplane('YZ').polyline([(0,-t/2),(sg*(dy+20),-t/2),(sg*(dy+20),t/2),(0,t/2)]).close().extrude(h/2,both=True)
    bar=cq.Workplane('XZ').polyline([(-h/2,0),(h/2,0),(h/4,0),(-h/4,0)]).close()  # placeholder (replaced below)
    prof=cq.Workplane('XY').polyline([(-h/2,0),(h/2,0),(h/4,dy+20),(-h/4,dy+20)]).close().extrude(t/2,both=True)
    bar=prof.union(prof.mirror('XZ')).translate((0,0,-r_mm))
    if not taper: bar=cq.Workplane('XY').box(h,2*dy+40,t).translate((0,0,-r_mm))
    ch=lambda sg: cq.Workplane('XY').box(h,8,r_mm+10).translate((0,sg*(dy+16),-r_mm/2))
    return bar.union(ch(1)).union(ch(-1))
OUT={}
def rec(name,s,mat,group,note=''):
    m=kg(s,mat); OUT[name]=dict(mass=m,mat=mat,group=group,note=note); cq.exporters.export(s,f'{H}/cad/{name}.step'); return m
rec('hip_yaw_housing',rotary('TBM2G-06008','CSG-17-100')[0],'7075','housing')
rec('hip_roll_housing',rotary('TBM2G-08508','CSG-25-100')[0],'7075','housing')
rec('hip_pitch_body_x1',linear_body('TBM2G-07613',bosses='none')[0],'7075','housing','v4 D62: unused trunnion bosses removed (axial eye mount)')
rec('knee_body_x1',linear_body('TBM2G-07613',bosses='outer',web=45)[0],'7075','housing','v4 D59: half of knee_twin_housing (outer boss +x, half web to the mid-plane)')
rec('knee_twin_housing',knee_twin(),'7075','reference','v4 D59: one-piece twin housing, = 2 x knee_body_x1')
rec('ankle_body_x1',linear_body('TBM2G-06013',fins=4,bosses='none',eye=True)[0],'7075','housing','v4 D60/D61: axial GE 12 C top eye lug, no trunnion bosses; 4 fins')
rec('nut_rotor_hub_x1',hub(),'7075','linkage')
rec('trunnion_pins_pair',pins(),'steel','linkage')
rec('hip_pitch_lever_r50',lever(50),'7075','linkage','new part (hip_pitch twin screw); Legs to integrate on thigh')
rec('knee_lever_r47p5',lever(47.5),'7075','linkage','replaces v3 r58.5 lever in shank CAD')
rec('knee_lever_r58p5_v3',lever(58.5,taper=False),'7075','reference','v3 shank part (already in Legs structure mass)')
# stress check of the crossbar at actuator max force (T_out/arm/2 per screw), bending about pivot at cheek offset dy+16
for nm,T,r in (('hip_pitch',454,0.050),('knee',345,0.0475)):
    F=T/r/2; M=F*0.061; Z=12*24**2/6*1e-9; OUT[f'{nm}_lever_check']=dict(F_N=F,sigma_MPa=M/Z/1e6,SF_yield=503/(M/Z/1e6))
# fastener / connector allowance, counted from the bolt patterns (12.9 socket head mass per ISO 4762 tables [EST ±10 %])
FAST=dict(rotary=8*3.6e-3+6*1.0e-3+0.015, linear=6*1.0e-3+4*1.9e-3+0.010)   # rotary: 8xM5x16 flange + 6xM3 cap + connector; linear: 6xM3 + 4xM4 + connector
OUT['fasteners']=FAST
leg=dict(housing=OUT['hip_yaw_housing']['mass']+OUT['hip_roll_housing']['mass']+2*(OUT['hip_pitch_body_x1']['mass']+OUT['knee_body_x1']['mass']+OUT['ankle_body_x1']['mass'])+2*FAST['rotary']+6*FAST['linear'],
         linkage=6*OUT['nut_rotor_hub_x1']['mass']+4*OUT['trunnion_pins_pair']['mass']+OUT['hip_pitch_lever_r50']['mass']+OUT['knee_lever_r47p5']['mass']-OUT['knee_lever_r58p5_v3']['mass'])
OUT['per_leg']=leg
json.dump(OUT,open(f'{H}/results/cad_mass.json','w'),indent=1)
for k,v in OUT.items(): print(k,{a:(round(b,3) if isinstance(b,float) else b) for a,b in v.items()})
