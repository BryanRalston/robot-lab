"""Shoulder pad R6 (R-060): 7075 doubler REPLACES the PC saddle; lot-tested 4.5 pcf core (Materials R042_EPP_SHOULDER.md: sigma band 1.87-2.47 MPa incl. rate 1.10-1.30, lot +-5 %)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
a=0.0609; t=0.055; A=a*a; EFF=0.72; SMIN,SMAX=1.87e6,2.47e6; FMAX=9170; E=265
Fpk=SMAX*A; Emin=SMIN*A*EFF*t
# doubler: 7075-T6 (sy ~500 MPa) flat 1.5 mm top plate on 4 ribs (1.5 mm, conformal to roll housing, avg 6.5 mm tall) at 20 mm pitch + integral 0.8 mm lips 6 mm tall (replace guide posts)
SY=500e6; tp=1.5e-3; pitch=0.020
M=SMAX*pitch**2/8; sig=M/(tp**2/6)
rib_bear=FMAX/(4*1.5e-3*0.061)
V=(a*a*tp)+4*(0.061*0.0065*1.5e-3)+4*(0.061*0.006*0.8e-3)
items=dict(core_HC_4p5pcf_61x61x55_lot_tested=A*t*72, face_plate_Al_0p3=A*0.3e-3*2700, doubler_7075_plate_ribs_lips=V*2810,
 retention_aramid_strap_plus_2_M3_in_doubler_lips=0.003, EPP80_face_4mm=A*0.004*80, face_sleeve_TPU_film=0.0025)
per=sum(items.values())
out=dict(location='ROLL-OUTPUT MOUNT (Arms c64ab91 R6 §5): pad on the upper-arm/roll-output lateral face at shoulder height; moves with roll; covers the Controls contact band at all roll angles; no overlap with the upper arm',
 load_path='core -> 7075 doubler (ribs land on the roll-output flange, 4x M4, 615 N shear each at 15 deg) -> roll output -> roll bearing -> shoulder_P bracket; bare 2 mm housing ring NOT loaded',
 fallback='shoulder_P-bracket load ring (Materials fd46ad8 ring frame) with pad raised to z>=+0.19 (covers band only 10 mm below / 21 mm above; arm 11 mm inboard of pad face -> risk of out-of-footprint arm hits on hip-first lean)',
 core='60.9x60.9x55 (61 nominal, 60.9 max) 4.5 pcf pre-crushed, lot-tested +-5 %',peak_kN=round(Fpk/1e3,2),M_Nm=round(Fpk*0.06),pass_peak=Fpk<=FMAX,E_min_J=round(Emin),pass_energy=Emin>=E,
 doubler=dict(top_plate_sigma_MPa=round(sig/1e6),SF=round(SY/sig,2),rib_bearing_MPa=round(rib_bear/1e6,1),shear_15deg_kN=round(FMAX*0.268/1e3,2),note='ribs conformal to roll housing carry compression to metal; lips locate core (no posts); 2 M3 lips also retain cosmetic cap'),
 mass_items_kg_side={k:round(v,4) for k,v in items.items()},kg_side=round(per,4),kg_pair=round(2*per,3),booked_R060=0.127,delta_vs_booked=round(2*per-0.127,3),vs_cap_0p100=round(2*per-0.100,3))
json.dump(out,open(os.path.join(H,'pad_r6.json'),'w'),indent=1); print(json.dumps(out,indent=1))
