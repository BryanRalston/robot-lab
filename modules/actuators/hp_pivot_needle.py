"""R4 M1(a): hip_pitch pivot as a needle-roller straddle instead of one CRBH 5013 A.
Two IKO TLA 3520 Z shell needle bearings (Fw 35, D 42, C 20, 43.5 g, C 20.7 kN, C0 42.3 kN; datasheets/iko_shell_needle_catalog.pdf p. TLA 35xx),
outer rings pressed in the two lever cheeks (ø42 N7, |y| 13.5..33.5), running directly on a case-hardened 16MnCr5 hollow shaft ø35/ø30 x 67
(HRC 58-64, raceway per IKO shaft spec) pressed into the femur tongue (|y| < 12.5). Axial: 2 PTFE/bronze thrust washers ø35/ø52 x 1.5 + 2 circlips.
IKO: shell bearings require static safety factor > 3. Loads as hp_bearing.py; moment carried as a couple over the bearing span."""
import json, os
H=os.path.dirname(os.path.abspath(__file__))
BW=65*9.81; Fs=454.2/0.050/2; Fa=0.3*BW; M_need=(180**2+66**2)**0.5; M_walk=M_need/1.5
C,C0,mb=20700,42300,0.0435; span=2*23.5/1000
Fr_max=(2*Fs+1.5*BW)/2+M_need/span
Fr_fault=(Fs+1.5*BW)/2+(M_need+Fs*0.069)/span
Pw=((2*Fs*0.52+1.5*BW)/2+M_walk/span)*0.65
L10h=(C/Pw)**(10/3)*1e6/(1/3)/3600
shaft=3.14159/4*(35**2-30**2)*67*7.85e-6
Ms=(2*Fs+1.5*BW)*span/4+M_need/2; Z=3.14159*(35**4-30**4)/(32*35); sig=Ms*1e3/Z
parts=dict(TLA3520Z_x2=2*mb,shaft_16MnCr5_35x30x67=shaft,thrust_washers_x2=2*0.006,circlips_x2=2*0.002)
out=dict(span_m=span,Fr_bearing_max_N=Fr_max,fs_max=C0/Fr_max,Fr_bearing_fault_N=Fr_fault,fs_fault=C0/Fr_fault,P_walk_N=Pw,L10_h_walking=L10h,
   shaft_bending_MPa=sig,parts=parts,mass_line=sum(parts.values()),crbh_line=0.314,delta_per_leg=sum(parts.values())-0.314,
   notes='fs >= 3 (IKO shell rule) in both cases; lever cheeks change -> lever FEA HUB=needle; lateral clearance rod (|y| 63) to cheek (33.5) = 29.5 mm; Legs: tongue bore ø80 -> ø35 press fit')
json.dump(out,open(f'{H}/results/hp_pivot_needle.json','w'),indent=1); print(json.dumps(out,indent=1))
