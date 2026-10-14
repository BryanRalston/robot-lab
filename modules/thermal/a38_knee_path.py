# A38 rev: knee trunnion->femur path as a fin to the collar, plus hip break paths. RL Thermal hand calc.
import math, json
k=157; A=math.pi*0.050*0.0012; P=math.pi*0.050; L=0.160
def par(*r): return 1/sum(1/x for x in r)
out={}
for h in (12,20):
  m=math.sqrt(h*P/(k*A)); kAm=k*A*m
  for dTk_case,lab in ((60,'knee case 95C (carry)'),(50,'knee case 85C (walk)')):
    for Rtr in (2.5,5.0,30.0):              # housing->femur end via trunnion bearings/bracket; 30 = with a PEI break
      for rod in (58,85):                   # hip rod path w/o / with lever-eye sleeve
        Rb=par(26,rod)                      # tine break ø22 rev D (~26) || rod path
        for dTh,hl in ((50,'A35 h15'),(62.6,'vents short')):
          for Rc in (8,14):
            # unknowns thk (femur knee end), thc (collar). fin between them:
            # q_k_in = kAm(thk*cosh - thc)/sinh ; q_c_in = kAm(thk - thc*cosh)/sinh
            ch,sh=math.cosh(m*L),math.sinh(m*L); Gloc=0.10
            # knee node: (dTk-thk)/Rtr = Gloc*thk + kAm(thk*ch-thc)/sh
            # collar:   (dTh-thc)/Rb + kAm(thk-thc*ch)/sh = thc/Rc
            a11=1/Rtr+Gloc+kAm*ch/sh; a12=-kAm/sh; b1=dTk_case/Rtr
            a21=-kAm/sh; a22=1/Rb+1/Rc+kAm*ch/sh; b2=dTh/Rb
            det=a11*a22-a12*a21; thk=(b1*a22-a12*b2)/det; thc=(a11*b2-a21*b1)/det
            thc0=dTh*Rc/(Rb+Rc)   # no knee path (but same Rc)
            out[f'h{h}|{lab}|Rtr{Rtr}|rod{rod}|{hl}|Rc{Rc}']=dict(femur_knee_end=round(35+thk,1),bond=round(35+thc,1),bond_no_knee=round(35+thc0,1),knee_add_K=round(thc-thc0,1),Q_femur_W=round((dTk_case-thk)/Rtr,1))
json.dump(out,open('results/a38_knee_path.json','w'),indent=1)
for k_,v in out.items():
  if ('Rc14' in k_ or 'Rc8' in k_) and 'A35' in k_ and 'carry' in k_: print(k_,v)
