import os
p='/tmp/rl8/modules/design/cad/covers/hip_skirt_r8.py'
src=open(p).read().split("single=[b for b")[0]
src=src.replace("POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]",
 "POSES=[(p,r,y) for p in list(range(-105,41,5))+[-107.5,42.5] for r in (-20,-14.5,-12,-8,-4,0,5,10,15,17.5) for y in (-37.5,-35,-17,0,22,45,47.5)]")
src=src.replace("R1=dmin[0]-25","R1=152.8")
ns={'__file__':p}; exec(compile(src,'x','exec'),ns)
hem=ns['hem']
inrom=[(g,q) for g,q in hem if -12<=q[1]<=15 and -35<=q[2]<=45 and -105<=q[0]<=40]
ovt=[(g,q) for g,q in hem if -14.5<=q[1]<=17.5]
print('poses',len(hem)); print('min all',min(hem)); print('min ROM',min(inrom)); print('min ROM+ovt',min(ovt)); print('max ROM',max(inrom))
print('band all/ROM/ovt',sum(5<g<25 for g,q in hem),sum(5<g<25 for g,q in inrom),sum(5<g<25 for g,q in ovt))
print('frac >=100 ROM',round(sum(g>=100 for g,q in inrom)/len(inrom),2),'25-100',round(sum(25<=g<100 for g,q in inrom)/len(inrom),2))
lrb=[b for b in ns['lr_bad'] if b['q2']!=(0,0,0) and b['cause'].startswith('cover') and -14.5<=b['q'][1]<=17.5]
print('LR cover-bad ROM+ovt',len(lrb),sorted(lrb,key=lambda b:b['gap'])[:3])
r=[b for b in lrb if -12<=b["q"][1]<=15 and -35<=b["q"][2]<=45 and -105<=b["q"][0]<=40]; print("LR ROM-only",len(r),sorted(set((b["q"][1],b["q"][2]) for b in r)), min(b["q"][0] for b in r), max(b["q"][0] for b in r))
