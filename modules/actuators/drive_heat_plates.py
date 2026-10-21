"""R-134..R-136 Elmo G-TWI standoff heat plates (RL Actuators). CadQuery 2.8; light compute.
Losses: Thermal R131_ELMO_MG.md (MAN-G-TWI v2.011 §11.2.1 chart -25% + 1 W control).
Duty = 0.6 x carry (R-096). Air 35 C (T2 basis). Limit: baseplate <=80 C (85-5), derate starts 75.
Pad: 1 mm gap pad >=3 W/mK over drive base -> 0.3 K/W per drive. Plates on G10/PEEK standoffs: no motor heat.
"""
import json, math, cadquery as cq
RHO=2.70e-3  # 6061 g/mm^3
K=167.0; TAIR=35.0; RPAD=0.30; DRV=(35.0,30.0)  # drive footprint mm (L51/MAN-G-TWI)
def finned(L,W,tb,nf,hf,tf):
    p=cq.Workplane("XY").box(W,L,tb,centered=(True,True,False))
    pitch=W/max(nf,1)
    for i in range(nf):
        x=-W/2+pitch*(i+0.5)
        p=p.union(cq.Workplane("XY").box(tf,L,hf,centered=(True,True,False)).translate((x,0,-hf)))
    for sx in (-1,1):
        for sy in (-1,1):  # 4 standoff holes dia 3.4 (M3 into G10) at corners
            p=p.cut(cq.Workplane("XY").circle(1.7).extrude(tb+hf+2).translate((sx*(W/2-3),sy*(L/2-3),-hf-1)))
    return p
PLATES={ # name: (qty, drives/plate, carry W/drive, L, W, tb, nfins, hfin, tfin)
 "knee":      (4,2,6.0,100,48,1.5,12,8.0,1.0),   # 2 per leg on one plate; fins toward femur, L51 box 26 deep
 "hip_pitch": (4,1,6.2, 80,80,1.5, 0,0,0),
 "ankle":     (4,1,3.0, 60,56,1.5, 0,0,0),
 "shoulder_pitch":(2,1,4.2,80,80,1.5,0,0,0),
}
out={}; total=0.0
for n,(q,nd,pc,L,W,tb,nf,hf,tf) in PLATES.items():
    plates=q//nd if n=="knee" else q
    s=finned(L,W,tb,nf,hf,tf) if nf else finned(L,W,tb,0,0,0)
    vol=s.val().Volume(); m=vol*RHO
    cq.exporters.export(s,f"cad/drive_plate_{n}.step")
    A=s.val().Area()/1e6 - nd*DRV[0]*DRV[1]/1e6  # wetted area minus drive-covered face
    if nf:
        mm=math.sqrt(2*8/(K*tf*1e-3)); eta=math.tanh(mm*hf*1e-3)/(mm*hf*1e-3)
    else: eta=0.97  # base spreading [EST]
    res={}
    for case,Q1,h in (("duty_h8",0.6*pc,8),("carry_cont_h8",pc,8),("carry_cont_h12",pc,12)):
        Q=Q1*nd; T=TAIR+Q/(h*A*eta)+Q1*RPAD
        res[case]=round(T,1)
    out[n]=dict(plates=plates,drives_per_plate=nd,L=L,W=W,t_base=tb,fins=nf,fin_h=hf,fin_t=tf,
               area_m2=round(A,4),fin_eta=round(eta,3),mass_g=round(m,1),T_base_C=res,
               pass_duty_h8=res["duty_h8"]<=80,step=f"cad/drive_plate_{n}.step")
    total+=m*plates
# standoffs: G10 dia6x6 tube, 4/plate ~0.25 g each + M3 A2 screw 0.6 g x4 [EST]
nplates=sum(v["plates"] for v in out.values()); hw=nplates*4*(0.25+0.6)
out["_total"]=dict(plates_g=round(total,1),standoff_hw_g=round(hw,1),total_kg=round((total+hw)/1000,3),
  r136_booked_as_addition_kg="in -0.25 net Elmo credit (Thermal +0.21..0.26)")
json.dump(out,open("results/drive_heat_plates.json","w"),indent=1); print(json.dumps(out,indent=1))
# L51 envelope (Legs DECISIONS L51): box 26(x depth) x 52(y) x 104(z); plate y 106-154 (48), z 688-792
k=out["knee"]; stack=(k["fin_h"]+0.5)+k["t_base"]+1.0+14.4   # standoff=fin+0.5 clear, pad 1.0, drive 14.4
env=dict(depth_stack_mm=stack,depth_margin_mm=round(26-stack,2),y_margin_mm=52-k["W"],z_margin_mm=104-k["L"],
         drives_on_plate_z_mm=2*DRV[0]+5, ok=stack<=26 and k["W"]<=52 and k["L"]<=104)
out["_L51_envelope"]=env; json.dump(out,open("results/drive_heat_plates.json","w"),indent=1); print(env)
