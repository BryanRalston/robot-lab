import math
sig=5.67e-8
def hr(e1,e2,T=60):return 4*sig*(273+T)**3/(1/e1+1/e2-1)
def UA(n=8,Hf=13,L=100,W=48,v=None,guard=True,eps_in=0.1):
  Hf*=1e-3;L*=1e-3;W*=1e-3
  A=n*2*Hf*L+W*L; m=math.sqrt(16/0.167);eta=math.tanh(m*(Hf+5e-4))/(m*(Hf+5e-4))
  rad=hr(0.85,0.9,55)*W*L*1.3*((0.6+0.4*(0.35 if eps_in<0.5 else 0.6)) if guard else 1)
  gf=0.85 if guard else 1
  if v is None: # standing Elenbaas
    s=5e-3;Ra=9.81/330*36*s**4/(1.7e-5*2.4e-5*L);Nu=Ra/24*(1-math.exp(-35/Ra))**0.75
    return (Nu*0.027/s*A*eta)*(0.95 if guard else 1)+rad
  mcp=(n-1)*5e-3*Hf*v*gf*1.15*1007;hA=20*A*eta;return mcp*(1-math.exp(-hA/mcp))+rad
def h8(n=8,Hf=13,L=100,W=48,guard=True):
  A=n*2*Hf*1e-3*L*1e-3+W*L*1e-6+n*1e-3*L*1e-3;return 8*A*0.994*(0.9 if guard else 1)
def Tbase(UAo,Q):
  G=UAo+0.012+0.016+0.027;Tp=(Q+(UAo+0.028)*35+0.027*45)/G;return Tp+Q/2*0.3
def Tguard(Tfin,eps_in,walk,Tgap=None):
  hri=4*sig*(273+Tfin-15)**3/(1/0.95+1/eps_in-1);ho=(10 if walk else 4)+6;hi=5 if walk else 3
  Tg=Tgap or (35+(6 if walk else 10))
  return (hri*Tfin+hi*Tg+ho*35)/(hri+hi+ho)
print('W/m mass g per fin per mm',0.27)
cases=[('rev3 bare',dict(guard=False)),('rev3+guard',{}),('Hf18',dict(Hf=18)),('Hf20',dict(Hf=20)),('Hf22',dict(Hf=22)),('L130',dict(L=130)),('L130 Hf18',dict(L=130,Hf=18)),('W60 n10',dict(n=10,W=60)),('W60 n10 Hf18',dict(n=10,W=60,Hf=18))]
for nm,k in cases:
  kk={x:y for x,y in k.items() if x!='guard'};g=k.get('guard',True)
  ua=[h8(**kk,guard=g),UA(**k,v=0.2),UA(**k,v=0.4),UA(**k)]
  Tb=[Tbase(u,7.2) for u in ua]
  n=k.get('n',8);Hf=k.get('Hf',13);L=k.get('L',100);W=k.get('W',48)
  mass=(n*Hf*L*1+W*L*1.5)*2.7e-3+ (0 if not g else 18*(L+10)/110*(1+(Hf-13)/40))
  print(nm,'UA h8/w.2/w.4/stand',[round(u,3) for u in ua],'Tb duty',[round(t,1) for t in Tb],'mass g',round(mass,1))
for e in (0.9,0.1):
  for Tf,walk,lab in ((68,1,'walk duty'),(80,0,'stand duty'),(84,0,'stand carry derate 85')):
    print('guard eps_in',e,lab,round(Tguard(Tf,e,walk),1))
