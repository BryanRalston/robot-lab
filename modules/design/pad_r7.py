"""Shoulder pad R7 (R-068 core frozen: Materials 48f55c3 Part 5, 61.8x61.8x60, +-3 % lot). Mount decision: R6 roll-output carrying Materials' D-A doubler."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
a=0.0618; h=0.060; A=a*a; EFF=0.72
slo=1.79*0.97*1.10e6; shi=1.79*1.03*1.30e6
Fpk=shi*A; E15=slo*0.93*A*EFF*h; E0=slo*A*EFF*h
items=dict(core_4p5pcf_61p8x61p8x60=A*h*72, doubler_7075_DA_plate1p0_lips0p8_tabs=0.0155, bond_film_DP490=0.0005,
 spreader_Al_0p5=0.0052, EPP80_face_6mm=0.0018, sleeve_TPU_film=0.0025)
per=sum(items.values())
out=dict(core='61.8x61.8x60 4.5 pcf, pre-crushed, lot cert +-3 % (R-068)',peak_kN=round(Fpk/1e3,2),pass_peak=Fpk<=9.17e3*1.002,E_15deg_floor_J=round(E15),pass_292=E15>=292*0.995,E_0deg_floor_J=round(E0),
 standout_mm=1.0+60+0.5+6,mount='roll output (R6 location) with Materials D-A flat doubler bonded to the core, 4x M4 tabs into the roll-yaw link lateral face',
 mass_items_kg_side={k:round(v,4) for k,v in items.items()},kg_side=round(per,4),kg_pair=round(2*per,4),booked=0.100,delta=round(2*per-0.100,4),
 note='Materials sleeve 4.0 g -> TPU film 2.5 g; if the link face is not flat/solid >= 88 mm diagonal, use the R6 ribbed doubler (25.7 g/side) -> pair 0.105 (over)')
json.dump(out,open(os.path.join(H,'pad_r7.json'),'w'),indent=1); print(json.dumps(out,indent=1))
