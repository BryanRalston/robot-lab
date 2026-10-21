"""D93 rev4 (Thermal 44b7c36 R131 rev4, ID e61cbf2 P-154 guard): knee fins 13 -> FH (18) mm, 8 at 6 mm pitch,
lower (z 690) fin ends tapered 45 deg x TAPER (8) mm to hold 10 mm under the ID guard lower chamfer, fin tips R0.5,
corner M3 standoffs counterbored dia 7 through the fins. UA calibrated to Thermal rev4 (0.246 W/K at 18 mm, no taper).
D91 rev3 (Thermal R131 rev2 16f8176): knee plate flipped: drives hang on the femur-facing side, plate outer
face is a black-anodised window in the thigh shell at the L51 26 mm boundary, 8 axial fins 13 x 1 at 6 mm pitch in the
open stream outside the box. Thermal basis: h 8 only on open black faces; enclosed/femur faces credited 0; UA>=0.185 W/K.
D90 rev2 (Electronics 23f6992 §18.5): G-TWI 4xM2 on 30.6x25.6 clearance holes (dia 2.4), M2x6 up from femur side;
one serrated washer per plate on a masked seat (PE via drive heat sink, §8.3). Knee fins moved to the DRIVE side
(strips beside the 30 mm drive footprint) so the femur-side standoff only clears the M2 heads.
R-134..R-136 Elmo G-TWI standoff heat plates (RL Actuators). CadQuery 2.8; light compute.
Losses: Thermal R131_ELMO_MG.md (MAN-G-TWI v2.011 §11.2.1 chart -25% + 1 W control).
Duty = 0.6 x carry (R-096). Air 35 C (T2 basis). Limit: baseplate <=80 C (85-5), derate starts 75.
Pad: 1 mm gap pad >=3 W/mK over drive base -> 0.3 K/W per drive. Plates on G10/PEEK standoffs: no motor heat.
"""
import json, math, cadquery as cq
RHO=2.70e-3  # 6061 g/mm^3
K=167.0; TAIR=35.0; RPAD=0.30; DRV=(35.0,30.0)  # drive footprint mm (L51/MAN-G-TWI)
DRVZ=lambda nd:[(i-(nd-1)/2)*(DRV[0]+5) for i in range(nd)]
def fin_x(W,nf,side):
    if side=="drive":   # nf/2 fins per strip between drive footprint (DRV[1]/2+1) and plate edge-1.5
        k=nf//2; x0=DRV[1]/2+1.0; x1=W/2-1.5; pitch=(x1-x0)/k
        return [sx*(x0+pitch*(i+0.5)) for sx in(-1,1) for i in range(k)]
    pitch=W/max(nf,1); return [-W/2+pitch*(i+0.5) for i in range(nf)]
def finned(L,W,tb,nf,hf,tf,nd=1,side="femur"):
    p=cq.Workplane("XY").box(W,L,tb,centered=(True,True,False))
    for x in fin_x(W,nf,side):
        z=tb if side=="drive" else -hf
        f=cq.Workplane("XY").box(tf,L,hf,centered=(True,True,False)).translate((x,0,z))
        if side=="out":
            try: f=f.edges("|Y").edges("<Z").fillet(min(0.5,tf/2-0.01))   # fin tip R0.5 (tip is at -hf)
            except Exception: pass
            if TAPER>0:  # 45 deg x TAPER chamfer on the lower (-y, z 690) fin end at the tip
                f=f.cut(cq.Workplane("YZ").polyline([(-L/2-1,-hf-1),(-L/2+TAPER+0.0,-hf-1),(-L/2+TAPER,-hf),(-L/2,-hf+TAPER),(-L/2-1,-hf+TAPER)]).close().extrude(tf+2,both=True).translate((x,0,0)))
        p=p.union(f)
    for zc in DRVZ(nd):  # G-TWI base 4xM2 30.6x25.6 (MAN-G-TWI p.79): clearance dia 2.4
        for sx in(-1,1):
            for sy in(-1,1):
                p=p.cut(cq.Workplane("XY").circle(1.2).extrude(tb+2).translate((sx*25.6/2,zc+sy*30.6/2,-1)))
    for sx in (-1,1):
        for sy in (-1,1):  # 4 standoff holes dia 3.4 (M3 into G10) at corners
            if side=="out": continue  # D93: knee plate held by 4 PEM FHS-M3 studs (inner face, 1.5 mm Al OK) + nuts behind the frame lip; no fin cut
            p=p.cut(cq.Workplane("XY").circle(1.7).extrude(tb+hf+2).translate((sx*(W/2-3),sy*(L/2-3),-hf-1)))
    return p
import sys,os
FH=float(os.environ.get("FH",18.5)); FT=float(os.environ.get("FT",0.75)); KN0=8; KW=float(os.environ.get("KW",46)); KN=int(os.environ.get("KN",8)); TAPER=float(os.environ.get("TAPER",8))
HP=float(sys.argv[1]) if len(sys.argv)>1 else 84.0
PLATES={ # name: (qty, drives/plate, carry W/drive, L, W, tb, nfins, hfin, tfin[, fin side, standoff mm])
 "knee":      (4,2,6.0,100,KW,1.5,KN,FH,FT,"out",0.0),    # D93 rev4 (D91: fins outward at 6 mm pitch (48/8), in stream beyond L51 26
 "hip_pitch": (4,1,6.2, HP,HP,1.5, 0,0,0),
 "ankle":     (4,1,3.0, 60,56,1.5, 0,0,0),
 "shoulder_pitch":(2,1,4.2,80,80,1.5,0,0,0),
}
PLATES={k:(v+("femur",8.5) if len(v)==9 else v) for k,v in PLATES.items()}
out={}; total=0.0
for n,(q,nd,pc,L,W,tb,nf,hf,tf,side,so) in PLATES.items():
    plates=q//nd if n=="knee" else q
    s=finned(L,W,tb,nf,hf,tf,nd,side)
    vol=s.val().Volume(); m=vol*RHO
    cq.exporters.export(s,f"cad/drive_plate_{n}.step")
    A=s.val().Area()/1e6 - nd*DRV[0]*DRV[1]/1e6  # wetted area minus drive-covered face
    if so<4.0: A-=0.7*L*W/1e6  # femur face in a <4 mm gap: credit 30% only [EST]
    if nf:
        mm=math.sqrt(2*8/(K*tf*1e-3)); eta=math.tanh(mm*hf*1e-3)/(mm*hf*1e-3)
    else: eta=0.97  # base spreading [EST]
    if side=="out":  # Thermal R131 rev2 basis: only the outer face + fins (open, black, >=6 mm pitch) at h; drive/femur side 0
        A=(L*W + nf*2*hf*L + nf*tf*L - nf*tf*L)/1e6 - 0.0  # base outer (roots~tips), fin faces
        A-=nd*4*math.pi*1.2**2/1e6
        A-=nf*2*(TAPER**2/2)/1e6   # D93 45 deg taper: triangle lost on both fin faces
        A_ref=(L*48+8*2*18.0*L)/1e6-nd*4*math.pi*1.2**2/1e6   # Thermal rev4 reference: 18 mm, no taper -> UA 0.246, standing 0.135
        thermal_rev4=dict(UA_h8_cal=round(0.246*A/A_ref,4),UA_stand_cal=round(0.135*A/A_ref,4),
            T_stand_duty_C=round(35+(75.5-35-3.6*RPAD)*A_ref/A+3.6*RPAD,1))
    res={}
    UA8=None
    for case,Q1,h in (("duty_h8",0.6*pc,8),("carry_cont_h8",pc,8),("carry_cont_h12",pc,12)):
        Q=Q1*nd; T=TAIR+Q/(h*A*eta)+Q1*RPAD
        res[case]=round(T,1)
        if h==8: UA8=round(h*A*eta,4)
    out[n]=dict(plates=plates,fin_side=side,standoff_mm=so,drives_per_plate=nd,L=L,W=W,t_base=tb,fins=nf,fin_h=hf,fin_t=tf,
               area_m2=round(A,4),fin_eta=round(eta,3),mass_g=round(m,1),T_base_C=res,
               pass_duty_h8=res["duty_h8"]<=80,UA_h8_WK=UA8,**(dict(thermal_rev4_scaled=thermal_rev4,taper_mm=TAPER) if side=="out" else {}),step=f"cad/drive_plate_{n}.step")
    total+=m*plates
# standoffs: G10 dia6x6 tube, 4/plate ~0.25 g each + M3 A2 screw 0.6 g x4 [EST]
nplates=sum(v["plates"] for v in out.values()); hw=nplates*4*(0.25+0.6)+nplates*0.1+2*0.6  # +Al foil femur shield 0.6 g/leg [EST];   # +1 serrated M3 washer/plate 0.1 g [EST]; M2 drive screws in R-141
out["_total"]=dict(plates_g=round(total,1),standoff_hw_g=round(hw,1),total_kg=round((total+hw)/1000,3),
  r136_booked_as_addition_kg="in -0.25 net Elmo credit (Thermal +0.21..0.26)")
json.dump(out,open("results/drive_heat_plates.json","w"),indent=1); print(json.dumps(out,indent=1))
# L51 envelope (Legs DECISIONS L51): box 26(x depth) x 52(y) x 104(z); plate y 106-154 (48), z 688-792
k=out["knee"]; # D91: plate outer face AT the 26 boundary (replaces ID shell locally); inward: base 1.5, pad 1.0, drive 14.9, PCB 1.6
stack=k["t_base"]+1.0+14.9+1.6; femur_gap=26-stack   # free gap PCB top -> femur (connector, foil shield)
k_fin_top=26+k["fin_h"]  # fin tips beyond the L51 box face
env=dict(depth_stack_mm=round(stack,2),femur_gap_mm=round(femur_gap,2),fin_protrusion_beyond_26_mm=k["fin_h"],fin_top_mm=k_fin_top,depth_margin_mm=round(26-stack,2),y_margin_mm=52-k["W"],z_margin_mm=104-k["L"],
         drives_on_plate_z_mm=2*DRV[0]+5, ok=stack<=26 and k["W"]<=52 and k["L"]<=104)
out["_L51_envelope"]=env; json.dump(out,open("results/drive_heat_plates.json","w"),indent=1); print(env)
