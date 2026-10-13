"""Speed-dependent motor loss (iron + rotor drag) from TBM2G datasheet rated points (datasheets/tbm2g_manual.pdf §9).
At the same winding limit (dT 130 K, '@155 C' rows) the motor delivers Tc130 at stall but only Trtd at Nrtd; the copper loss it gives up,
(Tc130^2 - Trtd^2)/Km_hot^2, is dissipated as speed-dependent loss at Nrtd. Two rated points (24 V and 48 V bus) give
P_fe(n) = a*n + b*n^2 (hysteresis + eddy), n in krpm. Run: python3 iron_loss.py -> results/iron_loss.json"""
import re, json, math, os
H=os.path.dirname(os.path.abspath(__file__)); T=open(f'{H}/datasheets/tbm2g_manual.txt').read().split('\n')
W={'A':0,'C':1,'D':2}
def section(m):
    i=[k for k,l in enumerate(T) if re.match(rf'^9\.[0-9.]+ {m} Frameless Motor Specifications',l)][-1]; return T[i:i+120]
def nums(l): return [float(x) for x in re.findall(r'\d+\.\d+|\d+',l)]
def fit(m,w):
    s=section(m); col=W[w]; pts=[]; mode=None; Tc=None; Km=None
    for l in s:
        if 'Max Cont. Torque for ΔT wdg. = 130' in l and Tc is None: Tc=nums(l.split('Nm')[1])[-3:][col]
        if 'Motor Constant' in l and Km is None: Km=nums(l.split('Km')[1])[-3:][col]
        if re.search(r'(24|48) V DC @ 155',l): mode=l
        elif re.search(r'@ (85|155)',l): mode=None
        if mode and 'Rated Torque' in l: Tr=nums(l.split('Nm')[1])[-3:][col]
        if mode and 'Rated Speed' in l: pts.append((Tr,nums(l.split('rpm')[1])[-3:][col]))
    if m=='TBM2G-07613' and w=='C': Km=0.201   # datasheet typo (D15)
    Kmh=Km/math.sqrt(1.4); P=[((Tc/Kmh)**2-(Tr/Kmh)**2,n/1000) for Tr,n in pts]
    (P1,n1),(P2,n2)=sorted(P,key=lambda x:x[1])[:2]
    b=(P2/n2-P1/n1)/(n2-n1); a=P1/n1-b*n1
    if a<0: a,b=0.0,P2/n2**2      # keep physical (non-negative hysteresis term)
    if b<0: a,b=P2/n2,0.0
    return dict(Tc130=Tc,Km=Km,points=pts,P_at_points=P,a_W_per_krpm=a,b_W_per_krpm2=b)
OUT={f'{m}{w}':fit(m,w) for m,w in [('TBM2G-07613','D'),('TBM2G-06013','D'),('TBM2G-06008','A'),('TBM2G-08508','A')]}
json.dump(OUT,open(f'{H}/results/iron_loss.json','w'),indent=1)
for k,v in OUT.items(): print(k,v['points'],[(round(p,1),n) for p,n in v['P_at_points']],round(v['a_W_per_krpm'],2),round(v['b_W_per_krpm2'],3))
